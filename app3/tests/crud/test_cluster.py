from typing import Generator

from ..utils.cluster import create_random_cluster
from ..utils.utils import random_lower_string
from ...cluster.crud import cluster
from ...cluster.schemas import ClusterCreate, ClusterUpdate


def test_create_item(setup_and_teardown_db: Generator) -> None:
    description = random_lower_string()
    item_in = ClusterCreate(description=description)
    item = cluster.create(obj_in=item_in)
    assert item.description == description


def test_create_item_default_values(setup_and_teardown_db: Generator) -> None:
    item_in = ClusterCreate()
    item = cluster.create(obj_in=item_in)
    assert item.description == ""


def test_get_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_cluster()
    stored_item = cluster.get(uid=item.uid)
    assert stored_item
    assert item.uid == stored_item.uid
    assert item.description == stored_item.description


def test_get_items(setup_and_teardown_db: Generator) -> None:
    item = create_random_cluster()
    item2 = create_random_cluster()
    stored_items = cluster.get_multi()
    assert len(stored_items) == 2

    stored_items = cluster.get_multi(limit=1)
    assert len(stored_items) == 1

    stored_items = cluster.get_multi(uid=item.uid)
    assert len(stored_items) == 1
    assert stored_items[0].uid == item.uid
    assert stored_items[0].description == item.description

    sorted_items = list(sorted([item, item2], key=lambda x: x.uid))
    stored_items = cluster.get_multi(sort="uid")
    assert stored_items[0].uid == sorted_items[0].uid
    assert stored_items[1].uid == sorted_items[1].uid
    stored_items = cluster.get_multi(sort="-uid")
    assert stored_items[0].uid == sorted_items[1].uid
    assert stored_items[1].uid == sorted_items[0].uid


def test_update_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_cluster()
    description2 = random_lower_string()
    item_update = ClusterUpdate(description=description2)
    item2 = cluster.update(db_obj=item, obj_in=item_update)
    assert item2.uid == item.uid
    assert item2.description == description2


def test_delete_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_cluster()
    item2 = cluster.remove(db_obj=item)
    item3 = cluster.get(uid=item.uid)
    assert item2 is True
    assert item3 is None
