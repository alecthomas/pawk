# PAWK - A Python line processor (like AWK)

PAWK aims to bring the full power of Python to AWK-like line-processing.

Here are some quick examples to show some of the advantages of pawk over AWK.

The first example transforms `/etc/hosts` into a JSON map of host to IP:

	cat /etc/hosts | pawk -sB 'd={}' -E 'json.dumps(d)' '!/^#/ d[f[1]] = f[0]'

And another example showing how to bzip2-compress + base64-encode a file:

	cat pawk.py | pawk -sE 'print base64.encodestring(bz2.compress(t))'

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
	ls -l | pawk -s -B 'c = 0' -E 'c' 'c += int(f[4])'

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

But if that doesn't work, just download the `pawk.py`, make it execuatable, and place it somewhere in your path.

## Expression evaluation

PAWK evaluates a Python expression (or statement if `--statement` is provided) against each line in stdin. The following variables are available in local context:

- `line` - Current line text, including newline.
- `l` - Current line text, excluding newline.
- `n` - The current 1-based line number.
- `f` - Fields of the line (split by the field separator `-F`).
- `nf` - Number of fields in this line.
- `m` - Tuple of match regular expression capture groups, if any.

Additionally, the `--import <module>[,<module>,...]` flag can be used to import symbols from a set of modules into the evaluation context.

eg. `--import os.path` will import all symbols from `os.path`, such as `os.path.isfile()`, into the context.

## Output

### Line actions

The type of the evaluated expression determines how output is displayed:

- `tuple` or `list`: the elements are converted to strings and joined with the output delimiter (`-O`).
- `None` or `False`: nothing is output for that line.
- `True`: the original line is output.
- Any other value is converted to a string.

### Start/end blocks

End and begin blocks are statements, but if the result of the statement is not `None` it will be displayed via `repr()`. This is a useful shortcut for non-string values, but strings will look like their Python representation:

	$ echo -ne 'foo\nbar' | pawk -sE t
	'foo\nbar'	

Explicitly print the output if this is not desirable:

	$ echo -ne 'foo\nbar' | pawk -sE 'print t'
	foo
	bar


## Examples

### Line processing

Print the name and size of every file from stdin:

	find . -type f | pawk 'f[0], os.stat(f[0]).st_size'

> **Note:** this example also shows how pawk automatically imports referenced modules, in this case `os`.

Print the sum size of all files from stdin:

	find . -type f | \
		pawk \
			--statement \
			--begin 'c=0' \
			--end c \
			'c += os.stat(f[0]).st_size'

Short-flag version:

	find . -type f | pawk -sB c=0 -E c 'c += os.stat(f[0]).st_size'


### Whole-file processing

If statement mode (`-s`)is enabled and you do not provide a line expression, pawk will accumulate each line, and the entire file's text will be available in the end statement as `t`. This is useful for operations on entire files, like the following example of converting a file from markdown to HTML:

	cat README.md | \
		pawk \
			--statement \
			--end 'print markdown.markdown(t)'

Short-flag version:

	cat README.md | pawk -sE 'print markdown.markdown(t)'

