from pydantic import BaseModel, Field


class PasteCodeRequest(BaseModel):
    language: str = Field(..., examples=["python"])
    code: str = Field(..., min_length=1)
