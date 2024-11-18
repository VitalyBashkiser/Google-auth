from enum import StrEnum


class Messages(StrEnum):
    EMAIL_CONFIRMATION = "confirmation_email"
    PASSWORD_RESET = "password_reset"
    CHANGE_EMAIL = "change_email"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "revoke_permission"
    ACCESS_FILES = "access_files"
    ACCESS_ADMIN_PANEL = "access_admin_panel"
    COMPANY_UPDATE_NOTIFICATION = "company_update_notification"
