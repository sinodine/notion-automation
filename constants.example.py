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


API_BASE_URL = "https://api.notion.com/v1"
RETRIEVE_BLOCK_URL = f"{API_BASE_URL}/blocks/{DATABASE_ID}/children" # GET: To retrieve the paginated blocks of a page (max 100 blocks) # POST: To create a new block # PATCH: To create and append a blocks
RETRIEVE_PAGE_URL = f"{API_BASE_URL}/pages/{DATABASE_ID}"
RETRIEVE_DATABASE_URL = f"{API_BASE_URL}/databases/{DATABASE_ID}" # GET: To retrieve a database columns
GET_BLOCK_URL = f"{API_BASE_URL}/blocks/{{block_id}}" # GET: To retrieve a block # PATCH: To update a block # DELETE: To delete a block
QUERY_DATABASE_URL = f"{API_BASE_URL}/databases/{{database_id}}/query" # POST to query the database with filters
RETRIEVE_USER_URL = f"{API_BASE_URL}/users/me" # GET to retrieve the bot token user
COMMENTS_URL = f"{API_BASE_URL}/comments" # POST to create a comment block_id and content # GET to retrieve all comments of a block_id


# One data base -> multiple pages
# One page -> multiple blocks

# properties = columns
# page = item (row)
# block = content


# pages are technically blocks