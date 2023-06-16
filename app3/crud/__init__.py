from .flavor import (
    create_flavor,
    get_flavor,
    get_flavors,
    remove_flavor,
    update_flavor,
)
from .identity_provider import (
    create_identity_provider,
    get_identity_provider,
    get_identity_providers,
    remove_identity_provider,
)
from .image import (
    create_image,
    get_image,
    get_images,
    remove_image,
    update_image,
)
from .location import (
    create_location,
    get_location,
    get_locations,
    remove_location,
    update_location,
)
from .provider import (
    create_provider,
    get_provider,
    get_providers,
    remove_provider,
    update_provider,
)
from .quota import (
    create_quota,
    connect_quota_to_sla,
    get_quota,
    get_quotas,
    remove_quota,
)
from .service import (
    create_service,
    connect_service_to_sla,
    get_service,
    get_services,
    remove_service,
)
from .sla import (
    create_sla,
    connect_sla_to_project_and_provider,
    get_sla,
    get_slas,
    remove_sla,
)
from .user_group import (
    create_user_group,
    get_user_group,
    get_user_groups,
    remove_user_group,
    update_user_group,
)

__all__ = [
    "create_flavor",
    "get_flavor",
    "get_flavors",
    "remove_flavor",
    "update_flavor",
    "create_identity_provider",
    "get_identity_provider",
    "get_identity_providers",
    "remove_identity_provider",
    "create_image",
    "get_image",
    "get_images",
    "remove_image",
    "update_image",
    "create_location",
    "get_location",
    "get_locations",
    "remove_location",
    "update_location",
    "create_provider",
    "get_provider",
    "get_providers",
    "remove_provider",
    "update_provider",
    "create_quota",
    "connect_quota_to_sla",
    "get_quota",
    "get_quotas",
    "remove_quota",
    "create_service",
    "connect_service_to_sla",
    "get_service",
    "get_services",
    "remove_service",
    "create_sla",
    "connect_sla_to_project_and_provider",
    "get_sla",
    "get_slas",
    "remove_sla",
    "create_user_group",
    "get_user_group",
    "get_user_groups",
    "remove_user_group",
    "update_user_group",
]
