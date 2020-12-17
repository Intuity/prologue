# Prologue
Extensible block-based preprocessor written in Python

## Running Tests
Prologue comes with a suite of tests, which use `pytest` for regression:

```bash
$> git clone git@github.com:Intuity/prologue
$> cd prologue
$> python3 setup.py test
```

## Progress
 * File registry (coded)
 * Directives registry (coded)
 * File stream reading (coded)
 * Anchored and floating directive recognition (coded)
 * Context object to track stack, defines, etc (coded)
 * Tag open/close/transition tracking (coded)
 * Migrate directives to use class to track state (coded)
 * Support context forking/joining (coded)
 * Context's formal stack deprecated in favour of parent pointers (coded)
 * Basic evaluation working, not yet taking account of conditions (coded)
 * Add proper evaluation of conditions (coded)
 * Value substitution - recognise defined values and substitute for them. (coded)
 * Line spanning - recognise \ at the end of the line and concatenate consecutive lines together. (coded)
 * Line concatenation into loop/condition - lines within blocks need to be held until the correct condition evaluates them. (coded)

## Still to Do
 * Source file and line number tracking.
 * Add C-style delimiter support to provide separation e.g.: ```MY_##CONST##_VALUE```.
 * Macro functions.
