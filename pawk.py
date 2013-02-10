#!/usr/bin/env python

"""cat input | pawk [<options>] <expr>

A Python line-processor (like awk).

See https://github.com/alecthomas/pawk for details. Based on
http://code.activestate.com/recipes/437932/.
"""

import inspect
import optparse
import re
import sys


class Action(object):
    """Represents a single action to be applied to each line."""

    def __init__(self, pattern=None, cmd='l', statement=False, negate=False):
        self.delim = None
        self.odelim = ' '
        self.negate = negate
        self.pattern = None if pattern is None else re.compile(pattern)
        self.context = {'m': ()}
        self.cmd = cmd
        self._compile(statement)

    @classmethod
    def from_options(cls, options, arg):
        self = cls()
        self.negate, self.pattern, self.cmd = self._parse_command(arg)
        self.context = self._context_from_options(options)
        self._compile(options.statement)
        return self

    def _compile(self, statement):
        self._codeobj = compile(self.cmd, 'EXPR', 'exec' if statement else 'eval')

    def apply(self, numz, line):
        """Apply action to line."""
        match = self._match(line)
        if match is None:
            return None
        l = line.strip()
        f = [w for w in l.split(self.delim) if w]
        self.context.update(
            m=match,
            line=line,
            l=l,
            n=numz + 1,
            f=f,
            nf=len(f),
            )
        return eval(self._codeobj, globals(), self.context)

    def _context_from_options(self, options):
        context = {
            'm': (),
        }
        if options.imports:
            for imp in options.imports.split(','):
                m = __import__(imp.strip(), fromlist=['.'])
                context.update((k, v) for k, v in inspect.getmembers(m) if k[0] != '_')

        self.delim = options.delim.decode('string_escape') if options.delim else None
        self.odelim = options.delim_out.decode('string_escape')
        if not self.cmd:
            if options.statement:
                context['t'] = ''
                self.cmd = 't += l'
            else:
                self.cmd = 'l'

        # Auto-import. This is not smart.
        all_text = ' '.join([(options.begin or ''), self.cmd, (options.end or '')])
        modules = re.findall(r'([\w.]+)+(?=\.\w+)\b', all_text)
        for m in modules:
            try:
                key = m.split('.')[0]
                context[key] = __import__(m)
            except:
                pass
        return context

    def _match(self, line):
        if self.pattern is None:
            return self.negate
        match = self.pattern.search(line)
        if match is not None:
            return None if self.negate else match.groups()
        elif self.negate:
            return ()

    def _parse_command(self, arg):
        match = re.match(r'(?:(!)?/((?:\\.|[^/])+)/)?(.*)', arg)
        negate, pattern, cmd = match.groups()
        cmd = cmd.strip()
        negate = bool(negate)
        if pattern is not None:
            pattern = re.compile(pattern)
        return negate, pattern, cmd


def process(input, output, begin_statement, action, end_statement, strict):
    """Process a stream."""
    if begin_statement:
        begin = compile(begin_statement, 'BEGIN', 'exec')
        eval(begin, globals(), action.context)

    write = output.write
    try:
        old_stdout_write = sys.stdout.write
        sys.stdout.write = write

        for numz, line in enumerate(input):
            try:
                result = action.apply(numz, line)
            except:
                if strict:
                    raise
                continue
            if result is None or result is False:
                continue
            elif result is True:
                result = line
            elif isinstance(result, (list, tuple)):
                result = action.odelim.join(map(str, result))
            else:
                result = str(result)
            write(result)
            if not result.endswith('\n'):
                write('\n')

        if end_statement:
            end = compile(end_statement, 'END', 'exec')
            eval(end, globals(), action.context)
    finally:
        sys.stdout.write = old_stdout_write


# For integration tests.
def run(argv, input, output):
    parser = optparse.OptionParser()
    parser.set_usage(__doc__.strip())
    parser.add_option('-i', '--import', dest='imports', help='comma-separated list of modules to "from x import *" from', metavar='<modules>')
    parser.add_option('-F', dest='delim', help='input delimiter', metavar='<delim>', default=None)
    parser.add_option('-O', dest='delim_out', help='output delimiter', metavar='<delim>', default=' ')
    parser.add_option('-B', '--begin', help='begin statement', metavar='<statement>')
    parser.add_option('-E', '--end', help='end statement', metavar='<statement>')
    parser.add_option('-s', '--statement', action='store_true', help='execute <expr> as a statement instead of an expression')
    parser.add_option('--strict', action='store_true', help='abort on exceptions')

    options, args = parser.parse_args(argv[1:])
    action = Action.from_options(options, ' '.join(args).strip())
    process(input, output, options.begin, action, options.end, options.strict)


def main():
    try:
        run(sys.argv, sys.stdin, sys.stdout)
    except EnvironmentError as e:
        # Workaround for close failed in file object destructor: sys.excepthook is missing lost sys.stderr
        # http://stackoverflow.com/questions/7955138/addressing-sys-excepthook-error-in-bash-script
        print >> sys.stderr, str(e)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == '__main__':
    main()
