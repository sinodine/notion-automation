import requests
from enum import Enum
from constants import DATABASE_ID, USER_ID1, NOTION_API_TOKEN, DATABASE_URL, PAGE_URL1, PAGE_URL2, PAGE_URL3, PAGE_URL_TEMPLATE, BLOCK_URL_TEMPLATE, USER_ID2, USER_URL, USER_URL_TEMPLATE
import re

# Enums for property IDs and display names
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

class NotionManager:
    """
    Base class for managing Notion entities.
    Provides utility functions for fetching data from the Notion API.
    """

    # Define URLs and API headers
    BASE_URL = "https://api.notion.com/v1"
    DATABASE_URL_TEMPLATE = f"{BASE_URL}/databases/{{database_id}}"
    PAGE_URL_TEMPLATE = f"{BASE_URL}/pages/{{page_id}}"
    BLOCK_URL_TEMPLATE = f"{BASE_URL}/blocks/{{page_id}}/children"
    USER_URL_TEMPLATE = f"{BASE_URL}/users/{{user_id}}"
    USER_URL = f"{BASE_URL}/users"
    COMMENTS_URL = f"{BASE_URL}/comments"
    
    HEADERS = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    def __init__(self, database_id=None):
        self.database_id = database_id

    def get_page_id_from_url(self, page_url):
        """Extract the page ID from a Notion page URL."""
        return page_url.split('-')[-1]

    def fetch_url(self, url, params=None):
        """Helper method to fetch data from a given URL with optional parameters."""
        response = requests.get(url, headers=self.HEADERS, params=params)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.text}")
        return response.json()

    # Fetch specific data

    def fetch_db_property_mapping(self):
        """Fetch and map property IDs to their names from the Notion database."""
        if not self.database_id:
            raise ValueError("Database ID must be provided.")
        
        url = self.DATABASE_URL_TEMPLATE.format(database_id=self.database_id)
        database_info = self.fetch_url(url)
        properties = database_info.get('properties', {})
        
        # Map property IDs to their respective names
        return {details['id']: name for name, details in properties.items()}

    def fetch_page_data(self, page_id):
        """Fetch the data of a Notion page using its ID."""
        url = self.PAGE_URL_TEMPLATE.format(page_id=page_id)
        return self.fetch_url(url)

    def fetch_page_data_from_url(self, page_url):
        """Fetch the data of a Notion page from a URL."""
        if not self._is_valid_notion_url(page_url):
            raise ValueError("Invalid Notion page URL format")

        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_page_data(page_id)

    def fetch_blocks_data(self, page_id):
        """Fetch all blocks associated with a Notion page."""
        return self._fetch_paginated_data(self.BLOCK_URL_TEMPLATE.format(page_id=page_id))

    def fetch_blocks_data_from_url(self, page_url):
        """Fetch all blocks associated with a Notion page from its URL."""
        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_blocks_data(page_id)

    def fetch_all_user_ids(self):
        """Fetch all user IDs and names from the Notion workspace."""
        users = self._fetch_paginated_data(self.USER_URL)
        return [{"id": user["id"], "name": user["name"]} for user in users]
    
    def fetch_user_name(self, user_id):
        """Fetch the name of a user from their ID."""
        url = self.USER_URL_TEMPLATE.format(user_id=user_id)
        user_data = self.fetch_url(url)
        return user_data.get("name", "Unknown")

    def fetch_comments(self, page_id):
        """Fetch all comments associated with a Notion page (ignores block comments)."""
        params = {"block_id": page_id}
        return self._fetch_paginated_data(self.COMMENTS_URL, params)

    def fetch_comments_from_url(self, page_url):
        """Fetch all comments associated with a Notion page from its URL."""
        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_comments(page_id)

    # Helper methods

    def _is_valid_notion_url(self, page_url):
        """Check if the URL follows the valid Notion page URL pattern."""
        pattern = re.compile(r"https://www\.notion\.so/[a-zA-Z0-9\-]+-[a-f0-9]{32}")
        return bool(pattern.match(page_url))

    def _fetch_paginated_data(self, url, params=None):
        """Fetch paginated data from a given Notion API endpoint."""
        data = []
        has_more = True
        start_cursor = None

        while has_more:
            if start_cursor:
                if params is None:
                    params = {}
                params['start_cursor'] = start_cursor
            
            response = self.fetch_url(url, params)
            data.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return data

class NotionPageManager(NotionManager):
    """Manager class for handling Notion pages and related operations."""

    def __init__(self, database_id):
        super().__init__(database_id)
        self.property_mapping = self.fetch_db_property_mapping()

    def get_page_interpreted_properties(self, page_data, for_display=False):
        """
        Returns a dictionary with human-readable values for Notion page properties.
        If `for_display` is True, it returns display-friendly values.
        """
        interpreted_properties = {}
        properties = page_data.get('properties', {})
        page_id = page_data.get('id')

        interpreted_properties[NotionPropertyID.ID] = page_id

        for property_name, property_data in properties.items():
            property_id = property_data['id']
            property_type = property_data['type']
            content = self._extract_property_content(property_data)

            try:
                interpreted_value = self._extract_property(property_type, content, for_display)
                interpreted_properties[NotionPropertyID(property_id)] = interpreted_value
            except ValueError as e:
                print(f"Error interpreting property '{property_name}': {str(e)}")
                interpreted_properties[NotionPropertyID(property_id)] = None

        return interpreted_properties

    def _extract_property_content(self, property_data):
        """Extracts the content for a given property type."""
        return property_data.get(property_data['type'], None)

    def _extract_plain_text_from_rich_text(self, rich_text_array):
        """Extracts plain text from a list of rich text objects."""
        return ''.join(item.get('plain_text', '') for item in rich_text_array)

    def _extract_property(self, property_type, content, for_display=False):
        """Extracts content based on property type and whether it's for display."""
        extractors = {
            'title': self._extract_plain_text_from_rich_text,
            'rich_text': self._extract_plain_text_from_rich_text,
            'select': lambda c: c.get('name') if for_display else c.get('id'),
            'multi_select': lambda c: [opt.get('name') if for_display else opt.get('id') for opt in c],
            'checkbox': lambda c: c,
            'date': lambda c: f"{c.get('start')} to {c.get('end')}" if c.get('end') else c.get('start'),
            'number': lambda c: c,
            'url': lambda c: c,
            'email': lambda c: c,
            'phone_number': lambda c: c,
            'people': lambda c: [p.get('name', 'Unknown') if for_display else p.get('id') for p in c],
            'files': lambda c: [f.get('name') for f in c],
            'relation': lambda c: [r.get('name') if for_display else r.get('id') for r in c],
            'status': lambda c: c.get('name') if for_display else c.get('id'),
            'emoji': lambda c: c.get('name') if for_display else c.get('id'),
            'formula': lambda c: c.get('name') if for_display else c.get('id'),
            'created_time': lambda c: c,
            'last_edited_time': lambda c: c,
            'last_edited_by': lambda c: c,
            'created_by': lambda c: c,
            'rollup': lambda c: c,
        }
        return extractors.get(property_type, lambda c: None)(content)

    def _extract_comment_text(self, comment, for_display=False):
        """Extracts and formats the rich text content of a comment."""
        return ''.join(part.get('plain_text', '') if part['type'] == 'text' else f"@{part['mention']['user'].get('name', 'Unknown')}"
                       for part in comment.get("rich_text", []))

    def _interpret_comments(self, comments, for_display=False):
        """Extracts and interprets comments from the API response."""
        interpreted_comments = []
        for comment in comments:
            created_by = comment.get("created_by", {})
            user_id = created_by.get("id", "Unknown")
            user_name = self.fetch_user_name(user_id) if for_display else None
            created_time = comment.get("created_time", "Unknown")
            comment_text = self._extract_comment_text(comment, for_display)
            last_edited_time = comment.get("last_edited_time", "Not edited")

            interpreted_comments.append({
                "user_id": user_id,
                "user_name": user_name,
                "created_time": created_time,
                "comment_text": comment_text,
                "id": comment.get("id", "Unknown"),
                "last_edited_time": last_edited_time
            })
        return interpreted_comments

    def display_comments(self, interpreted_comments, dev_data_display=False):
        """Displays the comments in a formatted manner."""
        line = "-" * 40
        print("\nComments:\n" + line)
        
        if not interpreted_comments:
            print("No comments found.")
            return

        for comment in interpreted_comments:
            created_time = comment.get("created_time", "Unknown")
            last_edited_time = comment.get("last_edited_time", "Not edited")
            user_name = comment.get("user_name", "Unknown")
            comment_text = comment.get("comment_text", "Unknown")

            if dev_data_display:
                print(f"Comment ID: {comment.get('id', 'Unknown')}")
                print(f"Created Time: {created_time}")
                print(f"Last Edited Time: {last_edited_time}")
                print(f"User ID: {comment.get('user_id', 'Unknown')}")
                print(f"User Name: {user_name if user_name else 'Unknown'}")
                print(f"Comment Text: {comment_text}")
            else:
                user_display = user_name or comment.get('user_id', 'Unknown')
                print(f"\n[{created_time}] - by {user_display}:")
                print(f"  {comment_text}\n")

            print(line)

    def display_page(self, interpreted_properties, detailed=False):
        """Displays the page properties in a formatted manner."""
        prefix = "* "
        n = 60
        c = 20

        page_id = interpreted_properties.get(NotionPropertyID.ID, 'N/A')
        print("\n" + "=" * n)
        print(f"{('Page - ' + NotionPropertyDisplayName.ID.value):{c}}: {page_id}")

        if detailed:
            print("\nDetailed Properties:\n" + "-" * n)
            for property_id, value in interpreted_properties.items():
                if property_id == NotionPropertyID.ID:
                    continue
                display_name = NotionPropertyDisplayName[property_id.name].value
                print(f"{(prefix + display_name):{c}}: {value if value is not None else 'N/A'}")

        print("=" * n)

    def display_list_page(self, interpreted_properties_list, detailed=False):
        """Displays a list of page properties in a formatted manner."""
        for interpreted_properties in interpreted_properties_list:
            self.display_page(interpreted_properties, detailed)
    

    def add_comment_to_page(self, page_id, comment_text, users_to_mention=None):
        """
        Adds a comment to a Notion page with optional user mentions.
        """
        url = "https://api.notion.com/v1/comments"
        rich_text = []
        parts = comment_text.split("@")

        if parts[0]:
            rich_text.append({"text": {"content": parts[0]}})
        
        for i, part in enumerate(parts[1:], 1):
            user_id = users_to_mention[i - 1] if users_to_mention and i - 1 < len(users_to_mention) else None
            if user_id:
                rich_text.append({"mention": {"user": {"id": user_id}}})
            if part:
                rich_text.append({"text": {"content": part}})

        data = {
            "parent": {"page_id": page_id},
            "rich_text": rich_text
        }

        response = requests.post(url, headers={
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to add comment: {response.text}")


### Testing Functions

def test_fetch_db_property_mapping():
    """Test fetching the property mapping from the Notion database."""
    page_manager = NotionPageManager(DATABASE_ID)
    property_mapping = page_manager.fetch_db_property_mapping()
    print(property_mapping)


def test_display_page():
    """Test fetching and displaying a Notion page with detailed properties."""
    page_manager = NotionPageManager(DATABASE_ID)
    page_id = page_manager.get_page_id_from_url(PAGE_URL2)
    page_data = page_manager.fetch_page_data(page_id)
    interpreted_properties = page_manager.get_page_interpreted_properties(page_data, for_display=True)
    page_manager.display_page(interpreted_properties, detailed=True)


def test_display_list_page():
    """Test fetching and displaying multiple Notion pages as a list with detailed properties."""
    page_manager = NotionPageManager(DATABASE_ID)
    page_urls = [PAGE_URL1, PAGE_URL2, PAGE_URL3]

    interpreted_properties_list = [
        page_manager.get_page_interpreted_properties(
            page_manager.fetch_page_data_from_url(page_url),
            for_display=True
        ) for page_url in page_urls
    ]
    
    page_manager.display_list_page(interpreted_properties_list, detailed=True)


def test_fetch_comments():
    """Test fetching and displaying comments for a given Notion page."""
    detailed = False
    for_display = True
    comment_manager = NotionPageManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL3)
    comments = comment_manager.fetch_comments(page_id)
    interpreted_comments = comment_manager._interpret_comments(comments, for_display)
    comment_manager.display_comments(interpreted_comments, detailed)


def test_add_comment():
    """Test adding a comment to a Notion page."""
    comment_manager = NotionPageManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL2)
    comment_manager.add_comment_to_page(page_id, "This is a test comment.")


def test_fetch_all_user_ids():
    """Test fetching all user IDs from Notion."""
    comment_manager = NotionPageManager(DATABASE_ID)
    user_info = comment_manager.fetch_all_user_ids()
    print(user_info)


def test_add_comment_with_mention():
    """Test adding a comment with mentions to a Notion page."""
    comment_manager = NotionPageManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL3)
    comment_manager.add_comment_to_page(
        page_id,
        "This is a test comment with a mention @ and another one @",
        users_to_mention=[USER_ID2, USER_ID1]
    )


def test_display_comments():
    """Test fetching and displaying comments from blocks of a Notion page."""
    comment_manager = NotionPageManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL1)
    comments = comment_manager.fetch_comments(page_id)
    interpreted_comments = comment_manager._interpret_comments(comments, for_display=True)
    comment_manager.display_comments(interpreted_comments)


if __name__ == "__main__":
    # Uncomment the function(s) you want to test
    # test_display_page()
    # test_display_list_page()
    # test_fetch_db_property_mapping()
    # test_add_comment()
    # test_add_comment_with_mention()
    # test_fetch_comments()
    # test_display_comments()
    pass