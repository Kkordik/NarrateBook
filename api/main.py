from fastapi import FastAPI, Depends, HTTPException, status, Form
from models.orm_interaction.book import BookModel
from models.orm_interaction.token import TokenModel
from models.orm_interaction.user import UserModel
from models.orm_interaction.oauth_client import OAuthClientModel
from models.oauth_code import OAuthCodeModel
from database.init_session import async_session
from .schemas import UserResponseModel


app = FastAPI()


@app.post("/token")
async def token(code: str = Form(), client_id: str = Form(), client_secret: str = Form()):
    if not await OAuthClientModel(async_session).validate_client_credentials(client_id, client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("code is ", type(code), code)
    user_id = OAuthCodeModel(code=code).validate_authorization_code()
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid authorization code")

    access_token = await TokenModel(async_session).create_and_store_access_token(user_id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user_info")
async def read_users_me(token_model: TokenModel = Depends(TokenModel(async_session).get_current_token), response_model=UserResponseModel):
    user = await UserModel(async_session).get_user(token_model.orm_obj.user_id) if token_model.orm_obj else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return response_model.model_validate(user.orm_obj)


@app.get("/user_books")
async def read_user_books(token_model: TokenModel = Depends(TokenModel(async_session).get_current_token)):
    if token_model.orm_obj is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user_books_list = await BookModel(async_session).get_user_books(token_model.orm_obj.user_id)
    result_list = []
    for book in user_books_list:
        result_list.append(
            {
                "book_id": book.book_id,
                "title": book.book_title,
                "author": book.book_author,
                "description": book.book_description,
                "progress_percentage":  int(book.last_char_id / book.char_len) * 100
            }
        )


@app.get("/book")
async def read_user_book(token_model: TokenModel = Depends(TokenModel(async_session).get_current_token), book_id: int = Form()):
    if token_model.orm_obj is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
