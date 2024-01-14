from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer
from services.token import TokenService
from services.user import UserService
from services.oauth_client import OAuthClientService
from services.oauth_code import OAuthCodeService
from database.init_session import async_session
from .schemas import UserResponseModel


app = FastAPI()
security = HTTPBearer()

token_service = TokenService(async_session)
user_service = UserService(async_session)
oauth_cli_service = OAuthClientService(async_session)
oauth_code_service = OAuthCodeService()


@app.post("/token")
async def token(code: str = Form(), client_id: str = Form(), client_secret: str = Form()):
    if not await oauth_cli_service.validate_client_credentials(client_id, client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = oauth_code_service.validate_authorization_code(code)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization code")

    access_token = await token_service.create_and_store_access_token(user_id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(user_id: int = Depends(token_service.get_current_user_id), response_model=UserResponseModel):
    user = await user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return response_model.model_validate(user)



