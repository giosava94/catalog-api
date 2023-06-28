from fastapi import APIRouter, Depends, HTTPException, status
from neomodel import db
from typing import List, Optional

from ..dependencies import valid_flavor_id
from ...crud import flavor
from ...models import Flavor as FlavorModel
from ...schemas import Flavor, FlavorQuery, FlavorUpdate
from ....pagination import Pagination, paginate
from ....query import CommonGetQuery

router = APIRouter(prefix="/flavors", tags=["flavors"])


@db.read_transaction
@router.get("/", response_model=List[Flavor])
def get_flavors(
    comm: CommonGetQuery = Depends(),
    page: Pagination = Depends(),
    item: FlavorQuery = Depends(),
):
    items = flavor.get_multi(
        **comm.dict(exclude_none=True), **item.dict(exclude_none=True)
    )
    return paginate(items=items, page=page.page, size=page.size)


@db.read_transaction
@router.get("/{flavor_uid}", response_model=Flavor)
def get_flavor(item: FlavorModel = Depends(valid_flavor_id)):
    return item


@db.write_transaction
@router.put("/{flavor_uid}", response_model=Optional[Flavor])
def put_flavor(
    update_data: FlavorUpdate, item: FlavorModel = Depends(valid_flavor_id)
):
    return flavor.update(old_item=item, new_item=update_data)


@db.write_transaction
@router.delete("/{flavor_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_flavors(item: FlavorModel = Depends(valid_flavor_id)):
    if not flavor.remove(item):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item",
        )
