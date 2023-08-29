from typing import List

from app.auth_method.schemas import AuthMethodRead
from app.identity_provider.schemas import IdentityProviderRead
from app.provider.schemas import ProviderRead
from app.user_group.schemas import UserGroupRead
from pydantic import Field


class ProviderReadExtended(ProviderRead):
    """Model to extend the Provider data read from the
    DB with the authentication method details.
    """

    relationship: AuthMethodRead = Field(
        description="Authentication method used by the Provider"
    )


class IdentityProviderReadExtended(IdentityProviderRead):
    """Model to extend the Identity Provider data read from the
    DB with the lists of related items.
    """

    user_groups: List[UserGroupRead] = Field(
        default_factory=list, description="List of owned user groups."
    )
    providers: List[ProviderReadExtended] = Field(
        default_factory=list, description="List of supported providers."
    )
