from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.property import Property as pModel
from resources.rates.RatesHelper import RatesFunctions as funtions
from models.property_filters import PropertyFiltersSchema as ModelSchema, GetPropertyFilterSchema as GetModelSchema, PropertyFilters as Model
from common.util import Util
from sqlalchemy import or_, and_
from models.property_description import PropertyDescription, DumpPropertyDescriptionSchema
from models.filters import Filters as FilterModel, FiltersSchema as FilterSchema
from common.public_auth import PublicAuth

class Propertyfilters(Resource):
    #api-property-filters-get-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:

            data = Model.query.get(id)

            schema = GetModelSchema(exclude=Util.get_default_excludes())

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

    #api-property-filters-post
    # @base.access_middleware
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
                
                #model.iddef_currency = data["iddef_property_lang"]
                model.iddef_property = data["iddef_property"]
                model.iddef_filter = data["iddef_filter"]
                #model.estado = data["estado"]
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

    #api-property-filters-put
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

                dataUpdate = model.query.filter_by(iddef_property_lang=id).first()

                dataUpdate.iddef_property = data["iddef_property"]
                dataUpdate.iddef_filter = data["iddef_filter"]
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

    #api-property-filters-delete
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
                dataUpdate = model.query.filter_by(iddef_property_lang=id).first()

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

class PropertyfiltersListSearch(Resource):
    #api-property-filters-get-all
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

class PublicPropertyfiltersListSearch(Resource):
    #api-public-media-get-all
    @PublicAuth.access_middleware
    def post(self):

        response = {}

        try:
            requestData = request.get_json(force=True)
            schemaDump = GetModelSchema(exclude=Util.get_default_excludes())
            dataRq = schemaDump.load(requestData)
            data = Model()         
            filterModel = FilterModel()   
            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            filterSchema = FilterSchema(exclude=Util.get_default_excludes())
            
            conditions = []

            conditions.append(pModel.estado == 1)

            if request.json.get("property_code") is not None and request.json.get("brand_code") is not None:
                if request.json.get("property_code") != "" and request.json.get("brand_code") == "":
                    property_code = dataRq["property_code"]
                    conditions.append(pModel.property_code==property_code)

                if request.json.get("brand_code") != "" and request.json.get("property_code") == "":
                    dataBrand = funtions.getBrandInfo(dataRq["brand_code"])
                    id_brand = dataBrand.iddef_brand
                    conditions.append(pModel.iddef_brand==id_brand)
                                    
                if request.json.get("property_code") != "" and request.json.get("brand_code") != "":
                    property_code = dataRq["property_code"]
                    conditions.append(pModel.property_code==property_code)

            if request.json.get("property_code") is not None or request.json.get("brand_code") is not None:
                data = Model.query.join(pModel).with_entities(Model.iddef_filter).filter(and_(*conditions,Model.estado)).distinct(Model.iddef_filter)
            else:
                data = Model.query.with_entities(Model.iddef_filter).filter(Model.estado==1).distinct(Model.iddef_filter)

            dataResult = schema.dump(data)

            for item in dataResult:
                idFilter = item["iddef_filter"]
                filteredData = filterModel.query.get(idFilter)
                filteredDataResult = filterSchema.dump(filteredData)
                #item["filters"] = filteredData
                item['iddef_filter'] = idFilter
                text_lang_info = funtions.getTextLangInfo('def_filters','description', dataRq['lang_code'],item['iddef_filter'])
                
                if text_lang_info is not None:
                    item['filters'] = text_lang_info.text
                

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
                    "data": schemaDump.dump(dataResult,many=True)
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response