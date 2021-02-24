from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
#from models.media_property import MediaPropertySchema as ModelSchema, GetMediaPropertySchema as GetModelSchema, GetListMediaPropertySchema as GetListModelSchema, MediaProperty as Model, GetMediaPropertyAdminSchema, PostMediaPropertySchema, UpdateOrderSchema
from models.media import Media as MedModel, MediaSchema as MedSchema, MediaSchemaStatus
from models.media_headers import MediaHeaders as Model, MediaHeadersSchema as ModelSchema, MediaHeadersGetSchema, MediaHeadersSchemaStatus
from models.brand import Brand
from models.property import Property
from models.media import Media
from common.util import Util
from common.utilities import Utilities
from sqlalchemy.sql.expression import and_
from sqlalchemy import func
from common.public_auth import PublicAuth
import json

class MediaHeaders(Resource):
    #Apis-basicas
    
    # @base.access_middleware
    def get(self, id):
        try:
            schema = MediaHeadersGetSchema(exclude=Util.get_default_excludes())
            data =  Model.query\
                    .add_columns(Model.iddef_media,Model.estado,Model.iddef_media_headers,(Media.name).label("media_name"), Model.order, Brand.code,(Brand.name).label("brand_name"), (Property.short_name).label("property_name"), Model.lang_code_list, Media.url, Model.property_code)\
                    .join(Media, and_(Media.iddef_media == Model.iddef_media))\
                    .outerjoin(Brand, and_(Brand.code == Model.brand_code))\
                    .outerjoin(Property, and_(Property.property_code == Model.property_code))\
                    .filter(and_(Model.iddef_media_headers == id, Model.estado == 1)).first()

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
    def post(self): 
        
        try:
            json_data = request.get_json(force=True)

            #credential_data = PublicAuth.get_credential_data()
            #username = credential_data.name
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            dataResponse = []

            for req_uniq in json_data:
                response = {}
                if isinstance(req_uniq["tags"], str):
                    req_uniq["tags"] = json.loads(request.json["tags"])
                else:
                    req_uniq["tags"] = req_uniq["tags"]

                media_req = {
                    "iddef_media_type": req_uniq["iddef_media_type"],
                    "iddef_media_group": req_uniq["iddef_media_group"],
                    "url": req_uniq["url"],
                    "description": req_uniq["description"],
                    "nombre_bucket": req_uniq["nombre_bucket"],
                    "bucket_type": req_uniq["bucket_type"],
                    "etag": req_uniq["etag"],
                    "show_icon": req_uniq["show_icon"],
                    "name": req_uniq["name"],
                    "tags":req_uniq["tags"],
                    "estado": 1
                }
            
                media_schema = MedSchema(exclude=Util.get_default_excludes())
                media_data = media_schema.load(media_req)
                med_model = MedModel()

                med_model.iddef_media_type = media_data["iddef_media_type"]
                med_model.iddef_media_group = media_data["iddef_media_group"]
                med_model.url = media_data["url"]
                med_model.description = media_data["description"]
                med_model.nombre_bucket = media_data["nombre_bucket"]
                med_model.bucket_type = media_data["bucket_type"]
                med_model.etag = media_data["etag"]
                med_model.show_icon = media_data["show_icon"]
                med_model.name = media_data["name"]
                med_model.tags = media_data["tags"]
                med_model.estado = 1
                med_model.usuario_creacion = user_name
                #Agregamos en la tabla def_media
                db.session.add(med_model)
                db.session.flush()

                insert_media = media_schema.dump(med_model)
                dataResponse.append(insert_media)
                
                media_headers_request = {
                    "iddef_media": insert_media["iddef_media"],
                    "brand_code": req_uniq["brand_code"],
                    "property_code": req_uniq["property_code"],
                    "all_lang": req_uniq["all_lang"],
                    "lang_code_list" :req_uniq["lang_code_list"],
                    "order": req_uniq["order"],
                    "estado": 1
                }

                media_headers_schema = ModelSchema(exclude=Util.get_default_excludes())
                headers_data = media_headers_schema.load(media_headers_request)
                head_model = Model()

                head_model.iddef_media = insert_media["iddef_media"]
                head_model.brand_code = headers_data["brand_code"]
                head_model.property_code = headers_data["property_code"]
                head_model.all_lang = headers_data["all_lang"]
                head_model.lang_code_list = headers_data.get("lang_code_list", {}).get("lang_code_list", [])
                head_model.estado = 1
                head_model.usuario_creacion = user_name
                db.session.add(head_model)
                #db.session.flush()
                db.session.commit()

                insert_headers= media_headers_schema.dump(head_model)
                dataResponse.append(insert_headers)

                if insert_media and insert_headers:
                    db.session.commit()
            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
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

    # @base.access_middleware
    def put(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []

            for req_uniq in json_data:
                aux = {}
                if isinstance(req_uniq["tags"], str):
                    req_uniq["tags"] = json.loads(request.json["tags"])
                else:
                    req_uniq["tags"] = req_uniq["tags"]

                media_req = {
                    "iddef_media_type": req_uniq["iddef_media_type"],
                    "iddef_media_group": req_uniq["iddef_media_group"],
                    "url": req_uniq["url"],
                    "description": req_uniq["description"],
                    "nombre_bucket": req_uniq["nombre_bucket"],
                    "bucket_type": req_uniq["bucket_type"],
                    "etag": req_uniq["etag"],
                    "show_icon": req_uniq["show_icon"],
                    "name": req_uniq["name"],
                    "tags":req_uniq["tags"],
                    "estado": 1
                }
            
                media_schema = MedSchema(exclude=Util.get_default_excludes())
                media_data = media_schema.load(media_req)
                med_model = MedModel.query.get(req_uniq["iddef_media"])

                med_model.iddef_media_type = media_data["iddef_media_type"]
                med_model.iddef_media_group = media_data["iddef_media_group"]
                med_model.url = media_data["url"]
                med_model.description = media_data["description"]
                med_model.nombre_bucket = media_data["nombre_bucket"]
                med_model.bucket_type = media_data["bucket_type"]
                med_model.etag = media_data["etag"]
                med_model.show_icon = media_data["show_icon"]
                med_model.name = media_data["name"]
                med_model.tags = media_data["tags"]
                med_model.estado = 1
                med_model.usuario_creacion = user_name
                #Agregamos en la tabla def_media
                #db.session.add(med_model)
                db.session.flush()

                insert_media = media_schema.dump(med_model)
                dataResponse.append(insert_media)
                
                media_headers_request = {
                    "iddef_media": insert_media["iddef_media"],
                    "brand_code": req_uniq["brand_code"],
                    "property_code": req_uniq["property_code"],
                    "all_lang": req_uniq["all_lang"],
                    "lang_code_list" :req_uniq["lang_code_list"],
                    "order": req_uniq["order"],
                    "estado": 1
                }

                media_headers_schema = ModelSchema(exclude=Util.get_default_excludes())
                headers_data = media_headers_schema.load(media_headers_request)
                head_model = Model.query.get(req_uniq["iddef_media_headers"])

                head_model.iddef_media = insert_media["iddef_media"]
                head_model.brand_code = headers_data["brand_code"]
                head_model.property_code = headers_data["property_code"]
                head_model.all_lang = headers_data["all_lang"]
                head_model.lang_code_list = headers_data.get("lang_code_list", {}).get("lang_code_list", [])
                head_model.order = headers_data["order"]
                head_model.estado = 1
                head_model.usuario_creacion = user_name
                db.session.add(head_model)
                #db.session.flush()
                db.session.commit()

                insert_headers= media_headers_schema.dump(head_model)
                dataResponse.append(insert_headers)

                if insert_media and insert_headers:
                    db.session.commit()
            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
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

class MediaHeadersList(Resource):
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")
            order = request.args.get("order")
            desc = request.args.get("desc")

            schema = MediaHeadersGetSchema(exclude=Util.get_default_excludes())
            
            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query\
                    .add_columns(Model.iddef_media,Model.estado,Model.iddef_media_headers,Brand.code,(Media.name).label("media_name"), Model.order, (Brand.name).label("brand_name"), (Property.short_name).label("property_name"), Model.lang_code_list)\
                    .join(Media, and_(Media.iddef_media == Model.iddef_media))\
                    .outerjoin(Brand, and_(Brand.code == Model.brand_code))\
                    .outerjoin(Property, and_(Property.property_code == Model.property_code))\
                    .all()

            if data is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                msg = "Success"
                format_data = schema.dump(data, many=True)

                try:
                    order_type = False if desc is None else True
                    if order is not None and Utilities.check_field_exists_schema(self,schema,order):
                        format_data = Utilities.sort_dict(self,format_data,order,asc=order_type)
                    elif order is not None:
                        msg = order + " not exist"
                except Exception as ex:
                    msg = str(ex)

                response = {
                    "Code": 200,
                    "Msg": msg,
                    "Error": False,
                    "data": format_data
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
    def put(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []

            for req_uniq in json_data:
                aux = {}
                media_req = {
                    "estado": req_uniq["estado"]
                }
            
                media_schema = MediaSchemaStatus(exclude=Util.get_default_excludes())
                media_data = media_schema.load(media_req)
                med_model = MedModel.query.get(req_uniq["iddef_media"])
                med_model.estado = media_data["estado"]
                med_model.usuario_creacion = user_name
                #Agregamos en la tabla def_media
                #db.session.add(med_model)
                db.session.flush()

                insert_media = media_schema.dump(med_model)
                dataResponse.append(insert_media)
                
                media_headers_request = {
                    "estado": req_uniq["estado"]
                }

                media_headers_schema = MediaHeadersSchemaStatus(exclude=Util.get_default_excludes())
                headers_data = media_headers_schema.load(media_headers_request)
                head_model = Model.query.get(req_uniq["iddef_media_headers"])

                

                head_model.estado = headers_data["estado"]
                head_model.usuario_creacion = user_name
                db.session.commit()

                insert_headers= media_headers_schema.dump(head_model)
                dataResponse.append(insert_headers)

                if insert_media and insert_headers:
                    db.session.commit()
            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
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


class headersPublic(Resource):

    @PublicAuth.access_middleware
    def get(self,property_code, brand_code, lang_code):
        
        try:
            schema = MediaHeadersGetSchema(exclude=Util.get_default_excludes())
            response = {}
            data = None
            #print(property_code)
            if property_code != 'null':
                #print("hola")
                data = Model.query\
                    .add_columns(Media.url, Model.lang_code_list)\
                    .join(Media, and_(Media.iddef_media == Model.iddef_media))\
                    .filter(and_(Model.property_code == property_code, Model.estado == 1)).all()
            else:
                data = Model.query\
                    .add_columns(Media.url, Model.lang_code_list)\
                    .join(Media, and_(Media.iddef_media == Model.iddef_media))\
                    .filter(and_(Model.brand_code == brand_code, Model.estado == 1)).all()

            if data is None:            
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                res = []
                for item in data:
                    #print(lang_code)
                    #print(item.lang_code_list)
                    if lang_code.upper() in item.lang_code_list:
                        res.append(item.url)
                
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": res
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response



