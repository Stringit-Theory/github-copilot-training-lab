# Good Prompts vs. Bad Prompts for GitHub Copilot

## What makes a good prompt?

A good prompt gives GitHub Copilot enough context to understand the task and enough constraints to produce code that fits the project. It usually includes:

- **Goal:** What should the code do?
- **Context:** Which language, framework, files, or existing functions are involved?
- **Inputs and outputs:** What data goes in, and what result is expected?
- **Constraints:** What rules, edge cases, or performance requirements matter?
- **Validation:** Which tests or examples should prove that the code works?

## Comparison

| Good prompt | Bad prompt |
| --- | --- |
| Specific about the desired behavior | Vague about the outcome |
| Includes relevant project context | Gives no language or file context |
| Describes inputs, outputs, and edge cases | Leaves important details to guesswork |
| States constraints and preferred patterns | Does not mention requirements or limitations |
| Requests tests or a way to verify the result | Assumes generated code will be correct |
| Asks for one focused change | Combines many unrelated tasks |

## Example 1: Function

### Bad prompt

```text
Write a function to process users.
```

This does not say what “process” means, what language to use, what the input looks like, or what the function should return.

### Good prompt

```text
In Python, add a function named group_active_users to user_utils.py.
It should accept a list of user dictionaries and return a dictionary keyed by
department containing only users whose active field is true. Preserve the
original user dictionaries, handle an empty list by returning {}, and add
pytest tests for multiple departments, inactive users, and missing departments.
```

## Example 2: Bug fix

### Bad prompt

```text
Fix this code. It does not work.
```

### Good prompt

```text
The calculate_total function in cart.py applies the discount twice when a cart
contains more than one item. Fix the smallest part of the implementation that
causes this behavior. Keep the existing public function signature, preserve
the current tax calculation, and add a regression test showing that a cart
with two items applies the discount exactly once.
```

## Example 3: Command-line script

### Bad prompt

```text
Create a file search script.
```

### Good prompt

```text
Create a Ruby command-line script named find_files.rb. Accept one filename
from ARGV, recursively search the script's directory for regular files whose
basename exactly matches that filename, and print each matching file's path
and contents. Print a usage message and exit with status 1 when no argument is
provided. Report no matches clearly, and do not follow directory entries as
files. Keep the implementation dependent only on Ruby's standard library.
```

## A useful prompt pattern

```text
In [language/framework], modify [file or component] to [desired behavior].
Inputs are [inputs], and the result should be [output]. Handle [edge cases].
Keep [constraints or existing APIs] unchanged. Add or update [tests] and
verify the implementation with [validation command or examples].
```

## Before accepting generated code

1. Check that it matches the requested behavior.
2. Review error handling, security, and edge cases.
3. Run the relevant tests, linter, or type checker.
4. Ask Copilot to explain or revise any code you do not understand.
