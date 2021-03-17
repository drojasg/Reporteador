from flask import Flask, request
from flask_restful import Resource
from config import db, base
from models.prueba import PruebaBooking, PruebaBookingSchema
from common.util import Util
from sqlalchemy import or_, and_
from datetime import datetime as dt
from dateutil.parser import parse
from common.public_auth import PublicAuth

class PruebaSearch(Resource):
   def getBookEstado1(estado):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(estado)
            response = {
                "Code": 200,
                "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(data)
            }
            else:
            response ={
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                    }

        except Exception as e:
                response = {
                    "Code": 500,
                    "Msg": str(e),
                    "Error": True,
                    "data": {}
                }

        return response