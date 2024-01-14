from api.main import hash_client_secret, hash_token, SECRET_SALT
import secrets


def create_client(length: int = 16):
    client_id = secrets.token_urlsafe(length)
    client_secret = secrets.token_urlsafe(length*2)
    saved_token = str(hash_token(client_secret, SECRET_SALT))
    saved_secret = str(hash_client_secret(client_secret))
    print(f"client_id: {client_id}\nclient_secret: {client_secret}\nsaved_secret: {saved_secret}\ntoken: {saved_token}")

create_client()
