from uuid import uuid4

from app.location.crud import location
from app.location.models import Location
from app.region.models import Region
from tests.utils.location import (
    create_random_location,
    create_random_location_patch,
    validate_create_location_attrs,
)


def test_create_item(db_region: Region) -> None:
    """Create a Location belonging to a specific Region."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_create_item_default_values(db_region: Region) -> None:
    """Create a Location, with default values when possible, belonging to a
    specific Region."""
    item_in = create_random_location(default=True)
    item = location.create(obj_in=item_in, region=db_region)
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_create_when_site_already_exists(db_location: Location) -> None:
    """Try to create a Location belonging to a specific Region, when a Location
    with the same site name already exists.

    At first create a location with new attributes but same site name of
    existing one. The result will have the attributes of the new one.

    Then create a location with default values, except one, and same
    site name of existing one. The result will keep the previous
    attributes instead of defaults and update the new given attributes.

    Finally create a location with everything equal to the existing one.
    No changes.
    """
    db_region = db_location.regions.all()[0]

    item_in = create_random_location()
    item_in.site = db_location.site
    item = location.create(obj_in=item_in, region=db_region)
    validate_create_location_attrs(obj_in=item_in, db_item=item)

    item_in = create_random_location(default=True)
    item_in.site = item.site
    item = location.create(obj_in=item_in, region=db_region)
    item_in.description = item.description
    item_in.latitude = item.latitude
    item_in.longitude = item.longitude
    validate_create_location_attrs(obj_in=item_in, db_item=item)

    item = location.create(obj_in=item_in, region=db_region)
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_get_item(db_region: Region) -> None:
    """Retrieve a Location from its UID."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    item = location.get(uid=item.uid)
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_get_non_existing_item(db_region: Region) -> None:
    """Try to retrieve a not existing Location."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    item = location.get(uid=uuid4())
    assert not item


def test_get_items(db_region: Region) -> None:
    """Retrieve multiple Locations."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    item_in2 = create_random_location()
    item2 = location.create(obj_in=item_in2, region=db_region)

    stored_items = location.get_multi()
    assert len(stored_items) == 2

    stored_items = location.get_multi(uid=item.uid)
    assert len(stored_items) == 1
    validate_create_location_attrs(obj_in=item_in, db_item=stored_items[0])

    stored_items = location.get_multi(uid=item2.uid)
    assert len(stored_items) == 1
    validate_create_location_attrs(obj_in=item_in2, db_item=stored_items[0])


def test_get_items_with_limit(db_region: Region) -> None:
    """Test the 'limit' attribute in GET operations."""
    item_in = create_random_location()
    location.create(obj_in=item_in, region=db_region)
    item_in2 = create_random_location()
    location.create(obj_in=item_in2, region=db_region)

    stored_items = location.get_multi(limit=0)
    assert len(stored_items) == 0

    stored_items = location.get_multi(limit=1)
    assert len(stored_items) == 1

    stored_items = location.get_multi(limit=None)
    assert len(stored_items) == 2


def test_get_sorted_items(db_region: Region) -> None:
    """Test the 'sort' attribute in GET operations."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    item_in2 = create_random_location()
    item2 = location.create(obj_in=item_in2, region=db_region)

    sorted_items = list(sorted([item, item2], key=lambda x: x.uid))

    stored_items = location.get_multi(sort="uid")
    assert sorted_items[0].uid == stored_items[0].uid
    assert sorted_items[1].uid == stored_items[1].uid

    stored_items = location.get_multi(sort="-uid")
    assert sorted_items[1].uid == stored_items[0].uid
    assert sorted_items[0].uid == stored_items[1].uid


def test_get_items_with_skip(db_region: Region) -> None:
    """Test the 'skip' attribute in GET operations."""
    item_in = create_random_location()
    location.create(obj_in=item_in, region=db_region)
    item_in2 = create_random_location()
    location.create(obj_in=item_in2, region=db_region)

    stored_items = location.get_multi(skip=0)
    assert len(stored_items) == 2

    stored_items = location.get_multi(skip=1)
    assert len(stored_items) == 1


def test_patch_item(db_region: Region) -> None:
    """Update the attributes of an existing Location, without updating its
    relationships."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    patch_in = create_random_location_patch()
    item = location.update(db_obj=item, obj_in=patch_in)
    for k, v in patch_in.dict().items():
        item_in.__setattr__(k, v)
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_patch_item_with_defaults(db_region: Region) -> None:
    """Try to update the attributes of an existing Location, without updating
    its relationships, with default values.

    The first attempt fails (no updates); the second one, with explicit
    default values, succeeds.
    """
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    patch_in = create_random_location_patch(default=True)
    assert not location.update(db_obj=item, obj_in=patch_in)

    patch_in = create_random_location_patch(default=True)
    patch_in.description = ""
    item = location.update(db_obj=item, obj_in=patch_in)
    item_in.description = patch_in.description
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_forced_update_item(db_region: Region) -> None:
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    item_in = create_random_location()
    item = location.update(db_obj=item, obj_in=item_in, force=True)
    validate_create_location_attrs(obj_in=item_in, db_item=item)


def test_delete_item(db_region: Region) -> None:
    """Delete an existing Location."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    result = location.remove(db_obj=item)
    assert result
    item = location.get(uid=item.uid)
    assert not item
    assert db_region