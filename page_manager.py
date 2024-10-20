import requests
from enum import Enum
from constants import COMMENTS_URL, DATABASE_ID, DATABASE_URL_TEMPLATE, USER_ID1, NOTION_API_TOKEN, DATABASE_URL, PAGE_URL1, PAGE_URL2, PAGE_URL3, PAGE_URL_TEMPLATE, BLOCK_URL_TEMPLATE, USER_ID2, USER_URL, USER_URL_TEMPLATE, NotionBasePropertyID, NotionCommentPropertyID, NotionDatabasePropertyID, NotionPagePropertyID
import re
from typing import Any, Optional

from utils import _extract_data_page_default_properties, _extract_property, _extract_property_content, display_data_item, _extract_comment_text, _extract_data_base_properties

class NotionManager:
    """
    Base class for managing Notion entities.
    Provides utility functions for fetching data from the Notion API.
    """
    
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
        
        url = DATABASE_URL_TEMPLATE.format(database_id=self.database_id)
        database_info = self.fetch_url(url)
        properties = database_info.get('properties', {})
        
        # Map property IDs to their respective names
        return {details['id']: name for name, details in properties.items()}

    def fetch_page_data(self, page_id):
        """Fetch the data of a Notion page using its ID."""
        url = PAGE_URL_TEMPLATE.format(page_id=page_id)
        return self.fetch_url(url)

    def fetch_page_data_from_url(self, page_url):
        """Fetch the data of a Notion page from a URL."""
        if not self._is_valid_notion_url(page_url):
            raise ValueError("Invalid Notion page URL format")

        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_page_data(page_id)

    def fetch_blocks_data(self, page_id):
        """Fetch all blocks associated with a Notion page."""
        return self._fetch_paginated_data(BLOCK_URL_TEMPLATE.format(page_id=page_id))

    def fetch_blocks_data_from_url(self, page_url):
        """Fetch all blocks associated with a Notion page from its URL."""
        page_id = self.get_page_id_from_url(page_url)
        return self.fetch_blocks_data(page_id)

    def fetch_all_user_ids(self):
        """Fetch all user IDs and names from the Notion workspace."""
        users = self._fetch_paginated_data(USER_URL)
        return [{"id": user["id"], "name": user["name"]} for user in users]
    
    def fetch_user_name(self, user_id):
        """Fetch the name of a user from their ID."""
        url = USER_URL_TEMPLATE.format(user_id=user_id)
        user_data = self.fetch_url(url)
        return user_data.get("name", "Unknown")

    def fetch_comments(self, page_id):
        """Fetch all comments associated with a Notion page (ignores block comments)."""
        params = {"block_id": page_id}
        return self._fetch_paginated_data(COMMENTS_URL, params)

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
    
    def _extract_comment_data(self, comment_data: dict[str, Any], for_display: bool = False) -> dict[str, Any]:
        """
        Extracts and interprets content from a Notion comment.
        """
        interpreted_properties = {}

        # Step 1: Extract base properties
        base_properties = _extract_data_base_properties(comment_data)
        interpreted_properties.update(base_properties)

        # Step 2: Extract comment text
        comment_text = _extract_comment_text(comment_data, for_display)
        interpreted_properties[NotionCommentPropertyID.COMMENT_TEXT] = comment_text

        # Step 3: Extract user ID and name
        user_data = comment_data.get("created_by", {})
        user_id = user_data.get("id")
        user_name = user_data.get("name")
        interpreted_properties[NotionCommentPropertyID.USER_ID] = user_id
        interpreted_properties[NotionCommentPropertyID.USER_NAME] = user_name

        if user_name is None and user_id:
            user_name = self.fetch_user_name(user_id)
            interpreted_properties[NotionCommentPropertyID.USER_NAME] = user_name + "(bot)"

        return interpreted_properties

class NotionPageManager(NotionManager):
    """Manager class for handling Notion pages and related operations."""

    def __init__(self, database_id: str):
        super().__init__(database_id)
        self.property_mapping = self.fetch_db_property_mapping()

    def _extract_data_page_database_properties(self, properties_data: dict[str, Any], for_display: bool = False) -> dict[NotionDatabasePropertyID, Any]:
        """
        Extracts properties from page_data['properties'] based on NotionDatabasePropertyID.
        Returns a dictionary with extracted properties.
        """
        interpreted_properties = {}

        for prop in NotionDatabasePropertyID:
            prop_name = self.property_mapping.get(prop.value)
            property_data = properties_data.get(prop_name)
            if property_data:
                property_type = property_data['type']
                content = _extract_property_content(property_data)
                interpreted_value = _extract_property(property_type, content, for_display)
                interpreted_properties[prop] = interpreted_value

        return interpreted_properties
    
    def extract_page_data(self, page_data: dict[str, Any], for_display: bool = False) -> dict[NotionPagePropertyID, Any]:
        """
        Extracts and interprets properties from a Notion page.
        """
        interpreted_properties = {}

        # Step 1: Extract properties from NotionBasePropertyID
        base_properties = _extract_data_base_properties(page_data)
        interpreted_properties.update(base_properties)

        # Step 2: Extract properties from NotionPagePropertyID
        page_properties = _extract_data_page_default_properties(page_data)
        interpreted_properties.update(page_properties)

        # Step 3: Extract properties from NotionDatabasePropertyID
        properties = page_data.get('properties', {})
        database_properties = self._extract_data_page_database_properties(properties, for_display)
        interpreted_properties.update(database_properties)

        return interpreted_properties

    def extract_data(self, page_or_comment_data: dict[str, Any]| list[dict[str, Any]], for_display: bool = False) -> dict[str, Any]| list[dict[str, Any]]:
        """
        General function to extract data from either a Notion page or a comment.
        It uses the 'object' field in the data to determine what to extract.
        """
        if type(page_or_comment_data) is list:
            return [self.extract_data(data, for_display) for data in page_or_comment_data]
        
        object_type = page_or_comment_data.get('object')
        if object_type == 'page':
            return self.extract_page_data(page_or_comment_data, for_display)
        elif object_type == 'comment':
            return self._extract_comment_data(page_or_comment_data, for_display)
        else:
            raise ValueError(f"Unsupported object type: {object_type}")

    def display_data(self, extracted_data_list: list[dict[str, Any]], detailed: bool = False):
        """
        General function to display either page or comment data.
        Uses the 'object' field to determine whether to display a page or comment.
        """
        
        if type(extracted_data_list) is list:
            for extracted_data in extracted_data_list:
                display_data_item(extracted_data, detailed, separator=False)
        else:
            display_data_item(extracted_data_list, detailed)

    def add_comment_to_page(self, page_id: str, comment_text: str, users_to_mention: Optional[list[str]] = None):
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
            raise Exception(f"Failed to add comment: {response.status_code} - {response.text}")



# Tests

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

    # Using the generalized extract_data method
    interpreted_properties = page_manager.extract_data(page_data, for_display=True)

    # print(interpreted_properties)
    
    # Using the generalized display_data method
    page_manager.display_data(interpreted_properties, detailed=True)


def test_display_list_page():
    """Test fetching and displaying multiple Notion pages as a list with detailed properties."""
    page_manager = NotionPageManager(DATABASE_ID)
    page_urls = [PAGE_URL1, PAGE_URL2, PAGE_URL3]

    interpreted_properties_list = [
        page_manager.extract_data(
            page_manager.fetch_page_data_from_url(page_url),
            for_display=True
        ) for page_url in page_urls
    ]
    
    # Using the generalized display_data method for a list of pages
    page_manager.display_data(interpreted_properties_list, detailed=True)


def test_display_comments():
    """Test fetching and displaying comments for a given Notion page."""
    detailed = True
    for_display = True
    comment_manager = NotionPageManager(DATABASE_ID)
    page_id = comment_manager.get_page_id_from_url(PAGE_URL3)
    
    # Fetching and interpreting comments
    comments = comment_manager.fetch_comments(page_id)
    interpreted_comments = comment_manager.extract_data(comments, for_display=for_display)
    
    # Using the generalized display_data method for comments
    comment_manager.display_data(interpreted_comments, detailed)


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


if __name__ == "__main__":
    # Uncomment the function(s) you want to test
    test_display_page()
    test_display_list_page()
    test_fetch_db_property_mapping()
    test_add_comment()
    test_add_comment_with_mention()
    test_display_comments()
    test_fetch_all_user_ids()
    pass
