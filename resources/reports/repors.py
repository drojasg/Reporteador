from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.reports import ReportsSchema as ModelSchema, Reports as Model
from common.util import Util


class ReportsListSearch(Resource):
    #api-reports-get-all
    #@base.access_middleware
    def get(self):
        try:

            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

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
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response