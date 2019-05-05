# PAWK - A Python line processor (like AWK)

PAWK aims to bring the full power of Python to AWK-like line-processing.

Here are some quick examples to show some of the advantages of pawk over AWK.

The first example transforms `/etc/hosts` into a JSON map of host to IP:

	cat /etc/hosts | pawk -B 'd={}' -E 'json.dumps(d)' '!/^#/ d[f[1]] = f[0]'

Breaking this down:

1. `-B 'd={}'` is a begin statement initializing a dictionary, executed once before processing begins.
2. `-E 'json.dumps(d)'` is an end statement expression, producing the JSON representation of the dictionary `d`.
3. `!/^#/` tells pawk to match any line *not* beginning with `#`.
4. `d[f[1]] = f[0]` adds a dictionary entry where the key is the second field in the line (the first hostname) and the value is the first field (the IP address).

And another example showing how to bzip2-compress + base64-encode a file:

	cat pawk.py | pawk -E 'base64.encodestring(bz2.compress(t))'

### AWK example translations

Most basic AWK constructs are available. You can find more idiomatic examples below in the example section, but here are a bunch of awk commands and their equivalent pawk commands to get started with:

Print lines matching a pattern:

	ls -l / | awk '/etc/'
	ls -l / | pawk '/etc/'

Print lines *not* matching a pattern:

	ls -l / | awk '!/etc/'
	ls -l / | pawk '!/etc/'

Field slicing and dicing (here pawk wins because of Python's array slicing):

	ls -l / | awk '/etc/ {print $5, $6, $7, $8, $9}'
	ls -l / | pawk '/etc/ f[4:]'

Begin and end end actions (in this case, summing the sizes of all files):

	ls -l | awk 'BEGIN {c = 0} {c += $5} END {print c}'
	ls -l | pawk -B 'c = 0' -E 'c' 'c += int(f[4])'

Print files where a field matches a numeric expression (in this case where files are > 1024 bytes):

	ls -l | awk '$5 > 1024'
	ls -l | pawk 'int(f[4]) > 1024'

Matching a single field (any filename with "t" in it):

	ls -l | awk '$NF ~/t/'
	ls -l | pawk '"t" in f[-1]'

## Installation

It should be as simple as:

```
pip install pawk
```

But if that doesn't work, just download the `pawk.py`, make it executable, and place it somewhere in your path.

## Expression evaluation

PAWK evaluates a Python expression or statement against each line in stdin. The following variables are available in local context:

- `line` - Current line text, including newline.
- `l` - Current line text, excluding newline.
- `n` - The current 1-based line number.
- `f` - Fields of the line (split by the field separator `-F`).
- `nf` - Number of fields in this line.
- `m` - Tuple of match regular expression capture groups, if any.


In the context of the `-E` block:

- `t` - The entire input text up to the current cursor position.

If the flag `-H, --header` is provided, each field in the first row of the input will be treated as field variable names in subsequent rows. The header is not output. For example, given the input:

```
count name
12 bob
34 fred
```

We could do:

```
$ pawk -H '"%s is %s" % (name, count)' < input.txt
bob is 12
fred is 34
```

To output a header as well, use `-B`:

```
$ pawk -H -B '"name is count"' '"%s is %s" % (name, count)' < input.txt
name is count
bob is 12
fred is 34
```

Module references will be automatically imported if possible. Additionally, the `--import <module>[,<module>,...]` flag can be used to import symbols from a set of modules into the evaluation context.

eg. `--import os.path` will import all symbols from `os.path`, such as `os.path.isfile()`, into the context.

## Output

### Line actions

The type of the evaluated expression determines how output is displayed:

- `tuple` or `list`: the elements are converted to strings and joined with the output delimiter (`-O`).
- `None` or `False`: nothing is output for that line.
- `True`: the original line is output.
- Any other value is converted to a string.

### Start/end blocks

The rules are the same as for line actions with one difference.  Because there is no "line" that corresponds to them, an expression returning True is ignored.

	$ echo -ne 'foo\nbar' | pawk -E t
    foo
    bar


## Command-line usage

```
Usage: cat input | pawk [<options>] <expr>

A Python line-processor (like awk).

See https://github.com/alecthomas/pawk for details. Based on
http://code.activestate.com/recipes/437932/.

Options:
  -h, --help            show this help message and exit
  -I <filename>, --in_place=<filename>
                        modify given input file in-place
  -i <modules>, --import=<modules>
                        comma-separated list of modules to "from x import *"
                        from
  -F <delim>            input delimiter
  -O <delim>            output delimiter
  -L <delim>            output line separator
  -B <statement>, --begin=<statement>
                        begin statement
  -E <statement>, --end=<statement>
                        end statement
  -s, --statement       DEPRECATED. retained for backward compatibility
  -H, --header          use first row as field variable names in subsequent
                        rows
  --strict              abort on exceptions
```

## Examples

### Line processing

Print the name and size of every file from stdin:

	find . -type f | pawk 'f[0], os.stat(f[0]).st_size'

> **Note:** this example also shows how pawk automatically imports referenced modules, in this case `os`.

Print the sum size of all files from stdin:

	find . -type f | \
		pawk \
			--begin 'c=0' \
			--end c \
			'c += os.stat(f[0]).st_size'

Short-flag version:

	find . -type f | pawk -B c=0 -E c 'c += os.stat(f[0]).st_size'


### Whole-file processing

If you do not provide a line expression, but do provide an end statement, pawk will accumulate each line, and the entire file's text will be available in the end statement as `t`. This is useful for operations on entire files, like the following example of converting a file from markdown to HTML:

	cat README.md | \
		pawk --end 'markdown.markdown(t)'

Short-flag version:

	cat README.md | pawk -E 'markdown.markdown(t)'

