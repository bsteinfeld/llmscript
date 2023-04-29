import pytest

import llmscript

class Test:
  def __init__(self, inside):
    self.inside = inside
    self.count = 0

  def abc(self, val):
    print(f"{self.inside} and {val}")

  def increment(self):
    self.count += 2
    print(f"count is {self.count}")
    return self.count

  def add(self, a, b):
    return a + b

def test_function_print(capfd):
    a = Test("b")
    instruction='x={_add(1,2)}; {abc({x})}'

    llm = llmscript.LLMScript(a)
    llm.run_langchain(instruction)
    captured = capfd.readouterr()
    assert captured.out == "b and 3\n"

def test_function_print_twice(capfd):
    a = Test("b")
    instruction='x={_add(1,2)}; {abc({x})}; {abc({x})}'

    llm = llmscript.LLMScript(a)
    llm.run_langchain(instruction)
    captured = capfd.readouterr()
    assert captured.out == "b and 3\nb and 3\n"

def test_simple_prime():
    instruction='a prime number between 10 and 12'

    llm = llmscript.LLMScript()
    prime = llm.run_langchain(instruction, int)
    assert prime == 11

def test_complex_prime():
    a = Test(12)
    instruction='a prime number between {_add(9,1)} and {inside}'

    llm = llmscript.LLMScript(a)
    prime = llm.run_langchain(instruction, int)
    assert prime == 11

def test_change_variable():
    a = Test("empty")
    a.inside = ["bob", "tony", "phil"]
    instruction='return a random name from {inside}'

    llm = llmscript.LLMScript(a)
    name = llm.run_langchain(instruction, str)
    assert name in ["bob", "tony", "phil"]

def test_changing_variable():
    a = Test("empty")
    instruction='{_increment()} {_increment()} {_increment()} return {count}'

    llm = llmscript.LLMScript(a)
    count = llm.run_langchain(instruction, int, debug=True)
    assert count == 6

def test_pass_local_variable():
    instruction='return what genus of animal is {animal} in a single word'

    llm = llmscript.LLMScript()
    genus = llm.run_langchain(instruction, str, localVariables={"animal": "dog"})
    assert genus == 'Canis'

def test_fake_db():
    class FakeDB:
        def getUser(self, name):
            users = {
                "bob": { "age": 65 },
                "sue": { "age": 12 },
            }
            return users[name]

    db = FakeDB()
    llm = llmscript.LLMScript(db)
    
    instruction='if {_getUser("bob")} is a senior citizen return "senior" else return "not senior"'
    result = llm.run_langchain(instruction, str)
    assert result == "senior"

    instruction='if {_getUser("sue")} is a senior citizen return "senior" else return "not senior"'
    result = llm.run_langchain(instruction, str)
    assert result == "not senior"
