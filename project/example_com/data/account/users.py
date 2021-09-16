# Imports
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
# Custom Imports
from example_com.data.modelbase import SqlAlchemyBase
from example_com.data.workspaces.projects import Project


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id: int = sa.Column(sa.Integer, primary_key=True)
    first_name: str = sa.Column(sa.String, nullable=False)
    last_name: str = sa.Column(sa.String, nullable=False)
    username: str = sa.Column(sa.String, unique=True, nullable=False, index=True)
    email: str = sa.Column(sa.String, unique=True, nullable=False, index=True)
    hashed_password: str = sa.Column(sa.String, nullable=False, index=True)
    profile_image_url = sa.Column(sa.String)
    confirmed: bool = sa.Column(sa.Boolean, nullable=False, default=False)
    confirmed_on = sa.Column(sa.DateTime, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
    last_login = sa.Column(sa.DateTime, default=datetime.datetime.now)
    is_admin = sa.Column(sa.Boolean, default=False)

    # Relationships
    projects = orm.relation("Project", order_by=Project.id.desc(), back_populates='user')
