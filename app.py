import os

from flask import Flask, request, jsonify, render_template, redirect, session, Response
from cs50 import SQL
from helpers import login_required
from error import apology
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import cv2
from predict import run
import pandas as pd
import numpy as np
from camera import VideoCamera
import get_aasan

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///user_info.db")

# camera configuration
camera = cv2.VideoCapture(0)

exercise = None

# success_exercise = False

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route('/')
@login_required
def home(methods=["GET", "POST"]):
    # if request.method == "GET":
    yog_df = get_aasan()
    print(yog_df)
    return render_template('index.html', qtys=yog_df)
# else:

    #     return render_template("camera.html")

def get_aasan_baby(key):
    scores = get_aasan.fun(key)
    d = {
        "plank": {"high": "2m", "medium": "1m", "low": "30s"},
        "downdog": {"high": "2m", "medium": "1m", "low": "30s"},
        "tree": {"high": "2m", "medium": "1m", "low": "30s"},
        "warrior2": {"high": "2m", "medium": "1m", "low": "30s"},
        "goddess": {"high": "2m", "medium": "1m", "low": "30s"}
    }

    scoring = {"high": [scores.exercise[0], scores.exercise[1]], "medium": [scores.exercise[2]], "low": [scores.exercise[3], scores.exercise[4]]}

    ret = {}

    for k, v in scoring.items():
        for v_ in v:
            ret[v_] = d[v_][k] + "-" +  d[v_][k] + "-" + d[v_][k]
    
    ret_final = {"exercise": [], "reps": []}
    for k, v in ret.items():
        ret_final["exercise"].append(k)
        ret_final["reps"].append(v)
    
    ret_final = pd.DataFrame(ret_final)
    
    return ret_final


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["u_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        rows = db.execute("SELECT * from users where username = :username",
        username = request.form.get("username"))

        if len(rows) == 1 or not request.form.get("username"):
            return apology("Username invalid!")

        elif not request.form.get("password"):
            return apology("Please enter password!")

        elif request.form.get("password") != request.form.get("password(again)"):
            return apology("The two passwords do not match!")
        
        elif not request.form.get("height"):
            return apology("Height invalid")
        
        elif not request.form.get("weight"):
            return apology("Weight invalid")

        username = request.form.get("username")
        password = request.form.get("password")
        height = request.form.get("height")
        weight = request.form.get("weight")

        db.execute("INSERT INTO users (username, password, height, weight) VALUES (:username, :hash, :height, :weight)", username=username, hash=generate_password_hash(password), height=height, weight=weight)

        return redirect("/")

# @app.route("/analytics")
# @login_required
# def analytics():
#     user = db.execute("SELECT username FROM users WHERE u_id = :u_id", u_id=session['user_id'])
#     user = user[0]['username']
#     return render_template("analytics.html", user=user)

# def gen_frames():  
#     while True:
#         success, frame = camera.read()  # read the camera frame
#         success_exercise = False
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             prediction = run(frame)
#             print(prediction, exercise)
#             _h, _w, _c = frame.shape
#             frame = cv2.putText(frame, prediction, (_h//2+2,_w//2+2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255))#, 2, cv2.LINE_AA)
#             cv2.imwrite("static/debug.jpg",frame)
#             # frame = np.zeros((_h, _w, _c))
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route("/camera", methods=["GET", "POST"])
@login_required
def camera_fn():
    if request.method == "POST":
        exercise = request.form.get("select1")
    return render_template("camera.html", exercise=exercise)

# @app.route('/video_feed', methods=["GET", "POST"])
# @login_required
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(camera):
    while True:
        frame, frame_bytes = camera.get_frame()
        print(frame.shape)
        # prediction = run(frame)
        # print(prediction, exercise)
        # frame = cv2.resize(frame, (640, 480), interpolation = cv2.INTER_AREA)
        # _h, _w, _c = frame_bytes.shape
        # cv2.putText(frame_bytes, prediction, (_h//2+2,_w//2+2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2, cv2.LINE_AA)
        try:
            cv2.imwrite("static/debug.jpg",frame)
        except:
            pass
        # frame = frame.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

@app.route('/video_feed', methods=["GET", "POST"])
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(debug=False)
