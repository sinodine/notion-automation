from typing import Any
from constants import NotionBasePropertyDisplayName, NotionBasePropertyID, NotionCommentPropertyDisplayName, NotionCommentPropertyID, NotionDatabasePropertyDisplayName, NotionDatabasePropertyID, NotionPagePropertyID


def _extract_property_content(property_data: dict[str, Any]) -> Any:
    """Extracts the content for a given property type."""
    return property_data.get(property_data['type'], None)

def _extract_plain_text_from_rich_text(rich_text_array: list[dict[str, Any]]) -> str:
    """Extracts plain text from a list of rich text objects."""
    return ''.join(item.get('plain_text', '') for item in rich_text_array)

def _extract_property(property_type: str, content: Any, for_display: bool = False) -> Any:
    """Extracts content based on property type and whether it's for display."""
    extractors = {
        'title': _extract_plain_text_from_rich_text,
        'rich_text': _extract_plain_text_from_rich_text,
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
    }
    return extractors.get(property_type, lambda c: None)(content)


def _extract_data_base_properties(page_data: dict[str, Any]) -> dict[NotionBasePropertyID, Any]:
    """
    Extracts base properties from a Notion page.
    Returns a dictionary with extracted properties.
    """
    interpreted_properties = {}
    for prop in NotionBasePropertyID:
        interpreted_properties[prop] = page_data.get(prop.value)
    return interpreted_properties

def _extract_data_page_default_properties(page_data: dict[str, Any]) -> dict[NotionPagePropertyID, Any]:
    """
    Extracts properties from a Notion page based on NotionPagePropertyID.
    Returns a dictionary with extracted properties.
    """
    interpreted_properties = {}
    for prop in NotionPagePropertyID:
        interpreted_properties[prop] = page_data.get(prop.value)
    return interpreted_properties

def _extract_comment_text(comment_data: dict[str, Any], for_display: bool = False) -> str:
    """
    Extracts the comment text from a Notion comment.
    """
    rich_text = comment_data.get("rich_text", [])
    return _extract_plain_text_from_rich_text(rich_text)


def display_page(interpreted_properties: dict[NotionPagePropertyID, Any], detailed: bool, separator: bool):
    """
    Displays a page's properties in a formatted manner.
    """
    n = 60
    c = 20
    prefix = "* "
    page_id = interpreted_properties.get(NotionBasePropertyID.ID, 'N/A')
    print("\n" + "=" * n) if separator else ()
    print(f"{'Page - ' + NotionBasePropertyDisplayName.ID.value:{c}}: {page_id}")

    if detailed:
        print("\nDetailed Properties:\n" + "-" * n)
        for prop in NotionDatabasePropertyID:
            display_name = NotionDatabasePropertyDisplayName[prop.name].value
            value = interpreted_properties.get(prop, 'N/A')
            print(f"{(prefix + display_name):{c}}: {value}")

    print("=" * n)

def display_comment(interpreted_properties: dict[str, Any], detailed: bool, separator: bool):
    """
    Displays a comment in a formatted manner.
    """
    n = 60
    c = 20
    prefix = "* "
    page_id = interpreted_properties.get(NotionBasePropertyID.ID, 'N/A')
    print("\n" + "=" * n) if separator else ()
    print(f"{'Comment - ' + NotionBasePropertyDisplayName.ID.value:{c}}: {page_id}")

    if detailed:
        print("\nDetailed Properties:\n" + "-" * n)
        for prop in NotionCommentPropertyID:
            display_name = NotionCommentPropertyDisplayName[prop.name].value
            value = interpreted_properties.get(prop, 'N/A')
            print(f"{(prefix + display_name):{c}}: {value}")
    
    print("=" * n)

def display_data_item(interpreted_data: dict[str, Any], detailed: bool, separator: bool = True):
    """
    General function to display either page or comment data.
    Uses the 'object' field to determine whether to display a page or comment.
    """
    obj_type = interpreted_data.get(NotionBasePropertyID.OBJECT, 'Unknown')
    if obj_type == 'page':
        display_page(interpreted_data, detailed, separator)
    elif obj_type == 'comment':
        display_comment(interpreted_data, detailed, separator)
    else:
        print(f"Unsupported object type: {obj_type}")