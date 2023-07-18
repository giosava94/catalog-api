from fastapi import APIRouter, Body, Depends, HTTPException, status
from neomodel import db
from typing import List, Optional, Union

from app.flavor.schemas import FlavorRead
from app.image.schemas import ImageRead
from app.project.models import Project as ProjectModel
from app.project.api.dependencies import valid_project_id
from app.pagination import Pagination, paginate
from app.query import CommonGetQuery
from app.service.schemas import (
    ChronosServiceRead,
    KubernetesServiceRead,
    MarathonServiceRead,
    MesosServiceRead,
    NovaServiceRead,
    OneDataServiceRead,
    RucioServiceRead,
)
from app.user_group.api.dependencies import (
    valid_user_group_id,
    is_unique_user_group,
)
from app.user_group.crud import user_group
from app.user_group.models import UserGroup as UserGroupModel
from app.user_group.schemas import (
    UserGroupQuery,
    UserGroupUpdate,
)
from app.user_group.schemas_extended import UserGroupReadExtended

router = APIRouter(prefix="/user_groups", tags=["user_groups"])


@db.read_transaction
@router.get(
    "/",
    response_model=List[UserGroupReadExtended],
)
def get_user_groups(
    comm: CommonGetQuery = Depends(),
    page: Pagination = Depends(),
    item: UserGroupQuery = Depends(),
):
    items = user_group.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    return paginate(items=items, page=page.page, size=page.size)


@db.read_transaction
@router.get("/{user_group_uid}", response_model=UserGroupReadExtended)
def get_user_group(item: UserGroupModel = Depends(valid_user_group_id)):
    return item


@db.write_transaction
@router.put(
    "/{user_group_uid}", response_model=Optional[UserGroupReadExtended]
)
def put_user_group(
    item: UserGroupModel = Depends(valid_user_group_id),
    update_data: UserGroupUpdate = Body(),
):
    if item.name != update_data.name:
        is_unique_user_group(update_data)
    return user_group.update(db_obj=item, obj_in=update_data)


@db.write_transaction
@router.delete("/{user_group_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_group(item: UserGroupModel = Depends(valid_user_group_id)):
    if not user_group.remove(db_obj=item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )


@db.read_transaction
@router.get("/{user_group_uid}/flavors", response_model=List[FlavorRead])
def read_user_group_flavors(
    item: UserGroupModel = Depends(valid_user_group_id),
):
    return item.flavors()


@db.read_transaction
@router.get("/{user_group_uid}/images", response_model=List[ImageRead])
def read_user_group_images(
    item: UserGroupModel = Depends(valid_user_group_id),
):
    return item.images()


@db.read_transaction
@router.get(
    "/{user_group_uid}/services",
    response_model=List[
        Union[
            ChronosServiceRead,
            KubernetesServiceRead,
            MarathonServiceRead,
            MesosServiceRead,
            NovaServiceRead,
            OneDataServiceRead,
            RucioServiceRead,
        ]
    ],
)
def read_user_group_services(
    item: UserGroupModel = Depends(valid_user_group_id),
):
    return item.services()


@db.write_transaction
@router.put("/{user_group_uid}/projects", response_model=UserGroupReadExtended)
def connect_user_group_project(
    item: UserGroupModel = Depends(valid_user_group_id),
    project: ProjectModel = Depends(valid_project_id),
):
    item.projects.connect(project)
    return item


@db.read_transaction
@router.delete(
    "/{user_group_uid}/projects", response_model=UserGroupReadExtended
)
def disconnect_user_group_project(
    item: UserGroupModel = Depends(valid_user_group_id),
    project: ProjectModel = Depends(valid_project_id),
):
    item.projects.disconnect(project)
    return item