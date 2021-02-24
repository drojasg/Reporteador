from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_penalty_cancel_fee import PolicyPenaltyCancelFeeSchema as ModelSchema, PolicyPenaltyCancelFee as Model, GetPolicyPenaltyCancelFeeSchema as GetModelSchema
from models.policy_cancel_penalty import PolicyCancelPenaltySchema, PolicyCancelPenalty, GetPolicyCancelPenaltySchema
from common.util import Util


class PolicyPenaltyCancelFee(Resource):
    #api-policy_penalty_cancel_fees-get-by-id
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

    #api-policy_penalty_cancel_fees-post
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
            
            model.iddef_policy_cancel_penalty = data["iddef_policy_cancel_penalty"]
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

    #api-policy_penalty_cancel_fees-put
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

    # def delete(self, id):
    #   response = {}
    #   try:
    #       schema = ModelSchema(exclude=Util.get_default_excludes())
    #       model = Model.query.get(id)

    #       user_data = base.get_token_data()
    #       user_name = user_data['user']['username']

    #       if model is None:
    #           return {
    #               "Code": 404,
    #               "Msg": "data not found",
    #               "Error": True,
    #               "data": {}
    #           }

    #       model.estado = 0
    #       model.usuario_ultima_modificacion = user_name
    #       db.session.commit()

    #       response = {
    #           "Code": 200,
    #           "Msg": "Success",
    #           "Error": False,
    #           "data": schema.dump(model)
    #       }
    #   except ValidationError as error:
    #       response = {
    #           "Code": 500,
    #           "Msg": error.messages,
    #           "Error": True,
    #           "data": {}
    #       }
    #   except Exception as e:
    #       db.session.rollback()
    #       response = {
    #           "Code": 500,
    #           "Msg": str(e),
    #           "Error": True,
    #           "data": {}
    #       }

    #   return response


class PolicyPenaltyCancelFeeListSearch(Resource):
    #api-policy_penalty_cancel_fees-get-all
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

class PolicyPenaltyCancelFeeDefault(Resource):
    # @base.access_middleware
    def get(self, id_policy_cancel_penalty):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter(Model.iddef_policy_cancel_penalty==id_policy_cancel_penalty).all()

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
                    "data": schema.dump(data, many=True)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class PolicyPenaltyCancelFeeList(Resource):
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = PolicyCancelPenaltySchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = PolicyCancelPenalty.query.get(request.json.get("iddef_policy_cancel_penalty", 0))

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
    
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            for cancel_fee in policy_cancel_penalty["cancel_fees"]:
                model_cancel_fee = PolicyPenaltyCancelFee()
                model_cancel_fee.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                model_cancel_fee.percent = cancel_fee["percent"]
                model_cancel_fee.option_percent = cancel_fee["option_percent"]
                model_cancel_fee.number_nights_percent = cancel_fee["number_nights_percent"]
                model_cancel_fee.fixed_amount = cancel_fee["fixed_amount"]
                model_cancel_fee.estado = 1
                model_cancel_fee.usuario_creacion = user_name

                model.cancel_fees.append(model_cancel_fee)

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

class PolicyPenaltyCancelFeeByCancelPenalty(Resource):
    #api-policy_cancel_fees_by_cancel_penalty-put
    # @base.access_middleware
    def put(self, iddef_policy_cancel_penalty):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema_response = GetPolicyCancelPenaltySchema(exclude=Util.get_default_excludes())
            schema = GetModelSchema(exclude=Util.get_default_excludes(), many=True)
            data = schema.load(json_data)
            model_cancel_penalty = PolicyCancelPenalty.query.get(iddef_policy_cancel_penalty)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']
    
            if model_cancel_penalty is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            # Nota: Los modelos nuevos se agregan fuera del loop debido a que al agregar un elemento nuevo
            # dentro del for se continuaba con el elemento agregado, generando un loop infinito 
            list_models_cancel_fees = []
            list_iddef_policy_cancel_penalty_request = []

            #Todos los elementos que lleguen en el request se ingresan como estado = 1, de otra forma se desactiva
            for cancel_fee in data:
                list_iddef_policy_cancel_penalty_request.append(cancel_fee["iddef_policy_rule"])
                if(len(model_cancel_penalty.cancel_fees) == 0):
                    model = Model()
                    model.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                    model.percent = cancel_fee["percent"]
                    model.option_percent = cancel_fee["option_percent"]
                    model.number_nights_percent = cancel_fee["number_nights_percent"]
                    model.fixed_amount = cancel_fee["fixed_amount"]
                    model.estado = 1 #cancel_fee["estado"]
                    model.usuario_creacion = user_name
                    list_models_cancel_fees.append(model)

                for id_cancel_fee, value_cancel_fee in enumerate(model_cancel_penalty.cancel_fees):
                    iddef_policy_rule = int(cancel_fee["iddef_policy_rule"])
                    count_cancel_fee = len(Model.query.filter(Model.iddef_policy_cancel_penalty==iddef_policy_cancel_penalty, Model.iddef_policy_rule==iddef_policy_rule).all())
                    if(model_cancel_penalty.cancel_fees[id_cancel_fee].iddef_policy_rule == iddef_policy_rule):
                        model_cancel_penalty.cancel_fees[id_cancel_fee].percent = cancel_fee["percent"]
                        model_cancel_penalty.cancel_fees[id_cancel_fee].option_percent = cancel_fee["option_percent"]
                        model_cancel_penalty.cancel_fees[id_cancel_fee].number_nights_percent = cancel_fee["number_nights_percent"]
                        model_cancel_penalty.cancel_fees[id_cancel_fee].fixed_amount = cancel_fee["fixed_amount"]
                        model_cancel_penalty.cancel_fees[id_cancel_fee].estado = 1 #cancel_fee["estado"]
                        model_cancel_penalty.cancel_fees[id_cancel_fee].usuario_ultima_modificacion = user_name
                    elif (count_cancel_fee == 0):
                        model = Model()
                        model.iddef_policy_rule = cancel_fee["iddef_policy_rule"]
                        model.percent = cancel_fee["percent"]
                        model.option_percent = cancel_fee["option_percent"]
                        model.number_nights_percent = cancel_fee["number_nights_percent"]
                        model.fixed_amount = cancel_fee["fixed_amount"]
                        model.estado = cancel_fee["estado"]
                        model.usuario_creacion = user_name
                        list_models_cancel_fees.append(model)
                        break

            #Se validan los elementos que se van a desactivar (Estos elementos no llegan en el request)
            for id_cancel_fee, value_cancel_fee in enumerate(model_cancel_penalty.cancel_fees):
                if(model_cancel_penalty.cancel_fees[id_cancel_fee].iddef_policy_rule not in list_iddef_policy_cancel_penalty_request):
                    model_cancel_penalty.cancel_fees[id_cancel_fee].estado = 0

            for temp_cancel_fee in list_models_cancel_fees:
                model_cancel_penalty.cancel_fees.append(temp_cancel_fee)

            db.session.commit()

            result = schema_response.dump(model_cancel_penalty)
            list_result = list(filter(lambda elem_cancel_fee: elem_cancel_fee["estado"] == 1, result["cancel_fees"]))

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