from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from os import environ
from datetime import datetime, timezone
import math

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = environ.get("DB_URL")
db = SQLAlchemy(app)


if __name__ == "__main__":
    app.run(debug=True)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    avatar = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def checkParam(data):
        mssg = ""
        print(data)
        try:
            data["email"]
        except:
            mssg += ",email is missing"
        try:
            data["first_name"]
        except:
            mssg += ",first name is missing"

        try:
            data["last_name"]
        except:
            mssg += ",last name is missing"

        try:
            data["avatar"]
        except:
            mssg += ",avatar is missing"

        return mssg[1:]

    def json(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "avatar": self.avatar,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "deleted_at": self.deleted_at,
        }


db.create_all()


# create a test route
@app.route("/test", methods=["GET"])
def test():
    return make_response(jsonify({"message": "test route"}), 200)


# create a user
@app.route("/user", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        takeErr = User.checkParam(data)
        new_user = User(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            avatar=data["avatar"],
            created_at=datetime.now(timezone.utc),
        )
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({"message": "user created", "data": data}), 201)
    except Exception as e:
        if not takeErr:
            takeErr = str(e).split("\n\n")[0]
        return make_response(
            jsonify({"message": "error creating user", "error": takeErr}),
            500,
        )


# get all users
@app.route("/user", methods=["GET"])
def get_users():
    try:
        page = int(request.args.get("page"))
        per_page = int(request.args.get("per_page"))
        users = (
            User.query.order_by(User.id)
            .limit(per_page)
            .offset((page * per_page) - per_page)
        )
        count = User.query.count()
        return make_response(
            jsonify(
                {
                    "page": page,
                    "per_page": per_page,
                    "total_page": math.ceil(count / per_page),
                    "total": count,
                    "data": [user.json() for user in users],
                }
            ),
            200,
        )
    except Exception as e:
        return make_response(
            jsonify({"message": "error getting users", "error": str(e)}), 500
        )


# get a user by id
@app.route("/user/<int:id>", methods=["GET"])
def get_user(id):
    try:
        user = User.query.filter_by(id=id).first()
        if user:
            return make_response(jsonify({"user": user.json()}), 200)
        return make_response(jsonify({"message": "user not found"}), 404)
    except Exception as e:
        return make_response(
            jsonify({"message": "error getting user", "error": str(e)}), 500
        )


# update a user
@app.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
    try:
        takeErr = User.checkParam(data)
        user = User.query.filter_by(id=id).first()
        if user:
            data = request.get_json()
            user.username = data["username"]
            user.email = data["email"]
            user.first_name = (data["first_name"],)
            user.last_name = (data["last_name"],)
            user.avatar = (data["avatar"],)
            user.updated_at = (datetime.now(timezone.utc),)
            db.session.commit()
            return make_response(
                jsonify({"message": "user updated", "data": data}), 200
            )
        return make_response(jsonify({"message": "user not found"}), 404)
    except Exception as e:
        if not takeErr:
            takeErr = str(e).split("\n\n")[0]
        return make_response(
            jsonify({"message": "error updating user", "error": takeErr}), 500
        )


# delete a user
@app.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    try:
        wrongToken = {"message": "error deleting user", "error": "token is wrong"}
        try:
            headers = request.headers
            bearer = headers.get("Authorization")
            token = bearer.split()[1]
        except Exception as e:
            return make_response(
                jsonify(wrongToken),
                500,
            )
        if not (token == "3cdcnTiBsl"):
            return make_response(
                jsonify(wrongToken),
                500,
            )
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return make_response(jsonify({"message": "user deleted"}), 200)
        return make_response(jsonify({"message": "user not found"}), 404)
    except Exception as e:
        return make_response(
            jsonify({"message": "error deleting user", "error": str(e)}), 500
        )
