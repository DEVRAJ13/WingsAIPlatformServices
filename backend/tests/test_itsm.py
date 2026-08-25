from app.itsm.providers.servicenow import ServiceNowProvider


def test_servicenow_priority_mapping():
    assert ServiceNowProvider._priority("CRITICAL") == "1"
    assert ServiceNowProvider._priority("High") == "2"
    assert ServiceNowProvider._priority("Medium") == "3"
    assert ServiceNowProvider._priority("Low") == "4"
