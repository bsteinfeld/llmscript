llmscript
---------

llmscript's main goal is making it as easy as possible to use llm logic within your own projects.

Compared to native code it is slow, so this is not meant to be used for performance critical code.

It's great for prototyping, learning, implementing various forms of logic with no need to worry about the underlying implementation, libraries, etc.

# Features:

- Super easy to use existing classes or implement your own logic, simply pass an instance of a class and you're good to go.
- A basic and easy to understand syntax.
- Ability to return typed values from your logic.

# Installation and Setup:

## Install the package

```bash
pip install llmscript
```

## Setup API Key
export OPENAI_API_KEY="<your openapi api key>"


# Basic Usage:

## Create an instance of LLMScript

```python
# Basic with no context
llm = llmscript.LLMScript()

# Basic with context (that can be later referenced in your logic)
llm = llmscript.LLMScript(context)
```

## Run a script

```python
# Just run the script with no return value
# This can be useful for running scripts that have side effects
llm.run("...")

# Run a script and return a value
llm.run("...", int)
llm.run("...", str)
llm.run("...", dict)

# Run a script with local variables
genus = llm.run("1+{number}", str, localVariables={"number": 1})

# Run a script in debug mode
llm.run(instruction, debug=True)
```

## Explaination of instruction syntax

Everything special is wrapped in curly braces.

- Immediate Actions
    - These cause LLMScript to immediately execute the action (e.g. python method call).
    - Every execution of an immediate action will require an extra call to the LLM.
    - Example: `{_methodname(arg1, arg2, ...)}`
- Delayed Actions
    - These cause LLMScript to delay the action until the end of the script.
    - Does not induce a call to the LLM.
    - Example:  `{methodname(arg1, arg2, ...)}`
- Variables
    - These are used to reference variables that are passed in to the script.
    - These can reference local variables or context variables.
    - Example: `{variableName}`


# Examples:

## Get a prime number

```python
instruction='a prime number between 100 and 400'

llm = llmscript.LLMScript()
prime = llm.run(instruction, int)
```

## Add a random name to a list

```python
mylist = ['John', 'Mary']
instruction='x = a random British sounding name; {append({x})}'
llm = llmscript.LLMScript(mylist)
llm.run(instruction)
# mylist will now contain a third name
```

## Query a db and return based on a condition

```python
class ExampleDB:
    ...
    def getUser(self, name):
        ...

db = ExampleDB()
instruction='if {_getUser("bob")} is a senior citizen return "senior" else return "not senior"'
llm = llmscript.LLMScript(db)
isSenior = llm.run(instruction, str)
```

## Pass in local variables for easy reference

```python
instruction='respond with the genus of {animal} as a single word'

llm = llmscript.LLMScript()
genus = llm.run(instruction, str, localVariables={"animal": "dog"})
```

## Debug mode for inspecting whats going on

```python
instruction='{_append(1)}; {_append(2)}; {_append(3)}'
llm = llmscript.LLMScript(db)
result = llm.run(instruction, debug=True)
```