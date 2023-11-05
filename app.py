#!/usr/bin/env python3

from quart import Quart, jsonify, render_template, request, Response, session
from traceback import format_exc
from time import time
from main import *

app = Quart(__name__)
app.secret_key = "abc"


async def show_error(message: str = "An error occurred"):

    return Response(message, 500, content_type="text/plain")


async def get_session_info() -> dict:

    session_info = {
        'mgmt_server': session.get('mgmt_server', ""),
    }
    if sid := session.get('sid'):
        now = time()
        if now < session.get('expire_time'):  # Check Session ID hasn't expired
            session_info['sid'] = sid
    return session_info


async def check_session() -> dict:

    session_info = await get_session_info()
    if session_info.get('sid'):
        return session_info


async def show_login_form(message: str = "Please login below"):

    try:
        mgmt_servers = await get_mgmt_servers()
        username = session.get('username', "")
        return await render_template('login.html', message=message, mgmt_servers=mgmt_servers, username=username)
    except Exception as e:
        return await show_error(str(format_exc()))


@app.route("/do-login", methods=["POST"])
async def _do_login():

    try:
        form = await request.form
        mgmt_server = form.get('mgmt_server', "")
        username = form.get('username', "")
        password = form.get('password', "")
        if mgmt_server == "" or username == "" or password == "":
            return await show_login_form(message="Username or Password cannot be blank")
        else:
            _ = await do_login(mgmt_server=mgmt_server, username=username, password=password)
            if api_version := str(_.get('api-server-version', 0.0)):
                min_api_version = await get_min_api_version()
                if api_version < min_api_version:
                    return await show_login_form(f"Server API version {api_version} is less than {min_api_version}")
            #print(_)
            session['sid'] = _.get('sid', "")
            session['expire_time'] = time() + int(_.get('session-timeout', 600))
            session['username'] = username
            session['mgmt_server'] = mgmt_server
            return jsonify(_)
    except Exception as e:
        return await show_error(str(format_exc()))


@app.route("/show-login-form")
async def _show_login_form():

    try:
        return await show_login_form()
    except Exception as e:
        return await show_error(str(format_exc()))


@app.route("/show-clusters")
async def show_clusters():

    try:
        if not (session_info := await check_session()):
            return await show_login_form(message="Session Expired")
        sid = session_info.get('sid')
        mgmt_server = session_info.get('mgmt_server', "")
        _ = await get_clusters(mgmt_server, sid)
        tasks = [get_cluster_details(mgmt_server, sid, uid=cluster['uid']) for cluster in _]
        clusters = [_ for _ in await gather(*tasks)]
        return await render_template('show_clusters.html', clusters=clusters)
    except Exception as e:
        return await show_error(str(format_exc()))


@app.route("/show-gateways")
async def show_gateways():

    try:
        if not (session_info := await check_session()):
            return await show_login_form(message="Session Expired")
        sid = session_info.get('sid')
        mgmt_server = session_info.get('mgmt_server', "")
        _ = await get_gateways(mgmt_server, sid)
        tasks = [get_gateway_details(mgmt_server, sid, uid=gateway['uid']) for gateway in _]
        gateways = [_ for _ in await gather(*tasks)]
        return await render_template('show_clusters.html', clusters=gateways)
    except Exception as e:
        return await show_error(str(format_exc()))


@app.route("/show-vpns")
async def show_vpns():

    try:
        if not (session_info := await check_session()):
            return await show_login_form(message="Session Expired")
        sid = session_info.get('sid')
        mgmt_server = session_info.get('mgmt_server', "")
        _ = await get_vpn_communities(mgmt_server, sid)
        tasks = [create_task(get_vpn_details(mgmt_server, sid, vpn=vpn_community)) for vpn_community in _]
        vpn_details = [_ for _ in await gather(*tasks)]
        return await render_template('show_vpns.html', vpns=vpn_details)
    except Exception as e:
        return await show_error(str(format_exc()))


@app.route("/")
async def root():

    try:
        if not (session_info := await check_session()):
            return await show_login_form(message="Session Expired")
        sid = session_info.get('sid')
        mgmt_server = session_info.get('mgmt_server', "")
        _ = await main(mgmt_server=mgmt_server, sid=sid)
        return jsonify(_)
    except Exception as e:
        return await show_error(str(format_exc()))


if __name__ == '__main__':
    app.run(debug=True)
