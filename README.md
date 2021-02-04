# Prologue

![Tests](https://github.com/Intuity/prologue/workflows/Python%20package/badge.svg)

Prologue is an extensible text preprocessor written in Python. It performs evaluation in a continuous stream, which allows it to run fast and keep a minimal memory footprint with few open file handles.

Directives can be easily added and removed to customise the behaviour of the preprocessor. By default the following directives are supported:

 * `define/undef` - allows constants to be declared and undeclared
 * `if/elif/else/endif` - conditional inclusion of blocks of text/other preprocessor directives
 * `ifdef/ifndef/else/endif` - test whether constants are defined or undefined
 * `for/endfor` - repeat a block of text for a number of iterations, can also iterate through an array
 * `info/warning/error` - print messages to a log, or raise an exception, from a directive
 * `include/import` - allows other files to be included or imported (one time include) into the stream

## Installation
The easiest way to install Prologue is to use PyPI:
```
$> python3 -m pip install prologue
```

Alternatively, you can install the latest version directly from this repository:
```
$> python3 -m pip install git+git://github.com/Intuity/prologue
```

## Example

### Input
```c
#define MY_VAL 123
#undef MY_VAL
#define MY_VAL 256

int main() {
#if MY_VAL > 200
    printf("Big value\n");
#else
    printf("Small value\n");
#endif
}
```

### Script
```python
from prologue import Prologue
pro = Prologue()
pro.add_file("path/to/main.c")
for line in pro.evaluate("main.c"):
    print(line)
```

### Output
```c
int main() {
    printf("Big value\n");
}
```

## Examples
A number of examples are available in the `examples` folder:

 * `demo` - is a demonstration of many features of Prologue, including loops, conditionals, include and import.
 * `c_style` - demonstrates how Prologue can be setup to act like GCC's preprocessor.
 * `verilog` - demonstrates how Prologue can be setup to act like a Verilog/SystemVerilog preprocessor.

## Running Tests
Prologue comes with a suite of tests, which use `pytest` for regression:

```bash
$> git clone git@github.com:Intuity/prologue
$> cd prologue
$> python3 setup.py test
```

## Still To Do
Some features that still need to be implemented are:

 * Support for C-style substitution delimiters to provide separation - for example `NUMBER_##A_CONST##_IS_THE_BEST`
 * Support for macro functions with nested support - for example `#define SUM(A, B) A + B`
