# Custom Imports
from example_com.services import user_service


class ValidationError(Exception):
    def __init__(self, error_msg: str, status_code: int):
        super().__init__(error_msg)

        self.status_code = status_code
        self.error_msg = error_msg


async def no_dups_validation(username: str, email: str):
    user = await user_service.find_user_by_username(username)
    if user:
        raise ValidationError(f"The username '{username}' already exists.", status_code=403)

    user = await user_service.find_user_by_email(email)
    if user:
        raise ValidationError(f"The email '{email}' already exists.", status_code=403)
