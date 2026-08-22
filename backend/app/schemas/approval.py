from pydantic import BaseModel, Field


class ApprovalCreate(BaseModel):
    tool_name: str = Field(
        min_length=1,
        max_length=100,
    )

    reason: str = Field(
        min_length=1,
        max_length=2000,
    )

    parameters: dict = {}


class ApprovalDecision(BaseModel):
    decision: str

    comment: str | None = Field(
        default=None,
        max_length=2000,
    )


class ApprovalResponse(BaseModel):
    id: int
    tool_name: str
    status: str
    reason: str
    parameters: dict | None = None