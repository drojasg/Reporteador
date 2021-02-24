from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.sql import exists
from sqlalchemy import func 

from config import db, base
from models.currency import GetCurrencySchema as GetModelSchema, CurrencySchema as ModelSchema, Currency as Model, CurrencyUpdateSchema
from models.text_lang import TextLang
from models.op_exchange_rate import OpExchangeRate, OpExchangeRateSchema
from common.util import Util
from sqlalchemy.sql.expression import and_
from common.public_auth import PublicAuth


class Currency(Resource):
    #api-currency-get-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            
            response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": schema.dump(data)
                }

        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response

    #api-currency-post
    # @base.access_middleware
    def post(self):
        
        response = {}

        if request.is_json:
            try:
                data = request.get_json(force=True)
                schema = ModelSchema(exclude=Util.get_default_excludes())
                schema.load(data)
                user_data = base.get_token_data()
                user_name = user_data['user']['username']
                model = Model()

                data_compare = data["currency_code"].strip()

                description_exist = self.get_desc_if_exists(data_compare.lower())
                
                if description_exist:
                    raise Exception("The Currency Code" + " " + data["currency_code"] + " " + "already exists, please enter a different Currency Code")
                else:
                    model.currency_code = data["currency_code"]
                    model.description = data["description"]
                    model.own_exchange_rate = data["own_exchange_rate"]
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

    #api-currency-put
    # @base.access_middleware
    def put(self,id):
        response = {}

        """
        validamos antes de actualizar que no exista el mismo codigo, con el id 
        consultamo el code con el id 
        """

        try:
            data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()
            data_compare = data["currency_code"].strip()
            data_compare_desc = data["description"]

            id_code_exist = self.get_code_if_exists_by_currency_id(id, data_compare)
            id_desc_exist = self.get_desc_if_exists_by_currency_id(id, data_compare_desc)
            

            if id_code_exist:
                raise Exception("The Currency Code" + " " + data["currency_code"] + " " + "already exists, please enter a different Currency Code")
                
            else:
                if id_desc_exist:
                    raise Exception("The Description" + " " + data["description"] + " " + "already exists, please enter a different Description")
                else:
                    dataUpdate = model.query.filter_by(iddef_currency=id).first()                           
                    dataUpdate.currency_code = data["currency_code"]
                    dataUpdate.description = data["description"]
                    dataUpdate.own_exchange_rate = data["own_exchange_rate"]
                    dataUpdate.estado = data["estado"]
                    dataUpdate.usuario_ultima_modificacion = user_name
                    db.session.flush()

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

    @staticmethod
    def get_desc_if_exists(parameter):

        data = db.session.query(exists().where(Model.currency_code == parameter)).scalar()

        if data:
            #si ya existe el nombre del parametro regresamos True
            return True
        else:
            #si no existe entonces False
            return False

    @staticmethod
    def get_code_if_exists_by_currency_id(id,parameter):
        
        data = db.session.query(exists().where(Model.iddef_currency != id).where(Model.currency_code == parameter)).scalar()
        if data:
            #si existe
            return True
        else:
            return False   
    @staticmethod
    def get_desc_if_exists_by_currency_id(id,parameter):
        
        data = db.session.query(exists().where(Model.iddef_currency != id).where(Model.description == parameter)).scalar()
        if data:
            #si existe
            return True
        else:
            return False 

    #api-currency-delete
    # @base.access_middleware
    def delete(self,id):
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

class CurrencyListSearch(Resource):
    #api-currency-get-all
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
            dataCurrency = schema.dump(data)

            dataResponse = []
            for dataC in dataCurrency:
                dataEx = OpExchangeRate.query.add_columns(OpExchangeRate.currency_code, OpExchangeRate.amount, func.max(OpExchangeRate.date).label("date"))\
                    .filter(and_(OpExchangeRate.estado ==1, OpExchangeRate.currency_code == dataC["currency_code"]))
                schemaExchange = OpExchangeRateSchema(exclude=Util.get_default_excludes(), many=True)
                dataExchange = schemaExchange.dump(dataEx)
                aux = {}
                aux["estado"] = dataC["estado"]
                aux["iddef_currency"] = dataC["iddef_currency"]
                aux["currency_code"] = dataC["currency_code"]
                aux["description"] = dataC["description"]
                aux["own_exchange_rate"] = dataC["own_exchange_rate"]
                isNone = 1 if dataExchange[0]["amount"]  == None else dataExchange[0]["amount"]
                aux["exchange_rate_today"] = isNone
                #count == N ? 0 : count + 1;

                dataResponse.append(aux)



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
                    "data": dataResponse
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response


class CurrencyUpdateStatus(Resource):
    #api-currency-update-status
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = CurrencyUpdateSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model.query.get(id)
            
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

class CurrencyList(Resource):
    #api
    @PublicAuth.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            if isAll is not None:
                result = Model.query.all()
            else:
                result = Model.query.filter(Model.estado==1)

            schema = GetModelSchema(many=True)

            if result is None:
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
                    "data": schema.dump(result)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class CurrencyLangList(Resource):
    #api
    @PublicAuth.access_middleware
    def get(self, lang_code):
        try:
            result = Model.query\
            .join(TextLang, and_(TextLang.id_relation == Model.iddef_currency, TextLang.table_name == "def_currency"))\
            .add_columns(Model.iddef_currency, Model.currency_code, (TextLang.text).label("description"), Model.estado)\
            .filter(Model.estado==1, TextLang.estado==1, TextLang.lang_code == lang_code, TextLang.attribute == 'description').all()

            schema = GetModelSchema(many=True)

            if result is None:
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
                    "data": schema.dump(result)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response