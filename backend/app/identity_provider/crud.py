from typing import List, Optional, Union

from app.crud import CRUDBase
from app.identity_provider.models import IdentityProvider
from app.identity_provider.schemas import (
    IdentityProviderCreate,
    IdentityProviderRead,
    IdentityProviderReadPublic,
    IdentityProviderReadShort,
    IdentityProviderUpdate,
)
from app.identity_provider.schemas_extended import (
    IdentityProviderReadExtended,
    IdentityProviderReadExtendedPublic,
)
from app.project.models import Project
from app.provider.models import Provider
from app.provider.schemas_extended import IdentityProviderCreateExtended
from app.user_group.crud import user_group


class CRUDIdentityProvider(
    CRUDBase[
        IdentityProvider,
        IdentityProviderCreate,
        IdentityProviderUpdate,
        IdentityProviderRead,
        IdentityProviderReadPublic,
        IdentityProviderReadShort,
        IdentityProviderReadExtended,
        IdentityProviderReadExtendedPublic,
    ]
):
    """"""

    def create(
        self, *, obj_in: IdentityProviderCreateExtended, provider: Provider
    ) -> IdentityProvider:
        db_obj = self.get(endpoint=obj_in.endpoint)
        if not db_obj:
            db_obj = super().create(obj_in=obj_in)
        else:
            updated_data = self.update(db_obj=db_obj, obj_in=obj_in)
            if updated_data:
                db_obj = updated_data
        db_obj.providers.connect(provider, obj_in.relationship.dict())

        for item in obj_in.user_groups:
            db_user_group = db_obj.user_groups.get_or_none(name=item.name)
            if db_user_group:
                user_group.update(
                    db_obj=db_user_group,
                    obj_in=item,
                    projects=provider.projects,
                    force=True,
                )
            else:
                user_group.create(
                    obj_in=item, identity_provider=db_obj, projects=provider.projects
                )

        return db_obj

    def remove(self, *, db_obj: IdentityProvider) -> bool:
        for item in db_obj.user_groups:
            user_group.remove(db_obj=item)
        return super().remove(db_obj=db_obj)

    def update(
        self,
        *,
        db_obj: IdentityProvider,
        obj_in: Union[IdentityProviderUpdate, IdentityProviderCreateExtended],
        projects: List[Project] = [],
        provider: Optional[Provider] = None,
        force: bool = False
    ) -> Optional[IdentityProvider]:
        edit = False
        if force:
            edit = self.__update_user_groups(
                db_obj=db_obj, obj_in=obj_in, provider_projects=projects
            )
            if provider is not None:
                rel = db_obj.providers.relationship(provider)
                if (
                    rel.protocol != obj_in.relationship.protocol
                    or rel.idp_name != obj_in.relationship.idp_name
                ):
                    db_obj.providers.replace(provider, obj_in.relationship.dict())
                    edit = True

        if isinstance(obj_in, IdentityProviderCreateExtended):
            obj_in = IdentityProviderUpdate.parse_obj(obj_in)

        updated_data = super().update(db_obj=db_obj, obj_in=obj_in, force=force)
        return db_obj if edit else updated_data

    def __update_user_groups(
        self,
        *,
        obj_in: IdentityProviderCreateExtended,
        db_obj: IdentityProvider,
        provider_projects: List[Project]
    ) -> bool:
        edit = False
        db_items = {db_item.name: db_item for db_item in db_obj.user_groups}
        for item in obj_in.user_groups:
            db_item = db_items.pop(item.name, None)
            if not db_item:
                user_group.create(
                    obj_in=item, identity_provider=db_obj, projects=provider_projects
                )
                edit = True
            else:
                updated_data = user_group.update(
                    db_obj=db_item, obj_in=item, projects=provider_projects, force=True
                )
                if not edit and updated_data is not None:
                    edit = True
        for db_item in db_items.values():
            user_group.remove(db_obj=db_item)
            edit = True
        return edit


identity_provider = CRUDIdentityProvider(
    model=IdentityProvider,
    create_schema=IdentityProviderCreate,
    read_schema=IdentityProviderRead,
    read_public_schema=IdentityProviderReadPublic,
    read_short_schema=IdentityProviderReadShort,
    read_extended_schema=IdentityProviderReadExtended,
    read_extended_public_schema=IdentityProviderReadExtendedPublic,
)
