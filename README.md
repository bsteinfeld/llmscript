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

# Examples:

## Get a prime number

```python
instruction='a prime number between 100 and 400'

llm = llmscript.LLMScript()
prime = llm.run_langchain(instruction, int)
```

## Add a random name to a list

```python
mylist = ['John', 'Mary']
instruction='x = a random British sounding name; {append({x})}'
llm = llmscript.LLMScript(mylist)
llm.run_langchain(instruction)
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
isSenior = llm.run_langchain(instruction, str)
```

## Pass in local variables for easy reference

```python
import llmscript
instruction='respond with the genus of {animal} as a single word'

llm = llmscript.LLMScript()
genus = llm.run_langchain(instruction, int, localVariables={"animal": "dog"})
```

## Debug mode for inspecting whats going on

```python
instruction='{_append(1)}; {_append(2)}; {_append(3)}'
llm = llmscript.LLMScript(db)
result = llm.run_langchain(instruction, debug=True)
```