from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db,base
from models.service_pricing_type import ServicePricingTypeSchema as ModelSchema, GetServicePricingTypeSchema as GetModelSchema, ServicePricingType as Model
from models.service_pricing_option import ServicePricingOptionSchema as SPOModelSchema, ServicePricingOption as SPOModel
from common.util import Util


class ServicePricingType(Resource):
    #api-service-pricing-type-get-by-id
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

    #api-service-pricing-type-put
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

    #api-service-pricing-type-delete
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

    #api-service-pricing-type-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            if request.json.get("iddef_service_pricing_type") == None:
                schema = GetModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
                model = Model()

                user_data = base.get_token_data()
                user_name = user_data['user']['username']                

                model.description = data["description"]
                model.estado = 1
                model.usuario_creacion = user_name
                db.session.add(model)
                db.session.commit()
                
                for option in data["options"]:
                    model_options = SPOModel()
                    if request.json.get("name") != None:
                        model_options.name = ""
                    model_options.formula = ""
                    model_options.params = []
                    model_options.price = 0.00
                    model_options.estado = 1
                    model_options.usuario_creacion = user_name
                    db.session.add(model_options)
                    db.session.commit()
            else:
                schema = GetModelSchema(exclude=Util.get_default_excludes())
                schemaSPO = SPOModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
                model = Model.query.get(json_data["iddef_service_pricing_type"])

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

                if model.iddef_service_pricing_type != None: #
                    data_options = SPOModel.query.filter_by(iddef_pricing_type=json_data["iddef_service_pricing_type"]).all()
                    dataOptions = schemaSPO.dump(data_options, many=True)
                    if dataOptions != None:
                        for y in dataOptions:
                            O = SPOModel.query.get(y['iddef_service_pricing_option'])
                            O.estado = 0
                            db.session.commit()

                    for option in data["options"]:
                        data_options = SPOModel.query.filter_by(iddef_service_pricing_option=option).first()
                        if data_options is None:
                            model_options = SPOModel()
                            model_options.iddef_pricing_type = json_data["iddef_service_pricing_type"]
                            model_options.name = ""
                            model_options.formula = ""
                            model_options.params = []
                            model_options.price = 0.00
                            model_options.estado = 1
                            model_options.usuario_creacion = user_name
                            db.session.add(model_options)
                            db.session.commit()
                        else:
                            data_options.iddef_pricing_type = json_data["iddef_service_pricing_type"]
                            if request.json.get("name") != None:
                                data_options.name = ""
                            data_options.formula = ""
                            data_options.params = []
                            data_options.price = 0.00
                            data_options.estado = 1
                            data_options.usuario_ultima_modificacion = user_name
                            db.session.commit()
            schema = GetModelSchema(exclude=Util.get_default_excludes())
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

class ServicePricingTypeListSearch(Resource):
    #api-service-pricing-type-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            schema2 = SPOModelSchema(only=('iddef_service_pricing_option','name','estado',))
            #schema2 = SPOModelSchema(exclude=Util.get_default_excludes(), many=True)
            result = []
            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)
                dataPricingType = schema.dump(data, many=True)
                for itemType in dataPricingType:
                    dataOption = SPOModel.query.filter_by(iddef_pricing_type=itemType['iddef_service_pricing_type']).all()
                    if dataOption is None:
                        resultOption = []
                    else:
                        dataPricingOption = schema2.dump(dataOption, many=True)
                        itemType['options'] = dataPricingOption
                    result.append(itemType)
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
                    "data": result
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response