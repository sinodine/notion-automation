import os
import json
import requests
from constants import NOTION_API_TOKEN, DATABASE_ID


class NotionKanban:
    # Class variables to hold the API token and Database ID
    NOTION_API_TOKEN = NOTION_API_TOKEN
    DATABASE_ID = DATABASE_ID

    # Common headers for all requests
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    @classmethod
    def fetch_kanban_cards(cls):
        """Fetch all Kanban cards from the database"""
        url = f"https://api.notion.com/v1/databases/{cls.DATABASE_ID}/query"
        response = requests.post(url, headers=cls.headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    @classmethod
    def filter_kanban_cards(cls, cards, responsible_id=None, status_name=None):
        """Filter Kanban cards based on responsible person and status"""
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

    @classmethod
    def print_kanban_cards(cls, cards):
        """Print Kanban cards"""
        if cards:
            for card in cards:
                print(f"Kanban Card: {card['title']}, Responsible: {card['responsible_id']}, Status: {card['status']}")
        else:
            print("No matching cards found.")

    @classmethod
    def create_kanban_card(cls, title, status="À faire"):
        """Create a new Kanban card"""
        url = "https://api.notion.com/v1/pages"
        
        # Data payload to create a new card
        data = {
            "parent": {"database_id": cls.DATABASE_ID},
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
        response = requests.post(url, headers=cls.headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print("Card created successfully!")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
        
    @classmethod
    def fetch_field_options(cls):
        """Fetch all unique options for each field (status, select, etc.) in the database."""
        url = f"https://api.notion.com/v1/databases/{cls.DATABASE_ID}"
        response = requests.get(url, headers=cls.headers)
        
        if response.status_code == 200:
            data = response.json()
            properties = data.get("properties", {})
            
            field_options = {}
            
            for field_name, field_data in properties.items():
                # Handle different types of fields (status, select, multi_select)
                if field_data["type"] in ["select", "multi_select", "status"]:
                    field_options[field_name] = {
                        "type": field_data["type"],
                        "options": field_data[field_data["type"]]["options"]
                    }

            return field_options
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None



def test_fetch_kanban_cards():
    """Test fetching all Kanban cards from the Notion database."""
    kanban_cards = NotionKanban.fetch_kanban_cards()
    if kanban_cards is not None:
        print(f"Fetched {len(kanban_cards)} Kanban cards.")
    else:
        print("Failed to fetch Kanban cards.")


def test_filter_kanban_cards():
    """Test filtering Kanban cards based on responsible person and status."""
    kanban_cards = NotionKanban.fetch_kanban_cards()
    
    if kanban_cards is not None:
        responsible_id_filter = "ac7a3bd0-c111-4464-8f45-8a857a1abc8a"  # Replace with actual ID
        status_filter = "En développement"  # Replace with actual status
        filtered_cards = NotionKanban.filter_kanban_cards(kanban_cards, responsible_id=responsible_id_filter, status_name=status_filter)

        print(f"Filtered down to {len(filtered_cards)} cards based on filters.")
    else:
        print("Failed to fetch Kanban cards for filtering.")


def test_print_kanban_cards():
    """Test printing Kanban cards."""
    kanban_cards = NotionKanban.fetch_kanban_cards()
    
    if kanban_cards is not None:
        print("Printing Kanban cards:")
        NotionKanban.print_kanban_cards(kanban_cards)
    else:
        print("Failed to fetch Kanban cards for printing.")


def test_create_kanban_card():
    """Test creating a new Kanban card."""
    new_card_title = "New Task Example"
    new_card_status = "À faire"  # You can change the status if needed
    NotionKanban.create_kanban_card(new_card_title, new_card_status)

def test_fetch_field_options():
    """Test fetching all unique options for each field (status, select, etc.) in the database."""
    field_options = NotionKanban.fetch_field_options()
    
    if field_options is not None:
        print("Fetched field options successfully:")
        for field_name, field_data in field_options.items():
            print(f"\nField: {field_name}")
            print(f"Type: {field_data['type']}")
            print("Options:")
            for option in field_data["options"]:
                print(f"  - Name: {option['name']}, ID: {option['id']}")
    else:
        print("Failed to fetch field options.")



# Run all tests
if __name__ == "__main__":
    # print("Testing fetch_kanban_cards:")
    # test_fetch_kanban_cards()

    # print("\nTesting filter_kanban_cards:")
    # test_filter_kanban_cards()

    # print("\nTesting print_kanban_cards:")
    # test_print_kanban_cards()

    # print("\nTesting create_kanban_card:")
    # test_create_kanban_card()

    print("\nTesting test_fetch_field_options:")
    test_fetch_field_options()

