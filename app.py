from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html", ip_address=request.remote_addr)

if __name__ == "__main__":
    app.run()