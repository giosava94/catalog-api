from uuid import uuid4

from app.identity_provider.models import IdentityProvider
from app.project.crud import project
from app.sla.crud import sla
from app.user_group.models import UserGroup
from tests.utils.project import create_random_project
from tests.utils.sla import (
    create_random_sla,
    create_random_sla_patch,
    validate_create_sla_attrs,
)


def test_create_item(db_user_group: UserGroup) -> None:
    """Create an SLA belonging to a specific user group and pointing to an
    existing projects."""
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = project.create(obj_in=create_random_project(), provider=db_provider)
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    validate_create_sla_attrs(obj_in=item_in, db_item=item)


def test_create_item_default_values(db_user_group: UserGroup) -> None:
    """Create an SLA, with default values when possible, belonging to a
    specific user group and pointing to existing projects."""
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = project.create(obj_in=create_random_project(), provider=db_provider)
    item_in = create_random_sla(default=True, project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    validate_create_sla_attrs(obj_in=item_in, db_item=item)


def test_get_item(db_user_group: UserGroup) -> None:
    """Retrieve an SLA from its UID."""
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = project.create(obj_in=create_random_project(), provider=db_provider)
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    item = sla.get(uid=item.uid)
    validate_create_sla_attrs(obj_in=item_in, db_item=item)


def test_get_non_existing_item(db_user_group: UserGroup) -> None:
    """Try to retrieve a not existing SLA."""
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = project.create(obj_in=create_random_project(), provider=db_provider)
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    item = sla.get(uid=uuid4())
    assert not item


def test_get_items(db_idp_with_multiple_user_groups: IdentityProvider) -> None:
    """Retrieve multiple SLAs."""
    db_user_group = db_idp_with_multiple_user_groups.user_groups.all()[0]
    item = db_user_group.slas.all()[0]

    stored_items = sla.get_multi()
    assert len(stored_items) == 2

    stored_items = sla.get_multi(uid=item.uid)
    assert len(stored_items) == 1
    assert stored_items[0].uid == item.uid


def test_get_items_with_limit(
    db_idp_with_multiple_user_groups: IdentityProvider,
) -> None:
    """Test the 'limit' attribute in GET operations."""
    stored_items = sla.get_multi(limit=0)
    assert len(stored_items) == 0

    stored_items = sla.get_multi(limit=1)
    assert len(stored_items) == 1

    stored_items = sla.get_multi(limit=None)
    assert len(stored_items) == 2


def test_get_sorted_items(db_idp_with_multiple_user_groups: IdentityProvider) -> None:
    """Test the 'sort' attribute in GET operations."""
    items = [i.slas.all()[0] for i in db_idp_with_multiple_user_groups.user_groups]
    sorted_items = list(sorted(items, key=lambda x: x.uid))

    stored_items = sla.get_multi(sort="uid")
    assert sorted_items[0].uid == stored_items[0].uid
    assert sorted_items[1].uid == stored_items[1].uid

    stored_items = sla.get_multi(sort="-uid")
    assert sorted_items[1].uid == stored_items[0].uid
    assert sorted_items[0].uid == stored_items[1].uid


def test_get_items_with_skip(
    db_idp_with_multiple_user_groups: IdentityProvider,
) -> None:
    """Test the 'skip' attribute in GET operations."""
    stored_items = sla.get_multi(skip=0)
    assert len(stored_items) == 2

    stored_items = sla.get_multi(skip=1)
    assert len(stored_items) == 1


def test_patch_item(db_user_group: UserGroup) -> None:
    """Update the attributes of an existing SLA, without updating its
    relationships."""
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = db_provider.projects.all()[0]
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    patch_in = create_random_sla_patch()
    item = sla.update(db_obj=item, obj_in=patch_in)
    for k, v in patch_in.dict().items():
        item_in.__setattr__(k, v)
    validate_create_sla_attrs(obj_in=item_in, db_item=item)


def test_patch_item_with_defaults(db_user_group: UserGroup) -> None:
    """Try to update the attributes of an existing SLA, without updating its
    relationships, with default values.

    The first attempt fails (no updates); the second one, with explicit
    default values, succeeds.
    """
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = db_provider.projects.all()[0]
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    patch_in = create_random_sla_patch(default=True)
    assert not sla.update(db_obj=item, obj_in=patch_in)

    patch_in = create_random_sla_patch(default=True)
    patch_in.description = ""
    item = sla.update(db_obj=item, obj_in=patch_in)
    item_in.description = patch_in.description
    validate_create_sla_attrs(obj_in=item_in, db_item=item)


def test_forced_update(db_user_group: UserGroup) -> None:
    """Update the attributes and relationships of an existing SLA.

    At first update only SLA attributes leaving untouched its
    connections (this is different from the previous test because the
    flag force is set to True).

    Then update the linked projects. The new project list will replace
    the previous linked projects.
    """
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = db_provider.projects.all()[0]
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.update(
        db_obj=item, obj_in=item_in, projects=db_provider.projects, force=True
    )
    validate_create_sla_attrs(obj_in=item_in, db_item=item)

    db_project = project.create(obj_in=create_random_project(), provider=db_provider)
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.update(
        db_obj=item, obj_in=item_in, projects=db_provider.projects, force=True
    )
    validate_create_sla_attrs(obj_in=item_in, db_item=item)


def test_delete_item(db_user_group: UserGroup) -> None:
    """Delete an existing SLA."""
    db_idp = db_user_group.identity_provider.single()
    db_provider = db_idp.providers.all()[0]
    db_project = db_provider.projects.all()[0]
    item_in = create_random_sla(project=db_project.uuid)
    item = sla.create(obj_in=item_in, user_group=db_user_group, project=db_project)
    result = sla.remove(db_obj=item)
    assert result
    item = sla.get(uid=item.uid)
    assert not item