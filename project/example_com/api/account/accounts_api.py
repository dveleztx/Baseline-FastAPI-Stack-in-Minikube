# Imports
import fastapi
from fastapi import Depends
from fastapi_cache import JsonCoder
from fastapi_cache.decorator import cache
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import Response
# Custom Imports
from example_com.data.account.users import User
from example_com.infrastructure.jwt_token_auth import get_current_user, set_token
from example_com.models.user_schema import BaseUserSchema, FullUserSchema, ResetPasswordSchema
from example_com.models.validation import ValidationError, no_dups_validation
from example_com.services import user_service

router = fastapi.APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


###############################################################################
# Account Index
###############################################################################
@router.get("/api/account")
#@cache(expire=7200, coder=JsonCoder, namespace="acct-index")
async def account_index(request: Request, response: Response, current_user: User = Depends(get_current_user)):
    try:
        return current_user

    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)
    except Exception as ex:
        print(f"Server crashed while processing request: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


###############################################################################
# Register Account
###############################################################################
@router.post("/api/account/register", status_code=201)
async def register_account(new_user: FullUserSchema):
    try:
        await no_dups_validation(new_user.username, new_user.email)
        return await user_service.create_user(new_user.first_name,
                                              new_user.last_name,
                                              new_user.username,
                                              new_user.email,
                                              new_user.password)
    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)
    except Exception as ex:
        print(f"The account could not be created: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


###############################################################################
# Login Account
###############################################################################
@router.post("/api/token")
async def login_account(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await user_service.find_user_by_username(form_data.username)
        if not user:
            raise ValidationError(error_msg="Incorrect username or password", status_code=400)

        user_login_creds = await user_service.login_user(form_data.username, form_data.password)
        if not user_login_creds:
            raise ValidationError(error_msg="Incorrect username or password", status_code=400)

        token = set_token(user.username)

        return {"access_token": token, "token_type": "Bearer"}

    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)


###############################################################################
# Update Account
###############################################################################
@router.put("/api/account/{username}", status_code=200)
async def update_account_info(payload: BaseUserSchema, current_user: User = Depends(get_current_user)):
    try:
        return await user_service.update_user(username=current_user.username, payload=payload)

    except Exception as ex:
        print(f"Server crashed while processing request: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


@router.put("/api/account/{username}/security", status_code=200)
async def update_account_password(payload: ResetPasswordSchema, current_user: User = Depends(get_current_user)):
    try:
        if len(payload.new_password) < 10:
            raise ValidationError(error_msg="Password length is less than 10 characters.", status_code=400)

        return await user_service.change_password(username=current_user.username,
                                                  old_pass=payload.old_password, new_pass=payload.new_password)

    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)
    except Exception as ex:
        print(f"Server crashed while processing request: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


###############################################################################
# Delete Account
###############################################################################
@router.delete("/api/account/{username}", status_code=204)
async def delete_account(current_user: User = Depends(get_current_user)):
    try:
        account = await user_service.find_user_by_username(username=current_user.username)
        if not account:
            return fastapi.Response(content="Account does not exist.", status_code=404)

        await user_service.delete_account(current_user.username)

    except Exception as ex:
        print(f"The account could not be found: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)
