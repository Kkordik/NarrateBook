import os
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import jwt


class OAuthCodeModel:
    def __init__(self, code: str = None, user_id=None, exp_date: datetime = None):
        self.code = code
        self.user_id = user_id
        self.exp_date = exp_date

    def validate_authorization_code(self):
        if not self.code:
            raise Exception("No code specified")
        print("code2 is ", type(self.code), self.code)
        try:
            payload = jwt.decode(self.code, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            self.user_id = payload.get("user_id")

            if self.user_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
            return self.user_id
        
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    async def create_auth_code(self):
        if not self.user_id:
            raise Exception("No user_id specified")
        
        self.exp_date = datetime.utcnow() + timedelta(minutes=int(os.getenv('CODE_EXPIRE_MIN')))
        self.code = jwt.encode(
            {'user_id': self.user_id, 'exp': self.exp_date},
            os.getenv('SECRET_KEY'), algorithm='HS256')
        return self.code
