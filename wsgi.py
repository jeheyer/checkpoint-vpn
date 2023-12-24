from flask import Flask, request, jsonify, render_template, Response, session
from traceback import format_exc
from random import randint
from main import *

DEFAULT_RESPONSE_HEADERS = {'Cache-Control': "no-cache, no-store"}
DEFAULT_SERVER_GROUPS = {'all': "All Servers"}
DEFAULT_STATUS_CODES = ["200", "400", "301", "403", "302", "500", "502", "503"]
PLAIN_TEXT_CONTENT_TYPE = "text/plain"


app = Flask(__name__, static_url_path='/static')
app.config['JSON_SORT_KEYS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = "Strict"
app.secret_key = str(randint(0, 1000000))


@app.route("/")
@app.route("/index.html")
def _root():
    try:
        return jsonify({'foo': "bar"})
    except Exception as e:
        return Response(format_exc(), 500, content_type=PLAIN_TEXT_CONTENT_TYPE)


if __name__ == '__main__':
    app.run()
