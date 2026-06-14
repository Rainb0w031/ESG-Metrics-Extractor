"""Text classification module."""

from .text_roles import TEXT_ROLES, ROLE_PATTERNS, get_role_description, get_all_roles
from .role_classifier import RoleClassifier
from .importance_analyzer import ImportanceAnalyzer

__all__ = [
    'TEXT_ROLES',
    'ROLE_PATTERNS',
    'get_role_description',
    'get_all_roles',
    'RoleClassifier',
    'ImportanceAnalyzer',
]

