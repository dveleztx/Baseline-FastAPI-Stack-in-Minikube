# Imports
from pydantic import BaseModel, EmailStr, constr


class BaseUserSchema(BaseModel):
    first_name: constr(strip_whitespace=True, min_length=1)
    last_name: constr(strip_whitespace=True, min_length=1)


class FullUserSchema(BaseUserSchema):
    username: constr(strip_whitespace=True, min_length=4)
    email: EmailStr
    password: constr(min_length=10)


class ResetPasswordSchema(BaseModel):
    old_password: constr(strip_whitespace=True, min_length=10)
    new_password: constr(strip_whitespace=True, min_length=10)
