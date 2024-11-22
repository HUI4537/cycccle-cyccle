from flask import Flask, render_template, send_from_directory

app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    return render_template("information.html")

@app.route("/data.json")
def data():
    return send_from_directory(app.static_folder, "data.json")

if __name__ == "__main__":
    app.run(debug=True)
