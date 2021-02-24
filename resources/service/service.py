from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from models.service import ServiceSchema as ModelSchema, ServicePublicSchema as ModelPbSchema, SaveServiceSchema as SaveModelSchema, UpdateServiceSchema as UpdateModelSchema, GetDataTextLangSchema as GetDataTLSchema, GetDataContentSchema as GetDataContentSchema,GetPublicServiceSchema as GetPublicServSchema, Service as Model
from models.text_lang import TextLangSchema as TLModelSchema, TextLang as TLModel
from models.service_price import ServicePriceSchema as SPModelSchema,GetServicePriceSchema as GetSPModelSchema, ServicePrice as SPModel
from models.property_lang import PropertyLangSchema as PLModelSchema, GetPropertyLangSchema as GetPLModelSchema, PropertyLang as PLModel
from models.media_service import MediaServiceSchema as MSModelSchema, GetMediaServiceSchema as GetMSModelSchema, GetListMediaServiceSchema as GetListMSModelSchema, MediaService as MSModel
from models.media import Media as MedModel
from models.media_group import MediaGroup as MedGruModel
from models.media_type import MediaType as MedTypModel
from models.media_service import MediaService as MedSerModel, MediaServiceSchema as MedSerModelSchema
from models.service_restriction import ServiceRestriction as ServRestrModel, ServicerestrictionSchema as ServRestrModelSchema
from models.age_code import AgeCode as agcModel
from models.currency import Currency as currencyModel
from resources.media_service import AdminMediaServiceList
from resources.property.propertyHelper import FilterProperty as propertyFuntions
from resources.market_segment.marketHelper import Market as markFuntions
from resources.text_lang.textlangHelper import Filter as textFuntions
from .serviceHelper import Search as servFuntions
from resources.restriction.restricctionHelper import RestricctionFunction as resFuntions
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2
from resources.rates.rates_helper_v2 import Search as ratesFuntions
from common.util import Util
from sqlalchemy import or_, and_, case, func
import datetime
from common.public_auth import PublicAuth

class Service(Resource):
    #api-service-get-by-id
    # @base.access_middleware
    def get(self, id):
        try:
            schema = ModelSchema(exclude=('iddef_tax_rule_group','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
            data = Model.query.filter_by(iddef_service=id).all()
            service_items=schema.dump(data, many=True)
            result=[]
            for x in service_items:
                service_item=x
                schema3 = SPModelSchema(exclude=('estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
                service_price = SPModel.query.filter_by(iddef_service=id, estado=1).all()
                service_price_items=schema3.dump(service_price, many=True)
                result_services=[]
                for y in service_price_items:
                    service_price_item=y
                    result_services.append(service_price_item)
            service_item['datos_services'] = result_services
            result.append(service_item)
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

    #api-service-delete
    # @base.access_middleware
    def put(self, id, estado):
        response = {}
        try:
            schema = ModelSchema(exclude=('iddef_tax_rule_group','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
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

            model.estado = estado
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

    #api-service-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            model = Model()
            if request.json.get("iddef_service") == None:
                schema = SaveModelSchema(exclude=('iddef_tax_rule_group','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
                data = schema.load(json_data)
                model.name = data["name"]
                model.service_code = data["service_code"]
                model.iddef_pricing_type = data["iddef_pricing_type"]
                model.pricing_option = data["datos_pricing_option"]
                model.is_same_price_all_dates = data["is_same_price_all_dates"]
                model.available_upon_request = data["available_upon_request"]
                model.auto_add_price_is_zero = data["auto_add_price_is_zero"]
                model.html_icon = data["html_icon"]
                model.iddef_property = data["iddef_property"]
                model.iddef_currency = data["iddef_currency"]
                model.estado = 1
                model.usuario_creacion = user_name
                db.session.add(model)
                db.session.commit()
                for toSave4 in json_data["datos_restriction"]:
                    model4 = ServRestrModel()
                    model4.iddef_service = model.iddef_service
                    model4.iddef_restriction = toSave4
                    model4.estado = 1
                    model4.usuario_creacion = user_name
                    db.session.add(model4)
                    db.session.commit()

                for toSave2 in json_data["datos_services"]:
                    schema2 = SPModelSchema()
                    data3 = schema2.load(toSave2)
                    model3 = SPModel()
                    model3.iddef_service = model.iddef_service
                    model3.start_date = data3["start_date"]
                    model3.end_date = data3["end_date"]
                    model3.price = data3["price"]
                    model3.min_los = data3["min_los"]
                    model3.max_los = data3["max_los"]
                    model3.estado = 1
                    model3.usuario_creacion = user_name
                    db.session.add(model3)
                    db.session.commit()

                for toSave in json_data["datos_cont_lang"]:
                    schema2 = GetDataTLSchema()
                    data2 = schema2.load(toSave)
                    if data2["datos_lang"] != None:
                        for toUpdate in data2["datos_lang"]:
                            schema3 = GetDataContentSchema()
                            dataContent = schema3.load(toUpdate)
                            elementos = dataContent.keys()
                            for x in elementos:
                                model4 = TLModel()
                                model4.lang_code = data2["language_code"]
                                model4.text = dataContent[x]
                                model4.table_name = "def_service"
                                model4.id_relation = model.iddef_service
                                model4.attribute = x
                                model4.estado = 1
                                model4.usuario_creacion = user_name
                                db.session.add(model4)
                                db.session.commit()
                    if data2["data_media"] != None:
                        for toSave3 in data2["data_media"]:
                            modelM = MedSerModel()
                            modelM.iddef_service = model.iddef_service
                            modelM.iddef_media = toSave3
                            modelM.lang_code = data2["language_code"]
                            modelM.estado = 1
                            modelM.usuario_creacion = user_name
                            db.session.add(modelM)
                            db.session.commit()
            else:
                schema = UpdateModelSchema(exclude=('iddef_tax_rule_group','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
                schemaSR = ServRestrModelSchema(exclude=Util.get_default_excludes())
                schemaMS = MSModelSchema(exclude=Util.get_default_excludes())
                data = schema.load(json_data)
                model = model.query.get(json_data["iddef_service"])
                if model is None:
                    return {
                        "Code": 404,
                        "Msg": "data not found",
                        "Error": True,
                        "data": {}
                    }
                
                if request.json.get("name") != None:
                    model.name = data["name"]
                if request.json.get("service_code") != None:
                    model.service_code = data["service_code"]
                if request.json.get("iddef_pricing_type") != None:
                    model.iddef_pricing_type = data["iddef_pricing_type"]
                if request.json.get("datos_pricing_option") != None:
                    model.pricing_option = data["datos_pricing_option"]
                if request.json.get("is_same_price_all_dates") != None:
                    model.is_same_price_all_dates = data["is_same_price_all_dates"]
                if request.json.get("available_upon_request") != None:
                    model.available_upon_request = data["available_upon_request"]
                if request.json.get("auto_add_price_is_zero") != None:
                    model.auto_add_price_is_zero = data["auto_add_price_is_zero"]
                if request.json.get("html_icon") != None:
                    model.html_icon = data["html_icon"]
                if request.json.get("iddef_property") != None:
                    model.iddef_property = data["iddef_property"]
                if request.json.get("iddef_currency") != None:
                    model.iddef_currency = data["iddef_currency"]
                if request.json.get("estado") != None:
                    model.estado = data["estado"]
                model.usuario_ultima_modificacion = user_name
                db.session.commit()

                if model.iddef_service != None:
                    #Resetear todos los datos a estado 0 service_restriction
                    data_service_restriction = ServRestrModel.query.filter_by(iddef_service=json_data["iddef_service"]).all()
                    dataServiceRestriction = schemaSR.dump(data_service_restriction, many=True)

                    if dataServiceRestriction != None:
                        for y in dataServiceRestriction:
                            R = ServRestrModel.query.get(y['iddef_service_restriction'])
                            R.estado = 0
                            db.session.commit()

                    if json_data["datos_restriction"] !=None:
                        for toSave4 in json_data["datos_restriction"]:
                            data_restriction = ServRestrModel.query.filter_by(iddef_service=json_data["iddef_service"], iddef_restriction=toSave4).first()
                            if data_restriction is None:
                                modelSR = ServRestrModel()
                                modelSR.iddef_service = json_data["iddef_service"]
                                modelSR.iddef_restriction = toSave4
                                modelSR.estado = 1
                                modelSR.usuario_creacion = user_name
                                db.session.add(modelSR)
                                db.session.commit()
                            else:
                                data_restriction.iddef_service = json_data["iddef_service"]
                                data_restriction.iddef_restriction = toSave4
                                data_restriction.estado = 1
                                data_restriction.usuario_ultima_modificacion = user_name
                                db.session.commit()

                    #Resetear todos los datos a estado 0 media_service
                    data_media_service = MedSerModel.query.filter_by(iddef_service=json_data["iddef_service"]).all()
                    dataMediaService = schemaMS.dump(data_media_service, many=True)

                    if dataMediaService != None:
                        for x in dataMediaService:
                            M = MedSerModel.query.get(x['iddef_media_service'])
                            M.estado = 0
                            db.session.commit()
                    
                    if json_data["datos_services"] !=None:
                        for toSave2 in json_data["datos_services"]:
                            schema2 = GetSPModelSchema()
                            data3 = schema2.load(toSave2)
                            dataSearch2 = SPModel.query.filter_by(iddef_service_price=data3["iddef_service_price"], estado=1).first()
                            if dataSearch2 is None:
                                model3 = SPModel()
                                model3.start_date = data3["start_date"]
                                model3.end_date = data3["end_date"]
                                model3.price = data3["price"]
                                model3.min_los = data3["min_los"]
                                model3.max_los = data3["max_los"]
                                model3.usuario_creacion = user_name
                                db.session.add(model3)
                                db.session.commit()
                            else:
                                dataSearch2.iddef_service = json_data["iddef_service"]
                                dataSearch2.start_date = data3["start_date"]
                                dataSearch2.end_date = data3["end_date"]
                                dataSearch2.price = data3["price"]
                                dataSearch2.min_los = data3["min_los"]
                                dataSearch2.max_los = data3["max_los"]
                                dataSearch2.usuario_ultima_modificacion = user_name
                                db.session.commit()

                    if json_data["datos_cont_lang"] !=None:
                        for toSave in json_data["datos_cont_lang"]:
                            schema2 = GetDataTLSchema()
                            data2 = schema2.load(toSave)
                            if data2["datos_lang"] != None:
                                for toUpdate in data2["datos_lang"]:
                                    schema3 = GetDataContentSchema()
                                    dataContent = schema3.load(toUpdate)
                                    elementos = dataContent.keys()
                                    for x in elementos:
                                        dataSearch = TLModel.query.filter_by(lang_code=data2["language_code"], table_name='def_service', id_relation=json_data["iddef_service"], attribute=x, estado=1).first()
                                        if dataSearch is None:
                                            Langmodel = TLModel()
                                            Langmodel.lang_code = data2["language_code"]
                                            Langmodel.text = dataContent[x]
                                            Langmodel.table_name = "def_service"
                                            Langmodel.id_relation = json_data["iddef_service"]
                                            Langmodel.attribute = x
                                            Langmodel.estado = 1
                                            Langmodel.usuario_creacion = user_name
                                            db.session.add(Langmodel)
                                            db.session.commit()
                                        else:
                                            dataSearch.lang_code = data2["language_code"]
                                            dataSearch.text = dataContent[x]
                                            dataSearch.table_name = "def_service"
                                            dataSearch.id_relation = json_data["iddef_service"]
                                            dataSearch.attribute = x
                                            dataSearch.usuario_ultima_modificacion = user_name
                                            db.session.commit()
                            if data2["data_media"] != None:
                                for toSave3 in data2["data_media"]:
                                    dataSearchMedia = MedSerModel.query.filter_by(lang_code=data2["language_code"], iddef_service=json_data["iddef_service"], iddef_media=toSave3).first()
                                    if dataSearchMedia is None:
                                        modelM = MedSerModel()
                                        modelM.iddef_service = json_data["iddef_service"]
                                        modelM.iddef_media = toSave3
                                        modelM.lang_code = data2["language_code"]
                                        modelM.estado = 1
                                        modelM.usuario_creacion = user_name
                                        db.session.add(modelM)
                                        db.session.commit()
                                    else:
                                        dataSearchMedia.iddef_service = json_data["iddef_service"]
                                        dataSearchMedia.iddef_media = toSave3
                                        dataSearchMedia.lang_code = data2["language_code"]
                                        dataSearchMedia.estado = 1
                                        dataSearchMedia.usuario_ultima_modificacion = user_name
                                        db.session.commit()
            schema = ModelSchema(exclude=('iddef_tax_rule_group','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
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

class ServiceListSearch(Resource):
    #api-service-get-all
    # @base.access_middleware
    def get(self):
        try:
            isAll = request.args.get("all")

            data = Model()

            if isAll is not None:
                data = Model.query.all()
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=('iddef_tax_rule_group','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            service_items=schema.dump(data, many=True)
            result=[]
            for x in service_items:
                service_item=x
                schemaMedia = GetListMSModelSchema(exclude=('iddef_media_service','service','iddef_service','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
                data_media = MSModel.query.join(MedModel).join(MedGruModel).join(MedTypModel).filter(MSModel.iddef_service == service_item['iddef_service'], MedGruModel.description == "Servicios", MedTypModel.description == "IMG", MSModel.lang_code == "EN", MSModel.estado == 1).all()
                media_service_items=schemaMedia.dump(data_media, many=True)
                service_item['url'] = ""
                for x in media_service_items:
                    media_service_item=x
                    service_item['url'] = media_service_item['media']['url']
                    media_service_item.pop('media')
                result.append(service_item)    

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

class ServiceLangSearch(Resource):
    #api-service-text-lang
    # @base.access_middleware
    def get(self, id, id_property):
        try:
            result_restriction = ServRestrModel.query.filter_by(iddef_service=id, estado=1).all()
            if result_restriction is None:
                data_restriction = []
            else:
                data_restriction = []
                schemaR = ServRestrModelSchema(only=('iddef_restriction',))
                data_restric = schemaR.dump(result_restriction, many=True)
                for itm_restric in data_restric:
                    data_restriction.append(itm_restric['iddef_restriction'])
            schema = GetPLModelSchema(exclude=('iddef_property_lang','property','language','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            data2 = PLModel.query.filter_by(iddef_property=id_property, estado=1).all()
            if data2 is None:
                result_cont_lang=[]
            else:
                langs_items=schema.dump(data2, many=True)
                result_cont_lang=[]
                for x in langs_items:
                    langs_item=x
                    schema2 = TLModelSchema(exclude=('id_relation','lang_code','table_name','iddef_text_lang','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
                    text_lang = TLModel.query.filter_by(id_relation=id, table_name='def_service', lang_code=langs_item['language_code'], estado=1).all()
                    text_lang_items=schema2.dump(text_lang, many=True)
                    result_content=[]
                    result_objet_content={}
                    for x in text_lang_items:
                        text_lang_item=x
                        name=text_lang_item['attribute']
                        text_lang_item[name] = text_lang_item['text']
                        text_lang_item.pop('text')
                        text_lang_item.pop('attribute')
                        result_objet_content.update(text_lang_item)
                    result_content.append(result_objet_content)
                    if len(text_lang) == 0:
                        result_content=[]
                    langs_item['datos_lang'] = result_content
                    result_media=[]
                    DataMedia = AdminMediaServiceList.get(self,id,langs_item['language_code'],id_property,1)
                    result_media = list(filter(lambda elem_selected: elem_selected['selected'] == 1, DataMedia['data']))
                    langs_item['data_media'] = result_media
                    result_cont_lang.append(langs_item)
            schema1 = ModelSchema(exclude=('property','service_pricing_type','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
            data = Model.query.filter_by(iddef_service=id).all()
            service_items=schema1.dump(data, many=True)
            result=[]
            for x in service_items:
                service_item=x
                schema3 = SPModelSchema(exclude=('estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
                service_price = SPModel.query.filter_by(iddef_service=id, estado=1).all()
                service_price_items=schema3.dump(service_price, many=True)
                result_services=[]
                for y in service_price_items:
                    service_price_item=y
                    result_services.append(service_price_item)
                service_item['datos_services'] = result_services
                service_item['datos_cont_lang'] = result_cont_lang
                service_item['datos_restriction'] = data_restriction
                result.append(service_item)

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

class ServiceProperty(Resource):
    #api-service-property
    # @base.access_middleware
    def get(self, id_property):
        try:
            schema = ModelSchema(only=('name','service_code','iddef_service','estado',))
            data = Model.query.filter_by(iddef_property=id_property).all()
            service_items=schema.dump(data, many=True)
            result=[]
            for x in service_items:
                service_item=x
                schema3 = SPModelSchema(exclude=('estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',))
                service_price = SPModel.query.filter_by(iddef_service=service_item['iddef_service'], estado=1).first()
                if service_price is None:
                    price = 0.0
                else:
                    price = service_price.price
                service_item['price'] = price
                result.append(service_item)
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

class PublicServicePropertyLang(Resource):
    #api-public-service-lang
    @PublicAuth.access_middleware
    def get(self,id_property, market,lang_code):
        return PublicServicePropertyLang.getInfoService(id_property, market, lang_code)

    @staticmethod
    def getInfoService(id_property, market, lang_code):
        try:
            markFuntion = markFuntions()
            msData = markFuntion.getMarketInfo(market)
            msId = msData.iddef_market_segment
            schema = ModelSchema(only=('iddef_service','html_icon'))
            #Obtenemos informacion de los servicios sin restrinccion
            data_serv_restr = ServRestrModel.query.with_entities(ServRestrModel.iddef_service).filter(ServRestrModel.estado == 1).subquery()
            data_serv = Model.query.filter(Model.iddef_service.notin_(data_serv_restr), Model.estado==1, Model.iddef_property==id_property).all()
            #Obtenemos informacion de las restrincciones
            # data_restrictions = resFuntions.getRestrictionDetails(restriction_by=6, restriction_type=4, market_targeting=msId, geo_targeting_country=market)
            obj = resFuntions2(restriction_by=6, restriction_type=4, market_targeting=msId, geo_targeting_country=market)
            data_restrictions = obj.get_restriction_details()
            if len(data_restrictions) > 0:
                #Se extraen los ids de restricciones
                ids_restrictions = [restriction_elem["iddef_restriction"] for restriction_elem in data_restrictions] 
                #Obtenemos informacion de servicios con las restrincciones activas
                data_services_restrictions = ServRestrModel.query.with_entities(ServRestrModel.iddef_service)\
                .filter(ServRestrModel.iddef_restriction.in_(ids_restrictions), \
                ServRestrModel.estado == 1).subquery()
                data_serv2 = Model.query.filter(Model.iddef_service.in_(data_services_restrictions), Model.estado==1, Model.iddef_property==id_property).all()
                data_srv = data_serv + data_serv2
            else:
                data_srv = data_serv
            services_items=schema.dump(data_srv, many=True)
            if data_srv is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                result=[]
                for x in services_items:
                    text, text2 = "", ""
                    data = TLModel.query.filter_by(id_relation=x['iddef_service'], table_name='def_service', lang_code=lang_code, attribute='Name', estado=1).first()
                    if data is not None:
                        text = data.text
                    data2 = TLModel.query.filter_by(id_relation=x['iddef_service'], table_name='def_service', lang_code=lang_code, attribute='icon_description', estado=1).first()
                    if data2 is not None:
                        text2 = data2.text
                    x['name_html_icon'] = text
                    x['description_html_icon'] = text2
                    result.append(x)
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

class ServicePropertyAdditional(Resource):
    #api-public-service-additional
    @PublicAuth.access_middleware
    def post(self):
        try:
            markFuntion = markFuntions()
            propFuntion = propertyFuntions()
            textFuntion = textFuntions()
            servFuntion = servFuntions()
            ratesHelper = ratesFuntions()
            json_data = request.get_json(force=True)
            load_schema = GetPublicServSchema()
            data = load_schema.load(json_data)
            date_start = data["date_start"]
            date_end = data["date_end"]
            #Obtenemos los dias de la reserva
            rangeDay = date_end - date_start
            rangeDay = rangeDay.days
            if request.json.get("lang_code") != None:
                lang_code = data["lang_code"]
            else:
                lang_code = "EN"
            if request.json.get("market") != None:
                market = data["market"]
            else:
                market = "CR"
            if request.json.get("services") != None:
                services = data["services"]
            else:
                services = []
            if request.json.get("currency_code") != None:
                currency_code = data["currency_code"]
            else:
                currency_code = "USD"
            #Obtenemos informacion del mercado seleccionado
            msData = markFuntion.getMarketInfo(market)
            msId = msData.iddef_market_segment
            #Obtenemos informacion de la propiedad seleccionada
            hotel = propFuntion.getHotelInfo(data["id_hotel"])
            id_property = hotel.iddef_property
            #Validacion con el catalogo age code
            agcData = agcModel.query.filter(agcModel.estado==1).all()
            age_code = [item.code for item in agcData]
            total_rooms = 0
            total_packs = 0
            for paxes in data["rooms"]:
                total_rooms += 1
                elemnts = paxes.keys()
                for x in elemnts:
                    if x in age_code:
                        total_packs += paxes[x]
            #Consulta de servicios
            try:
                result=[]
                data_services_items = servFuntion.get_service_by_additional(services,date_start,date_end,msId,id_property,total_rooms,total_packs,market)
                elementos = ["Name","Teaser","Description","icon_description"]
                if len(data_services_items)>0:
                    for x in data_services_items:
                        id_service = x['iddef_service']
                        data_traslate = servFuntion.get_service_by_lang_elements(id_service,elementos,lang_code)
                        x.update(data_traslate)
                        result_media=[]
                        DataMedia = AdminMediaServiceList.get(self,id_service,lang_code,id_property,1)
                        result_media = list(filter(lambda elem_selected: elem_selected['selected'] == 1, DataMedia['data']))
                        x['data_media'] = result_media
                        #convertimos precio si es necesario
                        if int(x["price"]) != 0:
                            amount_service = x["price"]
                            currency_data = currencyModel.query.get(x["iddef_currency"])
                            currency_service = currency_data.currency_code
                            exange_apply, to_usd_amount, exange_amount, exange_amount_tag = ratesHelper.get_currency_rate(currency_code,currency_service)
                            if exange_apply == True:
                                #Primero convertimos a dolares
                                amount_service = round(amount_service / to_usd_amount,2)
                                #De dolares convertimos al tipo de cambio solicitado
                                amount_service = round(amount_service * exange_amount,2)
                            x["price"] = amount_service
                        x.pop('iddef_currency')
                        result.append(x)
            except Exception as servEx:
                pass #raise Exception ("Error: "+str(servEx))
            
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
    

