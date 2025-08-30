from flask import Flask

web_server = Flask(__name__)

@web_server.route("/")
def home():
    return "Server is running"
