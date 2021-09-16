# Imports
from typing import List, Optional
from sqlalchemy import update, delete
from sqlalchemy.future import select
# Custom Libraries
from example_com.data import db_session
from example_com.data.workspaces.projects import Project
from example_com.models.project_schema import ProjectModel
from example_com.models.validation import ValidationError


async def get_projects(owner: str) -> Optional[List[Project]]:
    async with db_session.create_session() as session:
        query = select(Project).filter(Project.owner == owner)
        result = await session.execute(query)

    return list(result)


async def get_project_by_id(id: int, owner: str) -> Optional[Project]:
    async with db_session.create_session() as session:
        query = select(Project). \
            filter(Project.id == id). \
            filter(Project.owner == owner)
        result = await session.execute(query)

    return result.scalar_one_or_none()


async def find_project_by_name(project_name: str, owner: str) -> Optional[Project]:
    async with db_session.create_session() as session:
        query = select(Project). \
            filter(Project.project_name == project_name). \
            filter(Project.owner == owner)
        result = await session.execute(query)

        return result.scalar_one_or_none()


async def create_project(project_name: str, project_summary: str, owner: str, members: Optional[list]) -> Optional[
    Project]:
    project_exists = await find_project_by_name(project_name, owner)
    if project_exists:
        raise ValidationError(f"The project {project_name} already exists", status_code=403)

    # Create Project Object
    project = Project()
    project.project_name = project_name
    project.project_summary = project_summary
    project.owner = owner
    if members:
        project.members = members

    # Add project to database and commit
    async with db_session.create_session() as session:
        session.add(project)
        await session.commit()

    await session.close()

    return project


async def update_project(id: int, owner: str, payload: ProjectModel):
    async with db_session.create_session() as session:
        async with session.begin():
            query = (
                update(Project).
                where(Project.id == id).
                where(Project.owner == owner).
                values(project_name=payload.project_name, project_summary=payload.project_summary,
                       members=payload.members).
                returning(Project)
            )
            project_details = await session.execute(query)

            return dict(project_details.one())


async def delete_project(id: int, owner: str):
    async with db_session.create_session() as session:
        async with session.begin():
            query = (
                delete(Project).
                where(Project.id == id).
                where(Project.owner == owner)
            )
            await session.execute(query)
