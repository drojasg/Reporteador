from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from sqlalchemy import or_, and_
from models.filters import FiltersSchema as ModelSchema, Filters as Model, FiltersPostPutSchema
from models.text_lang import TextLang as TextModel, TextLangSchema as TextSchema
from common.util import Util
import json

class Filter(Resource):
    #api-filters-get-by-id
    # @base.access_middleware
    def get(self,id):

        response = {}

        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            dataFilters = schema.dump(data)
            dataResponse = []
            aux = {}

            aux['iddef_filters'] = dataFilters['iddef_filters']
            aux['name'] = dataFilters['name']
            aux['estado'] = dataFilters['estado']

            dataTextLang = TextModel.query.filter(and_(TextModel.estado == 1, TextModel.table_name == 'def_filters', TextModel.id_relation == dataFilters['iddef_filters']))
            textSchema = TextSchema(exclude=Util.get_default_excludes(), many=True)
            dataTextLangJson = textSchema.dump(dataTextLang)

            arrayDescription = []
            arrayName= []

            for x in dataTextLangJson:
                auxText = {}
                auxDescription = {}
                auxName ={}

                auxText['lang_code'] = x['lang_code']

                if x['attribute'] == 'description':
                    auxText['description'] = x['text']
                    auxText['iddef_text_lang_description'] = x['iddef_text_lang']
                    arrayDescription.append(auxText)
                else:
                    auxText['name'] = x['text']
                    auxText['iddef_text_lang_name'] = x['iddef_text_lang']
                    arrayName.append(auxText)

            for x1 in arrayDescription:
                value=[y for y in arrayName\
                    if y['lang_code']== x1['lang_code']]
                if value:
                    if x1['lang_code'] == value[0]['lang_code']:
                        x1['name'] = value[0]['name']
                        x1['iddef_text_lang_name'] = value[0]['iddef_text_lang_name']

            aux['info_filters_by_lang'] = arrayDescription

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
                    "Code":200,
                    "Msg":"Success",
                    "Error":False,
                    "data": dataResponse[0]
                }

        except Exception as e:
            

            response = {
                "Code":500,
                "Msg":str(e),
                "Error":True,
                "data":{}
            }

        return response

    #api-filters-post
    # @base.access_middleware
    def post(self):
        
        response = {}

        try:
            json_data = request.get_json(force=True)
            schema = FiltersPostPutSchema(exclude=Util.get_default_excludes())
            txt_schema = TextSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model()

            #consultamos los filtros que existen
            filterExistQuery = model.query.filter_by(name= data["name"]).first()

            dataResponse = []
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            model.name = data["name"]
            model.estado = data["estado"]
            model.usuario_creacion = user_name
            
            db.session.add(model)
            db.session.flush()
            dataInsertFilters = schema.dump(model)
            dataResponse.append(dataInsertFilters)

            for text in data["info_filters_by_lang"]:
                aux={}
                txt_model = TextModel()

                txt_model.lang_code = text["lang_code"]
                txt_model.text = text["text"]
                txt_model.table_name = "def_filters"
                txt_model.id_relation = dataInsertFilters["iddef_filters"]
                txt_model.attribute = text["attribute"]
                txt_model.estado = text["estado"]
                txt_model.usuario_creacion = user_name
                #insertamos en text_lang
                db.session.add(txt_model)
                db.session.flush()
                dataInsertText=txt_schema.dump(txt_model)
                aux["info_filters_by_lang"] = dataInsertText

                dataResponse.append(dataInsertText)

                if filterExistQuery:
                    raise Exception("The Filter %s exists, please verify" % model.name)
                db.session.commit()                    

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataResponse
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
                                        
        return response

    #api-filters-put
    # @base.access_middleware
    def put(self,id):
        response = {}

        try:
            json_data = request.get_json(force=True)
            schema = FiltersPostPutSchema(exclude=Util.get_default_excludes())
            schemaGetFilters = ModelSchema(exclude=Util.get_default_excludes())
            txt_schema = TextSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            model = Model.query.get(id)
            dataResponse = []
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            
            if model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
                
            dataFilters = schema.dump(model)
            #consultamos las descripciones
            
            descExistQuery = model.query.filter_by(name = data["name"]).first()
            descExist = schemaGetFilters.dump(descExistQuery)
            
            if descExist:
                pass
            else:
                descExist["iddef_filters"] = model.iddef_filters
                # 
            if model.iddef_filters != descExist["iddef_filters"]:
                raise Exception("The Filter %s exists, please verify" % data["name"])

            model.name = data["name"]
            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            #db.session.commit()
            # 
            for text in data["info_filters_by_lang"]:
                #data_texts_amenities =  
                aux = {}
                txt_model = TextModel.query.get(text["iddef_text_lang"])
                
                if txt_model:
                    txt_model.lang_code = text["lang_code"]
                    txt_model.text = text["text"]
                    txt_model.table_name = "def_filters"
                    txt_model.id_relation = id
                    txt_model.attribute = text["attribute"]
                    txt_model.estado = text["estado"]
                    txt_model.usuario_ultima_modificacion = user_name
                    
                    db.session.flush()
                    dataUpdateText = txt_schema.dump(txt_model)
                #aux["info_amenity_by_lang"] = dataInsertText
                
                    dataResponse.append(dataUpdateText)
                else:
                    
                    txt_exist = TextModel.query.filter(TextModel.lang_code == text["lang_code"], TextModel.table_name == "def_filters", TextModel.id_relation == id, TextModel.attribute == text["attribute"])
                    txt_existJSON = txt_schema.dump(txt_exist, many=True)
                    
                    if txt_existJSON:
                        txt_model_update = TextModel.query.get(txt_existJSON[0]["iddef_text_lang"])
                        txt_model_update.lang_code = text["lang_code"]
                        txt_model_update.text = text["text"]
                        txt_model_update.table_name = "def_filters"
                        txt_model_update.id_relation = id
                        txt_model_update.attribute = text["attribute"]
                        txt_model_update.estado = text["estado"]
                        txt_model_update.usuario_ultima_modificacion = user_name
                        
                        db.session.flush()
                        dataUpdateText = txt_schema.dump(txt_model_update)
                    else:
                        aux = {}
                        txt_model = TextModel()
                        txt_model.lang_code = text["lang_code"]
                        txt_model.text = text["text"]
                        txt_model.table_name = "def_filters"
                        txt_model.id_relation = id
                        txt_model.attribute = text["attribute"]
                        txt_model.estado = text["estado"]
                        txt_model.usuario_ultima_modificacion = user_name
                        db.session.add(txt_model)
                        db.session.flush()
                        dataInsertText = txt_schema.dump(txt_model)
                        aux["info_filters_by_lang"] = dataInsertText
                        
                        dataResponse.append(dataInsertText)
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

    #api-filters-delete
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
                dataUpdate = model.query.filter_by(iddef_filters=id).first()
                                
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

class FilterListSearch(Resource):
    #api-filters-get-all
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

    # @base.access_middleware
    def put(self, id):
        #update Status
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
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

            model.estado = data["estado"]
            model.name = data["name"]
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