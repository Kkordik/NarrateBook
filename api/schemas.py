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
    user_id: int = None
    date_time: datetime = None
    model_config = ConfigDict(from_attributes=True)
