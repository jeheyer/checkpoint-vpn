from flask import Flask

app = Flask(__name__)

@app.route("/", defaults = {'path': ""})
@app.route("/<path:path>")
@app.route("/<string:path>")
def main(path):

    headers = {'Content-Type': "text/plain"}
    message = "Welcome to Flask v2.x!  Set FLASK_APP to your custom entry point\n\n"
    return message, headers

if __name__ == '__main__':
    app.run(debug=True)
