from app.agents.supervisor import classify_intent


def test_knowledge_question_is_not_incident_operation():
    assert classify_intent("What should happen during a critical incident?") == "knowledge"


def test_incident_diagnosis_routes_to_incident_agent():
    assert classify_intent("Diagnose incident 25") == "incident"


def test_itsm_routes_to_itsm_agent():
    assert classify_intent("Create a ServiceNow ticket") == "itsm"
