from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.media_property import MediaPropertySchema as ModelSchema, GetMediaPropertySchema as GetModelSchema, GetListMediaPropertySchema as GetListModelSchema, MediaProperty as Model, GetMediaPropertyAdminSchema, PostMediaPropertySchema, UpdateOrderSchema
from models.media import Media as MedModel
from models.media_group import MediaGroup as MedGruModel
from models.media_type import MediaType as MedTypModel
from common.util import Util
from sqlalchemy.sql.expression import and_
from sqlalchemy import func
from common.public_auth import PublicAuth

class MediaProperty(Resource):
    #api-media-property-get-by-id
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

    #api-media-property-put
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

            if request.json.get("iddef_property") != None:
                model.iddef_property = data["iddef_property"]
            if request.json.get("iddef_media") != None:
                model.iddef_media = data["iddef_media"]
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

    #api-media-property-delete
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

    #api-media-property-post
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

            model.iddef_property = data["iddef_property"]
            model.iddef_media = data["iddef_media"]
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

class MediaPropertyListSearch(Resource):
    #api-media-property-get-all
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


class MediaPropertyListOrder(Resource):
    
    #api-media-property-update-media
    # @base.access_middleware
    def put(self):
        response =  {}
        try:
            json_data = request.get_json(force=True)
            OrderSchema = UpdateOrderSchema(exclude=Util.get_default_excludes())
            dataResponse = []
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            for item in json_data:
                aux = {}
                data = OrderSchema.load(item)
                M = Model.query.get(item['iddef_media_property'])
                M.iddef_media_property = item["iddef_media_property"]
                M.order = item["order"]
                M.usuario_ultima_modificacion = user_name
                aux['Datos_Actualizados'] = OrderSchema.dump(M)
                dataResponse.append(aux)
                db.session.flush()

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

    #api-media-room-seach-order-by-roomtype
    # @base.access_middleware
    def get(self, idProperty):
        try:
            schema = GetMediaPropertyAdminSchema(many=True)
            
            data = MedModel.query.with_entities(\
            MedModel.url)\
            .add_columns(func.IF(Model.estado == None, 0,1).label("selected"), Model.order.label("order"), Model.iddef_media_property) \
            .join(MedGruModel,and_(MedGruModel.iddef_media_group == MedModel.iddef_media_group))\
            .outerjoin(Model,and_(Model.iddef_media == MedModel.iddef_media, Model.estado == 1, Model.iddef_property == idProperty))\
            .filter(and_(MedModel.estado == 1, MedGruModel.estado == 1, MedModel.iddef_media_type == 1, Model.estado == 1))

            mediaRoomJson = schema.dump(data)
            
            response={
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": mediaRoomJson
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

    


class PublicMediaProperty(Resource):
    #api-public-media-property-get-by-id
    #Publica
    @PublicAuth.access_middleware
    def get(self, id):
        try:
            schema = GetListModelSchema(exclude=Util.get_default_excludes())
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

class PublicMediaPropertyList(Resource):
    #api-public-media-property-get-list
    #Publica
    @PublicAuth.access_middleware
    def get(self, id):
        try:
            schema = GetListModelSchema(exclude=Util.get_default_excludes())
            if id != None:
                data = Model.query.join(MedModel).join(MedGruModel).join(MedTypModel).filter(Model.iddef_property == id, MedGruModel.description == "Propiedad", MedTypModel.description == "Image").all()
                
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
                    "data": schema.dump(data,many=True)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class AdminMediaPropertyList(Resource):
    #api-media-property-get-list
    #api get administrativa
    # @base.access_middleware
    def get(self, idProperty, idDefMediaType):
        response={}

        try:
            #inicializamos el schema
            schema = GetMediaPropertyAdminSchema(many=True)
            conditions = [MedModel.estado == 1, MedGruModel.iddef_property == idProperty]
            
            if idDefMediaType != 0:
                conditions.append(MedModel.iddef_media_type == idDefMediaType)
            
            data = MedModel.query.with_entities(\
            MedModel.description, \
            MedModel.iddef_media, MedModel.name, MedModel.tags,\
            MedModel.url).add_columns(func.IF(Model.estado == None, 0,1).label("selected"), Model.order \
            ).outerjoin(Model,and_(Model.iddef_media == MedModel.iddef_media,\
            Model.estado == 1, Model.iddef_property == idProperty, \
            )).outerjoin(MedGruModel, and_(MedGruModel.iddef_media_group ==MedModel.iddef_media_group)).\
            filter(and_(*conditions))

            mediaPropertyDataJson = schema.dump(data)

            response={
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": mediaPropertyDataJson
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
        
    #api-media-property-post-and-put
    # @base.access_middleware
    def post(self):
        
        response = {}
        try: 
            json_data = request.get_json(force=True)
            schema  = ModelSchema(exclude=Util.get_default_excludes())
            postSchema = PostMediaPropertySchema(exclude=Util.get_default_excludes())
            data = postSchema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []
            
            data_media_prop = Model.query.filter(Model.iddef_property == data['iddef_property'])
            mediaPropertyDataJson = schema.dump(data_media_prop, many=True)

            
            for x in mediaPropertyDataJson:
                M = Model.query.get(x['iddef_media_property'])
                M.estado = 0
                
            for media_id in data["medias_id"]:
            
                if media_id['iddef_media'] not in [ x["iddef_media"] for x in mediaPropertyDataJson ]:
                    aux = {}
                    model = Model()
                    model.iddef_property = data['iddef_property']
                    model.iddef_media = media_id['iddef_media']
                    model.order = media_id['order']                    
                    model.estado = 1
                    model.usuario_creacion = user_name
                    db.session.add(model)
                    db.session.flush()
                    aux['Datos_Insertados'] = schema.dump(model)
                    dataResponse.append(aux)    
                else:
                    aux = {}
                    value =  [x for x in mediaPropertyDataJson \
                    if x["iddef_media"] == media_id["iddef_media"] \
                    and x["iddef_property"] == data["iddef_property"] \
                    ]
                    M = Model.query.get(value[0]['iddef_media_property'])
                    M.usuario_ultima_modificacion = user_name
                    M.estado = 1
                    aux['Datos_Actualizados'] = schema.dump(M)
                    value[0]
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

