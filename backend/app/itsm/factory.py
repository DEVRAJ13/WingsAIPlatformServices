from app.itsm.base import ITSMProvider
from app.itsm.providers.jira import JiraProvider
from app.itsm.providers.remedy import RemedyProvider
from app.itsm.providers.servicenow import ServiceNowProvider


def get_itsm_provider(
    provider: str,
) -> ITSMProvider:

    normalized = provider.strip().lower()

    providers: dict[str, ITSMProvider] = {
        "jira": JiraProvider(),
        "servicenow": ServiceNowProvider(),
        "remedy": RemedyProvider(),
    }

    selected = providers.get(normalized)

    if selected is None:
        raise ValueError(
            f"Unsupported ITSM provider: {provider}"
        )

    return selected