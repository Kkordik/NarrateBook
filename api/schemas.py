from pydantic import BaseModel, ConfigDict
from datetime import datetime


# Token request form model
class TokenRequestForm(BaseModel):
    grant_type: str
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str


class UserResponseModel(BaseModel):
    user_id: int
    date_time: datetime
    model_config = ConfigDict(from_attributes=True)


class Book(BaseModel):
    book_id: int
    book_title: str
    book_author: str
    book_description: str
    model_config = ConfigDict(from_attributes=True)