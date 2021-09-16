# Imports
from pydantic import BaseModel, constr
from typing import Optional


class ProjectModel(BaseModel):
    project_name: constr(strip_whitespace=True, min_length=1)
    project_summary: str
    members: Optional[str] = []
