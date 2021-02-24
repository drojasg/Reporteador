from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
import json
from config import db, base
from models.media_group import MediaGroupSchema as ModelSchema, GetMediaGroupSchema as GetModelSchema, MediaGroup as Model, UpdateMediaGroupStatusGallery
from models.media import Media as MediaModel, MediaSchema as MediaModelSchema, GetListMediaSchemaGallery
from common.util import Util
from sqlalchemy import func


class MediaGroup(Resource):
    #api-media-group-get-by-id
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

    #api-media-group-put
    @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.json
            schema = GetModelSchema(exclude=Util.get_default_excludes())
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

            if request.json.get("description") != None:
                model.description = data["description"]
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

    #api-media-group-delete
    @base.access_middleware
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

    #api-media-group-post
    @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.json
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()

            model.description = data["description"]
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

class MediaGroupListSearch(Resource):
    #api-media-group-get-all
    @base.access_middleware
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

class MediaGroupGalleryListSearch(Resource):
    #api-media-group-get-all-gallery
    @base.access_middleware
    def get(self, id):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)

            dataGroups = schema.dump(data)
            
            dataResponse = []

            for Groups in dataGroups:
                aux = {}


                aux["iduser_gallery"] = Groups["iddef_media_group"]
                aux["type"] = id
                aux["name"] = Groups["description"]
                aux["description"] = Groups["description"]
                aux["estado"] = Groups["estado"]

                dataResponse.append(aux)

            if dataResponse is None:
                response = {
                    "status": "Ok",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": {}
                }
            else:
                response = {
                    "status": "Ok",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": dataResponse
                }
        except Exception as e:
            response = {
                "status": "NOT FOUND",
                "Code": 404,
                "Message": str(e),
                "error": True,
                "data": {}
            }

        return response

class MediaGroupGalleryCountSearch(Resource):
    #api-media-group-get-count-group
    @base.access_middleware
    def get(self, id):
        try:
            mediaGroupCount = db.session.query(func.count(MediaModel.iddef_media_group).label("total"))\
            .filter(MediaModel.iddef_media_group == id)

            mediaSchema = GetListMediaSchemaGallery(exclude=Util.get_default_excludes(), many=True)
            mediaData = mediaSchema.dump(mediaGroupCount)

            if mediaData is None:
                response = {
                    "status":"Ok",
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                response = {
                    "status":"Ok",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": mediaData
                }
        except Exception as e:
            response = {
                "status":"NOT FOUND",
                "code": 404,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class  MediaGroupGalleryAssetsSearch(Resource):
    #api-media-group-get-all-media-by-group
    @base.access_middleware
    def get(self,idGroup,Nlimit, Noffset):
        try:
            Type = request.args.get("type")

            if Type is not None:
                #rint('si')
                mediaInfoByGroup = MediaModel.query\
                    .filter(MediaModel.iddef_media_type == Type)

            else:
                mediaInfoByGroup = MediaModel.query\
                    .filter(MediaModel.iddef_media_group == idGroup, MediaModel.estado == 1, MediaModel.iddef_media_type == 1).offset(Noffset).limit(Nlimit)

            mediaSchema = MediaModelSchema(exclude=Util.get_default_excludes(), many=True)

            mediaInfo = mediaSchema.dump(mediaInfoByGroup)
            
            dataResponse = []

            for media in mediaInfo:
                
                aux={}
                aux["idasset_user_gallery"] = media["iddef_media_group"]
                aux["idfrm_sistema"] = base.system_id
                aux["id_asset_gallery"] = media["iddef_media"]
                aux["descripcion"] = media["description"]
                aux["nombre_bucket"] = media["nombre_bucket"]
                aux["nombre_archivo"] = media["url"].replace("https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/images/", "")
                aux["publico"] = media["bucket_type"]
                aux["idasset_type"] = media["iddef_media_type"]
                aux["etag"] = media["etag"]
                aux["url"] = media["url"]
                aux["estado"] = media["estado"]
                aux["tags"] = media["tags"]["tags"]
                aux["name"] = media["name"]

                dataResponse.append(aux)

            if dataResponse is None:
                response = {
                    "status": "OK",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": {}
                }
            else:
                response = {
                    "status":"Ok",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": dataResponse
                }
        except Exception as e:
            response = {
                "status":"Ok",
                "code": 500,
                "Message": str(e),
                "error": True,
                "data": {}
            }

        return response

    #api-media-group-update-status
    @base.access_middleware
    def put(self,id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = UpdateMediaGroupStatusGallery()
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

        
            if model is None:
                response = {
                    "status": "OK",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": {}
                }
            else:
                response = {
                    "status":"Ok",
                    "code": 200,
                    "Message": "Success",
                    "error": False,
                    "data": schema.dump(model)
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

class MediaGeneralSearch(Resource):
    #get from media group = 0 
    @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            data = MediaModel()
            data = db.session.query(MediaModel).\
                                join(Model, MediaModel.iddef_media_group == Model.iddef_media_group)\
                                .filter(Model.iddef_property == json_data["idproperty"])\
                                .filter(MediaModel.iddef_media_type ==  json_data["type"] )\
                                .filter(MediaModel.name.like("%"+json_data["search"]+"%" )).all() 

            schema = MediaModelSchema(exclude=Util.get_default_excludes(), many=True)
            datos = schema.dump(data)
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": datos
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response