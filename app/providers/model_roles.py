from enum import StrEnum


class ModelRole(StrEnum):
    DEFAULT = "default"
    GRAPH_LIBRARIAN = "graph_librarian"
    ARCHITECT = "architect"
    VISION = "vision"
    SANITIZER = "sanitizer"
    CODER = "coder"
    CRITIC = "critic"
    AUDITOR = "auditor"
