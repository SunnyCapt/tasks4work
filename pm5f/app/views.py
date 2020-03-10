import time

import requests
from flask import render_template, request, make_response, redirect

import config
from app import app

patt = "=" * 20 + "\nFLAG: %s\nSTATUS: %s\nIP: %s\n" + 20 * "="


@app.route("/")
def main():
    return redirect("/friends/")


@app.route("/oauth/", methods=["GET", "POST"])
def oauth():
    flag = str(hash(time.time()))
    if request.cookies.get("token"):
        return redirect("/friends/")
    code = request.args.get("code")
    try:
        resp = requests.get(config.vk.token_url + str(code)).json()
        token = resp.get("access_token")
        assert token
        response = make_response(redirect("/friends/"))
        response.set_cookie("token", token)
        response.set_cookie("user_id", str(resp.get("user_id", "")))
        debug_message = patt % (flag, "OK", request.remote_addr)
    except Exception as e:
        response = render_template("error.html", message="Не удалось авторизоваться")
        debug_message = patt % (flag, "ERROR: " + str(e), request.remote_addr)
    print(debug_message)
    return response


@app.route("/friends/")
def friends():
    flag = str(hash(time.time()))
    token = request.cookies.get("token", "")
    user_id = str(request.cookies.get("user_id", 0))
    if not token:
        response = render_template("start.html", oauth_url=config.vk.oauth_url)
        debug_message = patt % (flag, "OK", request.remote_addr)
    else:
        try:
            ids = requests.get(config.vk.friends_get + token).json().get("response").get("items")
            if not user_id:
                user_id = str(requests.get(config.vk.names_get + token).json().get("response")[0]["id"])
                time.sleep(1)
            ids.insert(0, user_id)
            ids = ",".join([str(i) for i in ids])
            resp = requests.get(config.vk.names_get + token + "&user_ids=" + ids).json().get("response")
            response = make_response(render_template("friends.html", friends=resp))
            response.set_cookie("user_id", user_id)
            debug_message = patt % (flag, "OK", request.remote_addr)
        except Exception as e:
            response = make_response(render_template("error.html", message="проблемы в ВК.."))
            response.set_cookie("token", "")
            debug_message = patt % (flag, "ERROR: " + str(e), request.remote_addr)
    print(debug_message)
    return response


@app.route("/exit/")
def exit_():
    response = make_response(redirect("/"))
    response.set_cookie("token", "")
    return response
