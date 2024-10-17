"""
doc https://developers.notion.com/docs/create-a-notion-integration

## STEP 1: Setup integration
    - Create new integration: https://www.notion.so/profile/integrations/form/new-integration
    - Copy API token (secret code)
    - Give wanted autorization (read, edit, etc)
    - Go to the notion page
    - Copy database id (notion page id in url)
    - Add connection: ... > Connection > Connect to > select your integration

## STEP 2: Setup script
    - Define const NOTION_API_TOKEN and DATABASE_ID

optional ?
    - pip install notion-client
    - 

# python3 -m venv notion-automation
source notion-automation/bin/activate                                    
python3 -m pip install requests
"""
import os
import json
import requests

# Notion API token
NOTION_API_TOKEN = "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"
DATABASE_ID = "122acdc2cc5880fa8643c616c6778bbb"

# Headers for Notion API requests
headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 1. Function to fetch all Kanban cards from the database
def fetch_kanban_cards(database_id):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    response = requests.post(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# 2. Function to filter Kanban cards based on responsible person and status (optional filters)
def filter_kanban_cards(cards, responsible_id=None, status_name=None):
    filtered_cards = []
    
    for result in cards:
        properties = result['properties']
        
        # Extract relevant fields
        responsible_person_id = properties['Responsable']['people'][0]['id'] if properties['Responsable']['people'] else None
        card_status = properties['Statut']['status']['name'] if properties['Statut']['status'] else None
        title = properties['Nom']['title'][0]['text']['content'] if properties['Nom']['title'] else "No Title"
        
        # Apply filters (if any)
        if (responsible_id is None or responsible_person_id == responsible_id) and \
           (status_name is None or card_status == status_name):
            filtered_cards.append({
                "title": title,
                "responsible_id": responsible_person_id,
                "status": card_status
            })
    
    return filtered_cards

# 3. Function to print Kanban cards
def print_kanban_cards(cards):
    if cards:
        for card in cards:
            print(f"Kanban Card: {card['title']}, Responsable: {card['responsible_id']}, Status: {card['status']}")
    else:
        print("No matching cards found.")

# Example usage:

# Fetch all Kanban cards from the Notion database
kanban_cards = fetch_kanban_cards(DATABASE_ID)

# Optional filters: you can specify a responsible_id and/or status_name
responsible_id_filter = "ac7a3bd0-c111-4464-8f45-8a857a1abc8a"  # Replace with actual ID
status_filter = None #"En développement"  # Replace with actual status

# Filter the cards (if no filters are provided, all cards are returned)
filtered_cards = filter_kanban_cards(kanban_cards, responsible_id=responsible_id_filter, status_name=status_filter)

# Print the filtered (or all) Kanban cards
# print_kanban_cards(filtered_cards)


# Function to create a new Kanban card
def create_kanban_card(database_id, title, status="À faire"):
    url = "https://api.notion.com/v1/pages"
    
    # Data payload to create a new card
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Nom": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Statut": {
                "status": {
                    "name": status
                }
            }
        }
    }
    
    # Send the POST request to create the card
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print("Card created successfully!")
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


# Title of the new card
card_title = "New Task Example"

# Create a new Kanban card in "À faire" status
create_kanban_card(DATABASE_ID, card_title)

# Sample result dictionary (simulating the API response)
properties = {
    'Date d’échéance': {'id': 'C%5C%3C%3A', 'type': 'date', 'date': {'start': '2022-12-19', 'end': None, 'time_zone': None}},
    'Statut': {'id': 'k%3FMm', 'type': 'status', 'status': {'id': 'a087807d-e7e9-4e12-8560-44a3d64d6110', 'name': 'Fait', 'color': 'green'}},
    'Équipe': {'id': 'rIvf', 'type': 'select', 'select': {'id': '2da75352-d78c-4b75-bd04-3e653eeb71e0', 'name': 'Design', 'color': 'default'}},
    'Responsable': {'id': 'xE%3EJ', 'type': 'people', 'people': [{'object': 'user', 'id': 'ac7a3bd0-c111-4464-8f45-8a857a1abc8a'}]},
    'Nom': {'id': 'title', 'type': 'title', 'title': [{'type': 'text', 'text': {'content': 'Réfléchir à des idées de fonctionnalités', 'link': None}, 'plain_text': 'Réfléchir à des idées de fonctionnalités'}]}
}