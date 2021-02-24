from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

import json
from config import db, base
from models.media import Media as MedModel
from models.room_type_category import RoomTypeCategory
from models.media_room import MediaRoom as Model, MediaRoomSchema as ModelSchema, GetMediaRoomAdminSchema, PostMediaRoomSchema, UpdateOrderSchema
from models.media_group import MediaGroup as MGroupModel
from common.util import Util
from sqlalchemy.sql.expression import and_
from sqlalchemy import func

class AdminMediaRoomList(Resource):
    #api-media-room-get-by-roomtype
    # @base.access_middleware
    def get(self, idRoomType, idProperty):
        try:
            schema = GetMediaRoomAdminSchema(many=True)
            
            data = MedModel.query.with_entities(\
            MedModel.description, \
            MedModel.iddef_media, MedModel.name, MedModel.tags,\
            MedModel.url)\
            .add_columns(func.IF(Model.estado == None, 0,1).label("selected"), MedModel.iddef_media_type ,Model.order) \
            .join(MGroupModel,and_(MGroupModel.iddef_media_group == MedModel.iddef_media_group))\
            .outerjoin(Model,and_(Model.iddef_media == MedModel.iddef_media, Model.estado == 1, Model.iddef_room_type_category == idRoomType))\
            .filter(and_(MedModel.estado == 1, MGroupModel.estado == 1, MGroupModel.iddef_property == idProperty)).all()            

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
        
    #api-media-room-post-and-put
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema  = ModelSchema(exclude=Util.get_default_excludes())
            postSchema = PostMediaRoomSchema(exclude=Util.get_default_excludes())
            data = postSchema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []
            
            data_media_room = Model.query.filter(Model.iddef_room_type_category == data['iddef_room_type_category'])
            mediaRoomDataJson = schema.dump(data_media_room, many=True)
                        
            for x in mediaRoomDataJson:
                M = Model.query.get(x['iddef_media_room'])
                M.estado = 0
                
            for media_id in data["medias_id"]:
                if media_id["iddef_media"] not in [x["iddef_media"] for x in mediaRoomDataJson  ]:
                    aux = {}
                    model = Model()
                    model.iddef_room_type_category = data['iddef_room_type_category']
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
                    schemaP  = ModelSchema(exclude=Util.get_default_excludes())
                    value =  [x for x in mediaRoomDataJson \
                    if x["iddef_media"] == media_id["iddef_media"] \
                    and x["iddef_room_type_category"] == data["iddef_room_type_category"] \
                    ]
                    M = Model.query.get(value[0]['iddef_media_room'])
                    M.usuario_ultima_modificacion = user_name
                    M.estado = 1
                    aux['Datos_Actualizados'] = schemaP.dump(M)
                    #value[0]
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

class AdminMediaRoomListOrder(Resource):
    #api-media-room-update-media
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
                M = Model.query.get(item['iddef_media_room'])
                M.iddef_media_room = item["iddef_media_room"]
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
    def get(self, idRoomType, idMediaType):
        try:
            schema = GetMediaRoomAdminSchema(many=True)
            
            data = MedModel.query.with_entities(\
            MedModel.url)\
            .add_columns(func.IF(Model.estado == None, 0,1).label("selected"), Model.order.label("order"), Model.iddef_media_room) \
            .join(MGroupModel,and_(MGroupModel.iddef_media_group == MedModel.iddef_media_group))\
            .outerjoin(Model,and_(Model.iddef_media == MedModel.iddef_media, Model.estado == 1, Model.iddef_room_type_category == idRoomType))\
            .filter(and_(MedModel.estado == 1, MGroupModel.estado == 1, Model.iddef_room_type_category == idRoomType, MedModel.iddef_media_type == idMediaType))

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