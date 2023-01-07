from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
import datetime
import uuid

app = Flask(__name__)

app.config["SECRET_KEY"] = "thisissecret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///AuctionAndBid_Sys.db"

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)


class AuctionsData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime)
    auction_duration = db.Column(db.String(10))
    end_time = db.Column(db.DateTime)
    start_price = db.Column(db.Float)
    latest_bid = db.Column(db.Float)
    item_name = db.Column(db.String(50))
    user_won = db.Column(db.String(50))
    complete = db.Column(db.Boolean)


class BidsData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    auction_id = db.Column(db.Integer)
    latest_bid_value = db.Column(db.Float)
    user_id = db.Column(db.Integer)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return jsonify({"message": "Token is invalid!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


currentDateTime = datetime.datetime.now()


def complete_auction_by_time(auction_details):
    """
    Function mark auction as completed once the auction duration is completed. This function is triggered in various functions where list of auctions are fetched.
    """
    if currentDateTime >= auction_details.end_time:
        auction_details.complete = True
        db.session.commit()
        return True
    else:
        False


@app.route("/user", methods=["POST"])  # Only Admin can access this route
@token_required
def create_user(current_user):
    """
    Function to create a user using the application. Only admin can add new users.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    data = request.get_json()

    """
    data = {
        "name": "Roman",
        "password": "Roman@123"
    }
    """

    hashed_password = generate_password_hash(data["password"], method="sha256")

    new_user = User(
        public_id=str(uuid.uuid4()),
        name=data["name"],
        password=hashed_password,
        admin=False,
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "New user created!"})


@app.route("/user", methods=["GET"])  # Only Admin can access this route
@token_required
def get_all_users(current_user):

    """
    Function to fetch the list of users registered by admin. Only admin can view the list of all users.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    users = User.query.all()

    output = []

    for user in users:
        user_data = {}
        user_data["public_id"] = user.public_id
        user_data["name"] = user.name
        user_data["password"] = user.password
        user_data["admin"] = user.admin
        output.append(user_data)

    return jsonify({"users": output})


@app.route("/user/<public_id>", methods=["GET"])  # Only Admin can access this route
@token_required
def get_one_user(current_user, public_id):

    """
    Function to fetch details of one user using user_public_id. Only admin can view the details of the user.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    user_data = {}
    user_data["public_id"] = user.public_id
    user_data["name"] = user.name
    user_data["password"] = user.password
    user_data["admin"] = user.admin

    return jsonify({"user": user_data})


@app.route("/user/<public_id>", methods=["PUT"])  # Only Admin can access this route
@token_required
def promote_user(current_user, public_id):

    """
    Function to promote normal user to admin level using user_public_id. Only admin can promote normal user.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    user.admin = True
    db.session.commit()

    return jsonify({"message": "The user has been promoted!"})


@app.route("/user/<public_id>", methods=["DELETE"])  # Only Admin can access this route
@token_required
def delete_user(current_user, public_id):

    """
    Function to delete user using user_public_id. Only admin can delete user.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({"message": "No user found!"})

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "The user has been deleted!"})


@app.route("/login")  # Both Admin and Normal User can access this route
def login():

    """
    Function to fetch access token to login into the application. Both Admin and normal user can access this route to fetch the access token.
    """

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )

    user = User.query.filter_by(name=auth.username).first()

    if not user:
        return make_response(
            "Could not verify",
            401,
            {"WWW-Authenticate": 'Basic realm="Login required!"'},
        )

    if check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            },
            app.config["SECRET_KEY"],
            "HS256",
        )

        return jsonify({"token": token})

    return make_response(
        "Could not verify", 401, {"WWW-Authenticate": 'Basic realm="Login required!"'}
    )


@app.route("/AuctionCreation", methods=["POST"])  # Only Admin can access this route
@token_required
def create_Auction(current_user):

    """
    Function to create auction with all the required parameters. Only Admin can access this route to create a auction.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    data = request.get_json()

    """
    data = {
    "auction_duration_in_mins": 3,
    "start_price": 70,
    "item_name": "Ship"
    }
    """

    new_Auction = AuctionsData(
        start_time=currentDateTime,
        auction_duration=data["auction_duration_in_mins"],
        end_time=currentDateTime
        + datetime.timedelta(minutes=data["auction_duration_in_mins"]),
        start_price=data["start_price"],
        latest_bid=data["start_price"],  # Initially latest_bid will be start_price
        item_name=data["item_name"],
        user_won=current_user.public_id,  # Initially user_won will be Admin
        complete=False,
    )
    db.session.add(new_Auction)
    db.session.commit()

    return jsonify({"message": "Auction created!"})


@app.route(
    "/AuctionUpdate/<Auction_id>", methods=["POST"]
)  # Only Admin can access this route
@token_required
def update_AuctionDetails(current_user, Auction_id):

    """
    Function to update auction with all the required parameters. Only Admin can access this route to update the details of an auction.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    data = request.get_json()

    """
    data = {
        "auction_duration_in_mins": 15,
        "start_price": 70,
        "item_name": "Pants"
    }
    """

    Auction = AuctionsData.query.filter_by(id=Auction_id).first()

    auction_duration = int(Auction.auction_duration) + int(
        data.get("auction_duration_in_mins", 0)
    )
    end_time = Auction.start_time + datetime.timedelta(minutes=auction_duration)
    if end_time <= Auction.start_time:
        return jsonify({"message": "End time cannot be <= to auction start time!"})

    if Auction.complete == True and int(Auction.auction_duration) < auction_duration:
        Auction.complete = False

    Auction.auction_duration = auction_duration
    Auction.end_time = end_time

    Auction.start_price = data.get("start_price", Auction.start_price)
    Auction.latest_bid = data.get("start_price", Auction.latest_bid)
    Auction.item_name = data.get("item_name", Auction.item_name)

    if data.get("start_price"):
        Auction.user_won = current_user.public_id

    db.session.commit()

    return jsonify({"message": "Auction details updated!"})


@app.route("/AuctionCreation", methods=["GET"])  # Only Admin can access this route
@token_required
def get_all_Auctions(current_user):

    """
    Function to fetch details of all auctions. Only Admin can access this route to view the complete list of Ongoing and Completed auctions.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    Auctions = AuctionsData.query.all()

    output = []

    for Auction in Auctions:
        complete_auction_by_time(Auction)
        Auction_data = {}
        Auction_data["id"] = Auction.id
        Auction_data["start_time"] = Auction.start_time
        Auction_data["auction_duration_in_mins"] = Auction.auction_duration
        Auction_data["end_time"] = Auction.end_time
        Auction_data["start_price"] = Auction.start_price
        Auction_data["latest_bid"] = Auction.latest_bid
        Auction_data["item_name"] = Auction.item_name
        Auction_data["user_won"] = Auction.user_won
        Auction_data["complete"] = Auction.complete
        output.append(Auction_data)

    return jsonify({"Auctions": output})


@app.route(
    "/CompletedAuctions", methods=["GET"]
)  # Both Admin and Normal User can access this route
@token_required
def get_all_CompletedAuctions(current_user):

    """
    Function to fetch the list of completed auctions. Both admin and normal user can access this route to know about the details of each auction.
    """

    Auctions = AuctionsData.query.filter_by(complete=True).all()

    output = []

    for Auction in Auctions:
        complete_auction_by_time(Auction)
        Auction_data = {}
        Auction_data["id"] = Auction.id
        Auction_data["start_time"] = Auction.start_time
        Auction_data["auction_duration_in_mins"] = Auction.auction_duration
        Auction_data["end_time"] = Auction.end_time
        Auction_data["start_price"] = Auction.start_price
        Auction_data["latest_bid"] = Auction.latest_bid
        Auction_data["item_name"] = Auction.item_name
        Auction_data["user_won"] = Auction.user_won
        Auction_data["complete"] = Auction.complete
        output.append(Auction_data)

    return jsonify({"result": "success", "Auctions": output})


@app.route(
    "/InCompletedAuctions", methods=["GET"]
)  # Both Admin and Normal User can access this route
@token_required
def get_all_IncompleteAuctions(current_user):

    """
    Function to fetch the list of incompleted auctions. Both admin and normal user can access this route to know about the details of each auction.
    """

    Auctions = AuctionsData.query.filter_by(complete=False).all()

    output = []

    for Auction in Auctions:
        if complete_auction_by_time(Auction):
            continue
        Auction_data = {}
        Auction_data["id"] = Auction.id
        Auction_data["start_time"] = Auction.start_time
        Auction_data["auction_duration_in_mins"] = Auction.auction_duration
        Auction_data["end_time"] = Auction.end_time
        Auction_data["start_price"] = Auction.start_price
        Auction_data["latest_bid"] = Auction.latest_bid
        Auction_data["item_name"] = Auction.item_name
        output.append(Auction_data)

    return jsonify({"Auctions": output})


@app.route("/Auction/<Auction_id>", methods=["PUT"])  # Only Admin can access this route
@token_required
def complete_Auction(current_user, Auction_id):

    """
    Function to mark auction as completed by admin using auction_id. Only Admin can access this route to mark auction as completed.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    Auction = AuctionsData.query.filter_by(id=Auction_id).first()

    if not Auction:
        return jsonify({"message": "No Auction item found!"})

    Auction.complete = True
    db.session.commit()

    return jsonify({"message": "Auction item has been completed!"})


@app.route(
    "/Auction/<Auction_id>", methods=["DELETE"]
)  # Only Admin can access this route
@token_required
def delete_Auction(current_user, Auction_id):

    """
    Function to delete auction by admin using auction_id. Only Admin can access this route to delete auction.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    Auction = AuctionsData.query.filter_by(id=Auction_id).first()

    if not Auction:
        return jsonify({"message": "No Auction item found!"})

    db.session.delete(Auction)
    db.session.commit()

    return jsonify({"message": "Auction item deleted!"})


@app.route("/BidCreation", methods=["POST"])  # Only Normal User can access this route
@token_required
def create_Bid(current_user):

    """
    Function to create bids on the ongoing auctions. Only Admin can access this route to mark auction as completed.
    """

    if current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    data = request.get_json()

    """
    data = {
        "auction_id": 3,
        "latest_bid_value": 100
        }
    """

    auction_id = data["auction_id"]
    latest_bid_value = data["latest_bid_value"]

    get_auction_details = AuctionsData.query.filter_by(id=auction_id).first()

    if get_auction_details.complete == True:
        return jsonify({"message": "You cannot make a bid on EXPIRED auction!"})

    if (
        latest_bid_value <= get_auction_details.start_price
        and latest_bid_value < get_auction_details.latest_bid
    ):
        return jsonify(
            {
                "message": "You cannot make a bid with amount less than item's start price and latest bid price!"
            }
        )

    new_Bid = BidsData(
        auction_id=data["auction_id"],
        latest_bid_value=data["latest_bid_value"],
        user_id=current_user.public_id,
    )

    get_auction_details.latest_bid = latest_bid_value
    get_auction_details.user_won = current_user.public_id

    db.session.add(new_Bid)
    db.session.commit()

    return jsonify({"message": "Bid created!"})


@app.route(
    "/BidsList/<Auction_id>", methods=["GET"]
)  # Only Admin can access this route
@token_required
def get_all_bids(current_user, Auction_id):

    """
    Function to fetch details of all bids pf an auction. Only Admin can access this route to view the complete list of bids on Ongoing and Completed auctions.
    """

    if not current_user.admin:
        return jsonify({"message": "Cannot perform that function!"})

    Bids = BidsData.query.filter_by(auction_id=Auction_id).all()

    output = []

    for Bid in Bids:
        Bid_data = {}
        Bid_data["id"] = Bid.id
        Bid_data["auction_id"] = Bid.auction_id
        Bid_data["latest_bid_value"] = Bid.latest_bid_value
        Bid_data["user_id"] = Bid.user_id
        output.append(Bid_data)

    return jsonify({"Bids": output})


if __name__ == "__main__":
    app.run(debug=True)
