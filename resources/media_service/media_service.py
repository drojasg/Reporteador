from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.media_service import MediaServiceSchema as ModelSchema, GetMediaServiceSchema as GetModelSchema, GetListMediaServiceSchema as GetListModelSchema, MediaService as Model, GetMediaServiceAdminSchema, PostMediaServiceSchema
from models.media import Media as MedModel
from models.media_group import MediaGroup as MedGruModel
from models.media_type import MediaType as MedTypModel
from common.util import Util
from sqlalchemy.sql.expression import and_
from sqlalchemy import func


class MediaService(Resource):
    #api-media-service-get-by-id
    #Administrativa
    # @base.access_middleware
    def get(self, id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)

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

    #api-media-service-put
    #Administrativa
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.json
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model.query.get(id)

            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            if request.json.get("iddef_service") != None:
                model.iddef_service = data["iddef_service"]
            if request.json.get("iddef_media") != None:
                model.iddef_media = data["iddef_media"]
            if request.json.get("lang_code") != None:
                model.lang_code = data["lang_code"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
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

    #api-media-service-delete
    #Administrativa
    # @base.access_middleware
    def delete(self, id):
        response = {}
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
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

            model.estado = 0
            model.usuario_ultima_modificacion = user_name
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

    #api-media-service-post
    #Administrativa
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.json
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            model.iddef_service = data["iddef_service"]
            model.iddef_media = data["iddef_media"]
            model.lang_code = data["lang_code"]
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
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

class MediaServiceListSearch(Resource):
    #api-media-service-get-all
    #Administrativa
    # @base.access_middleware
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

class AdminMediaServiceList(Resource):
    #api-admin-media-service-get-all
    #api get media service administrativa
    #@base.access_middleware
    def get(self, idService, langCode, idProperty, idDefMediaType):
        try:
            schema = GetMediaServiceAdminSchema(many=True)
            conditions = [MedModel.estado == 1, MedGruModel.iddef_property == idProperty]
            
            if idDefMediaType != 0:
                conditions.append(MedModel.iddef_media_type == idDefMediaType)
            
            #filtrar por id de servicio y por idioma
            data = MedModel.query.with_entities(\
            MedModel.description, \
            MedModel.iddef_media, MedModel.name, MedModel.tags,\
            MedModel.url)\
            .add_columns(func.IF(Model.estado == None, 0,1).label("selected"))\
            .join(MedGruModel,and_(MedGruModel.iddef_media_group == MedModel.iddef_media_group))\
            .outerjoin(Model,and_(Model.iddef_media == MedModel.iddef_media, Model.estado == 1, Model.iddef_service == idService, Model.lang_code == langCode))\
            .filter(and_(*conditions)).all()
            
            mediaServicedataJson= schema.dump(data)
        
            response={
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": mediaServicedataJson
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
        
    #api-media-service-post-and-put
    # @base.access_middleware    
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema  = ModelSchema(exclude=Util.get_default_excludes())
            postSchema = PostMediaServiceSchema(exclude=Util.get_default_excludes())
            data = postSchema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []
            
            data_media_service = Model.query.filter(Model.iddef_service == data['iddef_service'], Model.lang_code == data['lang_code'])
            mediaServiceDataJson = schema.dump(data_media_service, many=True)
                        
            for x in mediaServiceDataJson:
                M = Model.query.get(x['iddef_media_service'])
                M.estado = 0
                
            for media_id in data["medias_id"]:
                if media_id not in [ x["iddef_media"] for x in mediaServiceDataJson ]:
                    aux = {}
                    model = Model()
                    model.iddef_service = data['iddef_service']
                    model.lang_code = data['lang_code']
                    model.iddef_media = media_id
                    model.estado = 1
                    model.usuario_creacion = user_name
                    db.session.add(model)
                    db.session.flush()
                    aux['Datos_Insertados'] = schema.dump(model)
                    dataResponse.append(aux)
                else:
                    aux = {}
                    schemaP  = ModelSchema(exclude=Util.get_default_excludes())
                    value =  [x for x in mediaServiceDataJson \
                    if x["iddef_media"] == media_id \
                    and x["iddef_service"] == data["iddef_service"] \
                    and x["lang_code"] == data["lang_code"]
                    ]
                    M = Model.query.get(value[0]['iddef_media_service'])
                    M.usuario_ultima_modificacion = user_name
                    M.estado = 1
                    aux['Datos_Actualizados'] = schemaP.dump(M)
                    
                    dataResponse.append(aux)
            db.session.commit()
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data":dataResponse
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
        



