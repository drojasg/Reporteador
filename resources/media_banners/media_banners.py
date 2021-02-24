from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db, base
from models.media import Media as MedModel, MediaSchema as MedSchema, MediaSchemaStatus
from models.media_banners import MediaBanners as Model, MediaBannersSchema as ModelSchema,\
MediaBannersUpdateSchema as UpdateModelSchema, MediaBannersGetSchema as GetModelSchema
from models.brand import Brand
from models.property import Property
from models.country import Country
from .media_banners_service import MediaBannersService
from resources.market_segment.marketHelper import Market as FunctionsMark
from common.util import Util
from sqlalchemy.sql.expression import and_
from sqlalchemy import func
from common.public_auth import PublicAuth
import json

class MediaBanners(Resource):
    #Apis-basicas
    
    # @base.access_middleware
    def get(self, id):
        try:
            schema = GetModelSchema(exclude=Util.get_default_excludes())
            media_schema = MedSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            result = schema.dump(data)
            result_media = []
            if len(result["ids_media"]) > 0:
                for media in result["ids_media"]:
                    data_media = MedModel.query.get(media["iddef_media"])
                    inf_media = media_schema.dump(data_media)
                    media.update(inf_media)
                    result_media.append(media)
            result["ids_media"] = result_media
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
    
    # @base.access_middleware
    def post(self): 
        response = {}
        try:
            json_data = request.get_json(force=True)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            dataResponse, dataMediaResponse = [], []

            media_banners_request = {}
            media_banners_request["type_banner"] = json_data["type_banner"]
            if media_banners_request["type_banner"] == 1:
                if len(json_data["data_media"]) < 3:
                    raise Exception("The media %s invalid long" % media_banners_request["type_banner"])
            elif media_banners_request["type_banner"] == 2:
                if len(json_data["data_media"]) < 1:
                    raise Exception("The media %s invalid long" % media_banners_request["type_banner"])
            elif media_banners_request["type_banner"] == 3:
                if len(json_data["data_media"]) < 2:
                    raise Exception("The media %s invalid long" % media_banners_request["type_banner"])

            for item_img in json_data["data_media"]:
                if request.json.get("tags") != None:
                    if isinstance(item_img["tags"], str):
                        item_img["tags"] = json.loads(request.json["tags"])
                    else:
                        item_img["tags"] = item_img["tags"]
                else:
                    item_img["tags"] = {"tags": [""]}

                media_req = {
                    "iddef_media_type": item_img["iddef_media_type"],
                    "iddef_media_group": item_img["iddef_media_group"],
                    "url": item_img["url"],
                    "description": item_img["description"],
                    "nombre_bucket": item_img["nombre_bucket"],
                    "bucket_type": item_img["bucket_type"],
                    "etag": item_img["etag"],
                    "show_icon": item_img["show_icon"],
                    "name": item_img["name"],
                    "tags":item_img["tags"],
                    "estado": 1
                }
            
                #Agregamos en la tabla def_media           
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
                db.session.add(med_model)
                db.session.flush()

                insert_media = media_schema.dump(med_model)
                if media_banners_request["type_banner"] == 3:
                    data_media = {
                        "iddef_media":insert_media["iddef_media"],
                        "category":item_img["category"],
                        "href_banner": item_img["href_banner"]
                    }
                else:
                    data_media = {
                        "iddef_media":insert_media["iddef_media"],
                        "category":item_img["category"]
                    }
                dataMediaResponse.append(data_media)
                
            media_banners_request["ids_media"] = dataMediaResponse
            media_banners_request["name"] = json_data["name"]
            media_banners_request["lang_option"] = json_data["lang_option"]
            media_banners_request["lang_codes"] = json_data["lang_codes"]
            media_banners_request["market_option"] = json_data["market_option"]
            media_banners_request["marketing"] = json_data["marketing"]
            media_banners_request["booking_window_option"] = json_data["booking_window_option"]
            media_banners_request["booking_window"] = json_data["booking_window"]
            media_banners_request["brand_option"] = json_data["brand_option"]
            if media_banners_request["brand_option"] != 1:
                media_banners_request["property_codes"] = json_data["property_codes"]
                if media_banners_request["brand_option"] == 0:
                    media_banners_request["brand_codes"] = []
                elif media_banners_request["brand_option"] == 2:
                    media_banners_request["brand_codes"] = json_data["brand_codes"]
            else:
                media_banners_request["property_codes"] = []
                media_banners_request["brand_codes"] = []
            media_banners_request["geo_targeting_option"] = json_data["geo_targeting_option"]
            media_banners_request["geo_targeting_countries"] = json_data["geo_targeting_countries"]
            media_banners_request["pages"] = json_data["pages"]
            if request.json.get("order") != None:
                media_banners_request["order"] = json_data["order"]
            else:
                media_banners_request["order"] = 1
            media_banners_request["estado"] = 1

            #Agregamos en la tabla def_media_banners
            media_banners_schema = ModelSchema(exclude=Util.get_default_excludes())
            banners_data = media_banners_schema.load(media_banners_request)
            banner_model = Model()

            banner_model.ids_media = banners_data["ids_media"]
            banner_model.name = banners_data["name"]
            banner_model.type_banner = banners_data["type_banner"]
            banner_model.property_codes = banners_data["property_codes"]
            banner_model.lang_option = banners_data["lang_option"]
            banner_model.lang_codes = banners_data["lang_codes"]
            banner_model.market_option = banners_data["market_option"]
            banner_model.marketing = banners_data["marketing"]
            banner_model.booking_window_option = banners_data["booking_window_option"]
            banner_model.booking_window = banners_data["booking_window"]
            banner_model.brand_option = banners_data["brand_option"]
            banner_model.brand_codes = banners_data["brand_codes"]
            banner_model.geo_targeting_option = banners_data["geo_targeting_option"]
            banner_model.geo_targeting_countries = banners_data["geo_targeting_countries"]
            banner_model.pages = banners_data["pages"]
            banner_model.order = banners_data["order"]
            banner_model.estado = 1
            banner_model.usuario_creacion = user_name
            db.session.add(banner_model)

            db.session.commit()

            insert_banners= media_banners_schema.dump(banner_model)
            dataResponse.append(insert_banners)

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
            
            dataResponse, dataMediaResponse = [], []

            media_banners_request = {}
            media_banners_request["iddef_media_banners"] = json_data["iddef_media_banners"]
            media_banners_request["type_banner"] = json_data["type_banner"]
            if media_banners_request["type_banner"] == 1:
                if len(json_data["data_media"]) < 3:
                    raise Exception("The media %s invalid long" % media_banners_request["type_banner"])
            elif media_banners_request["type_banner"] == 2:
                if len(json_data["data_media"]) < 1:
                    raise Exception("The media %s invalid long" % media_banners_request["type_banner"])
            elif media_banners_request["type_banner"] == 3:
                if len(json_data["data_media"]) < 2:
                    raise Exception("The media %s invalid long" % media_banners_request["type_banner"])

            for item_img in json_data["data_media"]:
                if request.json.get("tags") != None:
                    if isinstance(item_img["tags"], str):
                        item_img["tags"] = json.loads(request.json["tags"])
                    else:
                        item_img["tags"] = item_img["tags"]
                else:
                    item_img["tags"] = {"tags": [""]}

                media_req = {
                    "iddef_media_type": 1,
                    "iddef_media_group": 10,
                    "url": item_img["url"],
                    "description": item_img["description"],
                    "nombre_bucket": item_img["nombre_bucket"],
                    "bucket_type": item_img["bucket_type"],
                    "etag": item_img["etag"],
                    "show_icon": item_img["show_icon"],
                    "name": item_img["name"],
                    "tags":item_img["tags"],
                    "estado": 1
                }
            
                #Agregamos en la tabla def_media           
                media_schema = MedSchema(exclude=Util.get_default_excludes())
                media_data = media_schema.load(media_req)
                if item_img["iddef_media"] != 0:
                    med_model = MedModel.query.get(item_img["iddef_media"])

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
                    med_model.usuario_ultima_modificacion = user_name
                    db.session.flush()
                else:
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
                    db.session.add(med_model)
                    db.session.flush()

                insert_media = media_schema.dump(med_model)
                if media_banners_request["type_banner"] == 3:
                    data_media = {
                        "iddef_media":insert_media["iddef_media"],
                        "category":item_img["category"],
                        "href_banner": item_img["href_banner"]
                    }
                else:
                    data_media = {
                        "iddef_media":insert_media["iddef_media"],
                        "category":item_img["category"]
                    }
                dataMediaResponse.append(data_media)
            
            media_banners_request["ids_media"] = dataMediaResponse
            media_banners_request["name"] = json_data["name"]
            media_banners_request["lang_option"] = json_data["lang_option"]
            media_banners_request["lang_codes"] = json_data["lang_codes"]
            media_banners_request["market_option"] = json_data["market_option"]
            media_banners_request["marketing"] = json_data["marketing"]
            media_banners_request["booking_window_option"] = json_data["booking_window_option"]
            media_banners_request["booking_window"] = json_data["booking_window"]
            media_banners_request["brand_option"] = json_data["brand_option"]
            if media_banners_request["brand_option"] != 1:
                media_banners_request["property_codes"] = json_data["property_codes"]
                if media_banners_request["brand_option"] == 0:
                    media_banners_request["brand_codes"] = []
                elif media_banners_request["brand_option"] == 2:
                    media_banners_request["brand_codes"] = json_data["brand_codes"]
            else:
                media_banners_request["property_codes"] = []
                media_banners_request["brand_codes"] = []
            media_banners_request["geo_targeting_option"] = json_data["geo_targeting_option"]
            media_banners_request["geo_targeting_countries"] = json_data["geo_targeting_countries"]
            media_banners_request["pages"] = json_data["pages"]
            if request.json.get("order") != None:
                media_banners_request["order"] = json_data["order"]
            else:
                media_banners_request["order"] = 1
            media_banners_request["estado"] = 1

            #Agregamos en la tabla def_media_banners
            media_banners_schema = UpdateModelSchema(exclude=Util.get_default_excludes())
            banners_data = media_banners_schema.load(media_banners_request)
            banner_model = Model.query.get(json_data["iddef_media_banners"])

            banner_model.ids_media = banners_data["ids_media"]
            banner_model.type_banner = banners_data["type_banner"]
            banner_model.name = banners_data["name"]
            banner_model.property_codes = banners_data["property_codes"]
            banner_model.lang_option = banners_data["lang_option"]
            banner_model.lang_codes = banners_data["lang_codes"]
            banner_model.market_option = banners_data["market_option"]
            banner_model.marketing = banners_data["marketing"]
            banner_model.booking_window_option = banners_data["booking_window_option"]
            banner_model.booking_window = banners_data["booking_window"]
            banner_model.brand_option = banners_data["brand_option"]
            banner_model.brand_codes = banners_data["brand_codes"]
            banner_model.geo_targeting_option = banners_data["geo_targeting_option"]
            banner_model.geo_targeting_countries = banners_data["geo_targeting_countries"]
            banner_model.pages = banners_data["pages"]
            banner_model.order = banners_data["order"]
            banner_model.estado = 1
            banner_model.usuario_creacion = user_name

            db.session.commit()

            insert_banners= media_banners_schema.dump(banner_model)
            dataResponse.append(insert_banners)
            
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

class MediaBannersList(Resource):
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            schema = GetModelSchema(exclude=Util.get_default_excludes())
            
            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

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
    
    # @base.access_middleware
    def put(self, id, status):
        response = {}
        try:
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            media_banners_schema = GetModelSchema(exclude=Util.get_default_excludes())
            banners_model = Model.query.get(id)

            if banners_model is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }

            banners_model.estado = status
            banners_model.usuario_creacion = user_name
            db.session.flush()

            for media in banners_model.ids_media:
                med_model = MedModel.query.get(media["iddef_media"])
                med_model.estado = status
                med_model.usuario_creacion = user_name

            db.session.commit()

            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": media_banners_schema.dump(banners_model)
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

class BannersPublic(Resource):

    @PublicAuth.access_middleware
    def get(self,property_code, brand_code, lang_code, market_code, booking_window):
        
        try:
            getMediaBanner = MediaBannersService()
            FunctionMark = FunctionsMark()
            response = {}
            result_obj = {}
            if lang_code != 'null':
                lang_code = '['+'"'+str(lang_code)+'"'+']'
            else:
                raise Exception("Lang Code no encontrado, favor de verificar")
            if market_code != 'null':
                #country
                data_country = Country.query.filter(Country.country_code==market_code).first()
                id_country = data_country.iddef_country
                country_code = '['+''+str(id_country)+''+']'
                #market
                msData = FunctionMark.getMarketInfo(market_code)
                id_market = msData.iddef_market_segment
                market_code = '['+''+str(id_market)+''+']'
            else:
                raise Exception("Market no encontrado, favor de verificar")
            if booking_window == 'null':
                raise Exception("Booking Window no encontrado, favor de verificar")
            if property_code != 'null':
                property_code = '['+'"'+str(property_code)+'"'+']'
            else:
                property_code = None
            if brand_code != 'null':
                brand_code = '['+'"'+str(brand_code)+'"'+']'
            else:
                brand_code = None

            home = '["home"]'
            data_home = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, pages=home, type_banner=1)
            result_mobile, result_web = [], []
            if len(data_home) > 0:
                for banner in data_home:
                    for img in banner["ids_media"]:
                        if img["category"] == "mobile":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_mobile.append({"img":data_media.url,"alt":""})
                        if img["category"] == "desktop":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_web.append({"img":data_media.url,"alt":""})
            result_obj["home"] = {
                "mobile":result_mobile,
                "web":result_web
            }
            rooms = '["rooms"]'
            data_rooms = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, pages=rooms, type_banner=1)
            result_mobile, result_web = [], []
            if len(data_rooms) > 0:
                for banner in data_rooms:
                    for img in banner["ids_media"]:
                        if img["category"] == "mobile":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_mobile.append({"img":data_media.url,"alt":""})
                        if img["category"] == "desktop":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_web.append({"img":data_media.url,"alt":""})
            result_obj["rooms"] = {
                "mobile":result_mobile,
                "web":result_web
            }

            services = '["services"]'
            data_services = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, pages=services, type_banner=1)
            result_mobile, result_web = [], []
            if len(data_services) > 0:
                for banner in data_services:
                    for img in banner["ids_media"]:
                        if img["category"] == "mobile":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_mobile.append({"img":data_media.url,"alt":""})
                        if img["category"] == "desktop":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_web.append({"img":data_media.url,"alt":""})
            result_obj["services"] = {
                "mobile":result_mobile,
                "web":result_web
            }

            confirmation = '["confirmation"]'
            data_confirmation = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, pages=confirmation, type_banner=1)
            result_mobile, result_web = [], []
            if len(data_confirmation) > 0:
                for banner in data_confirmation:
                    for img in banner["ids_media"]:
                        if img["category"] == "mobile":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_mobile.append({"img":data_media.url,"alt":""})
                        if img["category"] == "desktop":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_web.append({"img":data_media.url,"alt":""})
            result_obj["confirmation"] = {
                "mobile":result_mobile,
                "web":result_web
            }

            on_hold = '["on_hold"]'
            data_on_hold = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, pages=on_hold, type_banner=1)
            result_mobile, result_web = [], []
            if len(data_on_hold) > 0:
                for banner in data_on_hold:
                    for img in banner["ids_media"]:
                        if img["category"] == "mobile":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_mobile.append({"img":data_media.url,"alt":""})
                        if img["category"] == "desktop":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_web.append({"img":data_media.url,"alt":""})
            result_obj["on-hold"] = {
                "mobile":result_mobile,
                "web":result_web
            }

            payment = '["payment"]'
            data_payment = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, pages=payment, type_banner=1)
            result_mobile, result_web = [], []
            if len(data_payment) > 0:
                for banner in data_payment:
                    for img in banner["ids_media"]:
                        if img["category"] == "mobile":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_mobile.append({"img":data_media.url,"alt":""})
                        if img["category"] == "desktop":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_web.append({"img":data_media.url,"alt":""})
            result_obj["payment"] = {
                "mobile":result_mobile,
                "web":result_web
            }
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result_obj
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response
    
class BannersTrade(Resource):

    # @base.access_middleware
    def get(self,property_code, lang_code, market_code, booking_window):
        
        try:
            getMediaBanner = MediaBannersService()
            FunctionMark = FunctionsMark()
            response = {}
            result_obj = []
            if lang_code != 'null':
                lang_code = '['+'"'+str(lang_code)+'"'+']'
            else:
                raise Exception("Lang Code no encontrado, favor de verificar")
            if market_code != 'null':
                #country
                data_country = Country.query.filter(Country.country_code==market_code).first()
                id_country = data_country.iddef_country
                country_code = '['+''+str(id_country)+''+']'
                #market
                msData = FunctionMark.getMarketInfo(market_code)
                id_market = msData.iddef_market_segment
                market_code = '['+''+str(id_market)+''+']'
            else:
                raise Exception("Market no encontrado, favor de verificar")
            if booking_window == 'null':
                raise Exception("Booking Window no encontrado, favor de verificar")
            if property_code != 'null':
                data_brand = Brand.query.join(Property, Property.iddef_brand==Brand.iddef_brand\
                ).filter(Property.property_code == property_code).first()
                brand_code = None
                if data_brand is not None:
                    brand_code = data_brand.code
                property_code = '['+'"'+str(property_code)+'"'+']'
            else:
                raise Exception("Property Code no encontrado, favor de verificar")
            
            data_banner = getMediaBanner.get_media_banners_by_parameters(property_code=property_code,\
            lang_code=lang_code,brand=brand_code, market=market_code, country=country_code,\
            booking_window=booking_window, type_banner=1)
            if len(data_banner) > 0:
                for banner in data_banner:
                    for img in banner["ids_media"]:
                        if img["category"] == "trade":
                            data_media = MedModel.query.get(img["iddef_media"])
                            result_obj.append(data_media.url)
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result_obj
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        return response