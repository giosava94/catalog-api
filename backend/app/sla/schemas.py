from datetime import datetime
from pydantic import UUID4, BaseModel
from typing import Optional

from app.models import BaseNodeCreate, BaseNodeRead
from app.query import create_query_model


class SLABase(BaseModel):
    start_date: datetime
    end_date: Optional[datetime] = None
    document_uuid: Optional[UUID4] = None


class SLACreate(BaseNodeCreate, SLABase):
    """Service Level Agreement (SLA) Create Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT, PUT or POST request.

    Attributes:
        description (str): Brief description.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
        project (UUID4): UUID4 of the target Project.
        user_group (UUID4): UUID4 of the target UserGroup.
        quotas (list of QuotaCreate): List of quotas defined by the SLA.
    """


class SLAUpdate(SLACreate):
    """Service Level Agreement (SLA) Update Model class.

    Class without id (which is populated by the database).
    Expected as input when performing a PUT request.

    Attributes:
        description (str): Brief description.
        start_date (datetime | None): SLA validity start date.
        end_date (datetime | None): SLA validity end date.
        project (UUID4 | None): UUID4 of the target Project.
        user_group (UUID4 | None): UUID4 of the target UserGroup.
        quotas (list of QuotaCreate): List of quotas defined by the SLA.
    """


class SLARead(BaseNodeRead, SLABase):
    """Service Level Agreement (SLA) class.

    Class retrieved from the database.
    Expected as output when performing a REST request.
    It contains all the non-sensible data written
    in the database.

    Attributes:
        uid (uuid): Unique ID.
        description (str): Brief description.
        start_date (datetime): SLA validity start date.
        end_date (datetime): SLA validity end date.
        project (Project): UUID4 of the target Project.
        user_group (UserGroup): UUID4 of the target UserGroup.
        quotas (list of Quota): List of quotas defined by the SLA.
    """


SLAQuery = create_query_model("SLAQuery", SLABase)