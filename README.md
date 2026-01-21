# azure-devops-server-mcp-server

A minimal MCP (Model Context Protocol) server implementation for **on-premises Azure DevOps Server**, built with Python.

This project provides a simple bridge between LLM-based agents (via MCP) and a self-hosted Azure DevOps Server instance.

---

## Features

This MCP server exposes the following tools:

- **List Projects**  
  Retrieve basic information of all projects in the organization.

- **Recent Work Items**  
  Fetch recently updated work items for a specified project.

- **Recent Pipelines**  
  Retrieve recent pipeline (build) execution records and calculate success rates.

---

## Requirements

- Python 3.9+
- Azure DevOps Server (on-premises)
- Azure DevOps Personal Access Token (PAT) with **read-only** permissions

---

## Security Notice

- This project requires an Azure DevOps **Personal Access Token (PAT)**.  
  **Never hard-code credentials** in source code. Use environment variables instead.

- This project is intended for **local, trusted environments only**.

- The MCP server exposes project metadata and work item summaries to the connected LLM.  
  Do **not** use it with untrusted or public LLM endpoints.

---

## Disclaimer

This project is **not affiliated with or endorsed by Microsoft**.

---

## VS Code MCP Configuration Example

Create a `mcp.json` file under `.vscode/` in your workspace.

> ⚠️ The following configuration is for **reference only**.  
> Adjust paths according to your local environment.

```json
{
  "servers": {
    "azure-devops-server": {
      "type": "stdio",
      "command": "<path-to-python-interpreter>",
      "args": [
        "<path-to-azure-devops-server-mcp-server.py>"
      ]
    }
  }
}
