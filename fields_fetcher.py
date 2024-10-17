
import requests
import json
from constants import NOTION_API_TOKEN, DATABASE_ID


class NotionFieldFetcher:
    # Class variables for Notion API
    NOTION_API_TOKEN = NOTION_API_TOKEN
    DATABASE_ID = DATABASE_ID

    # Common headers for all requests
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    @classmethod
    def fetch_database_schema(cls):
        """Fetch the database schema to extract field options."""
        url = f"https://api.notion.com/v1/databases/{cls.DATABASE_ID}"
        response = requests.get(url, headers=cls.headers)

        if response.status_code == 200:
            data = response.json()
            return data["properties"]
        else:
            print(f"Error fetching database schema: {response.status_code}")
            print(response.text)
            return None

    @classmethod
    def deduce_field_options(cls, properties):
        """Deduces all fields and their options from the database schema."""
        field_options = {}

        for field_name, details in properties.items():
            field_type = details["type"]
            options = []

            if field_type == "select":
                options = [option["name"] for option in details["select"]["options"]]
            elif field_type == "status":
                options = [option["name"] for option in details["status"]["options"]]
            elif field_type == "multi_select":
                options = [option["name"] for option in details["multi_select"]["options"]]

            field_options[field_name] = {
                "type": field_type,
                "options": options
            }

        return field_options

    @classmethod
    def display_field_options(cls, field_options):
        """Display all fields and their options for creating constants."""
        if field_options:
            print("Fetched field options successfully:\n")
            for field_name, details in field_options.items():
                print(f"Field: {field_name}")
                print(f"Type: {details['type']}")
                print("Options:")
                for option in details["options"]:
                    print(f"  - {option}")
                print()  # New line for better readability
        else:
            print("No field options found.")

# Example Usage
if __name__ == "__main__":
    notion_fetcher = NotionFieldFetcher()
    
    # Fetch the database schema
    properties = notion_fetcher.fetch_database_schema()
    
    # Deduce field options
    field_options = notion_fetcher.deduce_field_options(properties)
    
    # Display the field options
    notion_fetcher.display_field_options(field_options)
