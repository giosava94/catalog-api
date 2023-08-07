from fastapi import APIRouter, Depends, HTTPException, Response, status
from neomodel import db
from typing import List, Optional

from app.flavor.api.dependencies import valid_flavor_id
from app.flavor.models import Flavor
from app.image.api.dependencies import valid_image_id
from app.image.models import Image
from app.project.api.dependencies import (
    valid_project_id,
    validate_new_project_values,
)
from app.project.crud import project
from app.project.models import Project
from app.project.schemas import ProjectQuery, ProjectUpdate
from app.project.schemas_extended import ProjectReadExtended
from app.pagination import Pagination, paginate
from app.query import CommonGetQuery

router = APIRouter(prefix="/projects", tags=["projects"])


@db.read_transaction
@router.get("/", response_model=List[ProjectReadExtended])
def get_projects(
    comm: CommonGetQuery = Depends(),
    page: Pagination = Depends(),
    item: ProjectQuery = Depends(),
):
    items = project.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    return paginate(items=items, page=page.page, size=page.size)


@db.read_transaction
@router.get("/{project_uid}", response_model=ProjectReadExtended)
def get_project(item: Project = Depends(valid_project_id)):
    return item


@db.write_transaction
@router.put(
    "/{project_uid}",
    response_model=Optional[ProjectReadExtended],
    dependencies=[Depends(validate_new_project_values)],
)
def put_project(
    update_data: ProjectUpdate,
    response: Response,
    item: Project = Depends(valid_project_id),
):
    db_item = project.update(db_obj=item, obj_in=update_data)
    if db_item is None:
        response.status_code = status.HTTP_304_NOT_MODIFIED
    return db_item


@db.write_transaction
@router.delete("/{project_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(item: Project = Depends(valid_project_id)):
    if not project.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


@db.write_transaction
@router.put("/{project_uid}/flavors/{flavor_uid}", response_model=ProjectReadExtended)
def connect_project_to_flavor(
    response: Response,
    item: Project = Depends(valid_project_id),
    flavor: Flavor = Depends(valid_flavor_id),
):
    if item.flavors.is_connected(flavor):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.flavors.connect(flavor)
    return item


@db.write_transaction
@router.delete("/{project_uid}/flavors/{flavor_uid}", response_model=ProjectReadExtended)
def disconnect_project_from_flavor(
    response: Response,
    item: Project = Depends(valid_project_id),
    flavor: Flavor = Depends(valid_flavor_id),
):
    if not item.flavors.is_connected(flavor):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.flavors.disconnect(flavor)
    return item


@db.write_transaction
@router.put("/{project_uid}/images/{image_uid}", response_model=ProjectReadExtended)
def connect_project_to_image(
    response: Response,
    item: Project = Depends(valid_project_id),
    image: Image = Depends(valid_image_id),
):
    if item.images.is_connected(image):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.images.connect(image)
    return item


@db.write_transaction
@router.delete("/{project_uid}/images/{image_uid}", response_model=ProjectReadExtended)
def disconnect_project_from_image(
    response: Response,
    item: Project = Depends(valid_project_id),
    image: Image = Depends(valid_image_id),
):
    if not item.images.is_connected(image):
        response.status_code = status.HTTP_304_NOT_MODIFIED
        return None
    item.images.disconnect(image)
    return item
