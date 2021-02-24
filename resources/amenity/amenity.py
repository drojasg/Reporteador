from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db,base
from models.amenity import AmenitySchema as ModelSchema, GetAmenitySchema as GetModelSchema, Amenity as Model, GetListAmenitySchema,GetIdAmenitySchema, AmenityPostPutSchema
from models.text_lang import TextLang as TextModel, TextLangSchema as TextSchema
from common.util import Util
from sqlalchemy.sql.expression import and_


class Amenity(Resource):
    #api-amenity-get-by-id
    #@base.access_middleware
    def get(self, id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            dataAmenity = schema.dump(data)
            dataResponse = []
            aux = {}

            aux['html_icon'] = dataAmenity['html_icon']
            aux['name'] = dataAmenity['name']
            aux['iddef_amenity'] = dataAmenity['iddef_amenity']
            aux['iddef_amenity_group'] = dataAmenity['iddef_amenity_group']
            aux['description'] = dataAmenity['description']
            aux['iddef_amenity_type'] = dataAmenity['iddef_amenity_type']

            dataTextLang = TextModel.query.filter(and_(TextModel.estado == 1, TextModel.table_name == 'def_amenity', TextModel.id_relation == dataAmenity['iddef_amenity']))
            textSchema = TextSchema(exclude=Util.get_default_excludes(), many=True)
            dataTextLangJson = textSchema.dump(dataTextLang)
            
            #print (dataTextLangJson)
            arrayDescription = []
            arrayName= []
            

            for  x in dataTextLangJson:
                auxText = {}
                auxDescription = {}
                auxName = {}
                
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
                                
                value = [y for y in arrayName \
                    if y['lang_code'] == x1['lang_code']]
                
                #print (value[0])
                if value:
                    if x1['lang_code'] == value[0]['lang_code']:
                        
                        x1['name'] = value[0]['name']
                        x1['iddef_text_lang_name'] = value[0]['iddef_text_lang_name']
                        #arrayDescription.append(x1)
                            
            aux['info_amenity_by_lang'] = arrayDescription
            
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

    #api-amenity-put
    #@base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = AmenityPostPutSchema(exclude=Util.get_default_excludes())
            schemaGetAmenity = ModelSchema(exclude=Util.get_default_excludes())
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

            dataAmenity = schema.dump(model)
            #consultamos las descripciones
            
            descExistQuery = model.query.filter_by(description = data["name"]).first()
            descExist = schemaGetAmenity.dump(descExistQuery)

            
            if descExist:
                pass
            else:
                descExist["iddef_amenity"] = model.iddef_amenity

            if model.iddef_amenity != descExist["iddef_amenity"]:
                raise Exception("The Amenity %s exists, please verify" % data["name"])

            if request.json.get("name") != None:
                model.name = data["name"]
            if request.json.get("description") != None:
                model.description = data["description"]
            if request.json.get("html_icon") != None:
                model.html_icon = data["html_icon"]
            if request.json.get("estado") != None:
                model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name#base.get_token_data()
            if request.json.get("iddef_amenity_group") != None:
                model.iddef_amenity_group = data["iddef_amenity_group"]
            if request.json.get("iddef_amenity_type") != None:
                model.iddef_amenity_type = data["iddef_amenity_type"]
            model.usuario_ultima_modificacion = user_name
            db.session.flush()
            #db.session.commit()

            for text in data["info_amenity_by_lang"]:
                #data_texts_amenities =  
                aux = {}
                txt_model = TextModel.query.get(text["iddef_text_lang"])
                if txt_model:
                    txt_model.lang_code = text["lang_code"]
                    txt_model.text = text["text"]
                    txt_model.table_name = "def_amenity"
                    txt_model.id_relation = id
                    txt_model.attribute = text["attribute"]
                    txt_model.estado = text["estado"]
                    txt_model.usuario_ultima_modificacion = user_name
                    #db.session.add(txt_model)
                    db.session.flush()
                    dataUpdateText = txt_schema.dump(txt_model)
                #aux["info_amenity_by_lang"] = dataInsertText
                
                    dataResponse.append(dataUpdateText)
                else:
                    txt_exist = TextModel.query.filter(TextModel.lang_code == text["lang_code"], TextModel.table_name == "def_amenity", TextModel.id_relation == id, TextModel.attribute == text["attribute"])
                    txt_existJSON = txt_schema.dump(txt_exist, many=True)

                    if txt_existJSON:
                        txt_model_update = TextModel.query.get(txt_existJSON[0]["iddef_text_lang"])
                        txt_model_update.lang_code = text["lang_code"]
                        txt_model_update.text = text["text"]
                        txt_model_update.table_name = "def_amenity"
                        txt_model_update.id_relation = id
                        txt_model_update.attribute = text["attribute"]
                        txt_model_update.estado = text["estado"]
                        txt_model.usuario_ultima_modificacion = user_name
                        #db.session.add(txt_model)
                        db.session.flush()
                        dataUpdateText = txt_schema.dump(txt_model_update)
                    else:
                        aux = {}
                        txt_model = TextModel()
                        txt_model.lang_code = text["lang_code"]
                        txt_model.text = text["text"]
                        txt_model.table_name = "def_amenity"
                        txt_model.id_relation = id
                        txt_model.attribute = text["attribute"]
                        txt_model.estado = text["estado"]
                        txt_model.usuario_ultima_modificacion = user_name
                        db.session.add(txt_model)
                        db.session.flush()
                        dataInsertText = txt_schema.dump(txt_model)
                        aux["info_amenity_by_lang"] = dataInsertText
                
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

    #api-amenity-delete
    #@base.access_middleware
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

    #api-amenity-post
    #@base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = AmenityPostPutSchema(exclude=Util.get_default_excludes())
            #schemaGetAmenity = ModelSchema(exclude=Util.get_default_excludes())
            txt_schema = TextSchema(exclude=Util.get_default_excludes())
            #txt_data = txt_schema.
            data = schema.load(json_data)
            model = Model()

            #consultamos las descripciones de las amenidades
            descExistQuery = model.query.filter_by(description = data["name"]).first()
            #descExist = schemaGetAmenity.dump(descExistQuery) 
            #print (descExist)

            #txt_model = TextModel()
            dataResponse = []
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            model.name = data["name"]
            model.description = data["description"]
            model.html_icon = data["html_icon"]
            model.estado = 1
            model.iddef_amenity_group = data["iddef_amenity_group"]
            model.iddef_amenity_type = data["iddef_amenity_type"]
            model.usuario_creacion = user_name

            db.session.add(model)
            db.session.flush()
            dataInsertAmenity = schema.dump(model)
            dataResponse.append(dataInsertAmenity)

            for text in data["info_amenity_by_lang"]:
                aux = {}
                txt_model = TextModel()
                txt_model.lang_code = text["lang_code"]
                txt_model.text = text["text"]
                txt_model.table_name = "def_amenity"
                txt_model.id_relation = dataInsertAmenity["iddef_amenity"]
                txt_model.attribute = text["attribute"]
                txt_model.estado = text["estado"]
                txt_model.usuario_creacion = user_name
                db.session.add(txt_model)
                db.session.flush()
                dataInsertText = txt_schema.dump(txt_model)
                aux["info_amenity_by_lang"] = dataInsertText
                
                dataResponse.append(dataInsertText)

            if descExistQuery:
                raise Exception("The Amenity %s exists, please verify" % model.name)                

            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataResponse
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

class AmenityListSearch(Resource):
    #api-amenity-get-all
    #@base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = GetListAmenitySchema(exclude=Util.get_default_excludes(), many=True)
            resp = schema.dump(data)
            dataResponse = []

            for x in resp :
                aux = {}
                aux["description"]= x['description']
                aux["iddef_amenity"] = x['iddef_amenity']
                aux["iddef_amenity_type"] = x['amenity_type']['iddef_amenity_type']
                aux["amenity_type_description"] = x['amenity_type']['descripcion']
                aux["iddef_amenity_group"] = x['amenity_group']['iddef_amenity_group']
                aux["amenity_group_name"] = x['amenity_group']['name']
                aux["amenity_group_description"] = x['amenity_group']['description']
                aux["name"] = x['name']
                aux["estado"] = x['estado']
                aux["html_icon"] = x['html_icon']

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

class AmenityUpdateStatus(Resource):
    #api-amenity-update-status
    #@base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = GetIdAmenitySchema()
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