from typing import Any
import httpx

from app.core.config import settings
from app.itsm.base import ITSMProvider


class ServiceNowProvider(ITSMProvider):
    name = "servicenow"

    def _validate(self) -> None:
        if not settings.servicenow_base_url or not settings.servicenow_username or not settings.servicenow_password:
            raise ValueError("ServiceNow integration is not configured.")

    def _url(self, ticket_id: str | None = None) -> str:
        base = settings.servicenow_base_url.rstrip("/")
        return f"{base}/api/now/table/incident" + (f"/{ticket_id}" if ticket_id else "")

    @staticmethod
    def _priority(priority: str) -> str:
        value = str(priority or "3").strip().lower()
        mapping = {"critical": "1", "highest": "1", "high": "2", "medium": "3", "moderate": "3", "low": "4", "lowest": "5"}
        return mapping.get(value, value if value in {"1", "2", "3", "4", "5"} else "3")

    async def create_ticket(self, *, title: str, description: str, priority: str, **kwargs: Any) -> dict:
        self._validate()
        payload = {
            "short_description": title,
            "description": description,
            "urgency": self._priority(priority),
            "impact": kwargs.get("impact", "2"),
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self._url(), auth=(settings.servicenow_username, settings.servicenow_password), json=payload, headers={"Accept": "application/json", "Content-Type": "application/json"})
        except httpx.HTTPError as exc:
            return {"success": False, "provider": self.name, "message": "Unable to connect to ServiceNow.", "details": str(exc)}
        if response.status_code >= 400:
            return {"success": False, "provider": self.name, "status_code": response.status_code, "message": "ServiceNow incident creation failed.", "details": response.text[:2000]}
        try:
            result = response.json().get("result", {})
        except ValueError:
            return {"success": False, "provider": self.name, "message": "ServiceNow returned an invalid response.", "details": response.text[:2000]}
        number = result.get("number") or result.get("sys_id")
        if not number:
            return {"success": False, "provider": self.name, "message": "ServiceNow created the record but returned no incident number."}
        return {"success": True, "provider": self.name, "ticket_id": number, "sys_id": result.get("sys_id"), "ticket_url": f"{settings.servicenow_base_url.rstrip('/')}/nav_to.do?uri=incident.do?sys_id={result.get('sys_id')}" if result.get("sys_id") else None, "message": "ServiceNow incident created successfully."}

    async def get_ticket(self, *, ticket_id: str, **kwargs: Any) -> dict:
        self._validate()
        params = {"sysparm_query": f"number={ticket_id}", "sysparm_limit": "1"}
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self._url(), params=params, auth=(settings.servicenow_username, settings.servicenow_password), headers={"Accept": "application/json"})
        except httpx.HTTPError as exc:
            return {"success": False, "provider": self.name, "message": "Unable to connect to ServiceNow.", "details": str(exc)}
        if response.status_code >= 400:
            return {"success": False, "provider": self.name, "status_code": response.status_code, "message": "ServiceNow incident lookup failed.", "details": response.text[:2000]}
        data = response.json().get("result", [])
        if not data:
            return {"success": False, "provider": self.name, "message": f"ServiceNow incident {ticket_id} was not found."}
        item = data[0]
        return {"success": True, "provider": self.name, "ticket_id": item.get("number"), "sys_id": item.get("sys_id"), "summary": item.get("short_description"), "status": item.get("state"), "priority": item.get("priority")}

    async def update_ticket(self, *, ticket_id: str, **fields: Any) -> dict:
        self._validate()
        payload = dict(fields)
        if "priority" in payload:
            payload["urgency"] = self._priority(payload.pop("priority"))
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                lookup = await client.get(self._url(), params={"sysparm_query": f"number={ticket_id}", "sysparm_limit": "1"}, auth=(settings.servicenow_username, settings.servicenow_password), headers={"Accept": "application/json"})
                if lookup.status_code >= 400:
                    return {"success": False, "provider": self.name, "status_code": lookup.status_code, "message": "ServiceNow incident lookup failed.", "details": lookup.text[:2000]}
                rows = lookup.json().get("result", [])
                if not rows:
                    return {"success": False, "provider": self.name, "message": f"ServiceNow incident {ticket_id} was not found."}
                sys_id = rows[0].get("sys_id")
                response = await client.patch(self._url(sys_id), auth=(settings.servicenow_username, settings.servicenow_password), json=payload, headers={"Accept": "application/json", "Content-Type": "application/json"})
        except httpx.HTTPError as exc:
            return {"success": False, "provider": self.name, "message": "Unable to connect to ServiceNow.", "details": str(exc)}
        if response.status_code >= 400:
            return {"success": False, "provider": self.name, "status_code": response.status_code, "message": "ServiceNow incident update failed.", "details": response.text[:2000]}
        return {"success": True, "provider": self.name, "ticket_id": ticket_id, "message": "ServiceNow incident updated successfully."}
