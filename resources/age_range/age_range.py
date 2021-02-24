from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.age_range import AgeRangeSchema as ModelSchema, GetListAgeRangeSchema as GetListModelSchema,\
GetAgeRangeSchema as GetModelSchema, GetAgeRangeListSchema as GetARListModelSchema,\
SaveAgeRangeSchema as SaveModelSchema,UpdateAgeRangeSchema as UpdateModelSchema, AgeRange as Model
from models.text_lang import TextLangSchema as TLModelSchema, TextLang as TLModel
from models.property_lang import GetPropertyLangSchema as GetPLModelSchema, PropertyLang as PLModel
from models.age_code import AgeCode as ACModel, AgeCodeSchema as ACModelSchema,\
GetAgeCodeSchema as GetACModelSchema, age_code_public as agcpublic
from models.languaje import Languaje as LModel
from models.property import Property as PropertyModel
from .age_range_service import AgeRangeService
from common.util import Util
from sqlalchemy import or_, and_
from common.public_auth import PublicAuth
from resources.age_code.age_code_helper import age_helper as agefunctions, agcModel
from resources.property.propertyHelper import FilterProperty as prfunction
from resources.text_lang.textlangHelper import Filter as txtHelper

class AgeRange(Resource):
    #api-age-range-get-by-id
    #@base.access_middleware
    def get(self, id):
        try:
            schema = GetACModelSchema(exclude=Util.get_default_excludes())
            data = ACModel.query.get(id)
            result=schema.dump(data)
            property_age = Model.query.filter_by(iddef_age_code=result['iddef_age_code'],estado=1).all()
            result["appliedproperties"] = [property_elem.iddef_property for property_elem in property_age]
            text_lang = TLModel.query.filter_by(id_relation=result['iddef_age_code'], table_name='def_age_code', estado=1).all()
            result_text = []
            if len(text_lang) > 0:
                for x in text_lang:
                    codeLangText = {
                        "codeLang": x.lang_code,
                        "text": x.text
                    }
                    result_text.append(codeLangText)
            result["nameGroup"] = result_text
            
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

    #api-age-range-put
    #@base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = UpdateModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = ACModel.query.get(id)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            #user_name = "mtun"
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            """ #desactivar registro
            model.estado = 0
            db.session.flush()
            #validar rango de edad
            validate_age_range = AgeRangeService.get_validate_age_range(data["iddef_property"],data["age_from"],data["age_to"])
            if validate_age_range:
                raise Exception("There is specified age range") """
            #actualizar registros
            if request.json.get("code") != None:
                model.code = data["code"]
            if request.json.get("disable_edit") != None:
                model.disable_edit = data["disable_edit"]
            if request.json.get("age_from") != None:
                model.age_from = data["age_from"]
            if request.json.get("age_to") != None:
                model.age_to = data["age_to"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            db.session.flush()

            #desactivar todos los activos
            data_age_property = Model.query.filter_by(iddef_age_code=id, estado=1).all()
            if len(data_age_property) > 0:
                for itmAge in data_age_property:
                    age = Model.query.get(itmAge.iddef_age_range)
                    age.estado = 0
                    db.session.flush()
            #activar los que estan en el nodo-> appliedproperties
            if len(data["appliedproperties"]) > 0:
                for idproperty in data["appliedproperties"]:
                    dataProperty = Model.query.filter_by(iddef_age_code=id, iddef_property=idproperty).first()
                    if dataProperty is None:
                        modelP = Model()
                        modelP.iddef_property = idproperty
                        modelP.iddef_age_code = id
                        modelP.estado = 1
                        modelP.usuario_creacion = user_name
                        db.session.add(modelP)
                        db.session.flush()
                    else:
                        dataProperty.iddef_property = idproperty
                        dataProperty.iddef_age_code = id
                        dataProperty.estado = 1
                        dataProperty.usuario_ultima_modificacion = user_name
                        db.session.flush()

            #desactivar todos los activos
            data_text_lang = TLModel.query.filter_by(table_name='def_age_code', id_relation=id, estado=1).all()
            if len(data_text_lang) > 0:
                for item in data_text_lang:
                    tl = TLModel.query.get(item.iddef_text_lang)
                    tl.estado = 0
                    db.session.flush()
            #activar los que estan en el nodo->nameGroup
            if len(data["nameGroup"]) > 0:
                for toSave in data["nameGroup"]:
                        dataSearch = TLModel.query.filter_by(lang_code=toSave["codeLang"], table_name='def_age_code', id_relation=id).first()
                        if dataSearch is None:
                            model2 = TLModel()
                            model2.lang_code = toSave["codeLang"]
                            model2.text = toSave["text"]
                            model2.table_name = "def_age_code"
                            model2.id_relation = id
                            model2.attribute = "descripcion"
                            model2.estado = 1
                            model2.usuario_creacion = user_name
                            db.session.add(model2)
                            db.session.flush()
                        else:
                            dataSearch.lang_code = toSave["codeLang"]
                            dataSearch.text = toSave["text"]
                            dataSearch.table_name = "def_age_code"
                            dataSearch.id_relation = id
                            dataSearch.attribute = "descripcion"
                            dataSearch.estado = 1
                            dataSearch.usuario_ultima_modificacion = user_name
                            db.session.flush()

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

    #api-age-range-post
    #@base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            item = json_data["datos"]
            schema = SaveModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            #validar si existe registro con el mismo rango en bd
            data_age_range_items = AgeRangeService.get_validate_age_range(data["iddef_property"],data["age_from"],data["age_to"])
            if data_age_range_items:
                raise Exception("There is specified age range")

            model = Model()
            model.iddef_property = data["iddef_property"]
            model.iddef_default_price_type = 1
            model.iddef_age_code = data["iddef_age_code"]
            model.age_from = data["age_from"]
            model.age_to = data["age_to"]
            model.default_price_value = 0.00
            model.estado = 1
            model.usuario_creacion = user_name
            db.session.add(model)
            db.session.commit()

            id=model.iddef_age_range

            if id is None:
                db.session.rollback()
                return {
                    "Code": 500,
                    "Msg": "could not create specified age range",
                    "Error": True,
                    "data": {}
                }
            else:
                for toSave in item:
                    schema2 = TLModelSchema(exclude=Util.get_default_excludes())
                    data2 = schema2.load(toSave)
                    model2 = TLModel()
                    model2.lang_code = data2["lang_code"]
                    model2.text = data2["text"]
                    model2.table_name = "def_age_range"
                    model2.id_relation = id
                    model2.attribute = "descripcion"
                    model2.estado = 1
                    model2.usuario_ultima_modificacion = user_name
                    db.session.add(model2)
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

class AgeRangeStatus(Resource):
    #api-age-range-delete
    #@base.access_middleware
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

class AgeRangeListSearch(Resource):
    #api-age-range-get-all
    #@base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = ACModel.query.all()
            else:
                data = ACModel.query.filter(ACModel.estado==1)

            schema = GetACModelSchema(exclude=Util.get_default_excludes(), many=True)
            age_range_items=schema.dump(data, many=True)
            result=[]
            if len(age_range_items) > 0:
                for item_age in age_range_items:
                    property_age = Model.query.filter_by(iddef_age_code=item_age['iddef_age_code'],estado=1).all()
                    item_age["appliedproperties"] = [property_elem.iddef_property for property_elem in property_age]
                    text_lang = TLModel.query.filter_by(id_relation=item_age['iddef_age_code'], table_name='def_age_code', estado=1).all()
                    result_text = []
                    if len(text_lang) > 0:
                        for x in text_lang:
                            codeLangText = {
                                "codeLang": x.lang_code,
                                "text": x.text
                            }
                            result_text.append(codeLangText)
                    item_age["nameGroup"] = result_text
                    result.append(item_age)

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

class AgeRangePropetyListSearch(Resource):
    #api-age-range-propety-get-all
    #@base.access_middleware
    def get(self, id):
        try:

            data = Model.query.filter_by(iddef_property=id, estado=1).all()
            schema = GetModelSchema(exclude=Util.get_default_excludes(), many=True)
            age_range_items=schema.dump(data, many=True)
            result=[]
            for x in age_range_items:
                age_range_item=x
                
                age_range_item['code'] = age_range_item['age_range_age_code']['code']
                age_range_item['disable_edit'] = age_range_item['age_range_age_code']['disable_edit']
                age_range_item.pop('age_range_age_code')
                schema2 = TLModelSchema(exclude=Util.get_default_excludes(), many=True)
                text_lang = TLModel.query.filter_by(id_relation=age_range_item['iddef_age_range'], table_name='def_age_range', estado=1).all()
                
                text_lang_items=schema2.dump(text_lang, many=True)
                nombre=''
                for j in text_lang_items:
                    text_lang_item=j
                    nombre='text'+text_lang_item['lang_code']
                    age_range_item[nombre] = text_lang_item['text']
                    
                result.append(age_range_item)

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

class AgeRangePropetySearch(Resource):
    #api-age-range-propety-get
    #@PublicAuth.access_middleware
    def get(self, property_code, lang_code):
        try:

            dataProperty = PropertyModel.query.filter_by(property_code=property_code, estado=1).first()
            if dataProperty is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                idProperty = dataProperty.iddef_property
                data = Model.query.order_by(Model.iddef_age_code).filter_by(iddef_property=idProperty, estado=1).all()
                schema = GetARListModelSchema()
                age_range_items=schema.dump(data, many=True)
                result=[]
                ojt_item = {}
                for x in age_range_items:
                    age_range_item=x
                    text_lang = TLModel.query.filter_by(id_relation=age_range_item['age_range_age_code']['iddef_age_code'], table_name='def_age_code', attribute='descripcion' , lang_code=lang_code, estado=1).first()
                    if text_lang is None:
                        nombre=''
                    else:
                        nombre = text_lang.text
                    ojt_item = {
                        "code": age_range_item['age_range_age_code']['code'] ,
                        "description": str(age_range_item['age_range_age_code']['age_from']) + '-' + str(age_range_item['age_range_age_code']['age_to']),
                        "text": nombre,
                        "age_min": str(age_range_item['age_range_age_code']['age_from']),
                        "age_max": str(age_range_item['age_range_age_code']['age_to'])
                    }
                    age_range_item.pop('age_range_age_code')
                    result.append(ojt_item)
            
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

class AgeProperty_V2(Resource):
    def get(self,property_code):
        response = {}
        
        try:

            property_info = prfunction.getHotelInfo(self,property_code)
            propertyid = property_info.iddef_property

            age_range = agefunctions.get_age_range_avail_by_property(self,propertyid)

            age_list = {}
            for age in age_range:
                
                agcdata = agcModel.query.get(age.iddef_age_code)
                
                if agcdata is not None:
                    code = agcdata.code
                    agcschema = agcpublic()

                    txtdata = txtHelper.get_text_data(self,table_name="def_age_range",\
                    attribute="descripcion",id_relation=age.iddef_age_range)
                        
                    data = {
                        "agc":agcdata,
                        "txt":txtdata
                    }
                    
                    agcdetail = agcschema.dump(data)
                    age_list[code]=agcdetail

            response["Code"]=200
            response["Error"]=False
            response["Msg"]="Success"
            response["data"]=age_list

        except Exception as age_error:
            response["Code"]=500
            response["Error"]=True
            response["Msg"]=str(age_error)
            response["data"]={}

        return response
class AgeRangeListSearchEnglish(Resource):
    #@base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = ACModel.query.all()
            else:
                data = ACModel.query.filter(ACModel.estado==1)

            schema = GetACModelSchema(exclude=Util.get_default_excludes(), many=True)
            age_range_items=schema.dump(data, many=True)
            result=[]
            if len(age_range_items) > 0:
                for item_age in age_range_items:
                    property_age = Model.query.filter_by(iddef_age_code=item_age['iddef_age_code'],estado=1).all()
                    item_age["appliedproperties"] = [property_elem.iddef_property for property_elem in property_age]
                    text_lang = TLModel.query.filter_by(id_relation=item_age['iddef_age_code'], table_name='def_age_code', estado=1, lang_code="EN").all()
                    result_text = []
                    if len(text_lang) > 0:
                        for x in text_lang:
                            item_age["codeLang"] = ""
                            item_age["text"] = ""

                            item_age["codeLang"] = x.lang_code
                            item_age["text"] = x.text

                            # = {
                            #    "codeLang": x.lang_code,
                            #    "text": x.text
                            #}
                            #result_text.append(codeLangText)
                    #item_age["nameGroup"] = result_text
                    result.append(item_age)

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
