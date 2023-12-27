#!/usr/bin/env python3

from asyncio import run, gather, create_task
from aiohttp import ClientSession
from yaml import load, FullLoader
from pathlib import Path

SETTINGS_FILE = "./settings.yaml"
DEFAULTS = {
    'management_servers': [{'hostname': "localhost", 'port': 443}]
}
MIN_VERSION = "1.8.1"
VERIFY_SSL = False


async def get_min_api_version():

    return str(MIN_VERSION)


async def read_settings(settings_file=SETTINGS_FILE):

    path = Path(settings_file)
    if path.is_file():
        with open(settings_file) as file:
            return load(file, Loader=FullLoader)

    return DEFAULTS


async def do_login(mgmt_server: str, username: str, password: str):

    body = {'user': username, 'password': password}
    try:
        _ = await ws_request(mgmt_server, "/web_api/login", sid=None, body=body)
        return _
    except Exception as e:
        raise e


async def ws_request(mgmt_server: str, command: str, sid: str, body: dict = {}, response_key: str = None) -> any:

    _ = await get_mgmt_servers()
    if not (mgmt_server := _.get(mgmt_server)):
        error_message = f"Management server with key '{mgmt_server}' not found in '{SETTINGS_FILE}'"
        raise RuntimeError(error_message)
    if not (hostname := mgmt_server.get('hostname')):
        hostname = 'localhost'
    if not (port := mgmt_server.get('port')):
        port = 443
    mgmt_server = f"{hostname}:{port}"

    url = f"https://{mgmt_server if not mgmt_server.startswith('https://') else mgmt_server}{command}"
    headers = {'X-chkp-sid': sid} if sid else {}
    if not 'Content-Type' in headers:
        headers.update({'Content-Type': "application/json"})

    try:
        async with ClientSession(raise_for_status=True) as session:
            #print(url)
            async with session.post(url=url, headers=headers, json=body, verify_ssl=VERIFY_SSL) as response:
                #print(response)
                if int(response.status) == 200:
                    data = await response.json()
                    #print(response_key, data)
                    #return data.get(response_key, []) if response_key else data
                else:
                    raise response
        #return r
        await session.close()
        return data.get(response_key, []) if response_key else data

    except Exception as e:
        raise e


async def get_vpn_communities(mgmt_server, sid) -> list:

    vpn_communities = []
    for call in ['show-vpn-communities-star', 'show-vpn-communities-meshed']:
        vpn_communities.extend(await ws_request(mgmt_server, f"/web_api/{call}", sid, response_key="objects"))

    _ = []
    for vpn_community in vpn_communities:
        _.append({
            'name': vpn_community.get('name'),
            'uid': vpn_community.get('uid'),
            'type': vpn_community.get('type'),
            #'vpn_community': vpn_community,
        })
    return _


async def get_vpn_details(mgmt_server, sid, vpn: dict) -> list:

    body = {'uid': vpn['uid']}
    _ = {}
    #print(body)
    if '-meshed' in vpn['type']:
        #_ = await ws_request(mgmt_server, "/web_api/show-vpn-community-meshed", sid, body, response_key='gateways')
        _ = await ws_request(mgmt_server, "/web_api/show-vpn-community-meshed", sid, body)
    if '-star' in vpn['type']:
        #_ = await ws_request(mgmt_server, "/web_api/show-vpn-community-star", sid, body, response_key='gateways')
        _ = await ws_request(mgmt_server, "/web_api/show-vpn-community-star", sid, body)
    #print(_)

    phase1 = _.get('ike-phase-1', {})
    phase2 = _.get('ike-phase-2', {})
    _['phase1_encryption'] = phase1.get('encryption-algorithm')
    _['phase1_integrity'] = phase1.get('data-integrity')
    _['phase1_dh_group'] = phase1.get('diffie-hellman-group')
    _['phase1_rekey_time'] = phase1.get('ike-p1-rekey-time')
    _['phase2_integrity'] = phase2.get('data-integrity')
    _['phase2_dh_group'] = phase2.get('ike-p2-pfs-dh-grp')
    _['phase2_rekey_time'] = phase2.get('ike-p2-rekey-time')
    _['phase2_use_pfs'] = phase2.get('ike-p2-use-pfs')
    _['encryption_method'] = _.get('encryption-method', "unknown")
    _['encryption_suite'] = _.get('encryption-suite', "unknown")
    _['tunnel_granularity'] = _.get('tunnel-granularity')

    return _


async def get_clusters(mgmt_server, sid) -> list:

    _ = await ws_request(mgmt_server, "/web_api/show-simple-clusters", sid, response_key='objects')
    return _


async def get_gateways(mgmt_server, sid) -> list:

    _ = await ws_request(mgmt_server, "/web_api/show-simple-gateways", sid, response_key='objects')
    return _


async def get_cluster_details(mgmt_server, sid, uid: str = None, name: str = None) -> dict:

    assert name or uid

    clusters = []
    body = {'uid': uid} if uid else {'name': name}
    _ = await ws_request(mgmt_server, "/web_api/show-simple-cluster", sid, body=body)
    _['ip_address'] = _.get('ipv4-address')
    _['num_interfaces'] = len(_['interfaces'].get('objects', []))
    return _


async def get_gateway_details(mgmt_server, sid, uid: str = None, name: str = None) -> dict:

    assert name or uid

    body = {'uid': uid} if uid else {'name': name}
    _ = await ws_request(mgmt_server, "/web_api/show-simple-gateway", sid, body=body)
    return _


async def get_mgmt_servers():

    try:
        settings = await read_settings()
        return settings.get('management_servers', DEFAULTS['management_servers'])
    except Exception as e:
        raise e


async def main(mgmt_server: dict, sid: str):

    _ = await get_gateways(mgmt_server, sid)
    print(_)
    tasks = [get_gateway_details(mgmt_server, sid, uid=gateway['uid']) for gateway in _]
    gateways = [_ for _ in await gather(*tasks)]
    print(gateways)

    _ = await get_clusters(mgmt_server, sid)
    tasks = [get_cluster_details(mgmt_server, sid, uid=cluster['uid']) for cluster in _]
    clusters = [_ for _ in await gather(*tasks)]
    print(clusters)

    try:
        vpn_communities = await get_vpn_communities(mgmt_server, sid)
        #for :
        tasks = [create_task(get_vpn_details(mgmt_server, sid, vpn=vpn_community)) for vpn_community in vpn_communities]

        vpn_details = [_ for _ in await gather(*tasks)]

        """
        for gateway in gateways:
            #print(gateway)
            vpns.append({
                #'vpn_name': vpn_community.get('name'),
                #'gateway_name': gateway.get('name'),
                #'gateway_type': gateway.get('type'),
                #'ip_address': gateway.get('ipv4-address'),
                'gateway': gateway,
            })
            #print(_)
        """
    except Exception as e:
        quit(str(e))

    #print(vpns)
    return {
        'vpns': vpn_details,
        'gateways': gateways,
        'clusters': clusters,
    }


if __name__ == "__main__":
    run(main())
