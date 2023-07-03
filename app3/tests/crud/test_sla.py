from typing import Generator

from ..utils.sla import create_random_sla
from ..utils.utils import random_lower_string, random_datetime
from ...sla.crud import sla
from ...sla.schemas import SLACreate, SLAUpdate


def test_create_item(setup_and_teardown_db: Generator) -> None:
    description = random_lower_string()
    start_date = random_datetime()
    end_date = random_datetime()
    item_in = SLACreate(
        description=description, start_date=start_date, end_date=end_date
    )
    item = sla.create(obj_in=item_in)
    assert item.description == description
    assert item.start_date == start_date
    assert item.end_date == end_date


def test_create_item_default_values(setup_and_teardown_db: Generator) -> None:
    start_date = random_datetime()
    item_in = SLACreate(start_date=start_date)
    item = sla.create(obj_in=item_in)
    assert item.description == ""
    assert item.start_date == start_date
    assert item.end_date is None


def test_get_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_sla()
    stored_item = sla.get(uid=item.uid)
    assert stored_item
    assert item.uid == stored_item.uid
    assert item.description == stored_item.description
    assert item.start_date == stored_item.start_date
    assert item.end_date == stored_item.end_date


def test_get_items(setup_and_teardown_db: Generator) -> None:
    item = create_random_sla()
    item2 = create_random_sla()
    stored_items = sla.get_multi()
    assert len(stored_items) == 2

    stored_items = sla.get_multi(limit=1)
    assert len(stored_items) == 1

    stored_items = sla.get_multi(uid=item.uid)
    assert len(stored_items) == 1
    assert stored_items[0].uid == item.uid
    assert stored_items[0].description == item.description
    assert stored_items[0].start_date == item.start_date
    assert stored_items[0].end_date == item.end_date

    sorted_items = list(sorted([item, item2], key=lambda x: x.uid))
    stored_items = sla.get_multi(sort="uid")
    assert stored_items[0].uid == sorted_items[0].uid
    assert stored_items[1].uid == sorted_items[1].uid
    stored_items = sla.get_multi(sort="-uid")
    assert stored_items[0].uid == sorted_items[1].uid
    assert stored_items[1].uid == sorted_items[0].uid


def test_update_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_sla()
    description2 = random_lower_string()
    start_date2 = random_datetime()
    end_date2 = random_datetime()
    item_update = SLAUpdate(
        description=description2, start_date=start_date2, end_date=end_date2
    )
    item2 = sla.update(db_obj=item, obj_in=item_update)
    assert item2.uid == item.uid
    assert item2.description == description2
    assert item2.start_date == start_date2
    assert item2.end_date == end_date2


def test_delete_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_sla()
    item2 = sla.remove(db_obj=item)
    item3 = sla.get(uid=item.uid)
    assert item2 is True
    assert item3 is None
