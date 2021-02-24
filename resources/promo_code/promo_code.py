from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError, EXCLUDE
from flask import Flask, jsonify
from json import JSONEncoder
import json
from config import db, base
#Sfrom models.promo_code_discount_type import PromoCodeDiscountType
from models.promo_code import PromoCodeSchema as ModelSchema,GetPromoCodeSchema as GetModelSchema, PromoCodeRefSchema as ModelRefSchema, PromoCode as Model, PromoCodePostPutSchema
from models.promo_code_discount_type import PromoCodeDiscountTypeSchema as PromoDiscountTypeModelSchema, PromoCodeDiscountType as PromoDiscountTypeModel
from models.promo_code_date import PromoCodeDateSchema as PromoDateModelSchema, PromoCodeDate as PromoCodeDateModel, PromoCodeDateInsertSchema
from models.promo_code_type_date import PromoCodeTypeDateSchema as PromoTypeDateModelSchema, PromoCodeTypeDate as PromoCodeTypeDateModel
from models.text_lang import TextLangSchema as TextModelSchema,TextLang as TextModel, GetTextLangSchema as GetTextSchema
from models.currency import CurrencySchema as CurrencyModelSchema, Currency as CurrencyModel
from models.promo_code_channels import PromoCodeChannelsSchema as PChannelsSchema, PromoCodeChannels as PChanelsModel
from models.promo_code_targeting_country import PromoCodeTargetingCountry as pTargetingModel, PromoCodeTargetingCountrySchema as pTargetingModelSchema
#from models.promo_code_date import PromoCodeDate
from models.promo_code_type_amount import PromoCodeTypeAmount, PromoCodeTypeAmountSchema
from models.property import Property as PropertyModel
from models.promo_code_rateplan import PromoCodeRatePlan, PromoCodeRatePlanSchema
from resources.promo_code.promocodeHelper import PromoCodeFunctions as functionsPromoCode
from common.util import Util
from sqlalchemy.sql.expression import and_, or_

class PromoCode (Resource):
    #api-promocode-get-by-id
    # @base.access_middleware
    def get(self,id):
        try:
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = Model.query.get(id)
            result = schema.dump(data)
            targetingData = pTargetingModel.query.filter_by(iddef_promo_code = result['iddef_promo_code'], estado = 1).first()
            if targetingData is not None:
                result['market_option'] = targetingData.market_option
                result['market_targeting'] = targetingData.market_targeting
                result['country_option'] = targetingData.country_option
                result['country_targeting'] = targetingData.country_targeting
            else:
                result['market_option'] = 0
                result['market_targeting'] = []
                result['country_option'] = 0
                result['country_targeting'] = []
            #data_f = float(data)

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

class PromoCodeListSearch (Resource) :
    #api-promocode-get-all
    # @base.access_middleware
    def get(self):

        response = {}

        try:
            isAll = request.args.get("all")
            #inicializamos el Schema season
            schema = ModelSchema(exclude=Util.get_default_excludes())
            
            #Obtenemos los datos de la tabla y hacemos join con los tipos de descuento
            if isAll is not None:
                promoData = promoData = Model.query\
                .join(PromoDiscountTypeModel, PromoDiscountTypeModel.iddef_promo_code_discount_type == Model.iddef_promo_code_discount_type)\
                .all()
            else:
                promoData = promoData = Model.query\
                .join(PromoDiscountTypeModel, PromoDiscountTypeModel.iddef_promo_code_discount_type == Model.iddef_promo_code_discount_type)\
                .filter(Model.estado == 1)

            #convertimos a JSON
            promoDataJson = schema.dump(promoData, many = True)

            dataList = []

            for data in promoDataJson:
                
                aux ={}
                targetingData = pTargetingModel.query.filter_by(iddef_promo_code = data['iddef_promo_code'], estado = 1).first()
                if targetingData is not None:
                    aux['market_option'] = targetingData.market_option
                    aux['market_targeting'] = targetingData.market_targeting
                    aux['country_option'] = targetingData.country_option
                    aux['country_targeting'] = targetingData.country_targeting
                else:
                    aux['market_option'] = 0
                    aux['market_targeting'] = []
                    aux['country_option'] = 0
                    aux['country_targeting'] = []
                aux['internal_name'] = data['name']
                aux['code'] = data['code']
                aux['status'] = data['estado']
                aux['type'] = data['discount_type']
                aux['offer'] = data['value_discount']
                aux['currency'] = data['currency_code']
                aux['sold'] = '0/0'
                #aux['bookable_until'] = data['bookable_until']
                aux['iddef_voucher'] = data['iddef_promo_code']

                dataList.append(aux)
           #Se construye el response
            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": dataList
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

class PromoCodeListByVoucher(Resource) :
    #api-promocode-get-all-by-voucher
    # @base.access_middleware
    def get(self, idVoucher):

        response = {}
        aux ={}
        
        try:
            #inicializamos el modelo
            schema = ModelSchema(exclude=Util.get_default_excludes())
            dateSchema = PromoDateModelSchema(exclude=Util.get_default_excludes())
            dateTypeSchema = PromoTypeDateModelSchema(exclude=Util.get_default_excludes())
            currencySchema = CurrencyModelSchema(exclude=Util.get_default_excludes())
            #channelSchema = PChannelsSchema(exclude=Util.get_default_excludes())
            #obtenemos los datos de information
            promoData = db.session.query(Model)\
            .join(PromoDiscountTypeModel, PromoDiscountTypeModel.iddef_promo_code_discount_type == Model.iddef_promo_code_discount_type)\
            .filter(Model.iddef_promo_code == idVoucher)\

            #convertimos a Json
            promoDataJson = schema.dump(promoData, many = True)
            #type_amount_name
            aux['type_amount_name'] = ''
            if promoDataJson[0]['iddef_promo_code_type_amount'] != 0:
                data_type_amount_name = PromoCodeTypeAmount.query.filter_by(iddef_promo_code_type_amount=promoDataJson[0]['iddef_promo_code_type_amount']).first()     
                if data_type_amount_name is not None:
                    aux['type_amount_name'] = data_type_amount_name.name
            #Datos de Currency
            aux['iddef_curency'] = ''
            aux['currency_code'] = ''
            if promoDataJson[0]['iddef_promo_code_type_amount'] != 4:
                currencyData = CurrencyModel.query.filter_by(currency_code = promoDataJson[0]['currency_code']).all()
                currencyDataJson = currencySchema.dump(currencyData, many=True)
                if len(currencyData) > 0:
                    aux['iddef_curency'] = currencyDataJson[0]['iddef_currency']
                    aux['currency_code'] = promoDataJson[0]['currency_code']
            #return currencyDataJson
                           
            #Datos de las descripciones
            textSchema = TextModelSchema(exclude=('id_relation','attribute','table_name','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            textData = TextModel.query.filter_by(id_relation=promoDataJson[0]['iddef_promo_code'], table_name='def_promo_code', estado=1).all()
            textdataJson = textSchema.dump(textData)

            #datos de Channels
            channelSchema = PChannelsSchema(exclude=('estado','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            channelData = PChanelsModel.query.filter_by(iddef_promo_code = idVoucher, estado=1)
            channelDataJson = channelSchema.dump(channelData)

            #datos de geoTargeting
            #targetingSchema = pTargetingModelSchema(exclude=('estado','estado','usuario_creacion', 'fecha_creacion', 'usuario_ultima_modificacion', 'fecha_ultima_modificacion',), many=True)
            targetingData = pTargetingModel.query.filter_by(iddef_promo_code = idVoucher, estado = 1).first()
            #targetingDataJson = targetingSchema.dump(targetingData)
            if targetingData is not None:
                aux['market_option'] = targetingData.market_option
                aux['market_targeting'] = targetingData.market_targeting
                aux['country_option'] = targetingData.country_option
                aux['country_targeting'] = targetingData.country_targeting
            else:
                aux['market_option'] = 0
                aux['market_targeting'] = []
                aux['country_option'] = 0
                aux['country_targeting'] = []
                    
            #sección Information
            aux['name'] = promoDataJson[0]['name']
            aux['code'] = promoDataJson[0]['code']
            aux['estado'] = promoDataJson[0]['estado']
            ##Sección offer
            aux['iddef_promo_code_discount_type'] = promoDataJson[0]['iddef_promo_code_discount_type']
            aux['discount_type'] = promoDataJson[0]['discount_type']
            aux['value_discount'] = promoDataJson[0]['value_discount']
            aux['iddef_promo_code_type_amount'] = promoDataJson[0]['iddef_promo_code_type_amount']                
            aux['description'] = textdataJson
            #Restriction
            aux['room_types_option'] = promoDataJson[0]['room_types_option']
            aux['min_LOS_option'] = promoDataJson[0]['min_LOS_option']
            aux['min_LOS_value'] = promoDataJson[0]['min_LOS_value']
            aux['min_booking_amount_option'] = promoDataJson[0]['min_booking_amount_option']
            aux['min_booking_value'] = promoDataJson[0]['min_booking_value']
            aux['max_booking_amount_option'] = promoDataJson[0]['max_booking_amount_option']
            aux['max_booking_value'] = promoDataJson[0]['max_booking_value']
            aux['stay_dates_option'] = promoDataJson[0]['stay_dates_option']
            aux['stay_dates_value']= promoDataJson[0]['stay_dates']
            aux['booking_dates_option'] = promoDataJson[0]['booking_dates_option']
            aux['booking_dates_value'] = promoDataJson[0]['booking_dates']
            aux['booking_times_value'] = promoDataJson[0]['booking_times']
            aux['global_sales_limit_option'] = promoDataJson[0]['global_sales_limit_option']
            aux['global_sales_limit_value'] = promoDataJson[0]['global_sales_limit_value']
            aux['promo_code_channels'] = channelDataJson
            #aux['promo_code_rateplans'] = promoDataJson[0]['promo_code_rateplans']
            aux['maximum_nights_value']= promoDataJson[0]['maximum_nights_value']
            aux['maximum_nights_option']= promoDataJson[0]['maximum_nights_option']
            aux['channel_option']= promoDataJson[0]['channel_option']
            aux['cancel_policy_id']= promoDataJson[0]['cancel_policy_id']
            #obtenemos propiedades activas
            data_rateplans = promoDataJson[0]['promo_code_rateplans']
            result_properties = []
            data_properties = PropertyModel.query.filter_by(estado=1).all()
            if len(data_properties) > 0:
                for item_property in data_properties:
                    result_plans = []
                    for item_rateplan in data_rateplans:
                        #filtramos rateplans activos por propiedad
                        if item_rateplan["estado"] == 1 and item_rateplan["iddef_property"] == item_property.iddef_property:
                            obj_rateplan = {
                                "idop_rateplan": item_rateplan["idop_rateplan"],
                                "op_rateplans": item_rateplan["op_rateplans"],
                                "rooms_rateplan": item_rateplan["rooms_rateplan"],
                                "estado": item_rateplan["estado"],
                                "iddef_promo_code_rateplan": item_rateplan["iddef_promo_code_rateplan"],
                            }
                            result_plans.append(obj_rateplan)
                    obj_property = {
                        "iddef_property":item_property.iddef_property,
                        "promo_code_rateplans":result_plans
                    }
                    result_properties.append(obj_property)
            aux['promo_code_rateplans'] = result_properties

           #Se construye el response
            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data": aux
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
    
    #api-promocode-create-all
    # @base.access_middleware        
    def post(self):
        response = {}

        try:
            json_data = request.get_json(force=True)
            schema_load = PromoCodePostPutSchema(exclude=Util.get_default_excludes())
            data = schema_load.load(json_data)

            result = functionsPromoCode.create_promocodes(data,data["iddef_promo_code"])            

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
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


    #api-promocode-update-all
    # @base.access_middleware
    def put(self, id):
        response = {}

        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            postSchema = PromoCodePostPutSchema(exclude=Util.get_default_excludes())
            json_data = postSchema.load(json_data)
            user_data = base.get_token_data()
            user_name = user_data['user']['username']
            dataResponse = []            
            #consulta simple: 
            data_promo_code = Model.query.filter(Model.iddef_promo_code == id)
            data_promo_codeJson = schema.dump(data_promo_code, many=True)
                        
            M = Model.query.get(id)
            M.name = json_data['name']
            M.code = json_data['code']
            M.estado = json_data['estado']
            M.iddef_promo_code_discount_type = json_data['iddef_promo_code_discount_type']
            M.usuario_ultima_modificacion = user_name
            db.session.flush()
            insert = schema.dump(M)
            insert_iddef_promo_code = insert["iddef_promo_code"]
            
            #Validacion discount type
            if json_data["iddef_promo_code_discount_type"] == 1:
                M.value_discount = json_data['value_discount']
                M.iddef_promo_code_type_amount = json_data['iddef_promo_code_type_amount']
                if json_data['iddef_promo_code_type_amount'] == 4:
                    M.currency_code = ""
                    M.maximum_nights_option = json_data['maximum_nights_option']
                    if json_data['maximum_nights_option'] != 0:
                        M.maximum_nights_value = json_data['maximum_nights_value']
                    else:
                        M.maximum_nights_value = 0.00
                elif json_data['iddef_promo_code_type_amount'] == 3:
                    M.currency_code = json_data['currency_code']
                    M.maximum_nights_option = json_data['maximum_nights_option']
                    if json_data['maximum_nights_option'] != 0:
                        M.maximum_nights_value = json_data['maximum_nights_value']
                    else:
                        M.maximum_nights_value = 0.00
                else:
                    M.currency_code = json_data['currency_code']
                    M.maximum_nights_option = 0
                    M.maximum_nights_value = 0.00
            else:
                M.value_discount = 0.00
                M.iddef_promo_code_type_amount = 0
                M.currency_code = ""
                M.maximum_nights_option = 0
                M.maximum_nights_value = 0.00
                db.session.flush()

            #baja nodo descripcion
            tSchema = TextModelSchema(exclude=Util.get_default_excludes())
            dataTextLang = TextModel.query.filter(TextModel.table_name == 'def_promo_code', TextModel.id_relation == id).all()
            textLang = tSchema.dump(dataTextLang, many=True)
            if len(textLang) > 0:
                for itemText in textLang:
                    btl = TextModel.query.get(itemText["iddef_text_lang"])
                    btl.estado = 0
                    db.session.flush()
            #meter logica de cuadro de descripcion
            for dataDescription in json_data["description"]:
                tUpdate =  TextModel.query.filter(TextModel.table_name == 'def_promo_code', TextModel.lang_code == dataDescription["lang_code"] , TextModel.id_relation == id).first() #descListJson = tSchema.dump(descList, many=True)
                #insertamos en la tabla de textlang
                if tUpdate is not None:
                    #si no esta vacio actualizamos
                    tUpdate.lang_code = dataDescription["lang_code"]
                    tUpdate.text = dataDescription["text"]
                    tUpdate.table_name = "def_promo_code"
                    tUpdate.id_relation = id
                    tUpdate.attribute = "description"
                    tUpdate.estado = 1
                    tUpdate.usuario_ultima_modificacion = user_name
                    db.session.flush()
                else:                        
                    #si esta vacio insertamos
                    Tmodel = TextModel()
                    Tmodel.lang_code = dataDescription["lang_code"]
                    Tmodel.text = dataDescription["text"]
                    Tmodel.table_name = "def_promo_code"
                    Tmodel.id_relation = insert_iddef_promo_code
                    Tmodel.attribute = "description"
                    Tmodel.estado = 1
                    Tmodel.usuario_creacion = user_name
                    db.session.add(Tmodel)
                    db.session.flush()

            #seccion Restrictions
            M.room_types_option = json_data["room_types_option"]
            #baja todos los rateplans
            dataRatePlans = PromoCodeRatePlan.query.filter(PromoCodeRatePlan.iddef_promo_code == id).all()
            promoRateSchema = PromoCodeRatePlanSchema(exclude=Util.get_default_excludes())
            ratePlans = promoRateSchema.dump(dataRatePlans, many=True)
            if len(dataRatePlans) > 0:
                for x in ratePlans:
                    rp = PromoCodeRatePlan.query.get(x['iddef_promo_code_rateplan'])
                    rp.estado = 0
                    db.session.flush()

            if json_data["room_types_option"] == 2:                
                for promo_code_property in json_data["promo_code_rateplans"]:
                    iddef_property = promo_code_property["iddef_property"]
                    if len(promo_code_property["promo_code_rateplans"]) > 0:
                        for promo_code_rateplan in promo_code_property["promo_code_rateplans"]:
                            if len(promo_code_rateplan["rooms_rateplan"]) > 0:
                                rpUpdate = PromoCodeRatePlan.query.filter(PromoCodeRatePlan.iddef_promo_code == id,\
                                PromoCodeRatePlan.iddef_property == iddef_property,\
                                PromoCodeRatePlan.idop_rateplan == promo_code_rateplan["idop_rateplan"]).first()
                                if rpUpdate is not None:
                                    #si no esta vacio actualizamos                                              
                                    rpUpdate.iddef_property = iddef_property
                                    rpUpdate.idop_rateplan = promo_code_rateplan["idop_rateplan"]                                             
                                    rpUpdate.rooms_rateplan = promo_code_rateplan["rooms_rateplan"]                        
                                    rpUpdate.estado = 1
                                    rpUpdate.usuario_ultima_modificacion = user_name
                                    db.session.flush()
                                else:
                                    #si esta vacio insertamos
                                    rpModel = PromoCodeRatePlan()
                                    rpModel.iddef_promo_code = id
                                    rpModel.iddef_property = iddef_property
                                    rpModel.idop_rateplan = promo_code_rateplan["idop_rateplan"]
                                    rpModel.rooms_rateplan = promo_code_rateplan["rooms_rateplan"]
                                    rpModel.estado = 1
                                    rpModel.usuario_creacion = user_name
                                    db.session.add(rpModel)
                                    db.session.flush()
            else:
                #si no tiene restricciones, no insertamos.
                pass
            M.min_LOS_option = json_data["min_LOS_option"]

            if json_data["min_LOS_option"] == 2:
                M.min_LOS_value = json_data["min_LOS_value"]
            else:
                M.min_LOS_value = 0.00
            
            M.min_booking_amount_option = json_data["min_booking_amount_option"]

            if json_data["min_booking_amount_option"] == 2:
                M.min_booking_value = json_data["min_booking_value"]
            else:
                M.min_booking_value = 0.00
            
            M.max_booking_amount_option = json_data["max_booking_amount_option"]

            if json_data["max_booking_amount_option"] == 2:
                M.max_booking_value = json_data["max_booking_value"]
            else:
                M.max_booking_value = 0.00
            
            M.stay_dates_option = json_data["stay_dates_option"]
            M.stay_dates = json_data["stay_dates_value"]
            """ if json_data["stay_dates_option"] != 1:               
                #recorremos dates_types_values
                for dates in json_data["dates_types_values"]:
                    if dates["iddef_promo_code_type_date"] == 1:
                        with db.session.no_autoflush:
                            stayDatesExist = PromoCodeDateModel.query.filter(PromoCodeDateModel.iddef_promo_code_type_date == 1, PromoCodeDateModel.iddef_promo_code == id, PromoCodeDateModel.start_date == dates["start_date"], PromoCodeDateModel.end_date == dates["end_date"]).all()
                            dateSchema = PromoDateModelSchema(exclude=Util.get_default_excludes())
                            stayDatesExistJson = dateSchema.dump(stayDatesExist, many= True)
                            
                        if stayDatesExistJson:
                            dateModel = PromoCodeDateModel.query.get(stayDatesExistJson[0]["iddef_promo_code_date"])
                            dateModel.iddef_promo_code_type_date = dates["iddef_promo_code_type_date"]
                            dateModel.start_date = dates["start_date"]
                            dateModel.end_date = dates["end_date"]
                            dateModel.estado = dates["estado"]
                            dateModel.usuario_ultima_modificacion = user_name
                            db.session.flush()
                        else:
                            dateModel = PromoCodeDateModel()
                            dateModel.iddef_promo_code = id
                            dateModel.iddef_promo_code_type_date = dates["iddef_promo_code_type_date"]
                            dateModel.start_date = dates["start_date"]
                            dateModel.end_date = dates["end_date"]
                            dateModel.estado = 1
                            dateModel.usuario_creacion = user_name
                            db.session.add(dateModel)
                            db.session.flush()
            else:
                pass """

            M.booking_dates_option = json_data["booking_dates_option"]
            M.booking_dates = json_data["booking_dates_value"]
            M.booking_times = json_data["booking_times_value"]
            """ if json_data["booking_dates_option"] != 1:               
                #recorremos dates_types_values
                for dates in json_data["dates_types_values"]:
                    if dates["iddef_promo_code_type_date"] == 2:
                        with db.session.no_autoflush:
                            bookingDatesExist = PromoCodeDateModel.query.filter(PromoCodeDateModel.iddef_promo_code_type_date == 2, PromoCodeDateModel.iddef_promo_code == id, PromoCodeDateModel.start_date == dates["start_date"], PromoCodeDateModel.end_date == dates["end_date"]).all()
                            dateSchema = PromoDateModelSchema(exclude=Util.get_default_excludes())
                            bookingDatesExistJson = dateSchema.dump(bookingDatesExist, many= True)
                            
                        if bookingDatesExistJson:
                            dateModel = PromoCodeDateModel.query.get(bookingDatesExistJson[0]["iddef_promo_code_date"])
                            dateModel.iddef_promo_code_type_date = dates["iddef_promo_code_type_date"]
                            dateModel.start_date = dates["start_date"]
                            dateModel.end_date = dates["end_date"]
                            dateModel.estado = dates["estado"]
                            dateModel.usuario_ultima_modificacion = user_name
                            db.session.flush()
                        else:
                            dateModel = PromoCodeDateModel()
                            dateModel.iddef_promo_code = id
                            dateModel.iddef_promo_code_type_date = dates["iddef_promo_code_type_date"]
                            dateModel.start_date = dates["start_date"]
                            dateModel.end_date = dates["end_date"]
                            dateModel.estado = 1
                            dateModel.usuario_creacion = user_name
                            db.session.add(dateModel)
                            db.session.flush()
            else:
                pass """
            
            M.global_sales_limit_option = json_data["global_sales_limit_option"]

            if json_data["global_sales_limit_option"] == 2:
                M.global_sales_limit_value = json_data["global_sales_limit_value"]
            else:
                M.global_sales_limit_value = 0.00
            
            M.cancel_policy_id = json_data["cancel_policy_id"]
            M.channel_option = json_data["channel_option"]
            
            if json_data["channel_option"] != 1:
                for channel in json_data["channel_list"]:                    
                    with db.session.no_autoflush:
                        channelsExist = PChanelsModel.query.filter(PChanelsModel.iddef_promo_code == id, PChanelsModel.iddef_channel == channel["iddef_channel"])
                        channelSchema = PChannelsSchema(exclude=Util.get_default_excludes())
                        channelsExistJson = channelSchema.dump(channelsExist, many=True)
                    
                    if channelsExistJson:
                        #actualizamos
                        channelUpdate = PChanelsModel.query.get(channelsExistJson[0]["iddef_promo_code_channels"])
                        channelUpdate.iddef_promo_code = id
                        channelUpdate.iddef_channel = channel["iddef_channel"]
                        channelUpdate.estado = channel["estado"]
                        channelUpdate.usuario_ultima_modificacion = user_name
                        db.session.flush()
                    else:
                        #insertamos
                        channelModel = PChanelsModel()

                        channelModel.iddef_promo_code = id
                        channelModel.iddef_channel = channel["iddef_channel"]
                        channelModel.estado = 1
                        channelModel.usuario_creacion = user_name
                        db.session.add(channelModel)
                        db.session.flush()
            else:
                pass
            
            #Guardado de def_promo_code_targeting_country
            countryUpdate = pTargetingModel.query.filter(pTargetingModel.iddef_promo_code == id).first()
            if countryUpdate is not None:
                countryUpdate.iddef_promo_code = id
                countryUpdate.market_option = json_data["market_option"]
                countryUpdate.market_targeting = json_data["market_targeting"]
                countryUpdate.country_option = json_data["country_option"]
                countryUpdate.country_targeting = json_data["country_targeting"]
                countryUpdate.estado = 1
                countryUpdate.usuario_ultima_modificacion = user_name
                db.session.flush()
            else:
                countryModel = pTargetingModel()
                countryModel.iddef_promo_code = id
                countryModel.market_option = json_data["market_option"]
                countryModel.market_targeting = json_data["market_targeting"]
                countryModel.country_option = json_data["country_option"]
                countryModel.country_targeting = json_data["country_targeting"]
                countryModel.estado = 1
                countryModel.usuario_creacion = user_name
                db.session.add(countryModel)
                db.session.flush()

            db.session.commit()

            promoUpdate = id

            return promoUpdate

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": promoUpdate
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