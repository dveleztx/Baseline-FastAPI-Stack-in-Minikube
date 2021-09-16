# Imports
import fastapi
import jwt
from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
# Custom Imports
from example_com.services import user_service
from example_com.models.validation import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
JWT_SECRET: Optional[str] = None


def set_token(username: str):
    payload = {
        'username': username,
        'iss': 'https://example.com',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    return jwt_token


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await user_service.find_user_by_username(username=payload.get('username'))
        if not user:
            raise ValidationError(error_msg="Incorrect username or password", status_code=401)

        return user

    except jwt.exceptions.DecodeError:
        return fastapi.Response(content="Invalid token", status_code=401)


async def decode_auth_value(token):
    """ Decode authorization token to get payload """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    except jwt.exceptions.DecodeError:
        raise ValidationError(error_msg="Invalid token", status_code=401)

    return payload
