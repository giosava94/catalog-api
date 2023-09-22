from typing import Optional

from app.models import BaseNode, BaseNodeCreate, BaseNodeRead
from app.query import create_query_model
from app.service.enum import ServiceType
from pydantic import Extra, Field, validator


class QuotaBase(BaseNode, extra=Extra.allow):
    """Model with Quota basic attributes."""

    type: ServiceType = Field(description="Service type.")
    per_user: bool = Field(default=False, description="Quota to apply for each user")


class QuotaCreate(BaseNodeCreate, QuotaBase):
    """Model to create a Quota.

    Class without id (which is populated by the database). Expected as
    input when performing a POST request.
    """


class QuotaUpdate(QuotaCreate):
    """Model to update a Quota.

    Class without id (which is populated by the database). Expected as
    input when performing a PUT request.

    Default to None mandatory attributes.
    """


class QuotaRead(BaseNodeRead, QuotaBase):
    """Model to read Service data retrieved from DB.

    Class to read data retrieved from the database. Expected as output
    when performing a generic REST request. It contains all the non-
    sensible data written in the database.

    Add the *uid* attribute, which is the item unique identifier in the
    database.
    """


class QuotaReadPublic(BaseNodeRead, QuotaBase):
    pass


class QuotaReadShort(BaseNodeRead, QuotaBase):
    pass


QuotaQuery = create_query_model("QuotaQuery", QuotaBase)


class ComputeQuotaBase(QuotaBase, extra=Extra.ignore):
    """Model derived from ServiceBase to inherit attributes common to all
    services. It adds the basic attributes for Compute services.

    Validation: type value is exactly ServiceType.openstack_nova.
    """

    type: ServiceType = Field(
        default=ServiceType.COMPUTE, description="Block storage type"
    )
    cores: Optional[int] = Field(default=None, description="")
    fixed_ips: Optional[int] = Field(default=None, description="")
    public_ips: Optional[int] = Field(default=None, description="")
    instances: Optional[int] = Field(default=None, description="")
    ram: Optional[int] = Field(default=None, description="")

    @validator("type", check_fields=False)
    def check_type(cls, v):
        if v != ServiceType.COMPUTE:
            raise ValueError(f"Not valid type: {v}")
        return v


class ComputeQuotaCreate(BaseNodeCreate, ComputeQuotaBase):
    pass


class ComputeQuotaUpdate(ComputeQuotaCreate):
    pass


class ComputeQuotaRead(BaseNodeRead, ComputeQuotaBase):
    pass


class ComputeQuotaReadPublic(BaseNodeRead, ComputeQuotaBase):
    pass


class ComputeQuotaReadShort(BaseNodeRead, ComputeQuotaBase):
    pass


ComputeQuotaQuery = create_query_model("ComputeQuotaQuery", ComputeQuotaBase)


class BlockStorageQuotaBase(QuotaBase, extra=Extra.ignore):
    """Model derived from ServiceBase to inherit attributes common to all
    services. It adds the basic attributes for BlockStorage services.

    Validation: type value is exactly ServiceType.openstack_nova.
    """

    type: ServiceType = Field(
        default=ServiceType.BLOCK_STORAGE, description="Block storage type"
    )
    gigabytes: Optional[int] = Field(default=None, description="")
    per_volume_gigabytes: Optional[int] = Field(default=None, description="")
    volumes: Optional[int] = Field(default=None, description="")

    @validator("type", check_fields=False)
    def check_type(cls, v):
        if v != ServiceType.BLOCK_STORAGE:
            raise ValueError(f"Not valid type: {v}")
        return v


class BlockStorageQuotaCreate(BaseNodeCreate, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaUpdate(BlockStorageQuotaCreate):
    pass


class BlockStorageQuotaRead(BaseNodeRead, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaReadPublic(BaseNodeRead, BlockStorageQuotaBase):
    pass


class BlockStorageQuotaReadShort(BaseNodeRead, BlockStorageQuotaBase):
    pass


BlockStorageQuotaQuery = create_query_model(
    "BlockStorageQuotaQuery", BlockStorageQuotaBase
)
