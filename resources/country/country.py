from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.country import CountrySchema as ModelSchema, SaveCountrySchema as SaveModelSchema,\
Country as Model
from models.text_lang import TextLangSchema as tlModelSchema, TextLang as tlModel
from common.util import Util
from sqlalchemy import and_, or_
from sqlalchemy.sql import exists

from common.public_auth import PublicAuth

class Country(Resource):
    #api-country-get-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:
            result = {}
            resultText = []
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            result = schema.dump(data)
            dataText = tlModel.query.filter_by(table_name='def_country', attribute='name', id_relation=id).all()
            if len(dataText) > 0:
                for x in dataText:
                    item = {
                        "iddef_text_lang":x.iddef_text_lang,
                        "lang_code": x.lang_code,
                        "text": x.text,
                        "estado": x.estado
                    }
                    resultText.append(item)
            result['data_langs'] = resultText

            response = {
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": result
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
    def get_param_if_exists(parameter):

        data = db.session.query(exists().where(Model.name == parameter)).scalar()

        if data:
            #si ya existe el nombre del parametro regresamos True
            return True
        else:
            #si no existe entonces False
            return False
    
    
    #api-country-post
    # @base.access_middleware
    def post(self):
        
        response = {}

        try:
            data = request.get_json(force=True)
            schema = SaveModelSchema(exclude=Util.get_default_excludes())
            schema.load(data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            model = Model()
            data_compare = data["name"].strip()
            param_exist = self.get_param_if_exists(data_compare.lower())

            if param_exist:
                raise Exception("The country" + " " + data["name"] + " " + "already exists, please enter a different name")
            else:
                model.name = data["name"]
                model.country_code = data["country_code"]
                model.alias = data["alias"]
                model.idmarket_segment = data["idmarket_segment"]
                model.dialling_code = data["dialling_code"]
                model.estado = data["estado"]
                model.usuario_creacion = user_name
                db.session.add(model)
                db.session.flush()

            for item in data['data_langs']:
                if int(item["iddef_text_lang"]) == 0:
                    Tmodel = tlModel()
                    Tmodel.lang_code = item["lang_code"]
                    Tmodel.text = item["text"]
                    Tmodel.table_name = "def_country"
                    Tmodel.id_relation = model.iddef_country
                    Tmodel.attribute = "name"
                    Tmodel.estado = item["estado"]
                    Tmodel.usuario_creacion = user_name
                    db.session.add(Tmodel)
                    db.session.flush()

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
        #else:
            #response = {
                #"Code":500,
                #"Msg":"INVALID REQUEST"
            #}

        return response

    @staticmethod
    def get_param_if_exists_by_parameter_idconfig(id,parameter):
        
        data = db.session.query(exists().where(Model.iddef_country == id).where(Model.name == parameter)).scalar()

        if data:
            #si existe
            return True
        else:
            return False

    #api-country-put
    # @base.access_middleware
    def put(self,id):
        response = {}

        try:
            data = request.get_json(force=True)
            schema = SaveModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(data)
            model = Model()
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            dataUpdate = model.query.filter_by(iddef_country=id).first()


            data_compare = data["name"].strip()
            param_exist = self.get_param_if_exists(data_compare.lower())

            #param_exist = self.get_param_if_exists(data["param"].strip())
            id_param_exist = self.get_param_if_exists_by_parameter_idconfig(id,data_compare.lower())

            if dataUpdate is not None:
                if id_param_exist :
                    dataUpdate.name = data["name"]
                    dataUpdate.country_code = data["country_code"]
                    dataUpdate.alias = data["alias"]
                    dataUpdate.idmarket_segment = data["idmarket_segment"]
                    dataUpdate.dialling_code = data["dialling_code"]
                    dataUpdate.estado = data["estado"]
                    dataUpdate.usuario_ultima_modificacion = user_name
                    for item in data['data_langs']:
                        if int(item["iddef_text_lang"]) == 0:
                            Tmodel = tlModel()
                            Tmodel.lang_code = item["lang_code"]
                            Tmodel.text = item["text"]
                            Tmodel.table_name = "def_country"
                            Tmodel.id_relation = id
                            Tmodel.attribute = "name"
                            Tmodel.estado = item["estado"]
                            Tmodel.usuario_creacion = user_name
                            db.session.add(Tmodel)
                            db.session.flush()
                        else:
                            dataUpdateText = tlModel.query.filter_by(lang_code=item['lang_code'],\
                            table_name='def_country', iddef_text_lang=item['iddef_text_lang'], id_relation=id).first()
                            if dataUpdateText is not None:
                                dataUpdateText.lang_code = item["lang_code"]
                                dataUpdateText.text = item["text"]
                                dataUpdateText.table_name = "def_country"
                                dataUpdateText.id_relation = id
                                dataUpdateText.attribute = "name"
                                dataUpdateText.estado = item["estado"]
                                dataUpdateText.usuario_ultima_modificacion = user_name
                                db.session.flush()
                else:
                    param_exist = self.get_param_if_exists(data_compare.lower())
                    if param_exist:
                        raise Exception("The name" + " " + data["name"] + " " + "already exists, please enter a different name")
                    else:
                        dataUpdate.name = data["name"]
                        dataUpdate.country_code = data["country_code"]
                        dataUpdate.alias = data["alias"]
                        dataUpdate.idmarket_segment = data["idmarket_segment"]
                        dataUpdate.dialling_code = data["dialling_code"]
                        dataUpdate.estado = data["estado"]
                        dataUpdate.usuario_ultima_modificacion = user_name
                        for item in data['data_langs']:
                            if int(item["iddef_text_lang"]) == 0:
                                Tmodel = tlModel()
                                Tmodel.lang_code = item["lang_code"]
                                Tmodel.text = item["text"]
                                Tmodel.table_name = "def_country"
                                Tmodel.id_relation = id
                                Tmodel.attribute = "name"
                                Tmodel.estado = item["estado"]
                                Tmodel.usuario_creacion = user_name
                                db.session.add(Tmodel)
                                db.session.flush()
                            else:
                                dataUpdateText = tlModel.query.filter_by(lang_code=item['lang_code'],\
                                table_name='def_country', iddef_text_lang=item['iddef_text_lang'], id_relation=id).first()
                                if dataUpdateText is not None:
                                    dataUpdateText.lang_code = item["lang_code"]
                                    dataUpdateText.text = item["text"]
                                    dataUpdateText.table_name = "def_country"
                                    dataUpdateText.id_relation = id
                                    dataUpdateText.attribute = "name"
                                    dataUpdateText.estado = item["estado"]
                                    dataUpdateText.usuario_ultima_modificacion = user_name
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

    #api-country-delete
    # @base.access_middleware
    def delete(self,id):
        response = {}

        try:
            data = request.json
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(data)
            model = Model()

            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            dataUpdate = model.query.filter_by(iddef_country=id).first()

            
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

        return response

class CountryListSearch(Resource):

    #api-country-get-all
    # @base.access_middleware
    def get(self):            
        try:

            isAll = request.args.get("all")
            market = request.args.get("market")

            conditions = []

            if isAll is None:
                conditions.append(Model.estado==1)

            if market is not None:
                markets = market.split(",")
                
                conditions.append(Model.idmarket_segment.in_(markets))

            if len(conditions) >= 1:
                data = Model.query.order_by(Model.name.asc()).filter(and_(*conditions))
            else:
                data = Model.query.order_by(Model.name.asc()).all()

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

class CountryLang(Resource):
    #api-public-country-lang
    @PublicAuth.access_middleware
    def get(self,lang_code):
        try:
            result = []
            lang_code = "EN" if lang_code.upper() == "EN" else "ES"

            query = "SELECT c.iddef_country, c.country_code, t.text, c.dialling_code \
                FROM def_country c \
                INNER JOIN def_text_lang t on t.id_relation = c.iddef_country \
                AND t.table_name='def_country' AND t.attribute='name' AND t.estado = 1 \
                WHERE c.estado = 1 AND t.lang_code = '"+lang_code+"' \
                ORDER BY t.text"
            
            query_result = db.session.execute(query)

            for iddef_country, country_code, text, dialling_code in query_result:
                data_country = {
                    "iddef_country":iddef_country,
                    "country_code": country_code,
                    "name": text,
                    "dialling_code": dialling_code
                }
                
                result.append(data_country)
            
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