import os
import json
import requests
from constants import NOTION_API_TOKEN, DATABASE_ID
from field_manager import FieldCategory, FieldManager


class NotionKanban:
    """
    A class to interact with a Notion Kanban board via the Notion API.
    """

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
            return response.json().get("results", [])
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
            responsible_person_id = properties['Responsable']['people'][0]['id'] if properties['Responsable']['people'] else None
            card_status = properties['Statut']['status']['name'] if properties['Statut']['status'] else None
            title = properties['Nom']['title'][0]['text']['content'] if properties['Nom']['title'] else "No Title"
            
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
                print(f"Card ID: {card['id']}")
                title = card['properties']['Nom']['title'][0]['text']['content'] if card['properties']['Nom']['title'] else "No Title"
                print(f"Title: {title}")
                print(f"Status: {card['properties']['Statut']['status']['name']}")
                responsible = card['properties']['Responsable']['people'][0]['id'] if card['properties']['Responsable']['people'] else "No Responsible"
                print(f"Responsible: {responsible}")
                print("")
        else:
            print("No matching cards found.")

    @classmethod
    def modify_kanban_card_field(cls, card_id, field_category, new_value):
        """Modify a field of a Kanban card"""
        field_manager = FieldManager()
        field_options = field_manager.list_options(field_category)
        
        # Debug print to check the structure of field_options
        print("Field Options:", field_options)
        
        # Find the option ID for the new value
        option_id = field_options.get(new_value)
        
        if not option_id:
            print(f"Error: Option '{new_value}' not found in field category '{field_category.name}'.")
            return
        
        url = f"https://api.notion.com/v1/pages/{card_id}"
        data = {
            "properties": {
                field_category.value: {
                    "status": {"id": option_id} if field_category == FieldCategory.STATUT else {"select": {"id": option_id}}
                }
            }
        }
        
        # Debug print to check the request payload
        print("Request Payload:", json.dumps(data, indent=2))
        
        response = requests.patch(url, headers=cls.headers, json=data)
        
        # Debug print to check the response
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        
        if response.status_code == 200:
            print("Kanban card field modified successfully.")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


    @classmethod
    def create_kanban_card(cls, title, status="À faire"):
        """Create a new Kanban card"""
        url = "https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": cls.DATABASE_ID},
            "properties": {
                "Nom": {
                    "title": [
                        {"text": {"content": title}}
                    ]
                },
                "Statut": {
                    "status": {"name": status}
                }
            }
        }
        
        response = requests.post(url, headers=cls.headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print("Card created successfully!")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
        # @classmethod
        # def fetch_field_options(cls):
        #     """Fetch all unique options for each field (status, select, etc.) in the database."""
        #     url = f"https://api.notion.com/v1/databases/{cls.DATABASE_ID}"
        #     response = requests.get(url, headers=cls.headers)
            
        #     if response.status_code == 200:
        #         properties = response.json().get("properties", {})
        #         field_options = {}
                
        #         for field_name, field_data in properties.items():
        #             if field_data["type"] in ["select", "multi_select", "status"]:
        #                 field_options[field_name] = {
        #                     "type": field_data["type"],
        #                     "options": field_data[field_data["type"]]["options"]
        #                 }

        #         return field_options
        #     else:
        #         print(f"Error: {response.status_code}")
        #         print(response.text)
        #         return None
    @classmethod
    def print_kanban_card_by_id(cls, card_id):
        """Print the details of a Kanban card with a given ID in a pretty format"""
        kanban_cards = cls.fetch_kanban_cards()
        
        if kanban_cards is not None:
            card = next((card for card in kanban_cards if card['id'] == card_id), None)

            if card:
                title = card['properties']['Nom']['title'][0]['text']['content'] if card['properties']['Nom']['title'] else "No Title"
                status = card['properties']['Statut']['status']['name'] if card['properties']['Statut']['status'] else "No Status"
                responsible = card['properties']['Responsable']['people'][0]['id'] if card['properties']['Responsable']['people'] else "No Responsible"
                
                # Print card details in a pretty format
                print("="*40)
                print(f"Card ID: {card['id']}")
                print(f"Title: {title}")
                print(f"Status: {status}")
                print(f"Responsible: {responsible}")
                
                # Fetch and print comments
                comments_url = f"https://api.notion.com/v1/comments?block_id={card_id}"
                comments_response = requests.get(comments_url, headers=cls.headers)
                
                if comments_response.status_code == 200:
                    comments = comments_response.json().get('results', [])
                    if comments:
                        print("Comments:")
                        for comment in comments:
                            rich_text = comment.get('rich_text', [])
                            if rich_text:
                                print(f"- {rich_text[0].get('text', {}).get('content', 'No Content')}")
                            else:
                                print("- No Content")
                    else:
                        print("No Comments")
                else:
                    print("Failed to fetch comments.")
                
                print("="*40)
                print("")
            else:
                print(f"No card found with ID: {card_id}")
        else:
            print("Failed to fetch Kanban cards.")

 
    @classmethod
    def add_comment_to_card(cls, card_id, comment_text):
        """Add a comment to a Kanban card"""
        url = "https://api.notion.com/v1/comments"
        data = {
            "parent": {
                "page_id": card_id
            },
            "rich_text": [
                {
                    "text": {
                        "content": comment_text
                    }
                }
            ]
        }
        
        response = requests.post(url, headers=cls.headers, json=data)
        
        if response.status_code == 200:
            print("Comment added successfully!")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
        
    # NEW FUNCTION TO TAG SOMEONE IN A COMMENT
    @classmethod
    def tag_person_in_comment(cls, card_id, comment_text, person_id):
        """Tag a person in a comment on a Kanban card"""
        url = "https://api.notion.com/v1/comments"
        data = {
            "parent": {
            "page_id": card_id
            },
            "rich_text": [
            {
                "type": "mention",
                "mention": {
                "type": "user",
                "user": {
                    "id": person_id
                }
                },
                "plain_text": f"@{person_id} {comment_text}" # fix text comment not showing
            }
            ]
        }
        
        response = requests.post(url, headers=cls.headers, json=data)
        
        if response.status_code == 200:
            print("Comment added successfully!")
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    # get all users ID
    @classmethod
    def get_all_users(cls):
        url = "https://api.notion.com/v1/users"
        response = requests.get(url, headers=cls.headers)

        if response.status_code == 200:
            return response.json().get("results", [])
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

def test_modify_kanban_card_field():
    """Test creating and then modifying a field of a Kanban card."""
    # Create a new card
    new_card_title = "Test Task for Modification"
    new_card_status = "À faire"
    new_card = NotionKanban.create_kanban_card(new_card_title, new_card_status)
    
    if new_card:
        card_id = new_card['id']
        field_category = FieldCategory.STATUT
        new_value = "Fait"
        
        # Fetch and print the card before modification
        kanban_cards = NotionKanban.fetch_kanban_cards()
        card_before = next((card for card in kanban_cards if card['id'] == card_id), None)
        if card_before:
            print("\nCard before modification:")
            NotionKanban.print_kanban_cards([card_before])
        else:
            print("Card not found before modification.")
        
        # Modify the card
        NotionKanban.modify_kanban_card_field(card_id, field_category, new_value)
        
        # Fetch and print the card after modification
        kanban_cards = NotionKanban.fetch_kanban_cards()
        card_after = next((card for card in kanban_cards if card['id'] == card_id), None)
        if card_after:
            print("\nCard after modification:")
            NotionKanban.print_kanban_cards([card_after])
        else:
            print("Card not found after modification.")
    else:
        print("Failed to create a new card for modification test.")

def test_create_and_comment_kanban_card():
    """Test creating a new Kanban card, adding a comment, and displaying the details."""
    # Step 1: Create a new card
    new_card_title = "Task with Comment"
    new_card_status = "À faire"
    new_card = NotionKanban.create_kanban_card(new_card_title, new_card_status)
    
    if new_card:
        card_id = new_card['id']
        
        # Step 2: Add a comment to the card
        comment_text = "This is a test comment."
        NotionKanban.add_comment_to_card(card_id, comment_text)
        
        # Step 3: Fetch and print the card details
        NotionKanban.print_kanban_card_by_id(card_id)
    else:
        print("Failed to create a new card for comment test.")

def test_tag_person_in_comment():
    """Test tagging a person in a comment on a Kanban card."""
    # Step 1: Create a new card
    new_card_title = "Task with Tagged Comment"
    new_card_status = "À faire"
    new_card = NotionKanban.create_kanban_card(new_card_title, new_card_status)
    
    if new_card:
        card_id = new_card['id']
        
        # Step 2: Tag a person in a comment
        comment_text = "This is a test comment with a tagged person."
        person_id = "f57955ac-c81f-451d-9641-9a548e0f8308"  
        NotionKanban.tag_person_in_comment(card_id, comment_text, person_id)
        
        # Step 3: Fetch and print the card details
        NotionKanban.print_kanban_card_by_id(card_id)
    else:
        print("Failed to create a new card for tagged comment test.")

def test_fetch_all_users():
    """Test fetching all users from the Notion workspace."""
    users = NotionKanban.get_all_users()
    
    if users is not None:
        print(f"Fetched {len(users)} users.")
        for user in users:
            print(f"User ID: {user['id']}")
            print(f"Name: {user['name']}")
            print(f"Email: {user.get('person', {}).get('email', 'No Email')}")
            print("="*40)
    else:
        print("Failed to fetch users.")

# def test_fetch_field_options():
#     """Test fetching all unique options for each field (status, select, etc.) in the database."""
#     field_options = NotionKanban.fetch_field_options()
    
#     if field_options is not None:
#         print("Fetched field options successfully:")
#         for field_name, field_data in field_options.items():
#             print(f"\nField: {field_name}")
#             print(f"Type: {field_data['type']}")
#             print("Options:")
#             for option in field_data["options"]:
#                 print(f"  - Name: {option['name']}, ID: {option['id']}")
#     else:
#         print("Failed to fetch field options.")


if __name__ == "__main__":
    # Uncomment the tests you want to run
    # print("Testing fetch_kanban_cards:")
    # test_fetch_kanban_cards()

    # print("\nTesting filter_kanban_cards:")
    # test_filter_kanban_cards()

    # print("\nTesting print_kanban_cards:")
    # test_print_kanban_cards()

    # test_create_and_comment_kanban_card()

    test_tag_person_in_comment()

    # test_fetch_all_users()

    # NotionKanban.print_kanban_card_by_id("123acdc2-cc58-8004-852e-f837c3ab0b08")

    # print("\nTesting create_kanban_card:")
    # test_create_kanban_card()

    # print("\nTesting fetch_field_options:")
    # test_fetch_field_options()

    # print("\nTesting test_modify_kanban_card_field:")
    # test_modify_kanban_card_field()
