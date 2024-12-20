from datetime import timedelta
import random
from flask import Flask, request, session
from flask_session import Session
from flask_cors import CORS
from utils import Game, determine_best_next

# **Flask App Initialization**
app = Flask(__name__)

# **Session Configuration**
app.config["SECRET_KEY"] = str(random.random())
app.config["SESSION_TYPE"] = "filesystem"
CORS(app, supports_credentials=True)
Session(app)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="None",
)
app.permanent_session_lifetime = timedelta(days=1000)


# **Start Route**
@app.route("/start", methods=["POST"])
def start():
    # starting a new game
    session.clear()
    session["game"] = Game(6)
    session["difficulty"] = request.json.get("difficulty", 3)

    # returning all the possible lines to draw for the user to choose
    return {"available": [list(i) for i in session["game"].available]}


# **Route for receiving the choice of the user**
@app.route("/respond", methods=["POST"])
def continuation():

    # getting the game from the session and drawing the line the user chose
    game = session["game"]
    game.draw_line(*[int(i) for i in request.json["response"].split(",")], 1)

    # checking if the user lost after their choice
    if game.lost():
        return {"lost": "player"}

    # making the AI player play
    move = determine_best_next(game, difficulty=int(session["difficulty"]))[0]
    game.draw_line(*move, 2)

    # checking if the AI player lost
    if game.lost():
        return {"lost": "AI", "move": list(move)}

    # if neither of the players lost,
    # give the user what AI played and available lines
    return {"move": list(move), "available": [list(i) for i in game.available]}


# **Dummy Route** Just a best practice a learned to ping the server
@app.route("/dummy", methods=["GET"])
def dummy():
    return {"result": 1}


# **App Start**
app.run(port=4000)
