
from langchain import PromptTemplate, FewShotPromptTemplate
from langchain.llms import OpenAI
# from langchain.chat_models import ChatOpenAI

import re
import json
import random
import string

from dotenv import load_dotenv
load_dotenv()

def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


class LLMScript:
    def __init__(self, context=None):
        self.context = context
        self.set_methods_and_variables()

    def run(self, instrution, returnClass=None):
        """
        The main method
        """

        result = run_langchain(self, instruction, returnClass)

        return result

    def set_methods_and_variables(self):
        self.methods = {}
        self.variables = {}

        for attr in dir(self.context):
            if not attr.startswith('__'):  # Ignore attributes starting with '__'
                attribute = getattr(self.context, attr)

                if callable(attribute):  # Check if it's a method
                    self.methods[attr] = attribute
                else:  # Otherwise, it's a variable
                    self.variables[attr] = attribute

        return self.methods, self.variables

        

    def run_langchain(self, instruction, returnClass=None, localVariables=None, debug=False):
        """
        The LLM code
        """

        self.set_methods_and_variables()

        # examples = [{'type': 'Local Variable', 'name': key, 'value': f" = {value}"} for key, value in self.variables.items()]

        examples = [{'type': 'Local Variable', 'name': key, 'value': f" = {str(value).replace('{', '{{').replace('}', '}}')}" if isinstance(value, dict) else f" = {value}"} for key, value in self.variables.items()]

        if localVariables is not None:
            examples.extend([{'type': 'Local Variable', 'name': key, 'value': f" = {str(value).replace('{', '{{').replace('}', '}}')}" if isinstance(value, dict) else f" = {value}"} for key, value in localVariables.items()])

        examples.extend([{'type': 'Action', 'name': key, 'value': ''} for key, value in self.methods.items()])

        example_formatter_template = '- {type}: {name}{value}'
        example_prompt = PromptTemplate(
            input_variables=["type", "name", "value"],
            template=example_formatter_template,
        )


#         prefix = '''Below will be an instruction I'd like you to follow. Do not just return what the instruction says, but follow it and respond as if you are a human expert.

# The instruction may contain actions in the format of _action(arg1, ..., argN) or _action(arg1, ..., argN)_.
# - Delayed Actions are prefixed with a single underscore (_) and NO trailing underscores. They are queued up to be run after the expression is finished.
#     - Never returns anything or sets variables
#     - e.g. _print("Hello") which will call the print function with the argument "Hello"
#     - These will be returned in the actions array. For example: {{ "actions": [ {{ "name": "print", "args": ["Hello"] }} ] }}
# - Immediate Actions are prefixed with a single underscore (_) as well as a trailing underscore and are run immediately when it's reached
#     - Can optionally set a local variable
#     - e.g. _open("file.txt")_ which after responding will call the open function with the argument "file.txt"
#     - If you find an immediate action stop processing the instruction, set action to this value and return right away, awaiting a subsequent call to finish.
#     - Example return value will look like: {{ "action": {{ "name": "open", "args": ["file.txt"] }} }}
#     - If there is no immediate action found, do NOT set action and continue processing the instruction.

# Your response will be formatted in JSON as follows:
# {{
#     "action": {{ "name": "<actionname>", "args": [<arg1>, ..., <argN>] }},
#     "actions": [{{ "name": "<action1name>", "args": [<arg1>, ..., <argN>] }}, ... {{ "name": "<actionNname>", "args": [<arg1>, ..., <argN>] }}],
#     "response": <response>
# }}

# Response is {returnClass}.

# There will be no other output or explainations.

# The following is a list of variables and actions you have access to:
# '''
#         suffix = '''
# Variables are called in the instructions via curvy brackets, e.g. {{name}} or {{}}. Please fill in the variables as appropriate in the instruction below.

# If the instruction contains variables which are not defined, assume they are english instructions and follow them as such. For example {{a random prime number}} would be replaced with a random prime number like 11, not the string "a random prime number".

# Ensure your response is in JSON format as specified above. Do not include backticks (`) in your response.

# Instruction:

# {instruction}
# '''

        prefix = '''Below will be an instruction I'd like you to follow. Do not just return what the instruction says, but follow it and respond as if you are a human expert.

The instructions may contain actions. There are two types of actions and both are only found between curly brackets, e.g.{{print("hello)}} or {{_open("file.txt")}}.
- Delayed Actions are are queued up to be run after the expression is finished.
    - Never returns anything or sets variables
    - e.g. print("Hello")
    - These will be returned in the delayed_actions array. For example: {{ "delayed_actions": [ {{ "name": "print", "args": ["Hello"] }} ] }}
- Immediate Actions  are run immediately when they are reached.
    - They are always between curly braces like delayed action, except they are also prefixed with an underscore (_)
    - Can optionally set a local variable
    - e.g. _open("file.txt")
    - If you find an immediate action stop processing the instruction immediately, set immediate_action to this value and respond right away.
    - Only process one immediate action at a time.
    - Example response value will look like: {{ "immediate_action": {{ "name": "open", "args": ["file.txt"] }} }}
    - If there is no immediate action found, do NOT set action and continue processing the instruction.

The main difference between calling a delayed and immediate action is the underscore prefix that only immediate actions have.
{returnClass}

There will be no other output or explainations.

The following is a list of variables and actions you have access to:
'''
        suffix = '''
Variables are called in the instructions via curvy brackets, e.g. {{name}} or {{}}. Please fill in the variables as appropriate in the instruction below.

If the instruction contains variables which are not defined, assume they are english instructions and follow them as such. For example {{a random prime number}} would be replaced with a random prime number like 11, not the string "a random prime number".

Ensure your response is in JSON format as specified above. Do not include backticks (`) in your response.

Instruction:

{instruction}
'''

        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix,
            suffix=suffix,
            input_variables=["instruction", "returnClass"],
            example_separator="\n\n",
        )

        if returnClass == str:
            format_string = '''Your response will be formatted in JSON as follows:
{{
    "immediate_action": {{ "name": "<actionname>", "args": [<arg1>, ..., <argN>] }},
    "delayed_actions": [{{ "name": "<action1name>", "args": [<arg1>, ..., <argN>] }}, ... {{ "name": "<actionNname>", "args": [<arg1>, ..., <argN>] }}],
    "response": "<response>"
}}

Response is a String. Ensure you follow the instructions and do NOT just return the instruction string unless it's within double quotes.'''
        elif returnClass == dict:
            format_string = '''Your response will be formatted in JSON as follows:
{{
    "immediate_action": {{ "name": "<actionname>", "args": [<arg1>, ..., <argN>] }},
    "delayed_actions": [{{ "name": "<action1name>", "args": [<arg1>, ..., <argN>] }}, ... {{ "name": "<actionNname>", "args": [<arg1>, ..., <argN>] }}],
    "response": {{ <response> }}
}}

Response is JSON.'''
        elif returnClass in (int, float):
            format_string = '''Your response will be formatted in JSON as follows:
{{
    "immediate_action": {{ "name": "<actionname>", "args": [<arg1>, ..., <argN>] }},
    "delayed_actions": [{{ "name": "<action1name>", "args": [<arg1>, ..., <argN>] }}, ... {{ "name": "<actionNname>", "args": [<arg1>, ..., <argN>] }}],
    "response": <response>
}}

Response is a number.'''
        elif returnClass is None:
            format_string = '''Your response will be formatted in JSON as follows:
{{
    "immediate_action": {{ "name": "<actionname>", "args": [<arg1>, ..., <argN>] }},
    "delayed_actions": [{{ "name": "<action1name>", "args": [<arg1>, ..., <argN>] }}, ... {{ "name": "<actionNname>", "args": [<arg1>, ..., <argN>] }}]
}}
'''
        else:
            format_string = '''Your response will be formatted in JSON as follows:
{{
    "immediate_action": {{ "name": "<actionname>", "args": [<arg1>, ..., <argN>] }},
    "delayed_actions": [{{ "name": "<action1name>", "args": [<arg1>, ..., <argN>] }}, ... {{ "name": "<actionNname>", "args": [<arg1>, ..., <argN>] }}],
    "response": "<response>"
}}

Response is a String.'''

        the_prompt = few_shot_prompt.format(instruction=instruction, returnClass=format_string)
        
        if debug:
            print("The Prompt is:")
            print(the_prompt)

        llm = OpenAI(temperature=0.5, model_name="gpt-4")
        # llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo")
        # llm = OpenAI(temperature=0.9, model_name="text-davinci-003")

        response = llm(the_prompt)

        if debug:
            print("The Response is:")
            print(response)

        responseJSON = json.loads(response)

        if 'immediate_action' in responseJSON and responseJSON['immediate_action'] is not None and 'name' in responseJSON['immediate_action']:
            action = responseJSON['immediate_action']['name']
            args = responseJSON['immediate_action']['args']
            value = self.methods[action](*args)

            if localVariables is None:
                localVariables = {}
            
            # pattern = r"{_%s+\()}" % action
            pattern = r"{_%s\([^)]*?\)}" % action

            if value is None:
                instruction = re.sub(pattern, "", instruction, count=1)
            else:
                newname = action + generate_random_string(5)
                localVariables[newname] = value
                instruction = re.sub(pattern, f"{{{newname}}}", instruction, count=1)
                print("Local Variables Are")
                print(localVariables)

            return self.run_langchain(instruction, returnClass=returnClass, localVariables=localVariables, debug=debug)
        
        elif 'delayed_actions' in responseJSON  and responseJSON['delayed_actions'] is not None:
            actions = responseJSON['delayed_actions']
            for action in actions:
                if debug:
                    print("Running action: ", action['name'])
                    print("args: ", action['args'])
                
                self.methods[action['name']](*action['args'])

        if 'response' in responseJSON:
            return responseJSON['response']

