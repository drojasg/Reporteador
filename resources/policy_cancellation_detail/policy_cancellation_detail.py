from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.policy_cancellation_detail import PolicyCancellationDetail as Model,\
PolicyCancellationDetailSchema as ModelSchema, GetPolicyCancellationDetailSchema as GetModelSchema,\
PostPolicyCancellationDetailSchema as PostModelSchema
from models.policy_cancellation_penalty import PolicyCancellationPenalty as PCPModel
from models.policy import Policy, PolicySchema, GetPolicySchema
from common.util import Util
from sqlalchemy import func


class PolicyCancellationDetail(Resource):
    #api-policy_cancel_penalties-get-by-id
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

    #api-policy_cancel_penalties-post
    # @base.access_middleware
    def post(self):
        """ secciones de detalles de politicas de cancelación
        sección details base: id_type_detail = 0
        sección details_seasonal_exception: id_type_detail = 1
        sección details_no_refundable_dates: id_type_detail = 2 """
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = PostModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            exists = Policy.query.filter(Policy.iddef_policy==data["iddef_policy"]).scalar() is not None

            if not exists:
                return {
                    "Code": 404,
                    "Msg": "Policy not found",
                    "Error": True,
                    "data": {}
                }
            

            if request.json.get("is_base") != None:
                is_base = data["is_base"]
            else:
                is_base = 0
                
            count_base_policy_detail = Model.query.filter(Model.iddef_policy == data["iddef_policy"],\
            Model.is_base==1, Model.estado == 1).with_entities(func.count()).scalar()
            if count_base_policy_detail == 0:
                is_base = 1
            else:
                is_base = 0

            model = Model()
            model.iddef_policy = data["iddef_policy"]
            model.id_type_detail = data["id_type_detail"]
            model.is_base = is_base #data["is_base"]
            model.is_refundable = request.json.get("is_refundable", 1) #data["is_refundable"]
            if model.is_base == 1 and model.id_type_detail != 0:
                model.start_date = "1901-01-01" #data["start_date"]
                model.end_date = "1901-01-01" #data["end_date"]
            else:
                model.start_date = data["start_date"]
                model.end_date = data["end_date"]
            if model.is_refundable == 0:
                model.iddef_cancellation_window = 0 #data["iddef_cancellation_window"]
                model.iddef_inside_penalty = 0 #data["iddef_inside_penalty"]
                model.amount_inside_penalty = 0 #data["amount_inside_penalty"]
            else:
                if model.id_type_detail != 2:
                    model.iddef_cancellation_window = data["iddef_cancellation_window"]
                    model.iddef_inside_penalty = data["iddef_inside_penalty"]
                    validate_type = PCPModel.query.get(model.iddef_inside_penalty)
                    if validate_type.type != "price":
                        model.amount_inside_penalty = 0
                    else:
                        model.amount_inside_penalty = data["amount_inside_penalty"]
            model.description_en = data["description_en"]
            model.description_es = data["description_es"]
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

    #api-policy_cancel_penalties-put
    # @base.access_middleware
    def put(self, id):
        """ secciones de detalles de politicas de cancelación
        sección details base: id_type_detail = 0
        sección details_seasonal_exception: id_type_detail = 1
        sección details_no_refundable_dates: id_type_detail = 2 """
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
            is_base, is_refundable = 0, 1
            if request.json.get("is_base") != None:
                is_base = data["is_base"]
                #no se puede cambiar de tipo de base
                #model.is_base = is_base
            if request.json.get("is_refundable") != None:
                is_refundable = data["is_refundable"]
            #no se puede cambiar de cambiar de sección cuando = details_no_refundable_dates
            if data["id_type_detail"] != 2: 
                model.is_refundable = is_refundable 

            if is_base == 0 and data["id_type_detail"] != 0:
                model.start_date = data["start_date"]
                model.end_date = data["end_date"]

            #si es de tipo = 2 no se puede agregar cancellation_window, inside_penalty
            if data["id_type_detail"] != 2:
                if is_refundable == 1:
                    model.iddef_cancellation_window = data["iddef_cancellation_window"]
                    model.iddef_inside_penalty = data["iddef_inside_penalty"]
                    validate_type = PCPModel.query.get(model.iddef_inside_penalty)
                    if validate_type.type == "price":
                        model.amount_inside_penalty = data["amount_inside_penalty"]
                    
            model.description_en = data["description_en"]
            model.description_es = data["description_es"]
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


class PolicyCancellationDetailDelete(Resource):
    #api-policy_cancel_penalties-delete
    # @base.access_middleware
    def put(self, id, status):
        response = {}
        try:
            schema = GetModelSchema(exclude=Util.get_default_excludes())
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

            model.estado = status
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


class PolicyCancellationDetailListSearch(Resource):
    #api-policy_cancel_penalties-get-all
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

class GetIdPolicyCancellationDetail(Resource):
    #api-policy_cancel_penalties-get-by-id-policy
    # @base.access_middleware
    def get(self, id_policy):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter(Model.iddef_policy==id_policy).all()

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