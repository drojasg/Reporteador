from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

import json

from config import db, base
from models.media import MediaSchema as ModelSchema, GetMediaSchema as GetModelSchema, GetListMediaSchema as GetListModelSchema, Media as Model, UpdateMediaStatusGallery
from common.util import Util


class Media(Resource):
    #api-media-get-by-id
    # @base.access_middleware
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

    #api-media-put
    # @base.access_middleware
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

            if request.json.get("iddef_media_type") != None:
                model.iddef_media_type = data["iddef_media_type"]
            if request.json.get("iddef_media_group") != None:
                model.iddef_media_group = data["iddef_media_group"]
            if request.json.get("url") != None:
                model.url = data["url"]
            if request.json.get("name") != None:
                model.name = data["name"]
            if request.json.get("description") != None:
                model.description = data["description"]
            if request.json.get("show_icon") != None:
                model.show_icon = data["show_icon"]
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

    #api-media-delete
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

    #api-media-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)

            if isinstance(json_data["tags"], str):
                json_data["tags"] = json.loads(request.json["tags"])
            else:
                json_data["tags"] = json_data["tags"]

            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            model.iddef_media_type = data["iddef_media_type"]
            model.iddef_media_group = data["iddef_media_group"]
            model.url = data["url"]
            model.name = data["name"]
            model.description = data["description"]
            model.nombre_bucket = data["nombre_bucket"]
            model.bucket_type = data["bucket_type"]
            model.etag = data["etag"]
            model.show_icon = data["show_icon"]
            model.tags = data["tags"]
            model.estado = data["estado"]
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

class MediaListSearch(Resource):
    #api-media-get-all
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

class MediaGalleryList(Resource):
    #api-media-update-status
    # @base.access_middleware
    def put(self,id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = UpdateMediaStatusGallery()
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
            #data["usuario_ultima_modificacion"]

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

    #return response

class MediaUpdateUrl(Resource):
    # @base.access_middleware
    def put(self,id):
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
            model.url = data["url"]
            model.name = data["name"]
            model.etag = data["etag"]
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