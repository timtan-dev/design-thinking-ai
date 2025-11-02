"""Jira API Service - Direct API calls using OAuth tokens"""

import requests
from typing import List, Dict, Any, Optional
from database.models import ImplementationTask, JiraConfig
from services.jira_oauth_service import JiraOAuthService

class JiraAPIService:
    """Handle direct Jira API calls with OAuth authentication"""

    def __init__(self, user_id: str, jira_url: str, cloud_id: str):
        """
        Initialize Jira API service

        Args:
            user_id: Application user ID
            jira_url: Jira instance URL
            cloud_id: Atlassian cloud ID
        """
        self.user_id = user_id
        self.jira_url = jira_url
        self.cloud_id = cloud_id
        self.oauth_service = JiraOAuthService()
        self.api_base = f"https://api.atlassian.com/ex/jira/{cloud_id}/rest/api/3"

    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers with valid access token"""
        access_token = self.oauth_service.get_valid_access_token(self.user_id)

        if not access_token:
            raise Exception("No valid OAuth token found. Please reconnect to Jira.")

        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_epic(self, project_key: str, epic_name: str, description: str = None) -> Dict[str, Any]:
        """
        Create an Epic in Jira

        Args:
            project_key: Jira project key (e.g., "PROJ")
            epic_name: Name of the epic
            description: Optional description

        Returns:
            Created epic data with key, id, etc.
        """
        url = f"{self.api_base}/issue"

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": epic_name,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description or f"Epic for {epic_name}"
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Epic"}
            }
        }

        response = requests.post(url, json=payload, headers=self._get_headers())
        response.raise_for_status()

        return response.json()

    def create_task(self, project_key: str, task: ImplementationTask,
                    epic_key: str = None) -> Dict[str, Any]:
        """
        Create a task in Jira

        Args:
            project_key: Jira project key
            task: ImplementationTask model with task details
            epic_key: Optional epic key to link to

        Returns:
            Created issue data
        """
        url = f"{self.api_base}/issue"

        # Build description with acceptance criteria
        description_content = [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": task.task_description
                    }
                ]
            }
        ]

        # Add acceptance criteria if present
        if task.acceptance_criteria:
            import json
            try:
                criteria_list = json.loads(task.acceptance_criteria)
                description_content.append({
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "\n\nAcceptance Criteria:",
                            "marks": [{"type": "strong"}]
                        }
                    ]
                })
                for criterion in criteria_list:
                    description_content.append({
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": f"• {criterion}"
                            }
                        ]
                    })
            except:
                pass

        # Map priority
        priority_map = {
            "highest": "Highest",
            "high": "High",
            "medium": "Medium",
            "low": "Low"
        }

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": task.task_title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": description_content
                },
                "issuetype": {"name": "Task"},
                "priority": {"name": priority_map.get(task.priority, "Medium")},
                "labels": [
                    task.moscow_category.upper(),
                    f"story-points-{task.story_points}"
                ]
            }
        }

        # Link to epic if provided
        if epic_key:
            payload["fields"]["parent"] = {"key": epic_key}

        # Story points field removed - field ID varies by Jira instance
        # Story points are still visible in labels (e.g., "story-points-8")
        # To re-enable: Find your Jira's story points custom field ID and add:
        # if task.story_points:
        #     payload["fields"]["customfield_XXXXX"] = task.story_points

        response = requests.post(url, json=payload, headers=self._get_headers())

        # Log detailed error for debugging
        if response.status_code >= 400:
            print(f"\n{'='*80}")
            print(f"JIRA API ERROR - Create Task Failed")
            print(f"{'='*80}")
            print(f"Task Title: {task.task_title}")
            print(f"Status Code: {response.status_code}")
            print(f"URL: {url}")
            print(f"\nRequest Payload:")
            import json
            print(json.dumps(payload, indent=2))
            print(f"\nError Response Body:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2))
            except:
                print(response.text)
            print(f"{'='*80}\n")

        response.raise_for_status()

        return response.json()

    def get_issue_status(self, issue_key: str) -> Dict[str, Any]:
        """
        Get status of a Jira issue

        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")

        Returns:
            Issue data with status information
        """
        url = f"{self.api_base}/issue/{issue_key}"

        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()

    def get_project_info(self, project_key: str) -> Dict[str, Any]:
        """
        Get Jira project information

        Args:
            project_key: Jira project key

        Returns:
            Project information
        """
        url = f"{self.api_base}/project/{project_key}"

        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()

        return response.json()

    def bulk_get_issue_statuses(self, issue_keys: List[str]) -> Dict[str, str]:
        """
        Get statuses for multiple issues efficiently

        Args:
            issue_keys: List of Jira issue keys

        Returns:
            Dictionary mapping issue_key to status name
        """
        if not issue_keys:
            return {}

        # Use JQL search to get multiple issues at once
        # Updated to use /search/jql endpoint (v3 API requirement)
        jql = f"key in ({','.join(issue_keys)})"
        url = f"{self.api_base}/search/jql"

        params = {
            "jql": jql,
            "fields": "status",
            "maxResults": len(issue_keys)
        }

        response = requests.get(url, params=params, headers=self._get_headers())
        response.raise_for_status()

        data = response.json()
        result = {}

        for issue in data.get("issues", []):
            issue_key = issue["key"]
            status_name = issue["fields"]["status"]["name"]

            # Map Jira status to our internal status
            if status_name in ["To Do", "Open", "Backlog"]:
                result[issue_key] = "to_do"
            elif status_name in ["In Progress", "In Review"]:
                result[issue_key] = "in_progress"
            elif status_name in ["Done", "Closed", "Resolved"]:
                result[issue_key] = "done"
            else:
                result[issue_key] = "to_do"  # Default

        return result

    def test_connection(self) -> bool:
        """
        Test if Jira connection is working

        Returns:
            True if connection successful
        """
        try:
            url = f"{self.api_base}/myself"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Jira connection test failed: {e}")
            return False

    @staticmethod
    def map_jira_status_to_internal(jira_status: str) -> str:
        """
        Map Jira status names to internal status values

        Args:
            jira_status: Jira status name

        Returns:
            Internal status: to_do, in_progress, or done
        """
        status_lower = jira_status.lower()

        if any(s in status_lower for s in ["to do", "open", "backlog", "todo"]):
            return "to_do"
        elif any(s in status_lower for s in ["in progress", "in review", "progress"]):
            return "in_progress"
        elif any(s in status_lower for s in ["done", "closed", "resolved", "complete"]):
            return "done"
        else:
            return "to_do"  # Default
