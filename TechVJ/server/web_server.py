from flask import Flask

# Initialize Flask app
web_server = Flask(__name__)

@web_server.route("/")
def home():
    return "Server is running ✅"

if __name__ == "__main__":
    # Run the server in debug mode for development
    web_server.run(host="0.0.0.0", port=8080, debug=False)
