from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError, EXCLUDE
from config import db, base
from models.property import GetHoldPublicSchema as GetHoldPublic, PublicProperty as GetPublicProperty,\
PropertySchema as ModelSchema, GetPropertySchema as GetModelSchema, GetListPropertySchema as GetListModelSchema,\
GetListFilterPropertySchema as GetListFilterModelSchema, GetSearchHotelsSchema as GetSHModelSchema,\
GetSearchRoomsSchema as GetSRModelSchema, GetDataRoomsSchema as GetDRModelSchema,\
GetDataRatePlanSchema as GetDRPModelSchema, Property as Model, PublicPropertyInfo as GetPublicPropertyInfo,\
PublicPropertyAmenityMedia as GetPublicPropertyAmenity
from models.property_filters import PropertyFiltersSchema as filtersSchema, PropertyFilters as filterModel, getPropertyByFilters as getpropertybyfilters
from models.property_lang import PropertyLang as PropertyLangModel, PropertyLangSchema 
from models.media import MediaSchema as MModelSchema, publicGetListMedia as publicSchema
from models.media_property import MediaPropertySchema as MedModelSchema, GetMediaPropertySchema as GetMedModelSchema, GetListMediaPropertySchema as GetListMedModelSchema, MediaProperty as MedModel
from models.rateplan import RatePlanSchema as RPModelSchema, RatePlan as RPModel
from models.rateplan_property import RatePlanPropertySchema as RPProModelSchema, RatePlanProperty as RPProModel
from models.rate_plan_rooms import RatePlanRoomsSchema as RPRModelSchema, RatePlanRooms as RPRModel
from models.room_type_category import RoomTypeCategorySchema as RTCModelSchema, RoomTypeCategory as RTCModel
from models.rateplan_prices import RatePlanPricesSchema as RPPModelSchema, RatePlanPrices as RPPModel
from models.cross_out_config import CrossOutConfigSchema as COCModelSchema, CrossOutConfig as COCModel
from models.sistemas import SistemasSchema as SModelSchema, Sistemas as SModel
from models.crossout_rate_plan import CrossoutRatePlanSchema as CRPModelSchema, CrossoutRatePlan as CRPModel
from models.market_segment import MarketSegmentSchema as MSModelSchema, MarketSegment as MSModel
from models.property_description import PropertyDescriptionSchema as PDodelSchema, PropertyDescription as PDModel
from resources.rateplan import RatePlanPublic as funtions_policy
from resources.rates.RatesHelper import RatesFunctions as funtions
from resources.media_property import PublicMediaPropertyList
from resources.property_amenity import PropertyAmenityDescriptions as funtions_amenity
#from resources.policy import PolicyListPropertySearch
from resources.room_amenity import RoomAmenityDescriptions as funtions_amennity_room
from resources.service import PublicServicePropertyLang
from resources.media_room import AdminMediaRoomList
from resources.media.MediaHelper import MediaFunctions as MedFunctions
from .property_service import PropertyService
from models.media_room import GetMediaRoomAdminSchema
from models.languaje import GetLanguajeSchema, LanguajeSchema,  Languaje
from common.util import Util
from sqlalchemy import or_, and_
import datetime
from datetime import datetime as dt
from dateutil.parser import parse
from common.public_auth import PublicAuth
from resources.restriction.restricctionHelper import RestricctionFunction as resfunction
from resources.terms_and_conditions.terms_and_conditions_service import TermsAndConditionsService
from models.media_group import MediaGroup, MediaGroupSchema

#Apis administrativas
class Property(Resource):

    #Administrador
    #api-property-get-by-id
    # @base.access_middleware
    def get(self,id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())            
            data = Model.query.get(id)
            dataDumped = schema.dump(data)
            
            pLangschema = PropertyLangSchema(exclude=Util.get_default_excludes())
            propertyLangs = PropertyLangModel.query.add_columns(PropertyLangModel.iddef_language).filter(PropertyLangModel.iddef_property == id, PropertyLangModel.estado ==1)
            propertyLangsJson = pLangschema.dump(propertyLangs, many=True)
            
            idLangs = []
            idFilters= []

            for x in propertyLangsJson:
                idLangs.append(x["iddef_language"])
            dataDumped["property_lang"] = idLangs

            pFiltersSchema = filtersSchema(exclude=Util.get_default_excludes())
            propertyFilters = filterModel.query.add_columns(filterModel.iddef_filter).filter(filterModel.iddef_property == id, filterModel.estado == 1)
            propertyFiltersJson = pFiltersSchema.dump(propertyFilters, many=True)

            for xF in propertyFiltersJson:
                idFilters.append(xF["iddef_filter"])
            dataDumped["filters"] = idFilters

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
                    "data": dataDumped
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

    #Administrador
    #api-property-put
    # @base.access_middleware
    def put(self, id):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data,unknown=EXCLUDE)
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
            
            exist_interface = PropertyService.validate_code_property(data["property_code"],user_name)
            if exist_interface["error"]:
                raise Exception(exist_interface["message"])
            else:
                if exist_interface["validate"] is False:
                    raise Exception("The property code %s invalid" % data["property_code"])

            model.short_name = data["short_name"]
            model.trade_name = data["trade_name"]
            model.icon_logo_name = data["icon_logo_name"]
            model.property_code = data["property_code"]
            model.web_address = data["web_address"]
            #model.currency_code = data["currency_code"]
            #model.time_zone = data["time_zone"]
            model.iddef_brand = data["iddef_brand"]
            model.iddef_property_type = data["iddef_property_type"]
            model.iddef_time_zone = data["iddef_time_zone"]
            model.estado = data["estado"]
            model.usuario_ultima_modificacion = user_name
            db.session.flush()
            #grabar en property_lang para lenguajes
            pLangschema = PropertyLangSchema(exclude=Util.get_default_excludes())
            propertyLangs = PropertyLangModel.query.filter(PropertyLangModel.iddef_property == id)
            propertyLangsJson = pLangschema.dump(propertyLangs, many=True)
            
            for x in propertyLangsJson:
                #recorremos y damos de baja
                L = PropertyLangModel.query.get(x["iddef_property_lang"])
                L.estado = 0
                db.session.flush()

            for langs in data["property_lang"]:
                if langs not in [x["iddef_language"] for x in propertyLangsJson]:
                    
                    #insertamos en la tabla
                    pModel = PropertyLangModel()
                    pModel.iddef_property = id,
                    pModel.iddef_language = langs
                    pModel.estado = 1
                    db.session.add(pModel)
                    db.session.flush()
                else:
                    #acualizamos el registro si ya existe
                    value = [x for x in propertyLangsJson \
                    if x["iddef_language"] == langs\
                    and x["iddef_property"] == id]
                    langUpdate = PropertyLangModel.query.get(value[0]["iddef_property_lang"])
                    langUpdate.estado = 1

            #grabar en property_filter para los filtros
            #filterModel
            pFiltersSchema = filtersSchema(exclude=Util.get_default_excludes())
            propertyFilters = filterModel.query.filter(filterModel.iddef_property == id)
            propertyFiltersJson = pFiltersSchema.dump(propertyFilters, many=True)
            
            for x in propertyFiltersJson:
                #recorremos y damos de baja
                F = filterModel.query.get(x["iddef_property_filters"])
                F.estado = 0
                db.session.flush()

            for filters in data["filters"]:
                
                if filters not in [x["iddef_filter"] for x in propertyFiltersJson]:
                    #insertamos en la tabla
                    fModel = filterModel()
                    fModel.iddef_property = id
                    fModel.iddef_filter = filters
                    fModel.estado = 1
                    db.session.add(fModel)
                    db.session.flush()
                else:
                    #actualizamos el registro ya existente
                    value = [x for x in propertyFiltersJson \
                        if x["iddef_filter"]== filters\
                        and x["iddef_property"]== id]
                    filterUpdate = filterModel.query.get(value[0]["iddef_property_filters"])
                    filterUpdate.estado =1

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
    
    #Administrador
    #api-property-delete
    # @base.access_middleware
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

    #Administrador
    #api-property-post
    # @base.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data, unknown=EXCLUDE)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']

            exist_interface = PropertyService.validate_code_property(data["property_code"],user_name)
            if exist_interface["error"]:
               raise Exception(exist_interface["message"])
            else:
               if exist_interface["validate"] is False:
                   raise Exception("The property code %s invalid" % data["property_code"])

            model = Model()

            model.short_name = data["short_name"]
            model.trade_name = data["trade_name"]
            model.icon_logo_name = data["icon_logo_name"]
            model.property_code = data["property_code"]
            model.web_address = data["web_address"]
            #model.currency_code = data["currency_code"]
            #model.time_zone = data["time_zone"]
            model.iddef_brand = data["iddef_brand"]
            model.iddef_property_type = data["iddef_property_type"]    
            model.iddef_time_zone = data["iddef_time_zone"]        
            model.estado = data["estado"]
            #model.iddef_area_unit = 1
            #model.iddef_property_category = 1
            #model.iddef_segment = 1
            #model.iddef_zone = 1
            model.usuario_creacion = user_name


            existsProperty = Model.query.filter_by(property_code = model.property_code).first()

            if existsProperty:
                raise Exception("The property code %s exists" % model.property_code)

            db.session.add(model)
            db.session.flush()

            #property_lang
            for langs in data["property_lang"]: 
                pModel = PropertyLangModel() 
                pModel.iddef_property = model.iddef_property, 
                pModel.iddef_language = langs 
                pModel.estado = 1 
                pModel.usuario_creacion = user_name 
                db.session.add(pModel) 
                db.session.flush() 
            
            #media_group
            dump_model= schema.dump(model)
            MGModel = MediaGroup()
            MGModel.iddef_property = dump_model['iddef_property']
            MGModel.description = data["short_name"]
            MGModel.estado = 1
            MGModel.usuario_creacion = user_name
            db.session.add(MGModel)
            db.session.flush()

            #property_filter
            for filters in data["filters"]:
                fModel = filterModel() 
                fModel.iddef_property = model.iddef_property
                fModel.iddef_filter = filters
                fModel.estado = 1
                fModel.usuario_creacion = user_name
                db.session.add(fModel)
                db.session.flush()

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
                "data" : {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data" : {}
            }
        
        return response

class PropertyListSearch(Resource):

    #Administrador
    #api-property-get-all
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

            dumpData = schema.dump(data)

            for propertyItem in dumpData:
                try:

                    id_Property = propertyItem["iddef_property"]

                    mediaInfo = MedFunctions.GetMediaProperty(idProperty=id_Property,MediaType=1,only_one=True)

                    propertyItem["image_url"] = mediaInfo.url

                except Exception as exe:

                    propertyItem["image_url"] = None
            
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
                    "data": dumpData
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class PropertySearch(Resource):

    #Administrador
    #api-property-plans-get-all
    # @base.access_middleware
    def get(self):
        try:
            property_code = request.args.get("property")
            isall = request.args.get("all")

            data = Model()

            if property_code is not None:
                data = Model.query.filter(Model.iddef_property==property_code, Model.estado==1)
            else:
                data = Model.query.filter(Model.estado==1)

            schema = ModelSchema(exclude=Util.get_default_excludes(), many=True)
            RPchema = RPModelSchema(exclude=('usuario_creacion','fecha_creacion','usuario_ultima_modificacion','fecha_ultima_modificacion','crossout_rate_plans','rateplan_restrictions',), many=True)

            dumpData = schema.dump(data)

            for propertyItem in dumpData:

                #esta alreves, si no se envia un parametro devuelve todos los rateplans 
                #incluyendo los inactivados
                if isall is None:
                    data_rates_plans = RPModel.query.join(RPProModel,\
                    RPProModel.id_rateplan==RPModel.idop_rateplan)\
                    .filter(RPProModel.id_property==propertyItem["iddef_property"],\
                    RPProModel.estado==1).all()
                else:
                    data_rates_plans = RPModel.query.join(RPProModel,\
                    RPProModel.id_rateplan==RPModel.idop_rateplan)\
                    .filter(RPProModel.id_property==propertyItem["iddef_property"],\
                    RPProModel.estado==1,RPModel.estado==1).all()

                #data_rates_plans = RPModel.query.join(RPProModel).filter(RPModel.estado==1, RPProModel.id_property==propertyItem["iddef_property"]).all()
                #data_rates_plans = RPModel.query.join(RPProModel,RPProModel.id_rateplan==RPModel.idop_rateplan).filter(RPProModel.id_property==propertyItem["iddef_property"]).all()
                result_plans = []
                if len(data_rates_plans)>0:
                    dumpDataRP = RPchema.dump(data_rates_plans)
                    for item in dumpDataRP:
                        listRoom = []
                        if item["rate_plan_rooms"] is not None:
                            for itemRoom in item["rate_plan_rooms"]:
                                if itemRoom["estado"] != 0:
                                    if itemRoom["rooms"]["estado"] == 1 and itemRoom["rooms"]["iddef_property"] ==propertyItem["iddef_property"]:
                                        room_name = funtions.getTextLangInfo("def_room_type_category",\
                                        "room_name","en",itemRoom["rooms"]["iddef_room_type_category"])
                                        if room_name is None:
                                            room_description = ""
                                        else:
                                            room_description = room_name.text
                                        objtRoom = {
                                            "id_room":itemRoom["rooms"]["iddef_room_type_category"],
                                            "room_code":itemRoom["rooms"]["room_code"],
                                            "room_description":room_description
                                        }
                                        listRoom.append(objtRoom)
                        item.pop('rate_plan_rooms')
                        item["rate_plan_rooms"] = listRoom
                        result_plans.append(item)
            
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
                    "data": result_plans
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

##Apis Publicas
class PropertyPublic(Resource):
    
    #Public
    #api-public-property-get-by-id
    @PublicAuth.access_middleware
    def get(self, id):
        try:
            schema = GetListModelSchema(exclude=Util.get_default_excludes())            
            data = Model.query.get(id)

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
    
class PublicPropertyListSearch(Resource):

    #Publica
    #api-public-property-get-all-v2
    @PublicAuth.access_middleware
    def post(self):
        try:
            dataResponse = []
            schema = GetListFilterModelSchema(exclude=Util.get_default_excludes(), many=True)
            schemaRP = RPModelSchema(exclude=Util.get_default_excludes())
            schemaRPP = RPPModelSchema(exclude=Util.get_default_excludes())
            schemaRPR = RPRModelSchema(exclude=Util.get_default_excludes())

            loadSchema = getpropertybyfilters()

            dataRq = request.get_json(force=True)

            loadSchema.load(dataRq)

            filtersData = dataRq["filters"]

            conditions = []

            conditions.append(Model.estado == 1)

            data = None

            listItems = []
            if filtersData is not None:

                for item in filtersData:
                    listItems.append(item)
                
                if len(listItems) > 0:
                    conditions.append(filterModel.iddef_property == Model.iddef_property)
                    conditions.append(filterModel.iddef_filter.in_(listItems))

                    data = Model.query.join(filterModel).filter(and_(*conditions))
                else:
                    data = Model.query.filter(and_(*conditions))

            else:
                data = Model.query.filter(and_(*conditions))

            if request.json.get("arrival_date") != None:
                date_start = parse(dataRq["arrival_date"]).date()
            else:
                date_start = datetime.date.today()
            if request.json.get("end_date") != None:
                date_end = parse(dataRq["end_date"]).date()
            else:
                date_end = date_start + datetime.timedelta(days=15)
            totalDay = date_end - date_start
            totalDay = totalDay.days

            if request.json.get("lang_code") != None:
                lang_code = dataRq["lang_code"]
            else:
                lang_code = "EN"
            if request.json.get("currency") != None:
                currency = dataRq["currency"]
            else:
                currency = "USD"
            if request.json.get("promo_code") != None:
                promo_code = dataRq["promo_code"]
            dataMarket = funtions.getMarketInfo(dataRq["market"],lang_code)
            id_market_segment = dataMarket.iddef_market_segment
            dataProperty = schema.dump(data, many=True)

            for k in dataProperty:
                if type(k) is dict:
                    kL = {}
                    for f in k:
                        if type(k[f]) is str:
                            if f != "web_address" and f != "property_code":
                                kL.setdefault(f, k[f].capitalize())
                            else:
                                kL.setdefault(f, k[f])
                        else:
                            kL.setdefault(f, k[f])
                idP = kL
                idProperty = idP['iddef_property']
                codeProperty = idP['property_code']
                try:

                    #Obtenemos todos los rate plans disponibles para esa propiedad, mercado
                    # y rango de fechas seleccionados
                    dataRatePlans = funtions.getRateplanInfo(property_id=idProperty,\
                    date_start=date_start,date_end=date_end,\
                    market_id=id_market_segment,bookin_window=False,only_one=False,language=lang_code)

                    rates_info = []

                    porcentaje = 0,
                    avg_night_price_crossout = 0
                    avg_night_price = 0

                    #Obtenemos las tarifas de cada uno de los rate plans encontrados
                    for rate_plan in dataRatePlans:

                        try:
                            #Asignamos el id del rate plan a evaluar
                            idRate_plan = rate_plan.idop_rateplan

                            #obtenemos la habitacion con mayor prioridad de la lista
                            #de habitaciones mapeadas para este rate plan
                            roomsRatePlan = funtions.getRoomTypesForRatePlan(idRate_plan,\
                            idProperty,only_firts=True)

                            #asignamos la informacion del cuarto por defecto
                            roomId = roomsRatePlan.iddef_room_type_category
                            roomStd = roomsRatePlan.standar_ocupancy

                            #obtenemos las tarifas por dia
                            rates = funtions.getPricePerDay(idProperty,roomId,idRate_plan,\
                            date_start,date_end,roomStd,0,currency=currency)

                            #Creamos un objeto para la lista
                            detail = {
                                "porcentaje":rates["total_percent_discount"],
                                "avg_night_price_crossout":rates["total_crossout"],
                                "avg_night_price":rates["total"],
                                "nigts":rates["nights"]
                            }

                            #Agregamos el objeto a una lista                    
                            rates_info.append(detail)
                            
                        except Exception as ratesExection:
                            #En caso de encontrar un error al obtener las tarifas ignoramos este rate plan
                            pass


                    #Eliminamos las tarifas en 0 que se hayan encontrado
                    rates_info = list(filter(lambda elem_price: elem_price['avg_night_price'] > 0, rates_info))

                    #ordenamos la lista segun su precio total
                    rates_info.sort(key=lambda r: r["avg_night_price"])

                    if len(rates_info) > 0:
                        if rates_info[0]["nigts"] > 0:
                            porcentaje = rates_info[0]["porcentaje"]
                            porcentaje = round(porcentaje,0)
                            avg_night_price = rates_info[0]["avg_night_price"] / rates_info[0]["nigts"]
                            avg_night_price = round(avg_night_price,2)
                            avg_night_price_crossout = rates_info[0]["avg_night_price_crossout"] / rates_info[0]["nigts"]
                            avg_night_price_crossout = round(avg_night_price_crossout,2)

                    idP['porcent_discount']= int(porcentaje)
                    idP['avg_night_price_crossout']=avg_night_price_crossout
                    idP['avg_night_price']=avg_night_price

                    PropertyDescription = PDModel.query.filter(PDModel.estado == 1, PDModel.iddef_property == idProperty, PDModel.iddef_description_type == 1, PDModel.lang_code == lang_code).first()
                    if PropertyDescription is None:
                        description = ''
                    else:
                        description = PropertyDescription.description
                    idP['description']=description.capitalize()
                    MediaProperty = []
                    try:
                        dataMediaProperty = MedFunctions.GetMediaProperty(idProperty=idProperty,\
                        MediaType=1, only_one=False)

                        mediaSchemaDet = publicSchema()

                        if len(dataMediaProperty) > 0:
                            mediaItem = mediaSchemaDet.dump(dataMediaProperty,many=True)

                            MediaProperty = mediaItem

                    except Exception as ermp:
                        response = {
                            "Code": 500,
                            "Msg": str(ermp),
                            "Error": True,
                            "data": {}
                        }
                        #MediaProperty.append(response)
                    DataPropertyService = PublicServicePropertyLang.get(self,idProperty, lang_code)
                    if len(DataPropertyService) == 0:
                        PropertyService = []
                    else:
                        PropertyService= DataPropertyService["data"]
                    idP['service']=PropertyService
                    idP['media']=MediaProperty
                    DataAmenity = funtions_amenity.get_amenities_by_property_lang(idProperty, lang_code)
                    if len(DataAmenity) == 0:
                        PropertyAmenity = []
                    else:
                        PropertyAmenity = list(filter(lambda elem_priority: elem_priority['is_priority'] == 1, DataAmenity))
                    idP['amenities']=PropertyAmenity
                    idP['area_unit']=idP['area_unit_p']['description'].capitalize()
                    idP['unit_code']=idP['area_unit_p']['unit_code'].capitalize()
                    idP.pop('area_unit_p')
                    dataResponse.append(idP)
                except Exception as erp:
                    response = {
                        "Code": 500,
                        "Msg": str(erp),
                        "Error": True,
                        "data": {}
                    }
                    #dataResponse.append(response)    
            if dataResponse is None:
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": {}
                }
            else:
                dataResponseFilter = list(filter(lambda elem_price: elem_price['avg_night_price'] > 0, dataResponse))
                dataResponseFilter.sort(key=lambda avg_price: avg_price["avg_night_price"])
                response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": dataResponseFilter
                }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data" : {}
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class PropertyPublicSearchRooms(Resource):
    #Publica: api-public-property-search-rooms-get
    @PublicAuth.access_middleware
    def post(self):
        try:
            json_data = request.get_json(force=True)
            schema = GetListFilterModelSchema(exclude=Util.get_default_excludes())
            schema2 = GetSRModelSchema()
            schema3 = GetDRPModelSchema()
            schemaRP = RPModelSchema(exclude=Util.get_default_excludes())
            schemaRPR = RPRModelSchema(exclude=Util.get_default_excludes())
            schemaRPP = RPPModelSchema(exclude=Util.get_default_excludes())
            schemaRTC = RTCModelSchema(exclude=Util.get_default_excludes())
            schemaCOC = COCModelSchema(exclude=Util.get_default_excludes())
            data = schema2.load(json_data)
            if request.json.get("lang_code") != None:
                lang_code = data["lang_code"]
            else:
                lang_code = "EN"
            if request.json.get("currency") != None:
                currency = data["currency"]
            else:
                currency = "USD"
            market = data["market"]
            property_code = data["hotel_code"]
            date_start = data["arrival_date"]
            date_end = data["end_date"]
            rangeDay = date_end - date_start
            rangeDay = rangeDay.days
            promo_code = data["promo_code"]
            dataMarket = funtions.getMarketInfo(market,lang_code)
            id_market_segment = dataMarket.iddef_market_segment
            dataHotel = Model.query.filter(Model.property_code==property_code, Model.estado==1).all()
            dataResult = []
            totalListRoom = []
            rooms_items=schema.dump(dataHotel, many=True)
            for k in rooms_items:
                if type(k) is dict:
                    kL = {}
                    for f in k:
                        if type(k[f]) is str:
                            if f != "web_address" and f != "property_code":
                                kL.setdefault(f, k[f].capitalize())
                            else:
                                kL.setdefault(f, k[f])
                        else:
                            kL.setdefault(f, k[f])
                x = kL
                idProperty = x['iddef_property']
                try:
                    data_RatePlans = funtions.getRateplanInfo(property_id=idProperty,date_start=date_start,date_end=date_end,market_id=id_market_segment,bookin_window=True,only_one=False,language=lang_code)
                    RatePlans_items=schemaRP.dump(data_RatePlans, many=True)
                    total_percent = 0
                    dataResultRoom = []
                    listRoom = []
                    listRoom2 = []
                    avg_night_price = 0
                    avg_night_price_crossout = 0
                    dataRatePlan = []
                    response_rate_plan = {}
                    for itemRP in RatePlans_items:
                        id_rate_plan = itemRP['idop_rateplan']
                        try:
                            dataTextLangPlan = funtions.getTextLangInfo('op_rateplan','commercial_name',lang_code,id_rate_plan)
                            if dataTextLangPlan is not None:
                                name_Plan = dataTextLangPlan.text #
                            else:
                                name_Plan = ''
                        except Exception as ertlp:
                            response = {
                                "Code": 500,
                                "Msg": str(ertlp),
                                "Error": True,
                                "data": {}
                            }
                            #listRoom.append(response)
                        id_rate_plan_code = itemRP['code']
                        response_rate_plan = {
                            "id_rate_plan": id_rate_plan,
                            "plan_code": id_rate_plan_code,
                            "plan_name": name_Plan
                        }
                        dataRatePlan.append(response_rate_plan)
                        dataRatePlanRooms = funtions.getRoomTypesForRatePlan(id_rate_plan,idProperty,only_firts=False)
                        if dataRatePlanRooms is not None and len(dataRatePlanRooms) > 0:
                            RatePlanRooms_items=schemaRTC.dump(dataRatePlanRooms, many=True)
                            room_list = {}
                            cont_room = 0
                            for room_item in RatePlanRooms_items:
                                cont_room += 1
                                idroom_type = room_item['iddef_room_type_category']
                                acept_chd = room_item['acept_chd']
                                standar_ocupancy = room_item['standar_ocupancy']
                                max_pax = room_item['max_ocupancy']
                                area = room_item['area']
                                try:
                                    dataTextLangRoom2 = funtions.getTextLangInfo('def_room_type_category','room_name',lang_code,idroom_type)
                                    if dataTextLangRoom2 is not None:
                                        nameRoom = dataTextLangRoom2.text
                                    else:
                                        nameRoom = ''
                                except Exception as ertl:
                                    response = {
                                        "Code": 500,
                                        "Msg": str(ertl),
                                        "Error": True,
                                        "data": {}
                                    }
                                    #listRoom.append(response)

                                DataRoomAmenity = funtions_amennity_room.get_amenities_by_room_type_lang(idroom_type, lang_code)
                                if len(DataRoomAmenity) == 0:
                                    RoomAmenity = []
                                else:
                                    RoomAmenity = DataRoomAmenity

                                mediaInfo = MedFunctions.GetMediaRoom(idRoom=idroom_type,only_one=False)

                                schemaRoomMedia = GetMediaRoomAdminSchema(exclude=Util.get_default_excludes(),many=True)

                                MediaRoom = schemaRoomMedia.dump(mediaInfo)

                                #resultMediaRoom = AdminMediaRoomList.get(self,idroom_type)
                                #MediaRoom = list(filter(lambda elem_selected: elem_selected['selected'] == 1, resultMediaRoom['data']))
                                room_list = {
                                    "iddef_room_type":idroom_type,
                                    "trade_name_room":nameRoom,
                                    "acept_chd":acept_chd,
                                    "standar_ocupancy":standar_ocupancy,
                                    "max_pax":max_pax,
                                    "area":area,
                                    "media":MediaRoom,
                                    "amenities":RoomAmenity
                                    #,"policies": RoomPolicy
                                    }
                                dataResultRoom.append(room_list)
                        else:
                            response = {
                                "Code": 200,
                                "Msg": "Success",
                                "Error": False,
                                "data": {}
                            }
                            #dataResultRoom.append(response)

                    for room in dataResultRoom:
                        id_room = room['iddef_room_type']
                        if id_room not in listRoom2:
                            listRoom2.append(room['iddef_room_type'])
                            listRoom.append(room)

                    #Busqueda por cuarto
                    totalListRoom = []
                    for y in data["rooms"]:
                        if ("adults" in y):
                            adults = y["adults"]
                        else:
                            adults = 0
                        if ("teens" in y):    
                            teens = y["teens"]
                        else:
                            teens = 0
                        if ("kids" in y):    
                            kids = y["kids"]
                        else:
                            kids = 0
                        if ("infants" in y):    
                            infants = y["infants"]
                        else:
                            infants = 0
                        totalChild = teens + kids + infants
                        totalOcupacity = adults + kids + teens + infants
                        #rate-plans existentes
                        band_room = False # bandera para filtrar habitacion por pax
                        for itemRoom in listRoom:
                            #validar cuarto que sea menor al max pax
                            if totalOcupacity <= itemRoom['max_pax']:
                                band_room = True
                                if totalChild > 0:
                                    if itemRoom['acept_chd'] != 0:
                                        band_room = True
                                    else:
                                        band_room = False
                                else:
                                    band_room = True
                            else:
                                band_room = False
                            if totalOcupacity != 0:
                                totalAdults = adults
                            else:
                                totalAdults = itemRoom['standar_ocupancy']
                            if band_room == True:
                                TotalTarifa = []
                                itemsTarifa = []
                                RoomPolicy = []
                                for itemRate in dataRatePlan:
                                    #filtrar  politicas por rate
                                    item_policys = [] 
                                    DataRoomPolicy = funtions_policy.get(self,itemRate['id_rate_plan'], lang_code)
                                    if len(DataRoomPolicy) > 0:
                                        item_policys = DataRoomPolicy["data"]
                                        RoomPolicy += item_policys
                                    itemRoom['policies'] = RoomPolicy
                                    #calculo de tarifa por cuarto
                                    dataRatePlanPrices = funtions.getPricePerDay(idProperty,itemRoom['iddef_room_type'],itemRate['id_rate_plan'],date_start,date_end,totalAdults,totalChild,currency=currency)
                                    
                                    if dataRatePlanPrices['total'] != 0:
                                        night_price = 0
                                        if dataRatePlanPrices['nights'] == 0:
                                            night_price = 0
                                        else: 
                                            night_price = dataRatePlanPrices['total'] / dataRatePlanPrices['nights']
                                            percent_discount = int(dataRatePlanPrices["total_percent_discount"])
                                            night_price_cross = funtions.calculateRate(percent_discount,night_price)

                                        dataRatePlanPrices2 = schema3.dump(dataRatePlanPrices)
                                        dataRatePlanPrices2.setdefault("idop_rate_plan", itemRate['id_rate_plan'])
                                        dataRatePlanPrices2.setdefault("plan_name", itemRate['plan_name'])
                                        dataRatePlanPrices2.setdefault("plan_code", itemRate['plan_code'])
                                        dataRatePlanPrices2.setdefault("night_price", round(night_price,2))
                                        dataRatePlanPrices2["total_crossout"] = round(night_price_cross,2)
                                        TotalTarifa.append(dataRatePlanPrices2)
                                    else:
                                        pass
                                itemRoom['rates_plan'] = TotalTarifa
                                totalListRoom.append(itemRoom)
                            else:
                                pass
                                
                except Exception as erp:
                    response = {
                        "Code": 500,
                        "Msg": str(erp),
                        "Error": True,
                        "data": {}
                    }
                    #dataResult.append(response)
                PropertyDescription = PDModel.query.filter(PDModel.estado == 1, PDModel.iddef_property == idProperty, PDModel.iddef_description_type == 1, PDModel.lang_code == lang_code).first()
                if PropertyDescription is None:
                    description = ''
                else:
                    description = PropertyDescription.description
                x['description']=description.capitalize()
                #PropertyPolicy = PolicyListPropertySearch.get(self,idProperty)
                #x['polices']=PropertyPolicy["data"]
                dataResponseFilterRoom = list(filter(lambda elem_rates_plan: elem_rates_plan['rates_plan'] != [], totalListRoom))
                x['room']=dataResponseFilterRoom
                MediaProperty = []
                try:
                    dataMediaProperty = MedFunctions.GetMediaProperty(idProperty=idProperty,\
                    MediaType=1, only_one=False)

                    mediaSchemaDet = publicSchema()

                    if len(dataMediaProperty) > 0:
                        mediaItem = mediaSchemaDet.dump(dataMediaProperty,many=True)
                        MediaProperty = mediaItem

                except Exception as ermp:
                    response = {
                        "Code": 500,
                        "Msg": str(ermp),
                        "Error": True,
                        "data": {}
                    }
                    #MediaProperty.append(response)
                x['media']=MediaProperty
                DataPropertyAmenity = funtions_amenity.get_amenities_by_property_lang(idProperty, lang_code)
                if len(DataPropertyAmenity) == 0:
                    PropertyAmenity = []
                else:
                     PropertyAmenity = DataPropertyAmenity
                x['amenities']=PropertyAmenity
                x['area_unit']=x['area_unit_p']['description'].capitalize()
                x['unit_code']=x['area_unit_p']['unit_code'].capitalize()
                x.pop('area_unit_p')
                dataResult.append(x)

            if dataResult is None:
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
                    "data": dataResult
                }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class PropertyPublicListSearch(Resource):
    @PublicAuth.access_middleware
    def post(self):

        #Nota: Todas las propiedades que se encuentren activas con o sin filtros seran devueltas,
        # pero si se encuentra una restriccion, o ocurre algun error al obtener su informacion basica
        # se cambia su estado a 0 y se agrega un mensaje para indicar que la propiedad no se encuentra
        # disponible por el momento

        response = {}

        try:
            requestData = request.get_json(force=True)
            schema = GetPublicProperty()
            dataRq = schema.load(requestData)

            lang_code = dataRq["lang_code"]
            market = dataRq["market"]

            conditions = []

            conditions.append(Model.estado == 1)

            if request.json.get("property_code") is not None and request.json.get("brand_code") is not None:
                if request.json.get("property_code") != "" and request.json.get("brand_code") == "":
                    property_code = dataRq["property_code"] #request.json.get("property_code")
                    conditions.append(Model.property_code==property_code)
                
                if request.json.get("brand_code") != "" and request.json.get("property_code") == "":
                    dataBrand = funtions.getBrandInfo(dataRq["brand_code"])
                    id_brand = dataBrand.iddef_brand
                    conditions.append(Model.iddef_brand==id_brand)

                if request.json.get("property_code") != "" and request.json.get("brand_code") != "":
                    property_code = dataRq["property_code"]
                    conditions.append(Model.property_code==property_code)

            listItems = []
            if request.json.get("filters") is not None:
                listItems = dataRq["filters"]

            if len(listItems) > 0:
                conditions.append(filterModel.iddef_property == Model.iddef_property)
                conditions.append(filterModel.iddef_filter.in_(listItems))
                conditions.append(filterModel.estado==1)

                property_data = Model.query.join(filterModel).filter(and_(*conditions)).all()
            else:
                property_data = Model.query.filter(and_(*conditions)).all()

            date_start = None
            date_end = None
            if request.json.get("date_start") is None or request.json.get("date_end") is None:
                today = datetime.datetime.now().date()
                date_start = today + datetime.timedelta(days=15)
                date_end = today + datetime.timedelta(days=20)
            else:
                date_start = dataRq["date_start"]
                date_end = dataRq["date_end"]

            terms_cond = TermsAndConditionsService.get_all_terms_and_conditions()

            data_return = []
            for data in property_data:

                avail_msg = ""
                description = ""
                PropertyAmenity = []
                PropertyMedia = []
                PropertyService = []

                try:
                    #Obtenemos las restricciones que aplican para esta propiedad, si se encuentra alguna restriccion
                    #Que aplique para esta propiedad y mercado en las fechas indicadas, se cambia el estado a 0                

                    date_end_checkout = date_end - datetime.timedelta(days=1)

                    #Obtenemos su respectiva description
                    PropertyDescription = PDModel.query.filter(PDModel.estado == 1, \
                    PDModel.iddef_property == data.iddef_property, PDModel.iddef_description_type == 1, \
                    PDModel.lang_code == lang_code).first()

                    if PropertyDescription is not None:
                        description = PropertyDescription.description

                    #Obtenemos media de la propiedad
                    media = MedFunctions.GetMediaProperty(idProperty=data.iddef_property,\
                    MediaType=1,only_one=False)
                    PropertyMedia = media

                    #Obtenemos las amenidades de la propiedad
                    amenities = funtions_amenity.get_amenities_by_property_lang(data.iddef_property, lang_code)
                    if len(amenities) > 0:
                        PropertyAmenity = [elem_priority for elem_priority in amenities if elem_priority['is_priority'] == 1]
                        
                    #Obtenemos los servicios por propiedad
                    serviceData = PublicServicePropertyLang.getInfoService(data.iddef_property, market, lang_code)
                    if serviceData["Error"]==False and len(serviceData["data"]) > 0:
                        PropertyService= serviceData["data"]

                    restrictiont_property = resfunction.getOperaRestrictions(id_restriction_by=5,\
                    id_restriction_type=[1],id_property=data.iddef_property,\
                    date_start=date_start,date_end=date_end_checkout,estado=1)

                    if len(restrictiont_property) >= 1:
                        raise Exception("La propiedad no se encuentra disponible para las fechas seleccionadas")

                except Exception as exections:
                    data.estado = 0
                    avail_msg = str(exections)

                term_info = self.__find_term(terms_cond, data.iddef_brand)
                term_info_url = ""
                if term_info:
                    term_info_url = term_info.link_es if lang_code.lower() == "es" else term_info.link_en
                
                data_end = {
                    "property_code":data.property_code,
                    "trade_name": data.trade_name,
                    "short_name":data.short_name,
                    "brand_code":data.brand.code,
                    "property_icon":data.icon_logo_name,
                    #"time_zone":data.time_zone,
                    "web_address":data.web_address,
                    "iddef_property":data.iddef_property,
                    "description":description,
                    "estado":data.estado,
                    "media":PropertyMedia,
                    "amenity":PropertyAmenity,
                    "service":PropertyService,
                    "avail_msg":avail_msg,
                    "terms_and_conditions": term_info_url
                }

                data_return.append(data_end)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(data_return,many=True)
            }
        except ValidationError as schError:
            response = {
                "Code": 500,
                "Msg": str(schError),
                "Error": True,
                "data": {}
            }
        except Exception as error:
            response = {
                "Code": 500,
                "Msg": str(error),
                "Error": True,
                "data": {}
            }

        return response

    def __find_term(self, data_list, brand_id):
        for item in data_list:
            if item.iddef_brand == brand_id:
                return item
        return None
        
class PropertyPublicHoldExp(Resource):
    @PublicAuth.access_middleware
    def post(self):

        response = {}

        try:
            requestData = request.get_json(force=True)
            schema = GetHoldPublic()
            data = schema.load(requestData)
            date_today = dt.utcnow()
            data_result = PropertyService.get_hold_duration_policy(date_today,data["property_code"],\
            data["from_date"],data["to_date"],data["rooms"])

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(data_result,many=True)
            }
        except ValidationError as schError:
            response = {
                "Code": 500,
                "Msg": str(schError),
                "Error": True,
                "data": {}
            }
        except Exception as error:
            response = {
                "Code": 500,
                "Msg": str(error),
                "Error": True,
                "data": {}
            }

        return response

class PublicPropertyListSearchInfo(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:
            requestData = request.get_json(force=True)
            schema = GetPublicPropertyInfo()
            mediaSchema = publicSchema()
            dataRq = schema.load(requestData)

            conditions = []

            conditions.append(Model.estado == 1)

            if request.json.get("property_code") != "" and request.json.get("brand_code") == "":
                property_code = dataRq["property_code"]
                conditions.append(Model.property_code==property_code)
                
            elif request.json.get("brand_code") != "" and request.json.get("property_code") == "":
                dataBrand = funtions.getBrandInfo(dataRq["brand_code"])
                id_brand = dataBrand.iddef_brand
                conditions.append(Model.iddef_brand==id_brand)

            elif request.json.get("property_code") != "" and request.json.get("brand_code") != "":
                property_code = dataRq["property_code"]
                conditions.append(Model.property_code==property_code)
            else:
                pass

            property_data = Model.query.filter(and_(*conditions)).all()

            response_data = []
            for property_item in property_data:
                #Obtenemos media de la propiedad
                property_schema_item = schema.dump(property_item)
                PropertyMedia = MedFunctions.GetMediaProperty(idProperty=property_item.iddef_property,\
                MediaType=1,only_one=False)
                media_data = mediaSchema.dump(PropertyMedia,many=True)
                property_schema_item["media"] = media_data
                response_data.append(property_schema_item)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": response_data
            }
        except ValidationError as schError:
            response = {
                "Code": 500,
                "Msg": str(schError),
                "Error": True,
                "data": {}
            }
        except Exception as error:
            response = {
                "Code": 500,
                "Msg": str(error),
                "Error": True,
                "data": {}
            }

        return response

class PropertyPublicAmenityMedia(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:
            requestData = request.get_json(force=True)
            schema = GetPublicPropertyAmenity()
            dataRq = schema.load(requestData)

            lang_code = dataRq["lang_code"]

            conditions = []

            conditions.append(Model.estado == 1)

            if request.json.get("property_code") != "":
                property_code = dataRq["property_code"]
                conditions.append(Model.property_code==property_code)
            else:
                raise Exception("Property code may not be empty")

            data = Model.query.filter(and_(*conditions)).first()

            if data is None:
                raise Exception("Property not found")

            #Obtenemos media de la propiedad
            PropertyMedia = MedFunctions.GetMediaProperty(idProperty=data.iddef_property,\
            MediaType=1,only_one=False)

            #Obtenemos las amenidades de la propiedad
            amenities = funtions_amenity.get_amenities_by_property_lang(data.iddef_property, lang_code)
            if len(amenities) > 0:
                PropertyAmenity = [elem_priority for elem_priority in amenities if elem_priority['is_priority'] == 1]
            else:
                PropertyAmenity = []

            data_result = {}
            data_result['property_code'] = data.property_code
            data_result['media'] = PropertyMedia
            data_result['amenity'] = PropertyAmenity

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(data_result)
            }
        except ValidationError as schError:
            response = {
                "Code": 500,
                "Msg": str(schError),
                "Error": True,
                "data": {}
            }
        except Exception as error:
            response = {
                "Code": 500,
                "Msg": str(error),
                "Error": True,
                "data": {}
            }

        return response