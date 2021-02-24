from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.log_changes import LogChanges as Model, LogChangesSchema as Schema
from .log_changes_helper import LogChangesHelper

from common.util import Util
from sqlalchemy import or_, and_
from common.public_auth import PublicAuth

class LogChanges(Resource):
    #api-log-changes-get
    # @base.access_middleware
    def get(self, table, id):
        try:
            schema = Schema(many = True)
            data = Model.query.filter_by(table_name = table, row_id = id, estado = 1).all()
            result = schema.dump(data)
            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": result
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response

class LogChangesBooking(Resource):
    #api-log-changes-booking-get
    # @base.access_middleware
    def get(self, code_reservation):
        try:
            # Se busca estado 2 (histórico)
            result = LogChangesHelper.get_log_booking(code_reservation)
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response