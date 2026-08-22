from pydantic import BaseModel, Field


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=100_000)


class DocumentCreateResponse(BaseModel):
    id: int
    title: str
    chunks_created: int


class RAGQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4_000)


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    model: str

class AgentQueryRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=4_000,
    )

    incident_id: int | None = None


class AgentQueryResponse(BaseModel):
    answer: str
    intent: str
    sources: list[dict]
    diagnosis: dict | None = None

    