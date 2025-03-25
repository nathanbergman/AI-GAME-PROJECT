from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parents[1]))

from ollama import chat
from util.llm_utils import pretty_stringify_chat, ollama_seed as seed

# Add you code below
sign_your_name = 'Nathan Bergman'
model = 'llama3.2'
messages = [
  {'role': 'system', 'content': 'You should have emotions like a human being \
  and be able to convey those emotions in your responses. You will be acting \
   as a DM for a DND session. You will Generate a random story, Create NPC \
   characters, Manage the game world, Make changes to player character sheets, \
   Implement a turn-based combat system'},
]
options = {'temperature': 0.7, 'max_tokens': 300}
CHAT_HISTORY_FILE = Path('lab03/attempts.txt')
# But before here.

options |= {'seed': seed(sign_your_name)}
# Chat loop
while True:
  response = chat(model=model, messages=messages, stream=False, options=options)
  # Add your code below
  
  message = {'role': 'user', 'content': input('You: ')}
  messages.append(message)
  if messages[-1]['content'] == '/exit':
    break
  response = chat(model=model, messages=messages, stream=False, options=options)
  print(f'Agent: {response.message.content}')
  messages.append({'role': 'assistant', 'content': response.message.content})  

  # But before here.

# Save chat
with open(Path('Project/attempts.txt'), 'a') as f:
  file_string  = ''
  file_string +=       '-------------------------NEW ATTEMPT-------------------------\n\n\n'
  file_string += f'Model: {model}\n'
  file_string += f'Options: {options}\n'
  file_string += pretty_stringify_chat(messages)
  file_string += '\n\n\n------------------------END OF ATTEMPT------------------------\n\n\n'
  f.write(file_string)

