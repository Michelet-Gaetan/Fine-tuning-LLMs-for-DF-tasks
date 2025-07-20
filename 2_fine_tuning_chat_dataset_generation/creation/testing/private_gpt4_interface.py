from dotenv import load_dotenv

import os

import httpx

from openai import AzureOpenAI

import json

 

#Add your own API Endpoint and Key
AZURE_OPENAI_ENDPOINT = 'YOUR_API_ENDPOINT'
AZURE_OPENAI_KEY = 'YOUR_API_KEY'

load_dotenv()

 
#Initialize the parameters and data structures. Don't forget to add your own API proxy if you have one
class DefaultConversationalHandler:

    def __init__(self):
        self.openai_key = AZURE_OPENAI_KEY
        self.openai_api_base = AZURE_OPENAI_ENDPOINT
        self.openai_api_version = "2024-02-15-preview"
        self.deployment_name = "chat"
        self.proxies = {
            'http://': 'YOUR_PROXY',
            'https://': 'YOUR_PROXY'
        }
        self.proxy_client = httpx.Client(proxies=self.proxies)
        self.client = AzureOpenAI(
            api_key=self.openai_key, 
            api_version=self.openai_api_version,
            azure_endpoint=self.openai_api_base,
            http_client=self.proxy_client
        )

	#creates the history data structure that will keep track of the requests and answer. The initialization is already present
        self.history = [{
            "role": "system", 
            "content": "You are a helpful assistant. Generate responses accurately and truthworthiliy."
            }]

	#contains the next prompt
        self.next_prompt = []


    #resets the history
    def clear_history(self):
        self.history = [{
            "role": "system", 
            "content": "You are a helpful assistant. Generate responses accurately and truthworthiliy."
            }]
        
    #removes the next prompt
    def clear_prompt(self):
        self.next_prompt = []

    #resets the history and removes the next prompt
    def clear_all(self):
        self.history = [{
            "role": "system", 
            "content": "You are a helpful assistant. Generate responses accurately and truthworthiliy."
            }]
        self.next_prompt = []

    #lets the user chose the next action and implements it
    def interact_with_user(self):
        inp = str(input("Please enter your command (type 'help()' for help): "))

        if inp == 'quit()':
            print("Program is closing")
            return 0
        
        elif inp == 'see_prompt()':
            self.see_prompt()
            self.interact_with_user()

        elif inp == 'submit_prompt()':
            self.submit_prompt()
            self.interact_with_user()

        elif inp == 'help()':
            self.provide_help()
            self.interact_with_user()

        elif inp.startswith('save(') and inp.endswith(')'):
            params = str(inp).strip('save(').strip(')')
            self.save(params)
            self.interact_with_user()

        elif inp.startswith('load(') and inp.endswith(')'):
            params = str(inp).strip('load(').strip(')')
            self.load(params)
            self.interact_with_user()

        elif inp.startswith('add_message(') and inp.endswith(')'):
            params = str(inp).strip('add_message(').strip(')').split(",")
            if len(params) == 1:
                self.add_message(params[0])
            elif len(params) ==2:
                self.add_message(params[0],params[1])
            else:
                print("There is a problem with your parameters")
            self.interact_with_user()

        elif inp.startswith('add_file(') and inp.endswith(')'):
            params = str(inp).strip('add_file(').strip(')').split(",")
            print(params)
            if len(params) == 1:
                self.add_file(params[0])
            elif len(params) == 2:
                self.add_file(params[0],params[1])
            elif len(params) == 3:
                self.add_file(params[0],params[1],params[2])
            else:
                print("There is a problem with your parameters")
            self.interact_with_user()

        else:
            print('unkonwn command')
            self.interact_with_user()

        return 0

    #loads a conversation saved in a file
    def load(self,file_path):
        try:
            with open(file_path,'r') as f:
                self.history = json.load(f)
        except:
            print("there is a problem with the file provided")

        return 0

    #saves a conversation in a file
    def save(self,file_path):
        try:
            with open(file_path,'w') as f:
                json.dump(self.history,f)
        except:
            print("there is a problem with the file provided")

        return 0

    #display the next prompt
    def see_prompt(self):
        if self.next_prompt == []:
            print('The next prompt is currently empty')

        else:
            print('Current prompt: \n' + ''.join([(str(k['role']) + ': ' + str(k['content']) + '\n') for k in self.next_prompt]))

        return 0
 
    #sends the next prompt to the model and returns the response
    def submit_prompt(self, verb=False):

        if self.next_prompt == []:
            print('The next prompt is currently empty')

	#submit the prompt to the model
        else:

            response = self.client.chat.completions.create(

                model=self.deployment_name,

		#the history is added to the next prompt to provide all the discussion
                messages=(self.history + self.next_prompt),

                temperature=0.7,

                max_tokens=800,

                top_p=0.95,

                frequency_penalty=0,

                presence_penalty=0,

                stop=None,

            )

            if not response.choices:

                raise ValueError("No choices found in the response from Azure OpenAI.")

            #retrieves the role from the response
            message_role = response.choices[0].message.role
	    #retrieves the message from the response
            message_content = response.choices[0].message.content

            if message_content is None or message_role is None:
                print("Problem, the answer is None, retrying")
                return self.submit_prompt(verb)

	    #if verbose mode is active, displays the history, prompt submitted, and response
            if verb:
                print('History: \n\t' + ''.join([(str(k['role']) + ': ' + str(k['content']) + '\n\t') for k in self.history]))

                print('Prompt submitted: \n\t' + ''.join([(str(k['role']) + ': ' + str(k['content']) + '\n\t') for k in self.next_prompt]))

                print('Anwser received: \n\t' + message_content + '\n')

	    #adds the propmpt and response to the history
            self.history += self.next_prompt

            self.history += [{"role": message_role, "content": message_content}]

	    #clears the next prompt
            self.next_prompt = []

        return message_content


    #adds a message provided by the user to the next prompt
    def add_message(self,user_messages,context_messages=None):      

        if context_messages is None:
                context_messages = []       

	#if there is no context, just add the user/message, otherwise also add the context
        try:
            if context_messages == []:
                self.next_prompt += [{"role": "user", "content": user_messages}]
            else:
                self.next_prompt += [{"role": "system", "content": context_messages}] + [{"role": "user", "content": user_messages}]
        except:
            print('problem with the add_message command submitted')
    
        return 0

    # allows the user to add the content of a txt file with or without another message to the next prompt
    def add_file(self,file_path,user_messages=None,context_messages=None):           

        if user_messages is None:
                user_messages = []  

        if context_messages is None:
                context_messages = []  

	#if there is no context, just add the user/message and user/file, otherwise also add the context
	#if there is no message, just add the user/file, otherwise also add the context
        try:
            with open(file_path,'r') as f:
                lines = ''.join(f.readlines())
            if context_messages == [] and user_messages == []:
                self.next_prompt += [{"role": "user", "content": "File: " + lines}]

            elif context_messages == [] and user_messages != []:
                self.next_prompt += [{"role": "user", "content": user_messages}] + [{"role": "user", "content": "File: " + lines}]

            elif context_messages != [] and user_messages == []:
                self.next_prompt += [{"role": "context_provider", "content": context_messages}] + [{"role": "user", "content": "File: " + lines}]
            else:
                self.next_prompt += [{"role": "context_provider", "content": context_messages}] + [{"role": "user", "content": user_messages}] + [{"role": "user", "content": "File: " + lines}]
        except:
            print('problem with the add_file command submitted')
    
        return 0

    #displays the possible commands    
    def provide_help(self):

        print(
              "\nHere are the available commands:\n\n"
              "Use 'quit()' to exit the program\n"
              "Use 'see_prompt()' to see the prompt that you've been building\n"
              "Use 'submit_prompt()' to submit the prompt you've been building\n"
              "Use 'add_message(user_messages)' to add a message, only the user_mesage is mandatory\n"
              "Use 'add_file(file_path,user_messages,context_messages)' to add a file with a comment, the only mandatory parameter is the file_path\n"
              "Use 'save(file_path)' to save the state of the chat to a file\n"
              "Use 'load(file_path)' to load the state of a chat from a file\n"
              )
        
        return 0


# Example usage:

if __name__ == "__main__":

    handler = DefaultConversationalHandler()
    response = handler.interact_with_user()
