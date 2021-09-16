# Imports
import datetime
import sqlalchemy as sa
import sqlalchemy.orm as orm
# Custom Imports
from example_com.data.modelbase import SqlAlchemyBase


class Project(SqlAlchemyBase):
    __tablename__ = 'projects'

    id = sa.Column(sa.Integer, primary_key=True)
    project_name = sa.Column(sa.String, nullable=False)
    project_summary = sa.Column(sa.String)
    owner = sa.Column(sa.String, sa.ForeignKey("users.username"))
    members = sa.Column(sa.ARRAY(sa.String))
    project_profile_img = sa.Column(sa.String)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
    updated_at = sa.Column(sa.DateTime, default=datetime.datetime.now)

    # Relationships
    user = orm.relation('User')
