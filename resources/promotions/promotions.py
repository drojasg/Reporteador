from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db,base
from models.promotions import Promotions as Model, GetAllPromotionsSchema as GetModelSchema, PromotionsPostSchema as PostModelSchema, PromotionsPutSchema as PutModelSchema, PromotionsSchema as ModelSchema
from resources.promotions.promotionsHelper_v2 import Generate as functionsPromo, Filter as funcPromo
from common.util import Util
from common.utilities import Utilities

class Promotions(Resource):
    #api-promotions-get-by-id
    # @base.access_middleware
    def get(self, id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.filter_by(idop_promotions=id).first()
            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                auxFuncPromo = funcPromo()
                result_discounts = []
                if len(data.discounts) > 0:
                    for item_discount in data.discounts:
                        name_type = auxFuncPromo.get_promotion_discount_type(item_discount["type"])
                        if name_type is not None:
                            name_type = name_type.code
                        else:
                            name_type = ""
                        item_discount["name_type"] = name_type
                        result_discounts.append(item_discount)
                data.discounts = result_discounts
                result = schema.dump(data)
                data_restrinction = auxFuncPromo.get_detail_restriction(id)
                if data_restrinction is not None:
                    result["detail_restriction"] = data_restrinction
                data_rate_plans = auxFuncPromo.get_promotion_rateplan(id)
                if len(data_rate_plans) > 0:
                    result["rate_plans"] = data_rate_plans
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
    
    #api-promotions-update-status
    # @base.access_middleware
    def put(self, id, status):
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
        
    #api-promotions-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            result = []
            if int(json_data["idop_promotions"]) == 0:
                schema = PostModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
            else:
                schema = PutModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
            #Metodo para agregar o actualizar
            helperPromo = functionsPromo()
            result = helperPromo.create_promotion(data,data["idop_promotions"])
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
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

class PromotionsListSearch(Resource):
    #api-promotions-get-all
    # @base.access_middleware
    def get(self):
        try:
            
            isAll = request.args.get("all")
            order = request.args.get("order")
            desc = request.args.get("desc")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = GetModelSchema(many=True)
            
            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                msg = "Success"
                result = schema.dump(data)
                try:
                    order_type = False if desc is None else True
                    if order is not None and Utilities.check_field_exists_data(self,result,order):
                        result = Utilities.sort_dict(self,result,order,asc=order_type)
                    elif order is not None:
                        msg = order + " not exist"
                except Exception as ex:
                    msg = str(ex)

                response = {
                    "Code": 200,
                    "Msg": msg,
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