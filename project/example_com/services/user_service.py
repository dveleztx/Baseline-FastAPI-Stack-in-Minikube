# Imports
import datetime
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
from sqlalchemy import update, delete
from sqlalchemy.future import select
from typing import Optional
# Custom Libraries
from example_com.data import db_session
from example_com.data.account.users import User
from example_com.models.user_schema import BaseUserSchema
from example_com.models.validation import ValidationError


async def find_user_by_email(email: str) -> Optional[User]:
    async with db_session.create_session() as session:
        query = select(User).filter(User.email == email)
        result = await session.execute(query)

        return result.scalar_one_or_none()


async def find_user_by_username(username: str) -> Optional[User]:
    async with db_session.create_session() as session:
        query = select(User).filter(User.username == username)
        result = await session.execute(query)

        return result.scalar_one_or_none()


async def find_user_by_id(uid: int) -> Optional[User]:
    async with db_session.create_session() as session:
        query = select(User).filter(User.id == uid)
        result = await session.execute(query)

        return result.scalar_one_or_none()


async def create_user(first_name: str, last_name: str, username: str, email: str, password: str) -> Optional[User]:
    # Create User Object
    user = User()
    user.first_name = first_name
    user.last_name = last_name
    user.username = username
    user.email = email
    user.hashed_password = crypto.using(rounds=184_597).hash(password)

    # Add user to database and commit
    async with db_session.create_session() as session:
        session.add(user)
        await session.commit()

    await session.close()

    return user


async def confirm_user(email: str) -> Optional[User]:
    async with db_session.create_session() as session:
        query = select(User).filter(User.email == email)
        user = await session.execute(query)
        if not user:
            return None

        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        await session.commit()

    return user


async def login_user(username: str, password: str) -> Optional[User]:
    async with db_session.create_session() as session:
        query = select(User).filter(User.username == username)
        results = await session.execute(query)

        user = results.scalar_one_or_none()
        if not user:
            return None

        try:
            if not crypto.verify(password, user.hashed_password):
                return None
        except ValueError:
            return None

        return user


async def update_user(username: str, payload: BaseUserSchema):
    async with db_session.create_session() as session:
        async with session.begin():
            query = (
                update(User).
                where(User.username == username).
                values(first_name=payload.first_name, last_name=payload.last_name).
                returning(User)
            )
            user_details = await session.execute(query)

            return dict(user_details.one())


async def change_password(username: str, old_pass: str, new_pass: str):
    async with db_session.create_session() as session:
        async with session.begin():
            query = select(User).filter(User.username == username)
            results = await session.execute(query)

            user = results.scalar_one_or_none()

            # Change password
            if not crypto.verify(old_pass, user.hashed_password):
                raise ValidationError(error_msg="Password is incorrect.", status_code=400)
            else:
                new_hashed_password = crypto.using(rounds=184_597).hash(new_pass)
                query = (
                    update(User).
                    where(User.username == username).
                    values(hashed_password=new_hashed_password).
                    returning(User)
                )
                user_details = await session.execute(query)

                return dict(user_details.one())


async def delete_account(username: str):
    async with db_session.create_session() as session:
        async with session.begin():
            query = (
                delete(User).
                where(User.username == username)
            )
            await session.execute(query)
