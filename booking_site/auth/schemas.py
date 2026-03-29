from pydantic import BaseModel, Field

class FormSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=50)