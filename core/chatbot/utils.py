import re

def normalize_email(email: str) -> str:
    email = email.lower().strip()
    email = email.replace("%40", "@")
    email = email.replace("@", "")
    email = email.replace(".", "")
    return email

def get_chat_group_name(widget_id, email):
    safe_email = normalize_email(email)
    return f"chat_{widget_id}_{safe_email}"
