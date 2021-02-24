from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_guarantee_deposit import PolicyGuaranteeDepositSchema as ModelSchema, PolicyGuaranteeDeposit as Model, GetPolicyGuaranteeDepositSchema as GetModelSchema
from models.policy_guarantee import PolicyGuarantee, GetPolicyGuaranteeSchema
from common.util import Util


class PolicyGuaranteeDeposit(Resource):
    #api-policy_guarantee_deposits-get-by-id
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

    #api-policy_guarantee_deposits-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
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
            if request.json.get("iddef_policy_rule") != None:
                model.iddef_policy_rule = data["iddef_policy_rule"]
            if request.json.get("percent") != None:
                model.percent = data["percent"]
            if request.json.get("option_percent") != None:
                model.option_percent = data["option_percent"]
            if request.json.get("number_nights_percent") != None:
                model.number_nights_percent = data["number_nights_percent"]
            if request.json.get("fixed_amount") != None:
                model.fixed_amount = data["fixed_amount"]
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


class PolicyGuaranteeDepositDelete(Resource):
    #api-policy_guarantee_deposits-delete
    # @base.access_middleware
    def put(self, id):
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


class PolicyGuaranteeDepositListSearch(Resource):
    #api-policy_guarantee_deposits-get-all
    # @base.access_middleware
    def get(self):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            data = Model.query.all()
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

    #api-policy_guarantee_deposits-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)           
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            #model.iddef_policy_guarantee_deposit = data["iddef_policy_guarantee_deposit"]
            model.iddef_policy_guarantee = data["iddef_policy_guarantee"]
            model.iddef_policy_rule = data["iddef_policy_rule"]
            model.percent = data["percent"]
            model.option_percent = data["option_percent"]
            model.number_nights_percent = data["number_nights_percent"]
            model.fixed_amount = data["fixed_amount"]
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
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }
        
        return response

class PolicyGuaranteeDepositByGuarantee(Resource):
    #api-policy_guarantee_deposits_by_guarantee-put
    # @base.access_middleware
    def put(self, iddef_policy_guarantee):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema_response = GetPolicyGuaranteeSchema(exclude=Util.get_default_excludes())
            schema = GetModelSchema(exclude=Util.get_default_excludes(), many=True)
            data = schema.load(json_data)
            model_guarantee = PolicyGuarantee.query.get(iddef_policy_guarantee)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
    
            if model_guarantee is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            # Nota: Los modelos nuevos se agregan fuera del loop debido a que al agregar un elemento nuevo
            # dentro del for se continuaba con el elemento agregado, generando un loop infinito 
            list_models_policy_guarantee_deposits = []
            list_iddef_policy_rules_request = []

            #Todos los elementos que lleguen en el request se ingresan como estado = 1, de otra forma se desactiva
            for policy_guarantee_deposit in data:
                list_iddef_policy_rules_request.append(policy_guarantee_deposit["iddef_policy_rule"])
                if(len(model_guarantee.policy_guarantee_deposits) == 0):
                    model = Model()
                    model.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                    model.percent = policy_guarantee_deposit["percent"]
                    model.option_percent = policy_guarantee_deposit["option_percent"]
                    model.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                    model.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                    model.estado = 1 #policy_guarantee_deposit["estado"]
                    model.usuario_creacion = user_name
                    list_models_policy_guarantee_deposits.append(model)

                for id_policy_guarantee_deposit, value_policy_guarantee_deposit in enumerate(model_guarantee.policy_guarantee_deposits):
                    iddef_policy_rule = int(policy_guarantee_deposit["iddef_policy_rule"])
                    count_policy_guarantee_deposit = len(Model.query.filter(Model.iddef_policy_guarantee==iddef_policy_guarantee, Model.iddef_policy_rule==iddef_policy_rule).all())
                    if(model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].iddef_policy_rule == iddef_policy_rule):
                        model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].percent = policy_guarantee_deposit["percent"]
                        model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].option_percent = policy_guarantee_deposit["option_percent"]
                        model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                        model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].fixed_amount = policy_guarantee_deposit["fixed_amount"]
                        model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].estado = 1 #policy_guarantee_deposit["estado"]
                        model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].usuario_ultima_modificacion = user_name
                    elif (count_policy_guarantee_deposit == 0):
                        model = Model()
                        model.iddef_policy_rule = policy_guarantee_deposit["iddef_policy_rule"]
                        model.percent = policy_guarantee_deposit["percent"]
                        model.option_percent = policy_guarantee_deposit["option_percent"]
                        model.number_nights_percent = policy_guarantee_deposit["number_nights_percent"]
                        model.fixed_amount = policy_guarantee_deposit["fixed_amount"]
                        model.estado = policy_guarantee_deposit["estado"]
                        model.usuario_creacion = user_name
                        list_models_policy_guarantee_deposits.append(model)
                        break

            #Se validan los elementos que se van a desactivar (Estos elementos no llegan en el request)
            for id_policy_guarantee_deposit, value_policy_guarantee_deposit in enumerate(model_guarantee.policy_guarantee_deposits):
                if(model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].iddef_policy_rule not in list_iddef_policy_rules_request):
                    model_guarantee.policy_guarantee_deposits[id_policy_guarantee_deposit].estado = 0

            for temp_policy_guarantee_deposit in list_models_policy_guarantee_deposits:
                model_guarantee.policy_guarantee_deposits.append(temp_policy_guarantee_deposit)

            db.session.commit()

            result = schema_response.dump(model_guarantee)
            list_result = list(filter(lambda elem_policy_guarantee_deposit: elem_policy_guarantee_deposit["estado"] == 1, result["policy_guarantee_deposits"]))

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": list_result
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
