from typing import Generator

from ..utils.project import create_random_project
from ..utils.utils import random_lower_string
from ...project.crud import project
from ...project.schemas import (
    ProjectCreate,
    ProjectUpdate,
)


def test_create_item(setup_and_teardown_db: Generator) -> None:
    description = random_lower_string()
    public_network_name = random_lower_string()
    private_network_name = random_lower_string()
    private_network_proxy_host = random_lower_string()
    private_network_proxy_user = random_lower_string()
    item_in = ProjectCreate(
        description=description,
        public_network_name=public_network_name,
        private_network_name=private_network_name,
        private_network_proxy_host=private_network_proxy_host,
        private_network_proxy_user=private_network_proxy_user,
    )
    item = project.create(obj_in=item_in)
    assert item.description == description
    assert item.public_network_name == public_network_name
    assert item.private_network_name == private_network_name
    assert item.private_network_proxy_host == private_network_proxy_host
    assert item.private_network_proxy_user == private_network_proxy_user


def test_create_item_default_values(setup_and_teardown_db: Generator) -> None:
    item_in = ProjectCreate()
    item = project.create(obj_in=item_in)
    assert item.description == ""
    assert item.public_network_name is None
    assert item.private_network_name is None
    assert item.private_network_proxy_host is None
    assert item.private_network_proxy_user is None


def test_get_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_project()
    stored_item = project.get(uid=item.uid)
    assert stored_item
    assert item.uid == stored_item.uid
    assert item.description == stored_item.description
    assert item.public_network_name == stored_item.public_network_name
    assert item.private_network_name == stored_item.private_network_name
    assert (
        item.private_network_proxy_host
        == stored_item.private_network_proxy_host
    )
    assert (
        item.private_network_proxy_user
        == stored_item.private_network_proxy_user
    )


def test_get_items(setup_and_teardown_db: Generator) -> None:
    item = create_random_project()
    item2 = create_random_project()
    stored_items = project.get_multi()
    assert len(stored_items) == 2

    stored_items = project.get_multi(limit=1)
    assert len(stored_items) == 1

    stored_items = project.get_multi(uid=item.uid)
    assert len(stored_items) == 1
    assert stored_items[0].uid == item.uid
    assert stored_items[0].description == item.description
    assert stored_items[0].public_network_name == item.public_network_name
    assert stored_items[0].private_network_name == item.private_network_name
    assert (
        stored_items[0].private_network_proxy_host
        == item.private_network_proxy_host
    )
    assert (
        stored_items[0].private_network_proxy_user
        == item.private_network_proxy_user
    )

    sorted_items = list(sorted([item, item2], key=lambda x: x.uid))
    stored_items = project.get_multi(sort="uid")
    assert stored_items[0].uid == sorted_items[0].uid
    assert stored_items[1].uid == sorted_items[1].uid
    stored_items = project.get_multi(sort="-uid")
    assert stored_items[0].uid == sorted_items[1].uid
    assert stored_items[1].uid == sorted_items[0].uid


def test_update_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_project()
    description2 = random_lower_string()
    public_network_name2 = random_lower_string()
    private_network_name2 = random_lower_string()
    private_network_proxy_host2 = random_lower_string()
    private_network_proxy_user2 = random_lower_string()
    item_update = ProjectUpdate(
        description=description2,
        public_network_name=public_network_name2,
        private_network_name=private_network_name2,
        private_network_proxy_host=private_network_proxy_host2,
        private_network_proxy_user=private_network_proxy_user2,
    )
    item2 = project.update(db_obj=item, obj_in=item_update)
    assert item2.uid == item.uid
    assert item2.description == description2
    assert item.public_network_name == public_network_name2
    assert item.private_network_name == private_network_name2
    assert item.private_network_proxy_host == private_network_proxy_host2
    assert item.private_network_proxy_user == private_network_proxy_user2


def test_delete_item(setup_and_teardown_db: Generator) -> None:
    item = create_random_project()
    item2 = project.remove(db_obj=item)
    item3 = project.get(uid=item.uid)
    assert item2 is True
    assert item3 is None
