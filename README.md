# PAWK - A Python line processor (like AWK)

PAWK aims to bring the full power of Python to AWK-like line-processing.

## Examples

***Note:** most flags have short versions but the long versions are shown here for clarity.*
		
Print the name and size of every file from stdin:
	
	find . -type f | pawk 'f[0], os.stat(f[0]).st_size'

Print the sum size of all files from stdin:

	find . -type f | \
		pawk \
			--statement \
			--begin 'c=0' \
			--end 'print c' \
			'c += os.stat(f[0]).st_size'

Short-flag version:

	find . -type f | pawk -sB c=0 -E 'print c' 'c += os.stat(f[0]).st_size'

PAWK can also operate on entire files. This is useful for operations on entire files, like converting a file from markdown to HTML:

If we're evaluating statements (via `--statement`) and do not provide a line statement, a default statement accumulates the entire input text into the variable `t`. 

	cat README.md | \
		pawk \
			--statement \
			--end 'print markdown.markdown(t)'

Short-flag version:

	cat README.md | pawk -sE 'print markdown.markdown(t)'
		
## Expression evaluation

PAWK evaluates a Python expression (or statement if `--statement` is provided) with the following variables in local context:

- `l` - Current line text, including newline.
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