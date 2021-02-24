from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
import datetime
from config import base
from models.rates import PushRatesSchema
#from common.custom_log_request import CustomLogRequest

class Push(Resource):
    #api-rates-push-rates
    #@base.access_middleware
    def post(self):
        response = {}

        try: 
            dataRq = request.get_json(force=True)
            schema = PushRatesSchema()
            data = schema.load(dataRq)

            url_base = base.get_url("wire_reservation")
            #http://wire-dev6/clever_reservation/api/rates/PushRates_BEngine/

            url_service= '{}/rates/PushRates_BEngine/'.format(url_base)
            
            request_service= {
                "hotel":data["hotel"],
                "date_start": data["date_start"].strftime("%Y-%m-%d"),
                "date_end": data["date_end"].strftime("%Y-%m-%d"),
                "rate_plan_clever": data["rate_plan_clever"],
                "rate_plan_channel": data["rate_plan_channel"],
                "include_promotion": data["include_promotion"],
                "date_start_promotions": data["date_start_promotions"].strftime("%Y-%m-%d"),
                "refundable":data["refundable"]
            }

            response_api = CustomLogRequest.do_request(url=url_service,\
            method="post",data=request_service,timeout=100,verifi_ssl=False)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": response_api
            }               

            return response, 200, {"Access-Control-Allow-Origin": "*"}
            
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": []
            }

        return response


