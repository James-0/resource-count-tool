import base64

JIRA_BASE_URL = ""
JIRA_API_TOKEN = ""
JIRA_EMAIL = ""

auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
auth_bytes = auth_string.encode("utf-8")
auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

HEADERS = {
    "Authorization": f"Basic {auth_base64}",
    "Accept": "application/json"
}