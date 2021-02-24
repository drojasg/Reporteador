from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, app, base
from sqlalchemy import or_, and_
import os
import werkzeug
from models.geo_ip import GeoIpSchema as ModelSchema, GeoIp as Model
from socket import inet_aton
from common.util import Util
from resources.rates.RatesHelper import RatesFunctions as rFunctions
from models.currency import Currency
from common.public_auth import PublicAuth

class GeoIp(Resource):
    #api-geo-ip-post
    #@base.access_middleware
    def post(self):
        response = {}
        tmp_path_file = ""

        try:
            file = request.files['file']
            filename = werkzeug.utils.secure_filename(file.filename)
            tmp_path_file = os.path.join("tmp", filename)
            file.save(tmp_path_file)

            file = tmp_path_file
            ### load local csv
            sql = """
                LOAD DATA LOCAL INFILE '{csv}' REPLACE INTO TABLE {table} \r
                FIELDS TERMINATED BY ';' ENCLOSED BY '"' \r
                ({columns})""".format(
                csv=file,
                table="op_geo_ip",
                columns="start_ip_address, end_ip_address, start_ip_numeric, end_ip_numeric, country_code_iso_2, country_code_iso_3, country_code_iso_number, country_name"
            )

            db.session.execute(sql)
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {
                    "message": "The file was loaded"
                }
            }
        except Exception as e:
            app.log_exception(e)
            db.session.rollback()
            self.__add_error("An error occurred while saving data")
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        finally:
            os.remove(tmp_path_file)

        return response
    
class GeoIpPublic(Resource):
    #api-filters-get-by-ip
    @PublicAuth.access_middleware
    def get(self, ip):
        try:
            #ip is converted to int number to find in db
            ip_numeric = int.from_bytes(inet_aton(ip), byteorder="big")

            data = Model.query.filter(and_(
                ip_numeric >= Model.start_ip_numeric, ip_numeric <= Model.end_ip_numeric)).first()

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                schema = ModelSchema(exclude=Util.get_default_excludes())
                dataDump = schema.dump(data)
                dataDump["default_currency"] = "USD"
                dataDump["iddefault_currency"] = 1
                try:
                    marketInfo = rFunctions.getMarketInfo(dataDump["country_code_iso_2"])
                    dataDump["default_currency"] = marketInfo.currency_code
                except Exception as e:
                    pass

                try:
                    currencyInfo = Currency.query.filter(Currency.estado==1,\
                    Currency.currency_code==dataDump["default_currency"]).first()
                    dataDump["iddefault_currency"] = currencyInfo.iddef_currency
                except Exception as e:
                    pass
                
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": dataDump
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class GeoCountryPublic(Resource):
    @PublicAuth.access_middleware
    def get(self, market_code):
        try:
            data = Model.query.filter(and_(Model.country_code_iso_2 == market_code, Model.estado == 1)).first()

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                schema = ModelSchema(exclude=Util.get_default_excludes())
                dataDump = schema.dump(data)
                dataDump["default_currency"] = "USD"
                dataDump["iddefault_currency"] = 1
                try:
                    marketInfo = rFunctions.getMarketInfo(dataDump["country_code_iso_2"])
                    dataDump["default_currency"] = marketInfo.currency_code
                except Exception as e:
                    pass

                try:
                    currencyInfo = Currency.query.filter(Currency.estado==1,\
                    Currency.currency_code==dataDump["default_currency"]).first()
                    dataDump["iddefault_currency"] = currencyInfo.iddef_currency
                except Exception as e:
                    pass
                
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": dataDump
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
