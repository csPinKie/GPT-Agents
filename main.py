import os
import itertools
import random
import openai

api_key = 'enter api key here'
api_key1 = 'enter api key here'
api_key2 = 'enter api key here'

instructions = 'Enter Problem Solving Task instructions here'
list_of_items = ['enter item list here']
items_message = 'The list of items are: ' + ', '.join(list_of_items)
end_prompt = "End of conversation"
end_system_message = f'Once after there has been a discussion and all agents agree on ONE finalized list' \
                     f' each agent has to write the following exact message:' \
                     f' {end_prompt}'

discussion_instructions = 'enter discussion instructions here' \


class Client:
    def __init__(self, client_id, _api_key):
        self.client_id = client_id
        self.is_finished = False
        self.api_client = openai.Client(api_key=_api_key)
        self.messages_history_output = []
        self.prompt= ""
        self.get_user_prompt()
        self.messages_history = [

            {'role': 'system', 'content': instructions + items_message},
            {'role': 'system', 'content': f'You are identified by {client_id}.'},
           # {'role': 'system', 'content': self.prompt},   #disable if you want agents to have no persona
            {'role': 'user', 'content': 'Start the conversation'},
            # {'role': 'system', 'content': 'Provide your responses based on the information given,'
            #                               ' without simulating a conversation yourself.'},
            {'role': 'user', 'content': 'Make a list of the most important items and present it.'},
        ]
        self.messages_history_output = self.messages_history_output + self.messages_history

    def add_message(self, client_id, message):
        if not message.startswith(str(client_id)):
            message = f'{client_id}: {message}'
        if client_id == self.client_id:
            self.add_response(client_id, message)
        else:
            self.add_agent_response(client_id, message)

    def add_agent_response(self, client_id, message):
        self.messages_history.append({'role': 'user', 'content': message})
        self.messages_history_output.append({'role': client_id, 'content': message})

    def add_response(self, client_id, message):
        self.messages_history.append({'role': 'assistant', 'content': message})
        self.messages_history_output.append({'role': client_id, 'content': message})

    def get_response(self) -> str:
        try:
            _response = self.api_client.chat.completions.create(
                #model='gpt-4o',
                model='gpt-3.5-turbo',
                messages=self.messages_history,
                temperature=1.2,
                presence_penalty=0.1,
                max_tokens=700
            )
            return _response.choices[0].message.content
        except openai.APIError as e:
            print(f'An error occured: {e}')
            return ""

    def add_instructions(self):
        self.messages_history.append({'role': 'assistant', 'content': discussion_instructions})
        self.messages_history_output.append({'role': 'assistant', 'content': discussion_instructions})

    def add_user_message(self, message):
        self.messages_history.append({'role': 'user', 'content': message})
        self.messages_history_output.append({'role': 'user', 'content': message})

    def get_user_prompt(self):
        if self.client_id == "agent_1":
            self.prompt =  f"You are {self.client_id}. ######Enter Leader Prompt here."
        elif self.client_id == "agent_2":
            self.prompt = f"You are {self.client_id}. ######Enter Member Prompt here."
        else:  # for agent_3
            self.prompt = f"You are {self.client_id}. Y#####Enter Member prompt here."


def add_message_to_all_clients(msg_from_id, message):
    for _agent in agent_list:
        _agent.add_message(msg_from_id, message)


def add_message_to_all_clients_history(msg_from_id, message):
    for _agent in agent_list:
        _agent.messages_history_output.append({'role': _agent.client_id, 'content': message})

#make role promt for each agent

agent_list = [
    Client("agent_1", api_key),
    Client("agent_2", api_key1),
    Client("agent_3", api_key2)
]

possible_speaking_orders = list(itertools.permutations(agent_list, len(agent_list)))

total_max_rounds = 1 # change amount script is looped
total_rounds = 0
while total_rounds < total_max_rounds:

    first_round_messages = {}
    agent_1 = agent_list[0]
    agent: Client
    for agent in agent_list:
        response = agent.get_response()
        first_round_messages[agent.client_id] = response
        agent.add_message(agent.client_id, response)
        if agent.client_id is not agent_1.client_id:
            agent_1.messages_history_output.append(
                {'role': 'log', 'content': f"--- {agent.client_id} conversation prep ---"})
            agent_1.messages_history_output += agent.messages_history
           # agent_1.messages_history_output.append({'role': agent.client_id, 'content': response})
        agent.add_user_message(
                                discussion_instructions
                               + "The other agents have no knowledge of your list/ranking keep that in mind."
                               + "So you might want to share it with them."
                               )

    # for agent in first_round_messages.keys():
    #     add_message_to_all_clients(agent, first_round_messages[agent])

    # for agent in agent_list:
    #     agent.add_instructions()
    #     agent.add_system_message()


    last_agent = agent_list[0]
    conversation_end = False
    max_rounds = 10 # change amount of rounds per agent conversation
    rounds = 0
    while not conversation_end and rounds < max_rounds:
        if len(agent_list) <= 2:
            agent_list.reverse()
            random_combination = agent_list
        else:
            _temp = [x for x in possible_speaking_orders if x[0] != last_agent]
            random_combination = random.choice(_temp)
        agent: Client
        for agent in random_combination:
            response = agent.get_response()
            if response:
                add_message_to_all_clients(agent.client_id, response)
            if end_prompt in response:
                agent.is_finished = True
        conversation_end = all(agent.is_finished for agent in agent_list)
        rounds += 1

    # gen file name and folder by timestamp
    folder_name = 'conversations3.5-turbo'
    # create folder if not exists
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    # get len of folder contents
    folder_len = len(os.listdir(folder_name))
    file_name = f'{folder_name}/conversation_{folder_len}.txt'
    # generate a file with all responses
    with open(file_name, 'x') as f:
        agent1 = agent_list[0]
        for _msg in agent1.messages_history_output:
            f.write(f"{_msg['role']}:| {_msg['content']}\n")
            f.write(f"---------------------------------|\n")

    total_rounds += 1