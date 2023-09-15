from cruds.provider import ProviderCRUD
from providers.opnstk import get_os_provider
from utils import (
    build_cmdb_urls,
    choose_idp,
    generate_token,
    get_read_write_headers,
    load_config,
)

if __name__ == "__main__":
    config = load_config()
    cmdb_urls = build_cmdb_urls(config=config)

    tokens = {}
    providers = []
    for conf in config.openstack:
        # At first, Choose which IDP should be used to authenticate script.
        # Generate a token using OIDC-Agent if not yet present.
        # Then retrieve Provider data.
        chosen_idp = choose_idp(
            identity_providers=conf.identity_providers,
            preferred_idp_list=config.oidc_agent_accounts,
        )
        if tokens.get(chosen_idp.endpoint) is None:
            tokens[chosen_idp.endpoint] = generate_token(endpoint=chosen_idp.endpoint)

        provider = get_os_provider(
            config=conf, chosen_idp=chosen_idp, token=tokens[chosen_idp.endpoint]
        )
        providers.append(provider)

    # To update CMDB data, we use the last chosen token to generate
    # read and write headers.
    read_header, write_header = get_read_write_headers(
        token=tokens[chosen_idp.endpoint]
    )
    crud = ProviderCRUD(
        cmdb_urls=cmdb_urls, read_headers=read_header, write_headers=write_header
    )
    for provider in providers:
        crud.create_or_update(item=provider)
