import subprocess
from typing import List, Optional
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, root_validator, validator

from app.auth_method.schemas import AuthMethodBase
from app.identity_provider.schemas import IdentityProviderBase
from app.location.schemas import LocationBase
from app.provider.enum import ProviderType
from app.provider.schemas import ProviderBase
from app.provider.schemas_extended import find_duplicates
from app.quota.schemas import BlockStorageQuotaBase, ComputeQuotaBase, NetworkQuotaBase
from app.region.schemas import RegionBase
from app.sla.schemas import SLABase
from app.user_group.schemas import UserGroupBase


class SLA(SLABase):
    projects: List[str] = Field(
        default_factory=list, description="List of projects UUID"
    )

    @validator("projects", pre=True)
    def validate_projects(cls, v):
        v = [i.hex if isinstance(i, UUID) else i for i in v]
        find_duplicates(v)
        return v

    @root_validator
    def start_date_before_end_date(cls, values):
        start = values.get("start_date")
        end = values.get("end_date")
        assert start < end, f"Start date {start} greater than end date {end}"
        return values


class UserGroup(UserGroupBase):
    slas: List[SLA] = Field(default_factory=list, description="List of SLAs")

    @validator("slas")
    def validate_slas(cls, v):
        find_duplicates(v, "doc_uuid")
        assert len(v), "SLA list can't be empty"
        return v


class TrustedIDP(IdentityProviderBase):
    issuer: AnyHttpUrl = Field(description="issuer url")
    token: str = Field(description="Access token")
    user_groups: List[UserGroup] = Field(
        default_factory=list, description="User groups"
    )
    relationship: Optional[AuthMethodBase] = Field(default=None, description="")

    @root_validator(pre=True)
    def rename_issuer_to_endpoint(cls, values):
        values["endpoint"] = values.get("issuer")
        # Generate token
        if values.get("token") is None:
            token_cmd = subprocess.run(
                [
                    "docker",
                    "exec",
                    "catalog-api-oidc-agent-1",
                    "oidc-token",
                    values.get("endpoint"),
                ],
                stdout=subprocess.PIPE,
                text=True,
            )
            values["token"] = token_cmd.stdout.strip("\n")
        return values


class Limits(BaseModel):
    block_storage: Optional[BlockStorageQuotaBase] = Field(
        default=None, description="Block storage per user quota"
    )
    compute: Optional[ComputeQuotaBase] = Field(
        default=None, description="Compute per user quota"
    )
    network: Optional[NetworkQuotaBase] = Field(
        default=None, description="Network per user quota"
    )

    @validator("block_storage")
    def set_per_user_block_storage(
        cls, v: Optional[BlockStorageQuotaBase]
    ) -> Optional[BlockStorageQuotaBase]:
        if v is not None:
            v.per_user = True
        return v

    @validator("compute")
    def set_per_user_compute(
        cls, v: Optional[ComputeQuotaBase]
    ) -> Optional[ComputeQuotaBase]:
        if v is not None:
            v.per_user = True
        return v

    @validator("network")
    def set_per_user_network(
        cls, v: Optional[NetworkQuotaBase]
    ) -> Optional[NetworkQuotaBase]:
        if v is not None:
            v.per_user = True
        return v


class PrivateNetProxy(BaseModel):
    ip: str = Field(description="Proxy IP address")
    user: str = Field(description="Username to use when performing ssh operations")


class PerRegionProps(BaseModel):
    region_name: str = Field(description="Region name")
    default_public_net: Optional[str] = Field(
        default=None, description="Name of the default public network"
    )
    default_private_net: Optional[str] = Field(
        default=None, description="Name of the default private network"
    )
    private_net_proxy: Optional[PrivateNetProxy] = Field(
        default=None, description="Proxy details to use to access to private network"
    )
    per_user_limits: Optional[Limits] = Field(
        default=None,
        description="Quota limitations to apply to users owning this project",
    )


class AuthMethod(AuthMethodBase):
    idp_name: str = Field(
        alias="name", description="Identity provider name used to authenticate"
    )
    endpoint: AnyHttpUrl = Field(description="Identity Provider URL")


class BlockStorageVolMap(BaseModel):
    ...


class Project(BaseModel):
    id: str = Field(default=None, description="Project unique ID or name")
    default_public_net: Optional[str] = Field(
        default=None, description="Name of the default public network"
    )
    default_private_net: Optional[str] = Field(
        default=None, description="Name of the default private network"
    )
    private_net_proxy: Optional[PrivateNetProxy] = Field(
        default=None, description="Proxy details to use to access to private network"
    )
    per_user_limits: Optional[Limits] = Field(
        default=None,
        description="Quota limitations to apply to users owning this project",
    )
    per_region_props: List[PerRegionProps] = Field(
        default_factory=list, description="Region specific properties"
    )
    sla: str = Field(description="SLA document uuid")

    @validator("sla", pre=True)
    def sla_to_string(cls, v):
        if isinstance(v, UUID):
            return v.hex
        return v

    @validator("id", pre=True)
    def id_to_string(cls, v):
        if isinstance(v, UUID):
            return v.hex
        return v


class Region(RegionBase):
    location: Optional[LocationBase] = Field(
        default=None, description="Location details"
    )


class Provider(ProviderBase):
    auth_url: AnyHttpUrl = Field(description="Identity service endpoint")
    block_storage_vol_types: Optional[BlockStorageVolMap] = Field(default=None)
    identity_providers: List[AuthMethod] = Field(
        description="List of supported identity providers"
    )
    regions: List[Region] = Field(
        default_factory=list, description="List of hosted regions"
    )


class Openstack(Provider):
    type: ProviderType = Field(default="openstack", description="Provider type")
    projects: List[Project] = Field(
        description="List of Projects belonged by this provider"
    )
    image_tags: List[str] = Field(
        default_factory=list, description="List of image tags to filter"
    )
    network_tags: List[str] = Field(
        default_factory=list, description="List of network tags to filter"
    )

    @validator("type")
    def type_fixed(cls, v):
        assert v == ProviderType.OS
        return v

    @validator("regions")
    def default_region(cls, v):
        if len(v) == 0:
            v.append(Region(name="RegionOne"))
        return v


class Kubernetes(Provider):
    type: ProviderType = Field(default="kubernetes", description="Provider type")
    projects: List[Project] = Field(description="List of names")

    @validator("type")
    def type_fixed(cls, v):
        assert v == ProviderType.K8S
        return v

    @validator("regions")
    def default_region(cls, v):
        if len(v) == 0:
            v.append(Region(name="default"))
        return v


class SiteConfig(BaseModel):
    trusted_idps: List[TrustedIDP] = Field(
        description="List of OIDC-Agent supported identity providers endpoints"
    )
    openstack: List[Openstack] = Field(
        default_factory=list,
        description="List of openstack providers to integrate in the CMDB",
    )
    kubernetes: List[Kubernetes] = Field(
        default_factory=list,
        description="List of openstack providers to integrate in the CMDB",
    )
