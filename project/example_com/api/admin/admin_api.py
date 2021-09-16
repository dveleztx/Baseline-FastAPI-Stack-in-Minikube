# Imports
import fastapi
from fastapi import Depends
from fastapi_cache.decorator import cache
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
# Custom Imports
from example_com.config import Settings, get_settings
from example_com.data.account.users import User
from example_com.infrastructure.jwt_token_auth import get_current_user
from example_com.models.validation import ValidationError

router = fastapi.APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


###############################################################################
# Admin Settings
###############################################################################
@router.get("/api/admin/settings")
@cache(expire=7200, namespace="admin-settings")
async def account_index(request: Request, settings: Settings = Depends(get_settings), current_user: User = Depends(get_current_user)):
    try:
        if current_user.is_admin:
            return {
                "environment": settings.environment,
                "testing": settings.testing,
                "database_url": settings.database_url
            }
        else:
            raise ValidationError("Unauthorized", status_code=401)

    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)
    except Exception as ex:
        print(f"Server crashed while processing request: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)
