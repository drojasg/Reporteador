from flask import Flask, request
from flask_restful import Resource
from datetime import date
from xecd_rates_client import XecdClient

from models.currency import Currency as CurrencyModel
from models.country import Country as cnModel
from models.market_segment import MarketSegment as mkModel
from models.exchange_rate import ExchangeRate as ExchangeRateModel
from models.config_external_services import ConfigExternalServices as ConfigServicesModel
#from resources.rates.RatesHelper import RatesFunctions as rFunctions
from .exchange_rate_service import ExchangeRateService
from config import db, app, base
import json, requests

class ExchangeRate(Resource):

    def get(self,currency_code):
        response = {
            "code":200,
            "msg":"Success",
            "data":{},
            "error":False
        }

        # market_info = mkModel.query.join(cnModel,cnModel.idmarket_segment==mkModel.iddef_market_segment\
        # ).filter(mkModel.estado==1, cnModel.country_code==market_code, cnModel.estado==1).first()
        # if market_info is None:
        #     raise Exception("Mercado no encontrado")

        currency_exange = 0
        if currency_code.upper() == "MXN":
            currency_exange = ExchangeRateService.convert_to_currency(currency_code,"USD",\
            1,date.today())
        else:
            currency_exange = ExchangeRateService.convert_to_currency(currency_code,\
            "USD",1,date.today())

        response["data"]={
            "currency_base":"USD",
            "exange_amount":currency_exange
        }

        return response

    #api-exchange-rate-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            default_currency = "USD"
            current_date = date.today()
            default_amount = 1
            env = base.environment
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #get xe.com credentials
            config = ConfigServicesModel.query.filter(ConfigServicesModel.code == "xe", ConfigServicesModel.estado == 1, ConfigServicesModel.env == env).first()
            account_id = config.settings.get("account_id", "")
            secret_key = config.settings.get("secret_key", "")

            #init xe.com service
            xecd = XecdClient(account_id, secret_key)
            currency_list = CurrencyModel.query.filter(CurrencyModel.estado == 1, CurrencyModel.currency_code != default_currency).all()

            #currencies separate by comma
            currencies = ",".join([str(item.currency_code) for item in currency_list])
            
            #request to xe.com for all the currencies
            response = xecd.convert_from(default_currency, currencies, default_amount)
            response_list = response.get("to", {})

            exchange_list = ExchangeRateModel.query.filter(
                                                    ExchangeRateModel.estado == 1, 
                                                    ExchangeRateModel.date == current_date, 
                                                    ExchangeRateModel.currency_code.in_(currencies.split(","))).all()
            
            #iterate the results
            for item in response_list:
                quote_currency = item.get("quotecurrency", None)
                quote_amount = round(item.get("mid", 0), 4)

                exchange_rate = next((aux_item for aux_item in exchange_list if aux_item.currency_code ==
                                    quote_currency), None)
                
                #if not exist create
                if exchange_rate is None:
                    exchange_rate = ExchangeRateModel()
                    exchange_rate.date = current_date
                    exchange_rate.currency_code = quote_currency
                    exchange_rate.amount = quote_amount
                    exchange_rate.estado = 1
                    exchange_rate.usuario_creacion = user_name
                    db.session.add(exchange_rate)
                #if exists update
                elif exchange_rate.amount != quote_amount:
                    exchange_rate.amount = quote_amount
                    exchange_rate.usuario_ultima_modificacion = user_name
                    db.session.add(exchange_rate)
            
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
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

class ExchangeRateOpenEx(Resource):
    #api-exchange-rate-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            """ 
            si mandan por post, ingresa los datos de esa fecha, si no, inserta del dia de hoy
            {"history_date":"2020-06-06"}
            """            
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            json_data = request.json
            current_date = date.today()
            
            if json_data:
                current_date = json_data["history_date"]

            exchange_service = ExchangeRateService()
            response_rates = exchange_service.save_exchange_rate(current_date, user_name)
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": response_rates
            }            
        except Exception as e:            
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
