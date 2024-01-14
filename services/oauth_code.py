import os
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from jose import jwt


class OAuthCodeService:
    @staticmethod
    def validate_authorization_code(code: str):
        try:
            payload = jwt.decode(code,  os.getenv('SECRET_SALT'), algorithms=["HS256"])
            user_id = payload.get("user_id")
            if user_id is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
            return user_id
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    @staticmethod
    async def create_auth_code(user_id):
        auth_code_str = jwt.encode(
            {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(minutes=int(os.getenv('CODE_EXPIRE_MIN')))},
            os.getenv('SECRET_KEY'), algorithm='HS256')
        return auth_code_str
