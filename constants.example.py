NOTION_API_TOKEN = "your-integration-api-token"
DATABASE_ID = "your-notion-page-id"

# Sample result dictionary (simulating the API response)
properties = {
    'Date d’échéance': {'id': 'C%5C%3C%3A', 'type': 'date', 'date': {'start': '2022-12-19', 'end': None, 'time_zone': None}},
    'Statut': {'id': 'k%3FMm', 'type': 'status', 'status': {'id': 'a087807d-e7e9-4e12-8560-44a3d64d6110', 'name': 'Fait', 'color': 'green'}},
    'Équipe': {'id': 'rIvf', 'type': 'select', 'select': {'id': '2da75352-d78c-4b75-bd04-3e653eeb71e0', 'name': 'Design', 'color': 'default'}},
    'Responsable': {'id': 'xE%3EJ', 'type': 'people', 'people': [{'object': 'user', 'id': 'ac7a3bd0-c111-4464-8f45-8a857a1abc8a'}]},
    'Nom': {'id': 'title', 'type': 'title', 'title': [{'type': 'text', 'text': {'content': 'Réfléchir à des idées de fonctionnalités', 'link': None}, 'plain_text': 'Réfléchir à des idées de fonctionnalités'}]}
}

# URLs
NOTION_API_URL = "https://api.notion.com/v1"
DATABASE_URL = f"{NOTION_API_URL}/databases/{DATABASE_ID}"
PAGE_URL_TEMPLATE = f"{NOTION_API_URL}/pages/{{page_id}}"
BLOCK_URL_TEMPLATE = f"{NOTION_API_URL}/blocks/{{page_id}}/children"
USER_URL_TEMPLATE = f"{NOTION_API_URL}/users/{{user_id}}"

# For tests
MY_USER_ID = "your-user-id" # To test the mention feature
PAGE_URL1 = "https://www.notion.so/Notion-Test-Page-1-122acdc2cc5880fa8643c616c6778bbb"
PAGE_URL2 = "https://www.notion.so/Notion-Test-Page-2-122acdc2cc5880fa8643c616c6778bbb"
PAGE_URL3 = "https://www.notion.so/Notion-Test-Page-3-122acdc2cc5880fa8643c616c6778bbb"