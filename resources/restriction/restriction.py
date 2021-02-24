from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import and_, or_
import json

from config import db, base
from models.restriction import RestrictionSchema as ModelSchema, Restriction as Model, RestrictionPostSchema, RestrictionDetailDataSchema, RestrictionPutSchema, OperaInsertRestrictionSchema
from models.restriction_by import  RestrictionBy, RestrictionBySchema 
from models.restriction_type import  RestrictionType , RestrictionTypeSchema 
from models.restriction_detail import  RestrictionDetail , RestrictionDetailSchema
from models.opera_restrictions import OperaRestrictionCloseDateSchema as OpeResCloseSchema
from resources.restriction.restricctionHelper import RestricctionFunction as functions
from common.util import Util
#from common.custom_log_response import CustomLogResponse

class Restriction(Resource):
    #api-restriction-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")
            restricionby = request.args.get("restricionby")
            data = Model()
            conditions = []

            if isAll is None:
                data = db.session.query(Model)\
                                    .join(RestrictionBy, RestrictionBy.iddef_restriction_by == Model.iddef_restriction_by)\
                                    .join(RestrictionType, RestrictionType.iddef_restriction_type == Model.iddef_restriction_type)\
                                    .all()
            if restricionby is not None:
                restricionbys = restricionby.split(",")
                
                conditions.append(Model.iddef_restriction_by.in_(restricionbys))

            if len(conditions) >= 1:
                data = Model.query.filter(and_(*conditions))

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
    

    #api-restriction-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.json
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
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {}
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
        

    #api-restriction-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.json
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            #iddef_restriction indique 0 es que tanto la restricion como los detalles de ella son nuevos
            if int(json_data["iddef_restriction"]) == 0:
                 
                schema = RestrictionPostSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
                model = Model()
                model.name = data["name"]
                model.estado = data["estado"]
                model.iddef_restriction_by = data["iddef_restriction_by"]
                model.iddef_restriction_type = data["iddef_restriction_type"]
                model.estado = 1
                model.usuario_creacion = user_name
                db.session.add(model)
                db.session.flush()
                insert = schema.dump(model)
                iddef_restriction = insert["iddef_restriction"]
                
                
                #Inserta todos los detalles con id de la restriccion recien insertada
                for x in json_data["data"]:
                    restrictiondetail = RestrictionDetail()
                    schemaDetail = RestrictionDetailDataSchema(exclude=Util.get_default_excludes())
                    data = schemaDetail.load(x)
                    restrictiondetail.device_type_option = x["device_type_option"]
                    restrictiondetail.iddef_restriction = iddef_restriction
                    restrictiondetail.travel_window_option = x["travel_window_option"]
                    restrictiondetail.geo_targeting_option = x["geo_targeting_option"]
                    restrictiondetail.channel_option = x["channel_option"]
                    restrictiondetail.bookable_weekdays_option = x["bookable_weekdays_option"]
                    restrictiondetail.bookable_weekdays = x["bookable_weekdays"]
                    restrictiondetail.booking_window_dates = x["booking_window_dates"]
                    restrictiondetail.booking_window_times = x["booking_window_times"]
                    restrictiondetail.booking_window_option = x["booking_window_option"]
                    restrictiondetail.restriction_default = x["restriction_default"]
                    restrictiondetail.market_option = x["market_option"]
                    restrictiondetail.market_targeting = x["market_targeting"]
                    restrictiondetail.min_los = x["min_los"]
                    restrictiondetail.max_los = x["max_los"]
                    restrictiondetail.value = x["value"]
                    restrictiondetail.estado = x["estado"]
                    restrictiondetail.usuario_creacion = user_name
                    restrictiondetail.travel_window = x["travel_window"]
                    restrictiondetail.geo_targeting_countries = x["geo_targeting_countries"]
                    restrictiondetail.specific_channels = x["specific_channels"]
                    
                    db.session.add(restrictiondetail)
                    db.session.commit()
            else:
                #Edita tabla de restriction
                schema = RestrictionPutSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
                model = Model.query.get(json_data["iddef_restriction"])
                if json_data["name"] != None:
                    model.name = data["name"]
                if json_data["iddef_restriction_by"] != None:
                    model.iddef_restriction_by = data["iddef_restriction_by"]
                if json_data["iddef_restriction_type"] != None:
                    model.iddef_restriction_type = data["iddef_restriction_type"]
                if json_data["estado"] != None:
                    model.estado = data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.commit()
                
                #For para los detalles de la tabla restriction_detail
                for x in json_data["data"]:
                    # si iddef_restriction_detail indica 0 que es una nueva insercion sobre la restriccion
                    if int(x["iddef_restriction_detail"]) == 0:
                        restrictiondetail = RestrictionDetail()
                        schemaDetail = RestrictionDetailDataSchema(exclude=Util.get_default_excludes())
                        data = schemaDetail.load(x)
                        
                        restrictiondetail.device_type_option = x["device_type_option"]
                        restrictiondetail.iddef_restriction = json_data["iddef_restriction"]
                        restrictiondetail.travel_window_option = x["travel_window_option"]
                        restrictiondetail.geo_targeting_option = x["geo_targeting_option"]
                        restrictiondetail.channel_option = x["channel_option"]
                        restrictiondetail.booking_window_dates = x["booking_window_dates"]
                        restrictiondetail.bookable_weekdays_option = x["bookable_weekdays_option"]
                        restrictiondetail.bookable_weekdays = x["bookable_weekdays"]
                        restrictiondetail.booking_window_times = x["booking_window_times"]
                        restrictiondetail.booking_window_option = x["booking_window_option"]
                        restrictiondetail.restriction_default = x["restriction_default"]
                        restrictiondetail.min_los = x["min_los"]
                        restrictiondetail.max_los = x["max_los"]
                        restrictiondetail.value = x["value"]
                        restrictiondetail.estado = x["estado"]
                        restrictiondetail.usuario_creacion = user_name
                        restrictiondetail.travel_window = x["travel_window"]
                        restrictiondetail.geo_targeting_countries = x["geo_targeting_countries"]
                        restrictiondetail.specific_channels = x["specific_channels"]
                        restrictiondetail.market_option = x["market_option"]
                        restrictiondetail.market_targeting = x["market_targeting"]
                        
                        db.session.add(restrictiondetail)
                        db.session.commit()
                    #si iddef_restriction_detail viene con un numero se hara la modificacion sobre el exitente 
                    else:
                        
                        restrictiondetail = RestrictionDetail()
                        schema = RestrictionDetailDataSchema(exclude=Util.get_default_excludes())                       
                        data = schema.load(x)

                        model = RestrictionDetail.query.get(x["iddef_restriction_detail"])
                        
                        if x["device_type_option"] != None:
                            model.device_type_option = x["device_type_option"]
                        if x["iddef_restriction"] != None:
                            model.iddef_restriction = json_data["iddef_restriction"]
                        if x["travel_window_option"] != None:
                            model.travel_window_option = x["travel_window_option"]
                        if x["geo_targeting_option"] != None:
                            model.geo_targeting_option = x["geo_targeting_option"]
                        if x["channel_option"] != None:
                            model.channel_option = x["channel_option"]
                        if x["booking_window_dates"] != None:
                            model.booking_window_dates = x["booking_window_dates"]
                        if x["bookable_weekdays_option"] != None:
                            model.bookable_weekdays_option = x["bookable_weekdays_option"]
                        if x["bookable_weekdays"] != None:
                            model.bookable_weekdays = x["bookable_weekdays"]
                        if x["booking_window_times"] != None:
                            model.booking_window_times = x["booking_window_times"]
                        if x["booking_window_option"] != None:
                            model.booking_window_option = x["booking_window_option"]
                        if x["restriction_default"] != None:
                            model.restriction_default = x["restriction_default"]
                        if x["estado"] != None:
                            model.estado = x["estado"]
                        model.usuario_ultima_modificacion = user_name
                        if x["travel_window"] != None:
                            model.travel_window = x["travel_window"]
                        if x["geo_targeting_countries"] != None:
                            model.geo_targeting_countries = x["geo_targeting_countries"]
                        if x["specific_channels"] != None:
                            model.specific_channels = x["specific_channels"]
                        if x["market_option"] != None:
                            model.market_option = x["market_option"]
                        if x["market_targeting"] != None:
                            model.market_targeting = x["market_targeting"]
                        if x["min_los"] != None:
                            model.min_los = x["min_los"]
                        if x["max_los"] != None:
                            model.max_los = x["max_los"]
                        if x["value"] != None:
                            model.value = x["value"]
                        db.session.commit()
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {}
            }
        except ValidationError as error:
            db.session.rollback()
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
    

    # @base.access_middleware
    def ListaToJson(self, lista):
        item_data = {}
        for index, value in enumerate(lista):
            item_data[index] = value
        data = json.dumps(item_data)
        return item_data

class getSpecificRestriction(Resource):
    #api-restriction-test-all
    # @base.access_middleware
    def get(self):
        data = functions.getRestriction(self)

        schema = RestrictionDetailSchema(exclude=Util.get_default_excludes(), many=True)

        dataDump=schema.dump(data)

        return dataDump

class OperaRestriction(Resource):
    #@base.access_middleware
    #@CustomLogResponse.save
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = OperaInsertRestrictionSchema()
            data = schema.load(json_data)
            
            for index_data, obj_data in enumerate(data["data"]):
                if len(obj_data["restrictions"]) > 0:
                    for index_restriction, obj_restriction in enumerate(obj_data["restrictions"]):
                        data["data"][index_data]["restrictions"][index_restriction]["date_start"] = obj_restriction["date_start"].strftime("%Y-%m-%d")
                        data["data"][index_data]["restrictions"][index_restriction]["date_end"] = obj_restriction["date_end"].strftime("%Y-%m-%d")
                else:
                    raise Exception("Element witout dates")

            resultado = functions.process_opera_restriction(data["restriction_type"], data["data"], "admin")

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": resultado
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }
        
        return response

class OperaRestrictionCloseDate(Resource):
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = OpeResCloseSchema()
            data = schema.load(json_data)
            
            rateplans = request.json.get("rateplans", [])
            resultado = functions.getCloseDatesOperaRestriction(date_start=data["date_start"], date_end=data["date_end"], 
                property=data["property"], room=data["room"], rateplans=rateplans, all_rateplans=True)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": resultado
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }
        
        return response
