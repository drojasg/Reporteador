from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.log_apis import LogApis as Model, LogApisSchema as Schema, LogApisSchemaList as SchemaList

from common.util import Util
from sqlalchemy import or_, and_
from common.public_auth import PublicAuth
from datetime import timedelta
import re

class LogApis(Resource):
    #api-log-apis-search
    #@base.access_middleware
    def post(self):
        try:
            json_data = request.get_json(force=True)
            schema = Schema()
            data_info = schema.load(json_data)
            conditions = []

            if request.json.get("idlog_apis") != None:
                conditions.append(Model.idlog_apis==data_info["idlog_apis"])

            if request.json.get("url") != None:
                conditions.append(Model.url==data_info["url"])

            if request.json.get("request_method") != None:
                conditions.append(Model.request_method==data_info["request_method"])

            if request.json.get("request_headers") != None:
                for key_req_header in data_info["request_headers"]:
                    conditions.append(Model.request_headers.op('regexp')(f'{re.escape(str(key_req_header))}([[.quotation-mark.]]|[[.colon.]]|[[.backslash.]]|[[.space.]])*{re.escape(str(data_info["request_headers"][key_req_header]))}'))

            if request.json.get("request_data") != None:
                for key_req_data in data_info["request_data"]:
                    conditions.append(Model.request_data.op('regexp')(f'{re.escape(str(key_req_data))}([[.quotation-mark.]]|[[.colon.]]|[[.backslash.]]|[[.space.]])*{re.escape(str(data_info["request_data"][key_req_data]))}'))

            if request.json.get("response_headers") != None:
                for key_res_header in data_info["response_headers"]:
                    conditions.append(Model.response_headers.op('regexp')(f'{re.escape(str(key_res_header))}([[.quotation-mark.]]|[[.colon.]]|[[.backslash.]]|[[.space.]])*{re.escape(str(data_info["response_headers"][key_res_header]))}'))

            if request.json.get("response_data") != None:
                for key_res_data in data_info["response_data"]:
                    conditions.append(Model.response_data.op('regexp')(f'{re.escape(str(key_res_data))}([[.quotation-mark.]]|[[.colon.]]|[[.backslash.]]|[[.space.]])*{re.escape(str(data_info["response_data"][key_res_data]))}'))

            if request.json.get("username") != None:
                conditions.append(Model.username==data_info["username"])

            if request.json.get("estado") != None:
                conditions.append(Model.estado==data_info["estado"])
            else:
                conditions.append(Model.estado==1)

            if request.json.get("date_start") != None and request.json.get("date_end") != None:
                #Se convierte horario Chetumal a UTC para busqueda
                conditions.append(Model.fecha_creacion>=(data_info["date_start"] + timedelta(hours=5)))
                conditions.append(Model.fecha_creacion<=(data_info["date_end"] + timedelta(hours=5)))

            if request.json.get("limit") != None:
                limit=data_info["limit"]
            else:
                limit=100

            data = Model.query.filter(and_(*conditions)).limit(limit).all()

            schema = SchemaList(many = True)
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

