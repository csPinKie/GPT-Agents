import os
import itertools
import random

import openai

api_key = 'enter openai api key here'

instructions = 'enter instructions here'
list_of_items = [enter item list here]
items_message = 'The list of items are: ' + ', '.join(list_of_items)


class Client:
    def __init__(self, client_id, _api_key):
        self.client_id = client_id
        self.api_client = openai.Client(api_key=_api_key)
        self.messages_history_output = []
        self.messages_history = [
            {'role': 'system', 'content': instructions + items_message},
            {'role': 'user', 'content': 'Make a list of the most important items and present it.'},
        ]

    def get_response(self) -> str:
        try:
            _response = self.api_client.chat.completions.create(
                model='gpt-4o',
                #model='gpt-3.5-turbo',
                messages=self.messages_history,
                max_tokens=400,
                presence_penalty=0.1,
                temperature=1.2
            )
            return _response.choices[0].message.content
        except openai.APIError as e:
            error_msg = f"An error occurred: {e}"
            print(error_msg)
            return error_msg


agent_list = [
    Client("agent_1", api_key),
]

agent_1 = agent_list[0]
max_rounds = 1
rounds = 0
while rounds <= max_rounds:
    agent: Client
    response = agent_1.get_response()
    agent_1.messages_history_output.append(response)
    rounds += 1

# gen file name and folder by timestamp
folder_name = 'single_suggestions'
# create folder if not exists
if not os.path.exists(folder_name):
    os.makedirs(folder_name)
# get len of folder contents
folder_len = len(os.listdir(folder_name))
file_name = f'{folder_name}/conversation_{folder_len}.txt'
# generate a file with all responses
with open(file_name, 'x') as f:
    agent1 = agent_list[0]
    for i, _msg in enumerate(agent1.messages_history_output):
        f.write(f"-------- Iteration {i} --------\n")
        f.write(_msg)
        f.write("\n\n")
