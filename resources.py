from data_fetchers.fetch import JiraFetcher
RESOURCES = {
    # "Custom Fields": {
    #     "fetch_function": JiraFetcher.get_custom_fields,
    #     "keys": ["id", "name", "schema.type", "custom"],
    #     "should_additional_processes" : True
    # },
    "Projects": {
        "fetch_function": JiraFetcher.get_projects,
        "keys": ["id", "name", "insight.lastIssueUpdateTime", "insight.totalIssueCount", "archived"],
    },
    "Workflows": {
        "fetch_function": JiraFetcher.get_workflows,
        "keys": ["id", "name", "updated", "transitions"],
        "store_key": "Screen IDs in workflow",
        "dependencies": ["Workflow Schemes"],
        "should_additional_processes" : True,
    },
    "Workflow Schemes": {
        "fetch_function": JiraFetcher.get_workflow_schemes,
        "keys": ["id", "name"],
        "should_additional_processes" : True,
    },
    # "Issue Types": {
    #     "fetch_function": JiraFetcher.get_issue_types,
    #     "keys": ["id", "name"],
    #     "dependencies": ["Projects"],
    # },
    # "Issue Type Schemes": {
    #     "fetch_function": JiraFetcher.get_issue_type_schemes,
    #     "keys": ["id", "name"],
    #     "dependencies": ["Projects"]
    # },
    "Issue Statuses": { 
        "fetch_function": JiraFetcher.get_issue_statuses,
        "keys": ["id", "name", "workflowUsages"]
    },
    # "Issue Priorities": {
    #     "fetch_function": JiraFetcher.get_issue_priorities,
    #     "keys": ["id", "name"]
    # },
    # "Priority Schemes": {
    #     "fetch_function": JiraFetcher.get_priority_schemes,
    #     "sec_function": JiraFetcher.get_projects_by_priority_scheme,
    #     "should_additional_processes" : True,
    #     "keys": ["id", "name", "isDefault"]
    # },
    # "Issue Link Types": {
    #     "fetch_function": JiraFetcher.get_issue_link_types,
    #     "keys": ["id", "name"]
    # },
    # "Issue Resolutions": {
    #     "fetch_function": JiraFetcher.get_issue_resolutions,
    #     "keys": ["id", "name"]
    # },
    # "Permission Schemes" : {
    #     "fetch_function": JiraFetcher.get_permission_schemes,
    #     "keys": ["id", "name"],
    #     "dependencies" : ["Projects"]
    # },
    # "Groups": {
    #     "fetch_function": JiraFetcher.get_groups,
    #     "keys": ["groupId", "name"]
    # },
    # "Users": {
    #     "fetch_function": JiraFetcher.get_users,
    #     "keys": ["accountId", "displayName", "accountType", "active"]
    # },
    "Screens": {
        "fetch_function": JiraFetcher.get_screens,
        "keys": ["id", "name"],
        "should_additional_processes" : True,
        "dependencies": ["Screen Schemes", "Workflows"]
    },
    "Screen Schemes": {
        "fetch_function": JiraFetcher.get_screen_schemes,
        "sec_function": JiraFetcher.get_issue_type_screen_scheme,
        "keys": ["id", "name"],
        "dependencies": ["Issue Type Screen Schemes"]
    },
    "Issue Type Screen Schemes": {
        "fetch_function": JiraFetcher.get_issue_type_screen_schemes,
        "keys": ["id", "name"],
        "dependencies": ["Projects"]
    },
    # "Project Roles": {
    #     "fetch_function": JiraFetcher.get_project_roles,
    #     "keys": ["id", "name"]
    # },
    # "Field Configuration": {
    #     "fetch_function": JiraFetcher.get_field_configurations,
    #     "keys": ["id", "name", "description"]
    # },
    # "Field Configuration Schemes": {
    #     "fetch_function": JiraFetcher.get_field_configuration_schemes,
    #     "keys": ["id", "name"],
    #     "dependencies": ["Projects"]
    # },
    # "Notification Schemes": {
    #     "fetch_function": JiraFetcher.get_notification_schemes,
    #     "keys": ["id", "name"],
    #     "dependencies": ["Projects"]
    # },
    # "Issue Security Schemes": {
    #     "fetch_function": JiraFetcher.get_project_security_scheme,
    #     "sec_function": JiraFetcher.get_issue_security_scheme,
    #     "keys": ["id", "name"],
    #     "values" : "values",
    #     "should_additional_processes" : True,
    #     "unique" : True
    # }
    
    # "Dashboards": {
    #     "fetch_function": JiraFetcher.get_dashboards,
    #     "keys": ["id", "name"],
    #     "values" : "dashboards"
    # },
}
