from enum import Enum


class Permission(str, Enum):
    ACCESS_FILES = "access_files"
    ACCESS_ADMIN_PANEL = "access_admin_panel"
