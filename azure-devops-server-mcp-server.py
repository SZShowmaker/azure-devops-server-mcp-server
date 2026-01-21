
import base64
import requests
from mcp.server.fastmcp import FastMCP


# ========= Configuration Area =========
ORG_URL = "your azure devops server url" # such as http://192.168.1.101/DefaultCollection
PAT = "your PAT"  

# Azure DevOps using Basic Auth，no matter what username is
def _auth_header(pat: str) -> dict:
    token = base64.b64encode(f":{pat}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }

headers = _auth_header(PAT)

# ========= MCP Server =========
mcp = FastMCP("azure-devops-server")

@mcp.tool()
def list_projects() -> list[dict]:
    """
    List all projects of Azure DevOps Server 
    """
    url = f"{ORG_URL}/_apis/projects?api-version=6.0"
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    return [
        {
            "id": p["id"],
            "name": p["name"],
            "state": p["state"]
        }
        for p in data.get("value", [])
    ]

@mcp.tool()
def get_recent_work_items(project: str, limit: int = 30) -> list[dict]:
    """
    Retrieve the most recent changes of Work Items for the specified project (without limiting to any specific type)
    Return a structure suitable for summary analysis by Copilot/LLM
    """

    # 1️⃣ WIQL query（unlimited WorkItemType）
    wiql = {
        "query": f"""
        SELECT
          [System.Id],
          [System.Title],
          [System.State],
          [System.AssignedTo],
          [System.ChangedDate],
          [System.WorkItemType]
        FROM WorkItems
        WHERE
          [System.TeamProject] = '{project}'
        ORDER BY [System.ChangedDate] DESC
        """
    }

    wiql_url = f"{ORG_URL}/{project}/_apis/wit/wiql?api-version=6.0"
    resp = requests.post(wiql_url, headers=headers, json=wiql, timeout=10)
    resp.raise_for_status()

    work_items = resp.json().get("workItems", [])[:limit]
    if not work_items:
        return []

    # 2️⃣ Batch retrieval of Work Item details
    ids = ",".join(str(wi["id"]) for wi in work_items)
    items_url = f"{ORG_URL}/_apis/wit/workitems?ids={ids}&api-version=6.0"

    resp = requests.get(items_url, headers=headers, timeout=10)
    resp.raise_for_status()

    result = []
    for item in resp.json().get("value", []):
        fields = item["fields"]

        result.append({
            "id": item["id"],
            "title": fields.get("System.Title"),
            "state": fields.get("System.State"),
            "assigned_to": (
                fields.get("System.AssignedTo", {}).get("displayName")
                if isinstance(fields.get("System.AssignedTo"), dict)
                else fields.get("System.AssignedTo")
            ),
            "changed_date": fields.get("System.ChangedDate"),
            "work_item_type": fields.get("System.WorkItemType")
        })

    return result


@mcp.tool()
def get_recent_pipelines(project: str, limit: int = 30) -> dict:
    """
    Obtain the most recent Pipeline (Build) execution record of the specified project,
    Return the success rate along with the original data, for Copilot to analyze the reasons for failure
    """

    url = (
        f"{ORG_URL}/{project}/_apis/build/builds"
        f"?$top={limit}&api-version=6.0"
    )

    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()

    builds = resp.json().get("value", [])

    result = []
    success = 0
    failed = 0

    for b in builds:
        build_result = b.get("result")  # succeeded / failed / canceled
        if build_result == "succeeded":
            success += 1
        elif build_result == "failed":
            failed += 1

        result.append({
            "id": b.get("id"),
            "pipeline_name": b.get("definition", {}).get("name"),
            "status": b.get("status"),           # completed / inProgress
            "result": build_result,
            "reason": b.get("reason"),           # manual / individualCI / schedule
            "source_branch": b.get("sourceBranch"),
            "requested_by": b.get("requestedFor", {}).get("displayName"),
            "start_time": b.get("startTime"),
            "finish_time": b.get("finishTime"),
            "web_url": b.get("_links", {})
                .get("web", {})
                .get("href")
        })

    total = len(builds)

    return {
        "project": project,
        "total": total,
        "succeeded": success,
        "failed": failed,
        "success_rate": round(success / total * 100, 2) if total else 0,
        "pipelines": result
    }

if __name__ == "__main__":

   
    mcp.run(transport="stdio")

# if __name__ == "__main__":
#     # debug get_recent_work_items 
#     items = get_recent_work_items("WBTL_ADC", limit=10)
#     for i in items:
#         print(i)
    # projects = list_projects()
    # for p in projects:
    #     print(p)


# if __name__ == "__main__":
#     # debug get_recent_pipelines
#     data = get_recent_pipelines("WBTL_ADC", limit=10)
#     print(data["success_rate"])
#     for p in data["pipelines"]:
#         print(p)
