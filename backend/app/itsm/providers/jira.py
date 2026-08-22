from typing import Any

import httpx

from app.core.config import settings
from app.itsm.base import ITSMProvider


class JiraProvider(ITSMProvider):
    name = "jira"

    def _validate_configuration(self) -> None:
        if not settings.jira_base_url:
            raise RuntimeError(
                "Jira base URL is not configured."
            )

        if not settings.jira_email:
            raise RuntimeError(
                "Jira email is not configured."
            )

        if not settings.jira_api_token:
            raise RuntimeError(
                "Jira API token is not configured."
            )

        if not settings.jira_project_key:
            raise RuntimeError(
                "Jira project key is not configured."
            )

    def _base_url(self) -> str:
        return settings.jira_base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _auth(self) -> tuple[str, str]:
        return (
            settings.jira_email,
            settings.jira_api_token,
        )

    def _timeout(self) -> httpx.Timeout:
        return httpx.Timeout(
            connect=10.0,
            read=30.0,
            write=10.0,
            pool=10.0,
        )

    @staticmethod
    def _error_details(response: httpx.Response) -> str:
        try:
            data = response.json()

            if isinstance(data, dict):
                error_messages = data.get(
                    "errorMessages"
                )

                errors = data.get(
                    "errors"
                )

                if error_messages or errors:
                    return (
                        f"errorMessages={error_messages}, "
                        f"errors={errors}"
                    )

        except (ValueError, TypeError):
            pass

        return response.text[:2000]

    async def health_check(self) -> dict:
        """
        Verify Jira authentication without creating
        or modifying any Jira issue.
        """
        self._validate_configuration()

        url = (
            f"{self._base_url()}"
            "/rest/api/3/myself"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                )

        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Jira health check timed out.",
                "details": str(exc),
            }

        except httpx.HTTPError as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Unable to connect to Jira.",
                "details": str(exc),
            }

        if response.status_code >= 400:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": "Jira authentication failed.",
                "details": self._error_details(response),
            }

        try:
            data = response.json()

        except ValueError:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira returned an invalid JSON response."
                ),
                "details": response.text[:2000],
            }

        return {
            "success": True,
            "provider": self.name,
            "status_code": response.status_code,
            "account_id": data.get("accountId"),
            "display_name": data.get("displayName"),
            "email_address": data.get("emailAddress"),
            "message": "Jira authentication successful.",
        }

    async def verify_project(self) -> dict:
        """
        Verify that the configured Jira project exists
        and is accessible to the configured account.
        """
        self._validate_configuration()

        url = (
            f"{self._base_url()}"
            f"/rest/api/3/project/"
            f"{settings.jira_project_key}"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                )

        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Jira project check timed out.",
                "details": str(exc),
            }

        except httpx.HTTPError as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Unable to connect to Jira.",
                "details": str(exc),
            }

        if response.status_code >= 400:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "project_key": settings.jira_project_key,
                "message": (
                    "Jira project verification failed."
                ),
                "details": self._error_details(response),
            }

        try:
            data = response.json()

        except ValueError:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira returned an invalid JSON response."
                ),
                "details": response.text[:2000],
            }

        return {
            "success": True,
            "provider": self.name,
            "status_code": response.status_code,
            "project_key": data.get("key"),
            "project_name": data.get("name"),
            "message": "Jira project is accessible.",
        }

    async def _get_priority_id(
        self,
        priority: str | None,
    ) -> str | None:
        """
        Resolve a Jira priority name to its Jira priority ID.

        Example:
            WINGS priority "HIGH"
            -> Jira priority "High"
            -> Jira priority ID "10001"
        """

        if not priority:
            return None

        url = (
            f"{self._base_url()}"
            "/rest/api/3/priority"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                )

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Jira priority lookup timed out."
            ) from exc

        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Unable to retrieve Jira priorities."
            ) from exc

        if response.status_code >= 400:
            raise RuntimeError(
                "Unable to retrieve Jira priorities. "
                f"HTTP status: {response.status_code}. "
                f"Details: {self._error_details(response)}"
            )

        try:
            data = response.json()

        except ValueError as exc:
            raise RuntimeError(
                "Jira returned an invalid priority response."
            ) from exc

        if not isinstance(data, list):
            raise RuntimeError(
                "Jira returned an invalid priority list."
            )

        requested_priority = (
            priority.strip().lower()
        )

        # -----------------------------------------------------
        # Direct case-insensitive name match
        # -----------------------------------------------------

        for item in data:
            if not isinstance(item, dict):
                continue

            name = str(
                item.get("name", "")
            ).strip().lower()

            if name == requested_priority:
                priority_id = item.get("id")

                if priority_id:
                    return str(priority_id)

        # -----------------------------------------------------
        # WINGS -> Jira common priority aliases
        #
        # This handles cases such as:
        #
        # WINGS: HIGH
        # Jira:  High
        #
        # WINGS: CRITICAL
        # Jira:  Highest
        # -----------------------------------------------------

        aliases = {
            "critical": {
                "highest",
                "critical",
                "blocker",
            },
            "high": {
                "high",
                "major",
            },
            "medium": {
                "medium",
                "normal",
            },
            "low": {
                "low",
                "minor",
            },
        }

        allowed_names = aliases.get(
            requested_priority,
            set(),
        )

        for item in data:
            if not isinstance(item, dict):
                continue

            name = str(
                item.get("name", "")
            ).strip().lower()

            if name in allowed_names:
                priority_id = item.get("id")

                if priority_id:
                    return str(priority_id)

        return None

    async def get_priorities(self) -> dict:
        """
        Return all priorities available to the Jira account.

        Useful for diagnostics and configuration.
        """
        self._validate_configuration()

        url = (
            f"{self._base_url()}"
            "/rest/api/3/priority"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                )

        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Jira priority lookup timed out.",
                "details": str(exc),
            }

        except httpx.HTTPError as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Unable to retrieve Jira priorities.",
                "details": str(exc),
            }

        if response.status_code >= 400:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": "Jira priority lookup failed.",
                "details": self._error_details(response),
            }

        try:
            data = response.json()

        except ValueError:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira returned an invalid priority response."
                ),
                "details": response.text[:2000],
            }

        priorities = []

        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue

                priorities.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                    }
                )

        return {
            "success": True,
            "provider": self.name,
            "status_code": response.status_code,
            "priorities": priorities,
        }

    async def create_ticket(
        self,
        *,
        title: str,
        description: str,
        priority: str | None = None,
        **kwargs: Any,
    ) -> dict:
        """
        Create a Jira issue.

        Priority is resolved dynamically to the Jira
        priority ID instead of sending the priority name.
        """
        self._validate_configuration()

        # -----------------------------------------------------
        # RESOLVE PRIORITY
        # -----------------------------------------------------

        priority_id = None

        if priority:
            try:
                priority_id = await self._get_priority_id(
                    priority
                )

            except RuntimeError as exc:
                return {
                    "success": False,
                    "provider": self.name,
                    "message": str(exc),
                }

            if priority_id is None:
                return {
                    "success": False,
                    "provider": self.name,
                    "message": (
                        f"Jira priority '{priority}' "
                        "is not available."
                    ),
                    "details": (
                        "Use the Jira priority list returned by "
                        "the get_priorities operation."
                    ),
                }

        # -----------------------------------------------------
        # CREATE ISSUE URL
        # -----------------------------------------------------

        url = (
            f"{self._base_url()}"
            "/rest/api/3/issue"
        )

        # -----------------------------------------------------
        # ISSUE PAYLOAD
        # -----------------------------------------------------

        fields: dict[str, Any] = {
            "project": {
                "key": settings.jira_project_key,
            },
            "summary": title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": description,
                            }
                        ],
                    }
                ],
            },
            "issuetype": {
                "name": "Task",
            },
        }

        # -----------------------------------------------------
        # PRIORITY
        # -----------------------------------------------------

        if priority_id:
            fields["priority"] = {
                "id": priority_id,
            }

        payload = {
            "fields": fields,
        }

        # -----------------------------------------------------
        # CREATE ISSUE
        # -----------------------------------------------------

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.post(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                    json=payload,
                )

        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": (
                    "Jira ticket creation timed out."
                ),
                "details": str(exc),
            }

        except httpx.HTTPError as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Unable to connect to Jira.",
                "details": str(exc),
            }

        # -----------------------------------------------------
        # JIRA ERROR
        # -----------------------------------------------------

        if response.status_code >= 400:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira ticket creation failed."
                ),
                "details": self._error_details(
                    response
                ),
            }

        # -----------------------------------------------------
        # PARSE RESPONSE
        # -----------------------------------------------------

        try:
            data = response.json()

        except ValueError:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira returned an invalid "
                    "creation response."
                ),
                "details": response.text[:2000],
            }

        ticket_id = data.get("key")

        if not ticket_id:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira created the issue but "
                    "returned no ticket key."
                ),
                "details": response.text[:2000],
            }

        return {
            "success": True,
            "provider": self.name,
            "ticket_id": ticket_id,
            "ticket_url": (
                f"{self._base_url()}"
                f"/browse/{ticket_id}"
            ),
            "priority": priority,
            "priority_id": priority_id,
            "message": (
                "Jira ticket created successfully."
            ),
        }

    async def get_ticket(
        self,
        *,
        ticket_id: str,
        **kwargs: Any,
    ) -> dict:
        """
        Retrieve a Jira issue.
        """
        self._validate_configuration()

        url = (
            f"{self._base_url()}"
            f"/rest/api/3/issue/{ticket_id}"
        )

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                )

        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": (
                    "Jira ticket lookup timed out."
                ),
                "details": str(exc),
            }

        except httpx.HTTPError as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Unable to connect to Jira.",
                "details": str(exc),
            }

        if response.status_code >= 400:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": "Jira ticket lookup failed.",
                "details": self._error_details(
                    response
                ),
            }

        try:
            data = response.json()

        except ValueError:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": (
                    "Jira returned an invalid "
                    "ticket response."
                ),
                "details": response.text[:2000],
            }

        fields = data.get(
            "fields",
            {},
        )

        status_data = fields.get(
            "status",
            {},
        )

        priority_data = fields.get(
            "priority",
            {},
        )

        return {
            "success": True,
            "provider": self.name,
            "ticket_id": data.get("key"),
            "summary": fields.get("summary"),
            "status": status_data.get("name"),
            "priority": priority_data.get("name"),
        }

    async def update_ticket(
        self,
        *,
        ticket_id: str,
        **fields: Any,
    ) -> dict:
        """
        Update fields on an existing Jira issue.
        """
        self._validate_configuration()

        url = (
            f"{self._base_url()}"
            f"/rest/api/3/issue/{ticket_id}"
        )

        # -----------------------------------------------------
        # COPY FIELDS SO CALLER DATA IS NOT MUTATED
        # -----------------------------------------------------

        update_fields = dict(fields)

        # -----------------------------------------------------
        # RESOLVE PRIORITY IF PROVIDED
        # -----------------------------------------------------

        priority = update_fields.get(
            "priority"
        )

        if isinstance(priority, str):
            priority_id = await self._get_priority_id(
                priority
            )

            if priority_id is None:
                return {
                    "success": False,
                    "provider": self.name,
                    "message": (
                        f"Jira priority '{priority}' "
                        "is not available."
                    ),
                }

            update_fields["priority"] = {
                "id": priority_id,
            }

        payload = {
            "fields": update_fields,
        }

        try:
            async with httpx.AsyncClient(
                timeout=self._timeout()
            ) as client:
                response = await client.put(
                    url,
                    headers=self._headers(),
                    auth=self._auth(),
                    json=payload,
                )

        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": (
                    "Jira ticket update timed out."
                ),
                "details": str(exc),
            }

        except httpx.HTTPError as exc:
            return {
                "success": False,
                "provider": self.name,
                "message": "Unable to connect to Jira.",
                "details": str(exc),
            }

        if response.status_code >= 400:
            return {
                "success": False,
                "provider": self.name,
                "status_code": response.status_code,
                "message": "Jira ticket update failed.",
                "details": self._error_details(
                    response
                ),
            }

        return {
            "success": True,
            "provider": self.name,
            "ticket_id": ticket_id,
            "message": (
                "Jira ticket updated successfully."
            ),
        }