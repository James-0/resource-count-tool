from data_fetchers.fetch import JiraFetcher
RESOURCES = {
    "Custom Fields": {
        "fetch_function": JiraFetcher.get_custom_fields,
        "keys": ["id", "name", "schema.type", "custom"],
        "should_additional_processes" : True
    },
    "Projects": {
        "fetch_function": JiraFetcher.get_projects,
        "keys": ["id", "name", "insight.lastIssueUpdateTime", "insight.totalIssueCount"],
    },
    "Workflows": {
        "fetch_function": JiraFetcher.get_workflows,
        "keys": ["id.name", "created"],
        "dependencies": ["Workflow Schemes"],
        "should_additional_processes" : True,
    },
    "Workflow Schemes": {
        "fetch_function": JiraFetcher.get_workflow_schemes,
        "keys": ["id", "name"],
        "should_additional_processes" : True,
    },
    "Issue Types": {
        "fetch_function": JiraFetcher.get_issue_types,
        "keys": ["id", "name"],
        "dependencies": ["Projects"]
    },
    "Issue Type Schemes": {
        "fetch_function": JiraFetcher.get_issue_type_schemes,
        "keys": ["id", "name"],
        "dependencies": ["Projects"]
    },
    "Issue Type Screen Schemes": {
        "fetch_function": JiraFetcher.get_issue_type_screen_schemes,
        "keys": ["id", "name"],
        "should_temp" : True,
        "store_key" : "ids_list",
        "dependencies": ["Projects"]
    },
    "Issue Priorities": {
        "fetch_function": JiraFetcher.get_issue_priorities,
        "keys": ["id", "name"]
    },
    "Priority Schemes": {
        "fetch_function": JiraFetcher.get_priority_schemes,
        "sec_function": JiraFetcher.get_projects_by_priority_scheme,
        "should_additional_processes" : True,
        "keys": ["id", "name", "isDefault"]
    },
# Ignore thisss for now
    # "Issue Statuses": { 
    #     "fetch_function": JiraFetcher.get_issue_statuses,
    #     "keys": ["id", "name"]
    # },
# stop ignoring here
    "Issue Link Types": {
        "fetch_function": JiraFetcher.get_issue_link_types,
        "keys": ["id", "name"]
    },
    "Issue Resolutions": {
        "fetch_function": JiraFetcher.get_issue_resolutions,
        "keys": ["id", "name"]
    },
    "Permission Schemes" : {
        "fetch_function": JiraFetcher.get_permission_schemes,
        "keys": ["id", "name"],
        "dependencies" : ["Projects"]
    },
    "Groups": {
        "fetch_function": JiraFetcher.get_groups,
        "keys": ["groupId", "name"]
    },
    # "Users": {
        # "fetch_function": JiraFetcher.get_users,
    #     "keys": ["accountId", "displayName", "accountType", "active"]
    # },
    "Screens": {
        "fetch_function": JiraFetcher.get_screens,
        "keys": ["id", "name"],
        "should_additional_processes" : True,
        "dependencies": ["Screen Schemes"]
    },
    "Screen Schemes": {
        "fetch_function": JiraFetcher.get_screen_schemes,
        "sec_function": JiraFetcher.get_issue_type_screen_scheme,
        "keys": ["id", "name", "screens"],
        "should_temp" : True,
        "store_key" : "active_screens",
        "dependencies": ["Issue Type Screen Schemes"]
    },
    "Project Roles": {
        "fetch_function": JiraFetcher.get_project_roles,
        "keys": ["id", "name"]
    },
    "Dashboards": {
        "fetch_function": JiraFetcher.get_dashboards,
        "keys": ["id", "name"],
        "values" : "dashboards"
    },
    "Field Configuration Schemes": {
        "fetch_function": JiraFetcher.get_field_configuration_schemes,
        "keys": ["id", "name"],
        "dependencies": ["Projects"]
    },
    "Notification Schemes": {
        "fetch_function": JiraFetcher.get_notification_schemes,
        "keys": ["id", "name"],
        "dependencies": ["Projects"]
    },
    "Issue Security Schemes": {
        "fetch_function": JiraFetcher.get_project_security_scheme,
        "sec_function": JiraFetcher.get_issue_security_scheme,
        "keys": ["id", "name"],
        "values" : "values",
        "should_additional_processes" : True,
        "unique" : True
    }
}
