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
    """Base class for managing Notion entities."""

    def __init__(self, database_id=None):
        self.database_id = database_id

    def fetch_data(self, url):
        """Fetch data from a given URL."""
        response = requests.get(url, headers={
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Notion-Version": "2022-06-28"
        })
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.text}")
        return response.json()

    def fetch_db_property_mapping(self):
        """Fetch the property mapping from the Notion database."""
        if not self.database_id:
            raise ValueError("Database ID must be provided.")
        database_info = self.fetch_data(DATABASE_URL)
        properties = database_info.get('properties', {})
        
        # Map property IDs to their respective names
        property_id_to_name = {details['id']: name for name, details in properties.items()}
        
        return property_id_to_name


class NotionPageManager(NotionManager):
    """Manager class for Notion pages."""

    def __init__(self, database_id):
        super().__init__(database_id)
        self.property_mapping = self.fetch_db_property_mapping()

    def get_interpreted_properties(self, page_data, for_display=False):
        """Return a dictionary with human-readable values for all properties on a Notion page."""
        interpreted_properties = {}
        properties = page_data.get('properties', {})
        page_id = page_data.get('id')
        interpreted_properties[NotionPropertyID.ID] = page_id

        for property_name, property_data in properties.items():
            property_id = property_data['id']
            property_type = property_data['type']
            content = self._extract_property_content(property_data)

            # Interpret the property value based on its type
            try:
                interpreted_value = self._interpret_property_value(property_type, content, for_display)
                interpreted_properties[NotionPropertyID(property_id)] = interpreted_value
            except ValueError as e:
                interpreted_properties[NotionPropertyID(property_id)] = None
                print(f"Error interpreting property '{property_name}': {str(e)}")

        return interpreted_properties

    def _extract_property_content(self, property_data):
        """Extract the content associated with the property."""
        property_type = property_data['type']
        content = property_data.get(property_type)
        return content if content is not None else None

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

    def display_page(self, interpreted_properties, detailed=False, separator=True):
        """Print the interpreted properties in a formatted manner."""
        prefix = "* "
        n = 60  # Line length for separation
        c = 20  # Column width for display

        page_id = interpreted_properties.get(NotionPropertyID.ID, 'N/A')
        print("\n" + "=" * n + "\n")
        print(f"{('Page - ' + NotionPropertyDisplayName[NotionPropertyID.ID.name].value):{c}}: {page_id}") if interpreted_properties else None

        if detailed: 
            print("\nDetailed Properties:\n" + "-" * n)
            for property_id, value in interpreted_properties.items():
                if property_id == NotionPropertyID.ID:
                    continue  # Skip printing the page ID again
                display_name = NotionPropertyDisplayName[property_id.name].value
                formatted_value = value if value is not None else 'N/A'
                print(f"{(prefix + display_name):{c}}: {formatted_value}")

        print("\n" + "=" * n + "\n") if separator else None

    def display_list_page(self, interpreted_properties, detailed=False):
        """Print a list of interpreted properties in a formatted manner."""
        for page_data in interpreted_properties:
            self.display_page(page_data, detailed=detailed, separator=False)
        self.display_page({}, separator=False)

    def fetch_page_data(self, page_id):
        """Fetch the data of a Notion page with the given ID."""        
        url = PAGE_URL_TEMPLATE.format(page_id=page_id)
        return self.fetch_data(url)
    
    def fetch_page_data_from_url(self, page_url):
        """Fetch the data of a Notion page with the given URL."""
        # Regular expression to match a valid Notion page URL
        notion_url_pattern = re.compile(r"https://www\.notion\.so/[a-zA-Z0-9\-]+-[a-f0-9]{32}")

        if not notion_url_pattern.match(page_url):
            raise ValueError("Invalid Notion page URL format")

        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_page_data(page_id)
    
    def get_page_id_from_url(self, page_url):
        """Extract the page ID from a Notion page URL."""
        return page_url.split('-')[-1]


class NotionCommentManager(NotionManager):
    """Manager class for Notion comments."""

    def fetch_blocks_data(self, page_id):
        """Fetch all blocks associated with a Notion page."""
        url = BLOCK_URL_TEMPLATE.format(page_id=page_id)
        blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            response = requests.get(url, headers={
                "Authorization": f"Bearer {NOTION_API_TOKEN}",
                "Notion-Version": "2022-06-28"
            })
            
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve blocks: {response.text}")

            block_data = response.json()
            blocks.extend(block_data.get("results", []))
            has_more = block_data.get("has_more", False)
            start_cursor = block_data.get("next_cursor")

        return blocks
    
    def extract_comments_from_blocks(self, blocks):
        """Extract comments from blocks."""
        comments = []
        for block in blocks:
            if 'comments' in block:
                for comment in block['comments']:
                    comments.append({
                        'author': comment.get('user', {}).get('name', 'Unknown'),
                        'content': comment.get('content', ''),
                        'created_time': comment.get('created_time', '')
                    })
        return comments

    def display_comments(self, comments):
        """Display the comments in a formatted manner."""
        print("\nComments:\n" + "-" * 30)
        if not comments:
            print("No comments found.")
            return

        for comment in comments:
            print(f"{comment['created_time']} - {comment['author']}: {comment['content']}")

import requests
from enum import Enum
from constants import DATABASE_ID, NOTION_API_TOKEN, DATABASE_URL, PAGE_URL_TEMPLATE, BLOCK_URL_TEMPLATE, USER_URL_TEMPLATE
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
    """Base class for managing Notion entities."""

    def __init__(self, database_id=None):
        self.database_id = database_id

    def fetch_data(self, url):
        """Fetch data from a given URL."""
        response = requests.get(url, headers={
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Notion-Version": "2022-06-28"
        })
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.text}")
        return response.json()

    def fetch_db_property_mapping(self):
        """Fetch the property mapping from the Notion database."""
        if not self.database_id:
            raise ValueError("Database ID must be provided.")
        database_info = self.fetch_data(DATABASE_URL)
        properties = database_info.get('properties', {})
        
        # Map property IDs to their respective names
        property_id_to_name = {details['id']: name for name, details in properties.items()}
        
        return property_id_to_name
    
    def get_page_id_from_url(self, page_url):
        """Extract the page ID from a Notion page URL."""
        return page_url.split('-')[-1]
    
    def fetch_user_name(self, user_id):
        """Fetch the name of a user with the given ID."""
        url = USER_URL_TEMPLATE.format(user_id=user_id)
        user_data = self.fetch_data(url)
        return user_data.get("name", "Unknown")


class NotionPageManager(NotionManager):
    """Manager class for Notion pages."""

    def __init__(self, database_id):
        super().__init__(database_id)
        self.property_mapping = self.fetch_db_property_mapping()

    def get_interpreted_properties(self, page_data, for_display=False):
        """Return a dictionary with human-readable values for all properties on a Notion page."""
        interpreted_properties = {}
        properties = page_data.get('properties', {})
        page_id = page_data.get('id')
        interpreted_properties[NotionPropertyID.ID] = page_id

        for property_name, property_data in properties.items():
            property_id = property_data['id']
            property_type = property_data['type']
            content = self._extract_property_content(property_data)

            # Interpret the property value based on its type
            try:
                interpreted_value = self._interpret_property_value(property_type, content, for_display)
                interpreted_properties[NotionPropertyID(property_id)] = interpreted_value
            except ValueError as e:
                interpreted_properties[NotionPropertyID(property_id)] = None
                print(f"Error interpreting property '{property_name}': {str(e)}")

        return interpreted_properties

    def _extract_property_content(self, property_data):
        """Extract the content associated with the property."""
        property_type = property_data['type']
        content = property_data.get(property_type)
        return content if content is not None else None

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

    def display_page(self, interpreted_properties, detailed=False, separator=True):
        """Print the interpreted properties in a formatted manner."""
        prefix = "* "
        n = 60  # Line length for separation
        c = 20  # Column width for display

        page_id = interpreted_properties.get(NotionPropertyID.ID, 'N/A')
        print("\n" + "=" * n + "\n")
        print(f"{('Page - ' + NotionPropertyDisplayName[NotionPropertyID.ID.name].value):{c}}: {page_id}") if interpreted_properties else None

        if detailed: 
            print("\nDetailed Properties:\n" + "-" * n)
            for property_id, value in interpreted_properties.items():
                if property_id == NotionPropertyID.ID:
                    continue  # Skip printing the page ID again
                display_name = NotionPropertyDisplayName[property_id.name].value
                formatted_value = value if value is not None else 'N/A'
                print(f"{(prefix + display_name):{c}}: {formatted_value}")

        print("\n" + "=" * n + "\n") if separator else None

    def display_list_page(self, interpreted_properties, detailed=False):
        """Print a list of interpreted properties in a formatted manner."""
        for page_data in interpreted_properties:
            self.display_page(page_data, detailed=detailed, separator=False)
        self.display_page({}, separator=False)

    def fetch_page_data(self, page_id):
        """Fetch the data of a Notion page with the given ID."""        
        url = PAGE_URL_TEMPLATE.format(page_id=page_id)
        return self.fetch_data(url)
    
    def fetch_page_data_from_url(self, page_url):
        """Fetch the data of a Notion page with the given URL."""
        # Regular expression to match a valid Notion page URL
        notion_url_pattern = re.compile(r"https://www\.notion\.so/[a-zA-Z0-9\-]+-[a-f0-9]{32}")

        if not notion_url_pattern.match(page_url):
            raise ValueError("Invalid Notion page URL format")

        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_page_data(page_id)


class NotionCommentManager(NotionManager):
    """Manager class for Notion comments."""

    def fetch_all_user_ids(self):
        """Fetch all user IDs and names from the Notion workspace."""
        url = USER_URL
        users = []
        has_more = True
        start_cursor = None

        while has_more:
            response = requests.get(url, headers={
                "Authorization": f"Bearer {NOTION_API_TOKEN}",
                "Notion-Version": "2022-06-28"
            })
            
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve users: {response.text}")

            user_data = response.json()
            users.extend(user_data.get("results", []))
            has_more = user_data.get("has_more", False)
            start_cursor = user_data.get("next_cursor")

        # Extract user IDs and names
        user_info = [{"id": user["id"], "name": user["name"]} for user in users]
        return user_info

    def fetch_comments(self, page_id):
        """Fetch all comments associated with a Notion page, ignoring block comments."""
        url = f"https://api.notion.com/v1/comments"
        comments = []
        has_more = True
        start_cursor = None

        while has_more:
            response = requests.get(url, headers={
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Notion-Version": "2022-06-28"
            }, params={
            "block_id": page_id,
            })
            
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve comments: {response.text}")

            comment_data = response.json()
            comments.extend(comment_data.get("results", []))
            has_more = comment_data.get("has_more", False)
            start_cursor = comment_data.get("next_cursor")

        return comments
    
    def add_comment_to_page(self, page_id, comment_text, users_to_mention=None):
        """
        Add a comment to a Notion page, tagging multiple users if specified.
        Args:
            page_id (str): The ID of the Notion page to which the comment will be added.
            comment_text (str): The text of the comment. Use '@' to indicate where user mentions should be inserted.
            users_to_mention (list, optional): A ordered list of user IDs to mention in the comment. The number of user IDs should match the number of '@' symbols in the comment_text.
        Raises:
            Exception: If the API request to add the comment fails.
        Example:
            add_comment_to_page(
                page_id="some-page-id",
                comment_text="Hello @, please check this out @.",
                users_to_mention=["user1-id", "user2-id"]
            )
        """
        url = "https://api.notion.com/v1/comments"
        
        # Start with the text of the comment
        rich_text = []

        # Split the comment_text into parts for tagging
        parts = comment_text.split("@")
        
        # Add the initial part of the comment (before mentions)
        if parts[0]:
            rich_text.append({"text": {"content": parts[0]}})
        
        # Iterate through the parts, adding mentions and the following text
        for i in range(1, len(parts)):
            # If there's a mention part
            mention_part = parts[i]
            user_id = None
            
            # Check if this part is a mention for a user
            if users_to_mention and i-1 < len(users_to_mention):
                user_id = users_to_mention[i-1]
            
            # Add the mention
            if user_id:
                rich_text.append({
                    "mention": {
                        "user": {
                            "id": user_id
                        }
                    }
                })
            
            # Add the remaining text after the mention
            if mention_part:
                rich_text.append({"text": {"content": mention_part}})
        
        # Construct the request body
        data = {
            "parent": {
                "page_id": page_id
            },
            "rich_text": rich_text
        }
        
        # Make the API request to add the comment
        response = requests.post(url, headers={
            "Authorization": f"Bearer {NOTION_API_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }, json=data)
        
        # Check for a successful response
        if response.status_code != 200:
            raise Exception(f"Failed to add comment: {response.text}")


    def display_comments(self, interpreted_comments, dev_data_display=False):
        """Display the comments in a formatted manner."""
        line = "- " * 20
        print("\nComments:\n" + line)
        
        if not interpreted_comments:
            print("No comments found.")
            return

        for comment in interpreted_comments:
            created_time = comment.get("created_time", "Unknown")
            last_edited_time = comment.get("last_edited_time", "Not edited")
            user_name = comment.get("user_name", "Unknown")
            comment_text = comment.get("comment_text", "Unknown")
            user_id = comment.get("user_id", "Unknown")
            comment_id = comment.get("id", "Unknown")  # Assuming comment ID is included in the interpreted comments

            # Display the formatted comment
            if dev_data_display:
                print(f"Comment ID: {comment_id}")
                print(f"Created Time: {created_time}")
                print(f"Last Edited Time: {last_edited_time}")
                print(f"User ID: {user_id}")
                print(f"User Name: {user_name if user_name else 'Unknown'}")
                print(f"Comment Text: {comment_text}")
                print(line)
            else:
                # Display in a simple format
                user_display = user_name if user_name else user_id
                print(f"\n[{created_time}] - by {user_display}:")
                print(f"  {comment_text}\n")  # Indented comment text for clarity
                print(line)  # Separator for simple comments

    def _extract_comment_text(self, comment, for_display=False):
        """Extract and format the rich text content of a comment."""
        rich_text_parts = comment.get("rich_text", [])
        formatted_text = []

        for part in rich_text_parts:
            if part['type'] == 'text':
                formatted_text.append(part['plain_text'])
            elif part['type'] == 'mention':
                mention_user = part['mention']['user']
                mention_name = mention_user.get('name', 'Unknown')
                formatted_text.append(f"@{mention_name}")  # Format mentions as @username

        return ''.join(formatted_text)
    
    def _extract_intepreted_comments(self, comments, for_display=False):
        """Extract and interpret the comments from the API response."""
        interpreted_comments = []
        for comment in comments:
            created_by = comment.get("created_by", {})
            user_id = created_by.get("id", "Unknown")
            user_name =  self.fetch_user_name(user_id) if for_display else None
            created_time = comment.get("created_time", "Unknown")
            comment_text = self._extract_comment_text(comment, for_display)
            comment_id = comment.get("id", "Unknown")
            last_edited_time = comment.get("last_edited_time", "Not edited")

            interpreted_comments.append({
                "user_id": user_id,
                "user_name": user_name,
                "created_time": created_time,
                "comment_text": comment_text,
                "id": comment_id,
                "last_edited_time": last_edited_time

            })
        return interpreted_comments


### Testing Functions
def test_fetch_db_property_mapping():
    page_manager = NotionPageManager(DATABASE_ID)
    property_mapping = page_manager.fetch_db_property_mapping()
    print(property_mapping)

def test_display_page():
    page_manager = NotionPageManager(DATABASE_ID)
    page_id = page_manager.get_page_id_from_url(PAGE_URL2)
    page_data = page_manager.fetch_page_data(page_id)
    interpreted_properties = page_manager.get_interpreted_properties(page_data, for_display=True)
    page_manager.display_page(interpreted_properties, detailed=True)

def test_display_list_page():
    page_manager = NotionPageManager(DATABASE_ID)
    page_urls = [
        PAGE_URL1,PAGE_URL2,PAGE_URL3
    ]

    interpreted_properties_list = []
    for page_url in page_urls:
        interpreted_properties = page_manager.get_interpreted_properties(
            page_manager.fetch_page_data_from_url(page_url),
            for_display=True
        )
        interpreted_properties_list.append(interpreted_properties)
    
    page_manager.display_list_page(interpreted_properties_list, detailed=True)

def test_fetch_comments():
    detailed = False
    for_display = True
    comment_manager = NotionCommentManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL3)
    comments = comment_manager.fetch_comments(page_id)
    interpreted_comments = comment_manager._extract_intepreted_comments(comments, for_display)
    comment_manager.display_comments(interpreted_comments, detailed)

def test_add_comment():
    comment_manager = NotionCommentManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL2)
    comment_manager.add_comment_to_page(page_id, "This is a test comment.")

def test_fetch_all_user_ids():
    comment_manager = NotionCommentManager(DATABASE_ID)
    user_info = comment_manager.fetch_all_user_ids()
    print(user_info)

def test_add_comment_with_mention():
    comment_manager = NotionCommentManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL3)
    comment_manager.add_comment_to_page(page_id, "This is a test comment with a mention @ a mention and another one @", users_to_mention=[USER_ID2, USER_ID1])

def test_display_comments():
    comment_manager = NotionCommentManager(DATABASE_ID)
    page_url = PAGE_URL1
    page_id = comment_manager.get_page_id_from_url(page_url)
    blocks = comment_manager.fetch_blocks_data(page_id)
    comments = comment_manager.extract_comments_from_blocks(blocks)
    comment_manager.display_comments(comments)

if __name__ == "__main__":
    # Uncomment the function you want to test
    # test_display_page()
    # test_display_list_page()
    # test_fetch_db_property_mapping()

    # test_add_comment()
    # test_add_comment_with_mention()
    test_fetch_comments()
    # test_display_comments()
    pass
