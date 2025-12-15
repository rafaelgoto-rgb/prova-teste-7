# backend/schemas/email_schema.py
from pydantic import BaseModel

class EmailBase(BaseModel):
    sender: str
    subject: str
    body: str

class EmailCreate(EmailBase):
    pass

class EmailRead(EmailBase):
    id: int

    class Config:
        orm_mode = True
