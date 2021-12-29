import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
app.config["PROPAGATE_EXCEPTIONS"] = True
setup_db(app)
CORS(app)

@app.route('/headers')
@requires_auth
def headers(payload):
    print(payload)
    return 'Access Granted'

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["GET"])
#@requires_auth("get:drinks")
def get_drinks():
    drinks = Drink.query.all()
    drinks_formatted = [drink.short() for drink in drinks]
    print(drinks_formatted)
    return(jsonify({
        "success": True,
        "drinks": drinks_formatted
    }))

@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def get_drinks_detailed():
    drinks = Drink.query.all()
    drinks_formatted = [drink.long() for drink in drinks]
    return(jsonify({
        "success": True,
        "drinks": drinks_formatted
    }))

@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drinks():
    body = request.get_json()
    new_title = body["title"]
    new_recipe = body["recipe"]

    if new_title is None or new_recipe is None:
        abort(404)

    drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    drink.insert()

    return(jsonify({
        "success": True,
        "drinks": drink.long()
    }))

@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drinks(drink_id):
    body = request.get_json()

    if drink_id is None:
        abort(404)

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(404)

    if "title" in body.keys():
        drink.title = body["title"]    

    if "recipe" in body.keys():
        drink.recipe = body["recipe"]

    return(jsonify({
        "success": True,
        "drinks": [drink.long()]
    }))

@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drink")
def delete_drinks(drink_id):
    body = request.get_json()

    if drink_id is None:
        abort(404)

    drink = Drink.query.filter_by(id=drink_id).one_or_none()

    if drink is None:
        abort(404)

    id = drink.id

    drink.delete()

    return(jsonify({
        "success": True,
        "deleted": id
    }))


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404, 
        "message": "resource not found"
    }),404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422, 
        "message": "unprocessable"
    }),422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, "message": "bad request"
    }), 400

@app.errorhandler(500)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 500, 
        "message": "internal server error"
    }), 500

@app.errorhandler(AuthError)
def authentication_error(error):
    code = error.get_status_code()
    err = error.get_error()
    print(code, err)
    return jsonify({
        "success": False,
        "error": err,
        "decription": code
    }), code

