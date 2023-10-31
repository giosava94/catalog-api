import pytest
from app.location.crud import location
from app.location.models import Location
from app.region.models import Region
from tests.utils.location import create_random_location


@pytest.fixture
def db_location(db_region: Region) -> Location:
    """Location of the region of the first provider."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region)
    yield item


@pytest.fixture
def db_location2(db_region2: Region) -> Location:
    """Location of the first region of the second provider."""
    item_in = create_random_location()
    item = location.create(obj_in=item_in, region=db_region2)
    yield item


@pytest.fixture
def db_location_with_multiple_regions(
    db_location: Location, db_region3: Region
) -> Location:
    """Location connected to the region of the first provider and the second
    region of the second provider."""
    item_in = create_random_location()
    item_in.site = db_location.site
    item = location.create(obj_in=item_in, region=db_region3)
    yield item


@pytest.fixture
def db_region_with_location(db_location: Location) -> Region:
    """Region with a location."""
    yield db_location.regions.all()[0]
