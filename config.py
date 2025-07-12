import base64
import os
from dotenv import load_dotenv

load_dotenv()
# JIRA_BASE_URL = "https://alluvium-hq-sandbox-277.atlassian.net"
JIRA_BASE_URL = "https://alluvium-hq.atlassian.net"
# JIRA_BASE_URL = "https://goalluvium-sandbox.atlassian.net"
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
if JIRA_API_TOKEN is None:
    raise ValueError("JIRA_API_TOKEN environment variable not set.")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")

auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
auth_bytes = auth_string.encode("utf-8")
auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

HEADERS = {
    "Authorization": f"Basic {auth_base64}",
    "Accept": "application/json"
}