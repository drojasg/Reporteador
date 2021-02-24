from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.channel import ChannelSchema as ModelSchema, Channel as Model, ChannelTableSchema
from models.channel_type import ChannelTypeSchema as ModelChannelTypeSchema, ChannelType as ModelChannelType
from models.sistemas import Sistemas, SistemasSchema
from common.util import Util
from sqlalchemy.sql.expression import and_


class Channel(Resource):
    # api-Channel-get-by-id
    def get(self, id):

        response = {}

        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
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

    # api-channel-post
    def post(self):

        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                schema.load(data)
                user_data = base.get_token_data()
                user_name = user_data['user']['username']

                model = Model()

                model.name = data["name"]
                model.description = data["description"]
                model.iddef_channel_type = data["iddef_channel_type"]
                model.idop_sistemas = data["idop_sistemas"]
                model.external_id = data["external_id"]
                model.url = data["url"]
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

            except ValidationError as Error:
                db.session.rollback()
                response = {
                    "Code": 500,
                    "Msg": Error.messages,
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
        else:
            response = {
                "Code": 500,
                "Msg": "INVALID REQUEST"
            }

        return response

    # api-channel-put
    def put(self, id):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                model = Model()
                user_data = base.get_token_data()
                user_name = user_data['user']['username']

                dataUpdate = model.query.filter_by(iddef_channel=id).first()

                dataUpdate.name = data["name"]
                dataUpdate.description = data["description"]
                dataUpdate.iddef_channel_type = data["iddef_channel_type"]
                dataUpdate.idop_sistemas = data["idop_sistemas"]
                dataUpdate.url = data["url"]
                dataUpdate.estado = data["estado"]
                dataUpdate.external_id = data["external_id"]
                dataUpdate.usuario_ultima_modificacion = user_name

                db.session.commit()

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataUpdate)
                }

            except ValidationError as Error:
                response = {
                    "Code": 500,
                    "Msg": Error.messages,
                    "Error": True,
                    "data": {}
                }
            except Exception as e:
                response = {
                    "Code": 500,
                    "Msg": str(e),
                    "Error": True,
                    "data": {}
                }
        else:
            response = {
                "Code": 500,
                "Msg": "INVALID REQUEST",
                "Error": True,
                "data": {}
            }

        return response

    # api-channel-delete
    def delete(self, id):
        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                model = Model()
                user_data = base.get_token_data()
                user_name = user_data['user']['username']

                dataUpdate = model.query.filter_by(iddef_currency=id).first()
                dataUpdate.estado = 0
                dataUpdate.usuario_ultima_modificacion = user_name

                db.session.commit()

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataUpdate)
                }

            except ValidationError as Error:
                response = {
                    "Code": 500,
                    "Msg": Error.messages,
                    "Error": True,
                    "data": {}
                }
            except Exception as e:
                response = {
                    "Code": 500,
                    "Msg": str(e),
                    "Error": True,
                    "data": {}
                }
        else:
            response = {
                "Code": 500,
                "Msg": "INVALID REQUEST",
                "Error": True,
                "data": {}
            }

        return response


class ChannelListSearch(Resource):
    # api-channels-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado == 1)

            schema = ModelSchema(
                exclude=Util.get_default_excludes(), many=True)

            dataDumpChannel = schema.dump(data)

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


class channelsSearchTable(Resource):

    # @base.access_middleware
    def get(self):
        try:
            data = Model()

            data = Model.query.join(ModelChannelType, and_(Model.iddef_channel_type == ModelChannelType.iddef_channel_type))\
                .join(Sistemas, and_(Model.idop_sistemas == Sistemas.idop_sistemas))\
                .add_columns(Model.idop_sistemas, Model.estado, Model.iddef_channel, Model.name, Model.description, Model.external_id, Model.iddef_channel_type,
                             (Sistemas.nombre).label("nombre_sistema"), (ModelChannelType.name).label("name_channel_type"), Model.url).all()

            schema = ChannelTableSchema(
                exclude=Util.get_default_excludes(), many=True)

            dataDumpChannel = schema.dump(data)

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
                    "data": dataDumpChannel
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    # api-config-brand-delete-status
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
