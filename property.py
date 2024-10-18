import requests
from enum import Enum
from constants import DATABASE_ID, NOTION_API_TOKEN

class NotionPropertyID(Enum):
    """Enum for Notion property IDs based on the results of fetch_db_property_mapping."""
    DATE_ECHEANCE = 'C%5C%3C%3A'
    STATUS = "k%3FMm"  
    TEAM = "rIvf"
    RESPONSIBLE = "xE%3EJ"
    NAME = "title"
    ID = "id"

class NotionPropertyDisplayName(Enum):
    """Enum for Notion property display based on Notion property IDs."""
    DATE_ECHEANCE = "Date d’échéance"
    STATUS = "Statut"  
    TEAM = "Équipe"
    RESPONSIBLE = "Responsable"
    NAME = "Nom"
    ID = "ID"

NOTION_API_URL = "https://api.notion.com/v1/databases/"
headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

def fetch_db_property_mapping():
    """Fetch the property mapping from the Notion database."""
    url = f"{NOTION_API_URL}{DATABASE_ID}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve database: {response.text}")
    
    database_info = response.json()
    properties = database_info.get('properties', {})
    
    # Map property IDs to their respective names
    property_id_to_name = {details['id']: name for name, details in properties.items()}
    
    return property_id_to_name

class NotionPageManager:
    def __init__(self, database_id):
        self.database_id = database_id
        self.property_mapping = fetch_db_property_mapping()
    
    def get_interpreted_properties(self, page_data, for_display=False):
        """Return a dictionary with human-readable values for all properties on a Notion page."""
        interpreted_properties = {}
        properties = page_data.get('properties', {})

        # Add the page ID to the interpreted properties
        page_id = page_data.get('id')
        interpreted_properties[NotionPropertyID.ID] = page_id

        for property_name, property_data in properties.items():
            property_id = property_data['id']
            property_type = property_data['type']
            content = self._extract_property_content(property_data)

            # Interpret the property value based on its type
            try:
                interpreted_value = self._interpret_property_value(property_type, content, for_display)
                # Use NotionPropertyID to store the interpreted value
                interpreted_properties[NotionPropertyID(property_id)] = interpreted_value
            except ValueError as e:
                interpreted_properties[NotionPropertyID(property_id)] = None
                # Log error or handle as necessary
                print(f"Error interpreting property '{property_name}': {str(e)}")

        return interpreted_properties

    def _extract_property_content(self, property_data):
        """Extract the content associated with the property."""
        property_type = property_data['type']
        content = property_data.get(property_type)
        
        if content is None:
            return None  # Return None if content is missing
        
        return content

    # Extraction functions for each property type
    def _extract_plain_text_from_rich_text(self, rich_text_array):
        """Extract plain text from an array of rich text objects."""
        return ''.join(item.get('plain_text', '') for item in rich_text_array)

    def _extract_property(self, property_type, content, for_display=False):
        """Extract the content based on the property type."""
        extractors = {
            'title': lambda c: self._extract_plain_text_from_rich_text(c),
            'rich_text': lambda c: self._extract_plain_text_from_rich_text(c),
            'select': lambda c: c.get('name') if for_display else c.get('id'),
            'multi_select': lambda c: [option.get('name') if for_display else option.get('id') for option in c],
            'checkbox': lambda c: c,
            'date': lambda c: f"{c.get('start')} to {c.get('end')}" if c.get('end') else c.get('start'),
            'number': lambda c: c,
            'url': lambda c: c,
            'email': lambda c: c,
            'phone_number': lambda c: c,
            'people': lambda c: [person.get('name', "Unknown") if for_display else person.get('id') for person in c],
            'files': lambda c: [file.get('name') for file in c],
            'relation': lambda c: [relation.get('name') if for_display else relation.get('id') for relation in c],
            'status': lambda c: c.get('name') if for_display else c.get('id')
        }
        return extractors.get(property_type, lambda c: None)(content)

    def _interpret_property_value(self, property_type, content, for_display=False):
        """Interpret and return a human-readable value based on the property type."""
        return self._extract_property(property_type, content, for_display)

    def print_interpreted_properties(self, interpreted_properties, detailed=False):
        """Print the interpreted properties in a formatted manner."""
        prefix = "* " if detailed else "Card - "
        n = 60
        c = 16

        page_id = interpreted_properties.get(NotionPropertyID.ID, 'N/A')
        print("\n"+"=" * n + "\n\n"+f"{prefix}{NotionPropertyDisplayName[NotionPropertyID.ID.name].value:{c}}: {page_id}")
        
        if detailed: 
            for property_id, value in interpreted_properties.items():
                if property_id == NotionPropertyID.ID:
                    continue  # Skip printing the page ID again
                display_name = NotionPropertyDisplayName[property_id.name].value
                formatted_value = value if value is not None else 'N/A'
                print(f"{prefix}{display_name:{c}}: {formatted_value}")

        print("\n"+"=" * n + "\n")  # Footer for better separation

    def fetch_page_data(self, page_id):
        """Fetch the data of a Notion page with the given ID."""
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve page data: {response.text}")
        
        return response.json()
    
    def get_page_id_from_url(self, page_url):
        """Extract the page ID from a Notion page URL."""
        return page_url.split('-')[-1]
    
    def fetch_user_name(self, user_id):
        """Fetch the name of a user with the given ID."""
        url = f"https://api.notion.com/v1/users/{user_id}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            if response.status_code == 404:
                return 'User Not Found'
            raise Exception(f"Failed to retrieve user data: {response.text}")
        
        user_data = response.json()
        return user_data.get('name', 'Unknown User')
    

if __name__ == "__main__":
    page_manager = NotionPageManager(DATABASE_ID)
    page_url = "https://www.notion.so/Rassembler-les-retours-utilisateurs-122acdc2cc5881529bbcf82295be6b55"
    page_id = page_manager.get_page_id_from_url(page_url)
    page_data = page_manager.fetch_page_data(page_id)
    interpreted_properties = page_manager.get_interpreted_properties(page_data,for_display=True)
    page_manager.print_interpreted_properties(interpreted_properties, detailed=True)


