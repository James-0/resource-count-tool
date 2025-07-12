from data_fetchers.fetch import JiraFetcher

def categorize_workflows(workflows, schemes, project):

    if not workflows or not schemes:
        return

 # Get removing duplicates
    active_workflows = set()
    inactive_workflows = set()

    # Get active workflows from workflow schemes
    for scheme in schemes.get("values", []):
        scheme_details = JiraFetcher.get_workflow_schemes(scheme[id])
        for workflow in scheme_details.get("workflows", []):
            active_workflows.add(workflow["workflow"])

    # Identify inactive workflows
    all_workflows = {wf["name"] for wf in workflows}
    inactive_workflows = all_workflows - active_workflows

    categorise_workflow = {
        "active_workflows": list(active_workflows),
        "inactive_workflows": list(inactive_workflows)
    }
    return categorise_workflow