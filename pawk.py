#!/usr/bin/env python

"""
cat input | pawk [<options>] <expr>

A Python line-processor (like awk).

See https://github.com/alecthomas/pawk for details. Based on
http://code.activestate.com/recipes/437932/.
"""

import inspect
import optparse
import re
import sys


class Action(object):
    def __init__(self, arg):
        self._parse_command(arg)

    def match(self, line):
        if self.pattern is None:
            return self.negate
        match = self.pattern.search(line)
        if match is not None:
            return None if self.negate else match.groups()
        elif self.negate:
            return ()

    def _parse_command(self, arg):
        match = re.match(r'(?:(!)?/((?:\\.|[^/])+)/)?(.*)', arg)
        negate, self.pattern, self.cmd = match.groups()
        self.cmd = self.cmd.strip()
        self.negate = bool(negate)
        if self.pattern is not None:
            self.pattern = re.compile(self.pattern)


def process(context, delim, odelim, begin_statement, action, end_statement, as_statement, strict):
    if begin_statement:
        begin = compile(begin_statement, 'BEGIN', 'exec')
        eval(begin, globals(), context)

    context['m'] = ()

    _codeobj = compile(action.cmd, 'EXPR', 'exec' if as_statement else 'eval')
    write = sys.stdout.write

    for numz, line in enumerate(sys.stdin):
        match = action.match(line)
        if match is None:
            continue
        context['m'] = match
        context['line'] = line
        l = context['l'] = line.strip()
        context['n'] = numz + 1
        context['f'] = [w for w in l.split(delim) if w]
        context['nf'] = len(context['f'])
        try:
            result = eval(_codeobj, globals(), context)
        except:
            if strict:
                raise
            continue
        if as_statement:
            continue
        if result is None or result is False:
            continue
        elif result is True:
            result = line
        elif isinstance(result, (list, tuple)):
            result = odelim.join(map(str, result))
        else:
            result = str(result)
        write(result)
        if not result.endswith('\n'):
            write('\n')

    if end_statement:
        end = compile(end_statement, 'END', 'exec')
        eval(end, globals(), context)


def parse_commands(arg):
    match = re.match(r'(?:/((?:\\.|[^/])+)/)?(.*)', arg)
    return match.groups()


def main():
    parser = optparse.OptionParser()
    parser.set_usage(__doc__.strip())
    parser.add_option('-i', '--import', dest='imports', help='comma-separated list of modules to "from x import *" from', metavar='<modules>')
    parser.add_option('-F', dest='delim', help='input delimiter', metavar='<delim>', default=None)
    parser.add_option('-O', dest='delim_out', help='output delimiter', metavar='<delim>', default=' ')
    parser.add_option('-B', '--begin', help='begin statement', metavar='<statement>')
    parser.add_option('-E', '--end', help='end statement', metavar='<statement>')
    parser.add_option('-s', '--statement', action='store_true', help='execute <expr> as a statement instead of an expression')
    parser.add_option('--strict', action='store_true', help='abort on exceptions')

    context = {}

    options, args = parser.parse_args(sys.argv[1:])
    if options.imports:
        for imp in options.imports.split(','):
            m = __import__(imp.strip(), fromlist=['.'])
            context.update((k, v) for k, v in inspect.getmembers(m) if k[0] != '_')

    delim = options.delim.decode('string_escape') if options.delim else None
    odelim = options.delim_out.decode('string_escape')

    action = Action(' '.join(args).strip())
    if not action.cmd:
        if options.statement:
            context['t'] = ''
            action.cmd = 't += l'
        else:
            action.cmd = 'l'

    # Auto-import. This is not smart.
    all_text = ' '.join([(options.begin or ''), action.cmd, (options.end or '')])
    modules = re.findall(r'([\w.]+)+(?=\.\w+)\b', all_text)
    for m in modules:
        try:
            key = m.split('.')[0]
            context[key] = __import__(m)
        except:
            pass
    try:
        process(context, delim, odelim, options.begin, action, options.end, options.statement, options.strict)
    except EnvironmentError as e:
        # Workaround for close failed in file object destructor: sys.excepthook is missing lost sys.stderr
        # http://stackoverflow.com/questions/7955138/addressing-sys-excepthook-error-in-bash-script
        print >> sys.stderr, str(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    main()
