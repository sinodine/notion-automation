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