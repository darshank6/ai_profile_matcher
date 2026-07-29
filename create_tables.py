from app.database import Base
from app.database import engine
from fastapi import Depends
from app.models import *
from app.utils.security import verify_token
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database import get_db

from app.repositories.user_repo import UserRepository

from app.utils.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)

token: str = Depends(oauth2_scheme)
print(token)
payload = verify_token(token)
print(payload)

# def get_current_user(

#     token: str = Depends(
#         oauth2_scheme
#     ),

#     db: Session = Depends(
#         get_db
#     )
# ):
#     payload = verify_token(token)
print("Tables created successfully")