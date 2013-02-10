# PAWK - A Python line processor (like AWK)

PAWK aims to bring the full power of Python to AWK-like line-processing.

## Expression evaluation

PAWK evaluates a Python expression (or statement if `--statement` is provided) against each line in stdin. The following variables are available in local context:

- `line` - Current line text, including newline.
- `l` - Current line text, excluding newline.
- `n` - The current 1-based line number.
- `f` - Fields of the line (split by the field separator `-F`).
- `nf` - Number of fields in this line.

Additionally, the `--import <module>[,<module>,...]` flag can be used to import symbols from a set of modules into the evaluation context.

eg. `--import os.path` will import all symbols from `os.path`, such as `os.path.isfile()`, into the context.

## Output

The type of the evaluated expression determines how output is displayed:

- `tuple` or `list`: the elements are converted to strings and joined with the output delimiter (`-O`).
- `None` or `False`: nothing is output for that line.
- Any other value is converted to a string.

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
			--end 'print c' \
			'c += os.stat(f[0]).st_size'

Short-flag version:

	find . -type f | pawk -sB c=0 -E 'print c' 'c += os.stat(f[0]).st_size'
	
Transform `/etc/hosts` into a JSON map of host to IP:

	cat /etc/hosts | pawk -sB 'd={}' -E 'print json.dumps(d)' \
		'if not l.startswith("#"): d[f[1]] = f[0]'
	
### Whole-file processing

If statement mode (`-s`)is enabled and you do not provide a line expression, pawk will accumulate each line, and the entire file's text will be available in the end statement as `t`. This is useful for operations on entire files, like the following example of converting a file from markdown to HTML:

	cat README.md | \
		pawk \
			--statement \
			--end 'print markdown.markdown(t)'

Short-flag version:

	cat README.md | pawk -sE 'print markdown.markdown(t)'
		
