from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from common.util import Util
from models.op_rate import RatesSchema as rate_schema
from .rates_create_helper import Process_Rate as rate_helper
from common import util

class OpRate(Resource):
    #api-internal-rate-post
    #@base.access_middleware
    def post(self):
        response = {
            "Code":200,
            "Msg":"Success",
            "Error":False,
            "Errors":[],
            "Warnings":[],
            "data":{}
        }

        try:
            json_data = request.get_json(force=True)
            schema = rate_schema()
            data = schema.load(json_data)
            data_response = {
                "Success":[]
            }

            rate = rate_helper(data["rate_plan"],data["hotel"],data["room_type_category"],\
            data["currency_code"],data["include_kids"],data["market"])
            rate.process(data["rates"])

            data_response["Success"] = rate.Data_str
            response["Warnings"] = rate.Warnings
            response["Errors"] = rate.Errors

            response["data"]=data_response
        except ValidationError as error:
            message = util.Util.find_nested_error_message(error.messages)
            response["Code"]=501
            response["Error"]=True
            response["Msg"]=message

        except Exception as rate_error:
            response["Code"]=500
            response["Error"]=True
            response["Msg"]=str(rate_error)

        return response