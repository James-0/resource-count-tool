# Jira Resource Test Tool

This is a utility tool designed to fetch, count, and analyze various Jira resources (e.g. workflows, screens, schemes) from a Jira Cloud instance using its REST API.

⚠️ **Note:** This tool is still in active development. Results may not yet be 100% accurate. We are continually validating outputs manually and resolving issues as we encounter discrepancies.

---

## 🔧 Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/jira-resource-test-tool.git
cd jira-resource-test-tool
```

### 2. Install Requirements

Make sure you’re using Python 3.8+

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory with the following keys:

```env
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_BASE_URL=https://your-domain.atlassian.net
```

These credentials will be used to authenticate API requests.

---

### 4. Required Permissions

Ensure that the account used has **sufficient permissions** in Jira Cloud:

- Admin or Site Admin access is recommended.
- Without adequate permissions, the tool may fail to fetch certain resources (e.g. workflows, schemes, permissions) and return incomplete data or 403 errors.


## 📦 How to Use

### 1. Select Resources to Query

Open the `RESOURCES.py` file.  
This file contains a list of resources you can extract from Jira (e.g., Workflows, Screens, Issue Types, etc.).

To enable or disable a resource:
- **Uncomment** the resource entry to include it in the test.
- **Comment out** any resources you don’t want to include.

⚠️ **Important:**  
If a resource has dependencies (e.g., Workflows depend on Screens), **ensure that the dependent resource is also uncommented**. Missing dependencies may result in incomplete or incorrect results.

---

## 🧪 Development Status

This tool is in its **development stage**.

- Results are not guaranteed to be 100% accurate yet.
- Manual validation is ongoing for each resource.
- We’re actively improving the logic to ensure better match and consistency between Jira's internal representations and API responses.


---

## 📁 Output

After running, the tool exports results to an `.xlsx` file in the `reports/` folder with a filename like:

```
reports/jira_report_YYYYMMDD_HHMMSS.xlsx
```

This file contains counts and metadata for the selected resources.

---

