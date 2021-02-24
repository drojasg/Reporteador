from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.sql import alias

import json
from config import db, base
from models.media_property_desc import MediaPropertyDescSchema as ModelSchema, MediaPropertyDesc as Model, GetMediaPropertyDescSchema, PostMediaPropertyDescSchema
from models.media import MediaSchema as MediaModelSchema, GetMediaSchema as GetModelSchema, GetListMediaSchema as GetListModelSchema, Media as MediaModel
from models.media_group import MediaGroup as MGroupModel
from models.property_description import PropertyDescription
from models.property import Property
from common.util import Util
from sqlalchemy.sql.expression import and_
from sqlalchemy import func

class MediaPropertyDescListSearch(Resource):
    #api-media-get-all-by-property
    # @base.access_middleware
    def get(self, idProperty, idDescType, idDefMediaType):
        
        response = {}

        try:
            schema = GetMediaPropertyDescSchema(exclude=Util.get_default_excludes(), many=True)
            conditions = [MediaModel.estado == 1, MGroupModel.iddef_property == idProperty]

            if idDefMediaType != 0:
                conditions.append(MediaModel.iddef_media_type == idDefMediaType)

            data = MediaModel.query.with_entities(Model.iddef_description_type,\
            MediaModel.description, Model.iddef_media_property_desc, \
            MediaModel.iddef_media, MediaModel.name, MediaModel.tags,\
            MediaModel.url).add_columns(func.IF(Model.estado == None, 0,1).label("selected") \
            ).outerjoin(Model,and_(Model.iddef_media == MediaModel.iddef_media,\
            Model.estado == 1, Model.iddef_description_type == idDescType, \
            Model.iddef_property == idProperty )) \
            .outerjoin(MGroupModel,and_(MGroupModel.iddef_media_group == MediaModel.iddef_media_group)).\
            filter(and_(*conditions))

            mediaPropertyDataJson = schema.dump(data)
        
            response = {
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

    #api-media-property-desc-post-and-put
    # @base.access_middleware
    def post(self):
        response = {}
        try: 
            json_data = request.get_json(force=True)
            schema  = ModelSchema(exclude=Util.get_default_excludes())
            getSchema = GetMediaPropertyDescSchema(exclude=Util.get_default_excludes(), many=True)
            postSchema = PostMediaPropertyDescSchema(exclude=Util.get_default_excludes())
            data = postSchema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []    

            #select simple
            #preguntar si no es mejor traer solo los seleccionados con estado = 1
            data_media_desc = Model.query.filter(Model.iddef_property == data['iddef_property'], Model.iddef_description_type == data['iddef_description_type'])
            mediaPropertyDataJson = schema.dump(data_media_desc, many=True)

            for x in mediaPropertyDataJson:
                #print (x)
                M = Model.query.get(x['iddef_media_property_desc'])
                M.estado = 0

            for media_id in data["medias_id"]:
                if media_id not in [ x["iddef_media"] for x in mediaPropertyDataJson ]:
                    #Inserta en esta tabla
                    aux = {}
                    model = Model()
                    model.iddef_property = data['iddef_property']
                    model.iddef_description_type = data['iddef_description_type']
                    model.iddef_media = media_id
                    model.estado = 1
                    model.usuario_creacion = user_name
                    db.session.add(model)
                    db.session.flush()
                    aux['Datos_Insertados'] = schema.dump(model)
                    dataResponse.append(aux)


                else:
                    #Actualiza el registro que esta en data_media_desc
                    aux = {}
                    value =  [x for x in mediaPropertyDataJson \
                    if x["iddef_media"] == media_id \
                    and x["iddef_property"] == data["iddef_property"] \
                    and x["iddef_description_type"]== data["iddef_description_type"] ]
                    M = Model.query.get(value[0]['iddef_media_property_desc'])
                    M.estado = 1
                    M.usuario_ultima_modificacion = user_name
                    aux['Datos_Actualizados'] = schema.dump(M)
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