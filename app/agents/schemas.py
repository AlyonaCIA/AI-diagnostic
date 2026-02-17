from typing import List

from pydantic import BaseModel, Field


class FixSuggestion(BaseModel):
    explanation: str = Field(description="Brief explanation of the root cause.")
    before: str = Field(description="The faulty code snippet.")
    after: str = Field(description="The corrected code snippet.")
    confidence: float = Field(ge=0, le=1)


class DiagnosticReport(BaseModel):
    severity: str = Field(pattern="^(blocking|warning|info)$")
    stage: str = Field(
        pattern="^(xml_validation|code_generation|iec_compilation|c_compilation)$"
    )
    complexity: str = Field(pattern="^(trivial|moderate|complex)$")
    root_cause: str
    suggestions: List[FixSuggestion]
