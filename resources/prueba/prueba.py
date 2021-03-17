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
   def getBookEstado1(self, estado):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = pModel.query.filter(pModel.estado == 1)
            data = schema.load(json_data)
            model = Model.query.get(estado)
            
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                    }

            result = schema.dump(model)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
            }
        except ValidationError as error:
                response = {
                    "Code": 500,
                    "Msg": error.messages,
                    "Error": True,
                    "data": {}
                }
        except Exception as e:
                db.session.rollback()
                response = {
                    "Code": 500,
                    "Msg": str(e),
                    "Error": True,
                    "data": {}
                }

        return response