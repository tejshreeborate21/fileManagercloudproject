from flask import Flask, request, render_template, redirect, session, send_from_directory
import os
import uuid
import mimetypes

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

USER = {
    "username": "admin",
    "password": "admin123"
}

def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == USER["username"] and password == USER["password"]:
            session["user"] = username
            return redirect("/")
        return "Invalid credentials"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/")
@login_required
def index():
    files_data = []

    for file in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, file)
        size = os.path.getsize(path) // 1024
        mime_type, _ = mimetypes.guess_type(path)

        files_data.append({
            "name": file,
            "size": size,
            "type": mime_type or "Unknown"
        })

    return render_template("index.html", files=files_data)

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")

    if file and file.filename != "":
        filename = str(uuid.uuid4()) + "_" + file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))

    return redirect("/")

@app.route("/download/<path:filename>")
@login_required
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/delete/<path:filename>", methods=["POST"])
@login_required
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
