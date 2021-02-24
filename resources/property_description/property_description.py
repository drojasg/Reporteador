from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.property_description import PropertyDescriptionSchema as ModelSchema, PropertyDescriptionRefSchema as ModelRefSchema, PropertyDescription as Model
from models.property import PropertySchema as PropModelSchema, Property as PropModel
from common.util import Util

class PropertyDescription(Resource):

    #api-property-description-get-by
    def get(self,id):
        pass

    #api-property-description-post
    def post(self):
        pass

    #api-property-description-put
    # @base.access_middleware
    def put(self,id):

        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(data)
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                model = Model()

                dataUpdate = model.query.filter_by(iddef_property_description=id).first()

                #dataUpdate.iddef_description_type = data["iddef_description_type"]
                #dataUpdate.iddef_property = data["iddef_property"]
                #dataUpdate.lang_code = data["lang_code"]
                dataUpdate.title = data["title"]
                dataUpdate.description = data["description"]
                #dataUpdate.estado = data["estado"]
                #dataUpdate.fecha_creacion = data["fecha_creacion"]
                dataUpdate.usuario_ultima_modificacion = user_name
                #dataUpdate.fecha_ultima_modificacion = data["fecha_ultima_modificacion"]

                db.session.commit()

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataUpdate,many=True)
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
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response

    #api-property-description-delete
    # @base.access_middleware
    def delete(self,id):

        response = {}

        try:
            #data = request.json
            schema = ModelSchema(exclude=Util.get_default_excludes())
            #data = schema.load(data)
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataUpdate = model.query.filter_by(iddef_property_description=id).first()

            #dataUpdate.iddef_description_type = data["iddef_description_type"]
            #dataUpdate.iddef_property = data["iddef_property"]
            #dataUpdate.lang_code = data["lang_code"]
            #dataUpdate.title = data["title"]
            #dataUpdate.description = data["description"]
            dataUpdate.estado = 0
            #model.fecha_creacion = data["fecha_creacion"]
            model.usuario_ultima_modificacion = user_name
            #model.fecha_ultima_modificacion = data["fecha_ultima_modificacion"]

            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(dataUpdate)
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

class PropertyDescriptionList(Resource):

    #api-property-description-get-by-params
    # @base.access_middleware
    def get(self,hotelcode,type):

        response = {}

        try:
            #Inicializamos el schema
            schema = ModelSchema(exclude=Util.get_default_excludes())

            #Obtenemos los datos de la tabla property
            PropertyData = PropModel.query.filter_by(property_code=hotelcode, estado=1).first()

            if PropertyData != None:

                #Obtenemos los datos de la tabla property_description
                datos = Model.query.filter_by(iddef_property=PropertyData.iddef_property, iddef_description_type=type, estado=1)
                #Trackrace

                #Se construye el response
                response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": schema.dump(datos, many=True)
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

    #api-property-description-post-list
    # @base.access_middleware
    def post(self):

        response = {}

        if request.is_json:
            try:
                data = request.json
                schema = ModelSchema(exclude=Util.get_default_excludes())
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                dataResponse = []

                for dataRequest in data["data"]:
                    data = schema.load(dataRequest)
                    model = Model()

                    model.iddef_description_type = dataRequest["iddef_description_type"]
                    model.iddef_property = dataRequest["iddef_property"]
                    model.lang_code = dataRequest["lang_code"]
                    model.title = dataRequest["title"]
                    model.description = dataRequest["description"]
                    model.estado = dataRequest["estado"]
                    model.usuario_creacion = user_name
                    #model.fecha_creacion = data["fecha_creacion"]
                    #model.fecha_ultima_modificacion = data["fecha_ultima_modificacion"]

                    db.session.add(model)
                    dataResponse.append(model)

                db.session.commit()

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataResponse,many=True)
                }

            except ValidationError as Error:
                db.session.rollback()
                response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
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
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST"
            }

        return response

    #api-property-description-put-list
    # @base.access_middleware
    def put(self):
        response = {}
        if request.is_json:
            try:
                data = request.json
                schema = ModelRefSchema(exclude=Util.get_default_excludes())
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                dataResponse = []

                for toUpdate in data["data"]:
                    data = schema.load(toUpdate)
                    model = Model()

                    dataUpdate = model.query.filter_by(iddef_property_description=toUpdate["iddef_property_description"]).first()

                    if dataUpdate == None:
                        raise Exception("The property description %s doesn't exists" % model.iddef_property_description)

                    #dataUpdate.iddef_description_type = data["iddef_description_type"]
                    #dataUpdate.iddef_property = data["iddef_property"]
                    #dataUpdate.lang_code = data["lang_code"]
                    dataUpdate.title = toUpdate["title"]
                    dataUpdate.description = toUpdate["description"]
                    #dataUpdate.estado = data["estado"]
                    #dataUpdate.fecha_creacion = data["fecha_creacion"]
                    dataUpdate.usuario_ultima_modificacion = user_name
                    #dataUpdate.fecha_ultima_modificacion = data["fecha_ultima_modificacion"]

                    db.session.commit()

                    dataResponse.append(dataUpdate)

                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dataResponse,many=True)
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
        else:
            response = {
                "Code":500,
                "Msg":"INVALID REQUEST",
                "Error":True,
                "data": {}
            }

        return response

class PropertyDescriptionListSearch(Resource):
    def get(self):
        pass
