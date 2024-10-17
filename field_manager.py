from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

class FieldCategory(Enum):
    """Enum for field categories."""
    STATUT = "Statut"
    EQUIPE = "Équipe"
    RESPONSABLE = "Responsable"
    NOM = "Nom"

@dataclass(frozen=True)
class FieldOption:
    """Data class representing a field option."""
    name: str
    id: str

@dataclass
class FieldManager:
    """Class to manage fields and their corresponding options."""
    _options: Dict[FieldCategory, Dict[str, FieldOption]] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize known options."""
        options = {
            FieldCategory.STATUT: [
                ("À faire", "8e60037a-bd86-4bec-ae03-6dcd5c392137"),
                ("En développement", "41bab616-0dd9-46e7-8ef6-3f32c7a04032"),
                ("En test", "C[hY"),
                ("En relecture", "|y|:"),
                ("Fait", "a087807d-e7e9-4e12-8560-44a3d64d6110")
            ],
            FieldCategory.EQUIPE: [
                ("Design", "2da75352-d78c-4b75-bd04-3e653eeb71e0"),
                ("Ingénierie", "2d4d068c-c51e-4501-9a57-67fdf217de8f")
            ],
            FieldCategory.RESPONSABLE: [
                ("User 1", "user-1-id"),
                ("User 2", "user-2-id")
            ],
            FieldCategory.NOM: [
                ("Project Title", "project-title-id")
            ]
        }

        for category, opts in options.items():
            for name, option_id in opts:
                self.add_option(category, name, option_id)

    def add_option(self, category: FieldCategory, name: str, option_id: str) -> None:
        """Add a new option to a specified category."""
        if category not in self._options:
            self._options[category] = {}
        self._options[category][name] = FieldOption(name, option_id)

    def get_id(self, category: FieldCategory, name: str) -> Optional[str]:
        """Retrieve the ID for a given category and option name."""
        return self._options.get(category, {}).get(name, None).id if name in self._options.get(category, {}) else None

    def list_options(self, category: FieldCategory) -> Dict[str, str]:
        """List all options for a given category."""
        return {option.name: option.id for option in self._options.get(category, {}).values()}

# Example Usage
if __name__ == "__main__":
    field_manager = FieldManager()

    # Accessing IDs
    status_id = field_manager.get_id(FieldCategory.STATUT, "À faire")
    team_id = field_manager.get_id(FieldCategory.EQUIPE, "Ingénierie")
    responsible_id = field_manager.get_id(FieldCategory.RESPONSABLE, "User 1")
    project_title_id = field_manager.get_id(FieldCategory.NOM, "Project Title")

    print(f"Status 'À faire' ID: {status_id}")
    print(f"Team 'Ingénierie' ID: {team_id}")
    print(f"Responsible 'User 1' ID: {responsible_id}")
    print(f"Project Title ID: {project_title_id}")

    # Listing all statuses
    print("\nAvailable Statut options:")
    for name, id in field_manager.list_options(FieldCategory.STATUT).items():
        print(f"{name}: {id}")

    # Listing all teams
    print("\nAvailable Équipe options:")
    for name, id in field_manager.list_options(FieldCategory.EQUIPE).items():
        print(f"{name}: {id}")

    # Listing all Responsables
    print("\nAvailable Responsable options:")
    for name, id in field_manager.list_options(FieldCategory.RESPONSABLE).items():
        print(f"{name}: {id}")

    # Listing all Nom options
    print("\nAvailable Nom options:")
    for name, id in field_manager.list_options(FieldCategory.NOM).items():
        print(f"{name}: {id}")
