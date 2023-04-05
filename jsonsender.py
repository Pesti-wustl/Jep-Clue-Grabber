import asyncio
import json
import requests

curr_game_id = 15
with open(f'./json_clues/game_{curr_game_id}.json', 'r') as f:
    data = json.load(f)


response = requests.put('http://localhost:8080/jepClues', json=data)
if (response.status_code == 400):
    print("oh no")
    with open(f'./game_statuses.txt', 'a') as f:
        f.write(f"GAME {curr_game_id}: FAILURE\n")
        f.close()
else:
    print("yay")
    with open(f'./game_statuses.txt', 'a') as f:
        f.write(f"GAME {curr_game_id}: SUCCESS\n")
        f.close()

"""
random_fun = requests.get('http://localhost:8080/random')
random_json = random_fun.json()
print(f"Clue Category: {random_json['clue_category']}")
print(f"Question: {random_json['clue_question']}")
print(f"Answer: {random_json['clue_answer']}")
"""
