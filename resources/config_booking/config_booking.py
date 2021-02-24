from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, timedelta
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql import exists

from config import base, app, db, base
from models.config_booking import ConfigBooking as Model, ConfigBookingSchema as ModelSchema
from common.util import Util
from common.public_auth import PublicAuth
from resources.terms_and_conditions.terms_and_conditions_service import TermsAndConditionsService

class ConfigBooking(Resource):
    #api-config-booking-get-by-id
    # @base.access_middleware
    def get(self,id):
                
        response = {}

        try:

            data = Model.query.get(id)

            schema = ModelSchema(exclude=Util.get_default_excludes())

            response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": schema.dump(data)
                }

        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response

    #api-config-booking-create
    # @base.access_middleware
    def post(self):

        response = {}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            data_compare = data["param"].strip()

            param_exist = self.get_param_if_exists(data_compare.lower())

            if param_exist:
               raise Exception("The name" + " " + data["param"] + " " + "already exists, please enter a different name")
            else:
                model.param = data_compare.lower()
                model.enable_public = data["enable_public"]
                model.value = data["value"]
                model.type = data["type"]
                model.estado = data["estado"]
                model.usuario_creacion = user_name
                db.session.add(model)
                db.session.commit()

            response={
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as Error:
            db.session.rollback()
            response = {
                "Code":500,
                "Msg": Error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            

            db.session.rollback()
            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }
        return response

    #api-config-booking-update
    # @base.access_middleware
    def put(self, id):

        response = {}

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()
            data_compare = data["param"].strip()
            
            #param_exist = self.get_param_if_exists(data["param"].strip())
            id_param_exist = self.get_param_if_exists_by_parameter_idconfig(id,data_compare.lower())

            if id_param_exist:
                #si existe, es el mismo id con el mismo nombre lo actualizamos
                dataUpdate = model.query.filter_by(idconfig_booking = id).first()

                dataUpdate.param = data_compare.lower()
                dataUpdate.enable_public = data["enable_public"]
                dataUpdate.value = data["value"]
                dataUpdate.type = data["type"]
                dataUpdate.estado = data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.flush()
            else:

                # si no lo insertamos, pero primero preguntamos si el nombre ya existe en toda la tabla
                param_exist = self.get_param_if_exists(data_compare.lower())
                if param_exist:
                    raise Exception("The name" + " " + data["param"] + " " + "already exists, please enter a different name")
                else:
                    model.param =  data_compare.lower()
                    model.enable_public = data["enable_public"]
                    model.value = data["value"]
                    model.type = data["type"]
                    model.estado = data["estado"]
                    model.usuario_creacion = user_name
                    db.session.add(model)
                    db.session.flush()
            
            db.session.commit()

            response={
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
            }
        except ValidationError as Error:
            db.session.rollback()
            response = {
                "Code":500,
                "Msg": Error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            

            db.session.rollback()
            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }
        return response


    @staticmethod
    def get_param_if_exists(parameter):

        data = db.session.query(exists().where(Model.param == parameter)).scalar()

        if data:
            #si ya existe el nombre del parametro regresamos True
            return True
        else:
            #si no existe entonces False
            return False
    
    @staticmethod
    def get_param_if_exists_by_parameter_idconfig(id,parameter):
        
        data = db.session.query(exists().where(Model.idconfig_booking == id).where(Model.param == parameter)).scalar()

        if data:
            #si existe
            return True
        else:
            return False

class ConfigBookingListSearch(Resource):
    #api-config-booking-search-list
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.all()

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

    #api-config-booking-delete-status
    # @base.access_middleware
    def put(self, id):
        
        response = {}
        try:
                        
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            db.session.commit()

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

class ConfigBookingPublic(Resource):
    @PublicAuth.access_middleware
    def get(self, lang):
        response = {
            "Code": 200,
            "Msg": "",
            "Error": False,
            "data": {}
        }
        
        try:
            lang = lang.lower()
            data = Model.query.filter(Model.enable_public == 1, Model.estado == 1).all()
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            default_brand = "palace_resorts"
            
            terms_cond = TermsAndConditionsService.get_terms_and_conditions_by_brand(default_brand)
            
            if terms_cond:
                config_param = Model()
                config_param.enable_public = 1
                config_param.estado = 1
                config_param.type = "string"
                config_param.value = terms_cond.link_es if lang == "es" else terms_cond.link_en
                config_param.idconfig_booking = 0
                config_param.param = "default_terms_and_conditions"
                data.append(config_param)
            
            data += self.get_urls(lang)

            response["data"] = schema.dump(data)
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
    
    def get_urls(self, lang = "en"):
        data = []
        urls = {
            "terms_cookies_privacy": {
                "en": "https://www.palaceresorts.com/en/cookies-privacy-notice",
                "es": "https://www.palaceresorts.com/es/aviso-cookies"
            },
            "terms_users_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-users",
                "es": "https://www.palaceresorts.com/es/usuarios"
            },
            "terms_covid_privacy": {
                "en": "https://www.palaceresorts.com/en/full-privacy-notice-covid-19-monitoring",
                "es": "https://www.palaceresorts.com/es/aviso-privacidad-integral-monitoreo-covid-19"
            },
            "terms_mkt_privacy": {
                "en": "https://www.palaceresorts.com/en/general-privacy-notice-marketing-and-advertising",
                "es": "https://www.palaceresorts.com/es/aviso-de-privacidad-integral-mercadotecnia-y-publicidad-hotelera-palace-resorts"
            },
            "terms_gdpr_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-notice-clients-gdpr",
                "es": "https://www.palaceresorts.com/es/aviso-privacidad-clientes-rgpd"
            },
            "terms_ccpa_california_privacy": {
                "en": "https://www.palaceresorts.com/en/ccpa-privacy-policy",
                "es": "https://www.palaceresorts.com/es/ccpa-politica-privacidad"
            },
            "terms_mx_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-notice-reservations-mexico",
                "es": "https://www.palaceresorts.com/es/aviso-privacidad-integral-mexico"
            },
            "hurricane_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-users",
                "es": "https://www.palaceresorts.com/es/usuarios"
            },
            "sustainability_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-users",
                "es": "https://www.palaceresorts.com/es/usuarios"
            },
            "video_surveillance_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-users",
                "es": "https://www.palaceresorts.com/es/usuarios"
            },
            "eu_privacy": {
                "en": "https://www.palaceresorts.com/en/privacy-users",
                "es": "https://www.palaceresorts.com/es/usuarios"
            },
            "mettings_url": {
                "en": "https://meetings.palaceresorts.com/en/",
                "es": "https://meetings.palaceresorts.com/es"
            },
            "weddings_url": {
                "en": "http://weddings.palaceresorts.com/en",
                "es": "http://weddings.palaceresorts.com/es"
            },
            "travel_agent_url": {
                "en": "https://www.palaceproagents.com",
                "es": "https://www.palaceproagents.com"
            },
            "palace_url": {
                "en": "https://www.palaceresorts.com",
                "es": "https://www.palaceresorts.com"
            },
            "moon_url": {
                "en": "https://www.moonpalace.com",
                "es": "https://www.moonpalace.com"
            },
            "le_blanc_url": {
                "en": "https://www.leblancsparesorts.com",
                "es": "https://www.leblancsparesorts.com"
            }            
        }
        
        for key, value in urls.items():
            config_param_mx = Model()
            config_param_mx.enable_public = 1
            config_param_mx.estado = 1
            config_param_mx.type = "string"
            config_param_mx.value = value.get(lang, "")
            config_param_mx.idconfig_booking = 0
            config_param_mx.param = key
            data.append(config_param_mx)
            

        return data