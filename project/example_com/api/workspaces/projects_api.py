# Imports
import fastapi
from fastapi import Depends, Path
from fastapi_cache import JsonCoder
from fastapi_cache.decorator import cache
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
# Custom Imports
from example_com.data.account.users import User
from example_com.infrastructure.jwt_token_auth import get_current_user
from example_com.models.project_schema import ProjectModel
from example_com.models.validation import ValidationError
from example_com.services import project_service

router = fastapi.APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


###############################################################################
# Projects
###############################################################################
@router.get("/api/workspaces/projects")
#@cache(expire=7200, coder=JsonCoder, namespace="get-projects")
async def get_projects(request: Request, current_user: User = Depends(get_current_user)):
    try:
        project = await project_service.get_projects(owner=current_user.username)
        if not project:
            return fastapi.Response(content="Project does not exist.", status_code=404)

        return project

    except Exception as ex:
        print(f"Server crashed while processing request: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


@router.get("/api/workspaces/projects/{id}")
#@cache(expire=7200, coder=JsonCoder, namespace="get-project-by-id")
async def get_project(id: int = Path(..., gt=0), current_user: User = Depends(get_current_user)):
    try:
        project = await project_service.get_project_by_id(id=id, owner=current_user.username)
        if not project:
            return fastapi.Response(content="Project does not exist.", status_code=404)

        return project

    except Exception as ex:
        print(f"Server crashed while processing request: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


###############################################################################
# New Projects
###############################################################################
@router.post("/api/workspaces/projects/new", status_code=201)
async def post_new_project(new_project: ProjectModel,
                            current_user: User = Depends(get_current_user)):
    try:
        return await project_service.create_project(new_project.project_name,
                                                     new_project.project_summary,
                                                     current_user.username,
                                                     new_project.members
                                                     )

    except ValidationError as ve:
        return fastapi.Response(content=ve.error_msg, status_code=ve.status_code)
    except Exception as ex:
        print(f"The project could not be created: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


###############################################################################
# Update Project
###############################################################################
@router.put("/api/workspaces/projects/{id}", status_code=200)
async def update_project(payload: ProjectModel, id: int = Path(..., gt=0),
                          current_user: User = Depends(get_current_user)):
    try:
        project = await project_service.get_project_by_id(id=id, owner=current_user.username)
        if not project:
            return fastapi.Response(content="Project does not exist.", status_code=404)

        updated_project = await project_service.update_project(id=id, owner=current_user.username, payload=payload)

        return updated_project

    except Exception as ex:
        print(f"The project could not be found: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)


###############################################################################
# Delete Project
###############################################################################
@router.delete("/api/workspaces/projects/{id}", status_code=204)
async def delete_project(id: int = Path(..., gt=0), current_user: User = Depends(get_current_user)):
    try:
        project = await project_service.get_project_by_id(id=id, owner=current_user.username)
        if not project:
            return fastapi.Response(content="Project does not exist.", status_code=404)

        await project_service.delete_project(id=id, owner=current_user.username)

    except Exception as ex:
        print(f"The project could not be found: {ex}")
        return fastapi.Response(content="Error processing your request.", status_code=500)
