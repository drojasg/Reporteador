from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError, EXCLUDE
from flask import Flask, jsonify
import json
from config import db, base
from models.season import SeasonSchema as ModelSchema, SeasonRefSchema as ModelRefSchema, Season as Model
from models.period_season import PeriodSeasonSchema as PeriodModelSchema, PeriodSeasonRefSchema as PeriodModelRefSchema, PeriodSeason as PeriodModel
from models.property import PropertySchema as PropertyModelSchema, Property as PropertyModel
from common.util import Util

class Season(Resource):
#  @base.access_middleware
 def put(self, id):
     response = {}
     
     try:
        json_data = request.get_json(force=True)
        schema = ModelSchema(exclude=Util.get_default_excludes())
        data = schema.load(json_data,unknown=EXCLUDE)
        model = Model.query.get(id)
            
        dataResponseSeason = []
        dataResponsePeriods = []

        user_data = base.get_token_data()
        user_name = user_data['user']['username']
                    
        if model is None:
            return{
                "Code": 404,
                "Msg": "data not found",
                "Error": True,
                "data": {}
            }
            
        model.description = data["description"]
        model.iddef_property = data["iddef_property"]
        model.estado = data["estado"]
        model.usuario_ultima_modificacion = user_name
        db.session.commit()
            
        responseSeason = schema.dump(model)
            
        for dataRequest in json_data["periods"]:
            if dataRequest['iddef_period_season'] != None:
               
                period_model = PeriodModel.query.get(dataRequest['iddef_period_season'])
                period_model.iddef_season = responseSeason['iddef_season']
                period_model.start_date = dataRequest["start_date"]
                period_model.end_date = dataRequest["end_date"]
                period_model.estado = dataRequest["estado"]
                period_model.usuario_ultima_modificacion = user_name
                db.session.commit()
                dataResponsePeriods = []
                #dataResponsePeriods = schema.dump(period_model)
            else:
                period_model = PeriodModel()
                period_model.iddef_season = responseSeason['iddef_season']
                period_model.start_date = dataRequest["start_date"]
                period_model.end_date = dataRequest["end_date"]
                period_model.usuario_creacion = user_name
                period_model.estado = 1
                    
                db.session.add(period_model)
                dataResponsePeriods.append(period_model)
                    
                db.session.commit()
            
        response = {
            "Code": 200,
            "Msg": "Success",
            "Error": False,
            "data": schema.dump(model)
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


class SeasonList(Resource):

    # @base.access_middleware
    def post(self):
        
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            model = Model()
            data = schema.load(json_data, unknown=EXCLUDE)
            model = Model()
            dataResponseSeason = []
            dataResponsePeriods = []
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            model.iddef_property = data["iddef_property"]
            model.description = data["description"]
            model.estado = 1
            model.usuario_creacion = user_name
            
            db.session.add(model)
            dataResponseSeason.append(model)
            db.session.commit()
            
            responseSeason = schema.dump(dataResponseSeason, many=True)

            for dataRequest in json_data["periods"]:

                period_model = PeriodModel()

                period_model.iddef_season = responseSeason[0]['iddef_season']
                period_model.start_date = dataRequest["start_date"]
                period_model.end_date = dataRequest["end_date"]
                period_model.estado = 1
                period_model.usuario_creacion = user_name
                    
                db.session.add(period_model)
                dataResponsePeriods.append(period_model)

            db.session.commit()
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(model)
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
    def get(self,idHotel):

        response = {}

        try:
            #inicializamos el Schema season
            schema = ModelSchema(exclude=Util.get_default_excludes())
            #inicializamos el Schema PeriodSeasonSchema
            period_schema = PeriodModelSchema(exclude=Util.get_default_excludes())

            #Obtenemos los datos de la tabla Season
            SeasonData = Model.query.filter_by(iddef_property=idHotel, estado=1).all()
            season_data_json = schema.dump(SeasonData, many=True)
            
            if SeasonData != None:
                #obtenemos los datos de la tabla def_period_season
                # aux = {}
                listt = []
                for data_season in SeasonData:
                    aux = {}

                    period_data = PeriodModel.query.filter_by(iddef_season = data_season.iddef_season, estado = 1).all()                    
                    aux['iddef_season']= data_season.iddef_season
                    aux['description']= data_season.description
                    aux['iddef_property']= data_season.iddef_property
                    aux['estado']= data_season.estado
                    aux['periods'] = []

                    
                    if period_data:
                        period_dataSchema = period_schema.dump(period_data, many=True)
                        period_json = json.dumps(period_dataSchema)
                        decoded = json.loads(period_json)
                        aux['periods'] = decoded
                                        
                    listt.append(aux)

                #Se construye el response
                response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": listt
                    #"data": schema.dump(SeasonData, many=True)
                }

            else:

                response = {
                    "Code":500,
                    "Msg":"Property no found",
                    "Error":True,
                    "data":{}
                }

        except ValidationError as Error:
            
            response = {
                "Code":500,
                "Msg": Error.messages,
                "Error":True,
                "data": {}
            }
        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response
