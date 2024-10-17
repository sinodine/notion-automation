# Notion Automation
## Overview
Notion Automation is a project designed to automate tasks within Notion using the Notion API. This project includes scripts to fetch and manipulate data from a Notion database, making it easier to manage your projects, track tasks, and interact with your Notion pages efficiently.

## Features
- **Fetch Kanban Cards**: Easily retrieve and display Kanban cards from your Notion database.
- **Dynamic Field Management**: Manage field categories and options to customize the data structure according to your needs.
- **Error Handling and Logging**: Robust error handling to ensure smooth operation and easy debugging.
- **Environment Variable Configuration**: Securely manage sensitive information like API tokens and database IDs.

## Prerequisites
- Python 3.x
- Notion API token
- Git

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/sinodine/notion-automation
    cd notion-automation
    ```

2. **Create a virtual environment**:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the root directory and add your Notion API token and Database ID:
    ```env
    NOTION_API_TOKEN=your_notion_api_token
    DATABASE_ID=your_database_id
    ```

    - **Finding Your Notion API Token**:
      - Go to [Notion Integrations](https://www.notion.so/my-integrations) and create a new integration.
      - Copy the "Internal Integration Token" provided.

    - **Finding Your Database ID**:
      - Open the Notion database you want to use and copy the part of the URL after `notion.so/` and before the `?` or `/`. This is your Database ID.

## Setting Up Categories and Field Options

### 1. Configure Field Categories
In `field_manager.py`, you can define various categories for your fields by modifying the `FieldCategory` Enum. For example:
```python
class FieldCategory(Enum):
     """Enum for field categories."""
     STATUT = "Statut"
     EQUIPE = "Équipe"
     RESPONSABLE = "Responsable"
     NOM = "Nom"
     # Add your custom categories here
```

### 2. Add Field Options
To manage field options, you can edit the `__post_init__` method in the `FieldManager` class. You can add new options by calling the `add_option` method:
```python
self.add_option(FieldCategory.STATUT, "Your Option Name", "your-option-id")
```
For example, to add a new status:
```python
self.add_option(FieldCategory.STATUT, "In Review", "unique-id-for-in-review")
```

### 3. Update Constants
In `constants.py`, you can set your Notion API token and database ID. It’s better to load these values from environment variables:
```python
import os

NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")
```

## Usage

### Fetch Kanban Cards
To fetch Kanban cards from your Notion database, run:
```sh
python notion_kanban.py
```

### List Available Field Options
You can also list available options for each category directly in your Python scripts:
```python
# Example: Listing all statuses
from field_manager import FieldManager, FieldCategory

field_manager = FieldManager()
statuses = field_manager.list_options(FieldCategory.STATUT)
print(statuses)
```

### Testing Functionality
Each functionality has a corresponding test function within the scripts. You can uncomment the calls to these functions in the `__main__` section of your scripts to validate that everything is set up correctly. For example:
```python
if __name__ == "__main__":
     test_fetch_kanban_cards()
```

## Ideas and Improvements
We are always looking to improve Notion Automation. Here are some ideas for future enhancements:
- **Advanced Filtering**: Implement more advanced filtering options for fetching data from Notion.
<!-- - **Batch Operations**: Enable batch operations for updating multiple Kanban cards at once.
- **Webhooks**: Integrate with webhooks for real-time updates.

## Additional Scripts
You can add more scripts to automate other tasks within Notion. Ensure you update the `.env` file with any additional environment variables required.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or issues, please open an issue on GitHub or contact the repository owner. -->
