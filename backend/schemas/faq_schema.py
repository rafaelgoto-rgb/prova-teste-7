# backend/schemas/faq_schema.py
from pydantic import BaseModel

class FAQBase(BaseModel):
    question: str
    answer: str
    excerpt: str
    link: str

class FAQCreate(FAQBase):
    pass

class FAQRead(FAQBase):
    id: int

    class Config:
        orm_mode = True
