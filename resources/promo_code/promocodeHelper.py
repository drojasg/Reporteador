from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db,base
from models.promo_code import PromoCode as Model, PromoCodeSchema as ModelSchema, PromoCodeRefSchema as ModelRefSchema
from models.promo_code_targeting_country import PromoCodeTargetingCountry as PCTCModel
from models.property import Property as ModelProp
from models.text_lang import TextLang as tlModel, TextLangSchema as TextModelSchema
from models.promo_code_channels import PromoCodeChannelsSchema as PChannelsSchema, PromoCodeChannels as PChanelsModel
from models.promo_code_targeting_country import PromoCodeTargetingCountry as pTargetingModel, PromoCodeTargetingCountrySchema as pTargetingModelSchema
from models.room_type_category import RoomTypeCategory as rtcModel
from models.book_promo_code import BookPromoCode as bpcModel
from resources.restriction.restricctionHelper import RestricctionFunction
from models.promo_code_rateplan import PromoCodeRatePlan, PromoCodeRatePlanSchema
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_, func
import datetime, decimal
import json
from datetime import datetime as dt, timedelta

class PromoCodeFunctions():
    #Metodo para verificar si el voucher aplicado en la reserva es válido
    #Retorna un objeto con el voucher verificado, de otra forma enviará una excepción
    @staticmethod
    def getValidatePromoCode(promo_code, property=None, property_code=None, travel_window_start=None,travel_window_end=None, 
        rateplans=[], rooms=[], market=None, lang_code='EN', country=None, min_booking_amount=None,\
        max_booking_amount=None):
        try:
            data = None
            conditions = []
            description = ""
            flag_rateplans = None
            flag_rooms = None
            flag_travel = None
            flag_booking = None
            schema = ModelSchema(exclude=Util.get_default_excludes())

            rec_class = RestricctionFunction()
            rec_class.checkParameterType(param_name="promo_code", param_value=promo_code, param_type=str)
            rec_class.checkParameterType(param_name="property", param_value=property, param_type=int, isNone=True)
            rec_class.checkParameterType(param_name="property_code", param_value=property_code, param_type=str, isNone=True)
            rec_class.checkParameterType(param_name="travel_window_start", param_value=travel_window_start, param_type=datetime.date, isNone=True, isDate=True)
            rec_class.checkParameterType(param_name="travel_window_end", param_value=travel_window_end, param_type=datetime.date, isNone=True, isDate=True)
            #rec_class.checkParameterType(param_name="booking_window_date", param_value=booking_window_date, param_type=str, isNone=True)
            #rec_class.checkParameterType(param_name="booking_window_time", param_value=booking_window_time, param_type=str, isNone=True)
            rec_class.checkParameterType(param_name="rateplans", param_value=rateplans, param_type=list)
            rec_class.checkParameterType(param_name="rooms", param_value=rooms, param_type=list)
            #rec_class.checkParameterType(param_name="currency", param_value=currency, param_type=str, isNone=True)
            rec_class.checkParameterType(param_name="market", param_value=market, param_type=int, isNone=True)
            rec_class.checkParameterType(param_name="lang_code", param_value=lang_code, param_type=str)
            rec_class.checkParameterType(param_name="min_booking_amount", param_value=min_booking_amount, param_type=float, isNone=True)
            rec_class.checkParameterType(param_name="max_booking_amount", param_value=max_booking_amount, param_type=float, isNone=True)
            
            if promo_code == "":
                return None

            booking_window_date = dt.now().strftime('%Y-%m-%d')
            booking_window_time = dt.now().strftime('%H:%M')

            #Se reestructuran las listas a una lista sin elementos repetidos
            if isinstance(rateplans, list) and len(rateplans) > 0:
                rateplans = list(set(rateplans))
            if isinstance(rooms, list) and len(rooms) > 0:
                if not all(isinstance(item, int) for item in rooms):
                    raise Exception("Rooms needs to be a list of integers")
                rooms = list(set(rooms))
                list_rooms = rtcModel.query.filter(rtcModel.iddef_room_type_category.in_(rooms)).all()
                rooms = [elem_room.room_code for elem_room in list_rooms]
                rooms = list(set(rooms))

            if promo_code is not None:
                conditions.append(Model.code==promo_code)

            conditions.append(Model.estado==1)

            data_query = Model.query\
            .filter(and_(*conditions)).first()

            if data_query is not None:
                if property is None and property_code is not None:
                    property_obj = ModelProp.query.filter(ModelProp.property_code==property_code, ModelProp.estado==1).first()
                    if property_obj is not None:
                        property = property_obj.iddef_property
                    else:
                        raise Exception("Property code not found")

                if (isinstance(rooms, list) and len(rooms) > 0) or property is not None or (isinstance(rateplans, list) and len(rateplans) > 0):
                    flag_rooms = False
                    flag_rateplans = False
                    flag_property = False
                    all_flags = False
                    valid_rules = False

                    if len(data_query.promo_code_rateplans) > 0:
                        #raise Exception("No rateplans assigned")
                        for promo_rate_obj in data_query.promo_code_rateplans:
                            if promo_rate_obj.estado==1:
                                valid_rules = True
                                temp_flag_rooms = False
                                temp_flag_rateplans = False
                                temp_flag_property = False
                                if (isinstance(rooms, list) and len(rooms) > 0):
                                    if len(set(rooms).intersection(set(promo_rate_obj.rooms_rateplan))) > 0:
                                        flag_rooms = True
                                        temp_flag_rooms = True
                                else:
                                    flag_rooms = True
                                    temp_flag_rooms = True

                                if (isinstance(rateplans, list) and len(rateplans) > 0):
                                    if promo_rate_obj.idop_rateplan in rateplans:
                                        flag_rateplans = True
                                        temp_flag_rateplans = True
                                else:
                                    flag_rateplans = True
                                    temp_flag_rateplans = True

                                if property is not None:
                                    if promo_rate_obj.iddef_property == property:
                                        flag_property = True
                                        temp_flag_property = True
                                else:
                                    flag_property = True
                                    temp_flag_property = True

                                #Se valida que todo el registro sea válido
                                if temp_flag_rooms and temp_flag_rateplans and temp_flag_property:
                                    all_flags = True
                        if valid_rules:
                            if not flag_rooms:
                                raise Exception("Room not valid")
                            if not flag_rateplans:
                                raise Exception("Rateplan not valid")
                            if not flag_property:
                                raise Exception("Property not valid")
                            if not all_flags:
                                raise Exception("Rateplan, Room and Property are not valid")
                
                # if currency is not None:
                #     if data_query.currency_code!="" and data_query.currency_code!=currency:
                #         raise Exception("Currency not valid")

                if market is not None or country is not None:
                    targeting_countries = PCTCModel.query.filter(PCTCModel.iddef_promo_code==data_query.iddef_promo_code, PCTCModel.estado==1).all()
                    if len(targeting_countries) > 0:
                        flag_market = False
                        flag_country = False
                        # Se valida de esta forma ya que se espera que solo se revise 1 elemento targeting_countries (relación 1:1)
                        for targeting_country in targeting_countries:
                            if market is not None:
                                # market_option (0 - Inherent / 1 - All markets / 2 - Custom markets / 3 - All markets, with these exceptions)
                                if targeting_country.market_option == 0 or targeting_country.market_option == 1:
                                    flag_market = True
                                elif targeting_country.market_option == 2:
                                    if market in targeting_country.market_targeting:
                                        flag_market = True
                                elif targeting_country.market_option == 3:
                                    if market not in targeting_country.market_targeting:
                                        flag_market = True
                            else:
                                flag_market = True

                            if country is not None:
                                # country_option (0 - Inherent / 1 = All Countries / 2 = Custom Countries / 3 = All Countries, With These Exceptions)
                                if targeting_country.country_option == 0 or targeting_country.country_option == 1:
                                    flag_country = True
                                elif targeting_country.country_option == 2:
                                    if country in targeting_country.country_targeting:
                                        flag_country = True
                                elif targeting_country.country_option == 3:
                                    if country not in targeting_country.country_targeting:
                                        flag_country = True
                            else:
                                flag_country = True
                        if not flag_market:
                            raise Exception("Market not valid")
                        if not flag_country:
                            raise Exception("Country not valid")
                    else:
                        raise Exception("Promo code have not a Targeting Country Element assigned")

                if (travel_window_start is not None and travel_window_end is not None):
                    # stay_dates_option (1 - All dates, no restrictions / 2 - custom dates / 3 - blackout dates)
                    flag_travel = False
                    # Se reconvierte el DateTime para que solo tome en cuenta la fecha sin la Hora
                    temp_travel_window_start = dt.strptime(travel_window_start.strftime('%Y-%m-%d'), '%Y-%m-%d')
                    temp_travel_window_end = dt.strptime(travel_window_end.strftime('%Y-%m-%d'), '%Y-%m-%d')

                    if (data_query.stay_dates_option == 2 or data_query.stay_dates_option == 3) and len(data_query.stay_dates)==0:
                        raise Exception("Travel Window not configured")

                    if data_query.stay_dates_option == 1:
                        flag_travel = True
                    elif data_query.stay_dates_option == 2:
                        for db_stay_date in data_query.stay_dates:
                            db_stay_date_start = dt.strptime(db_stay_date["start_date"], '%Y-%m-%d')
                            db_stay_date_end = dt.strptime(db_stay_date["end_date"], '%Y-%m-%d')
                            # if db_stay_date_start <= temp_travel_window_start and temp_travel_window_end <= db_stay_date_end:
                            if ((db_stay_date_start <= temp_travel_window_start and db_stay_date_end >= temp_travel_window_end) 
                            or (db_stay_date_start >= temp_travel_window_start and db_stay_date_end <= temp_travel_window_end) 
                            or (db_stay_date_start > temp_travel_window_start and db_stay_date_end > temp_travel_window_end 
                                and db_stay_date_start <= temp_travel_window_end and db_stay_date_end >= temp_travel_window_start) 
                            or (db_stay_date_start <= temp_travel_window_start and db_stay_date_end < temp_travel_window_end 
                                and db_stay_date_start < temp_travel_window_end and db_stay_date_end >= temp_travel_window_start)):
                                flag_travel = True
                    elif data_query.stay_dates_option == 3:
                        for db_stay_date in data_query.stay_dates:
                            db_stay_date_start = dt.strptime(db_stay_date["start_date"], '%Y-%m-%d')
                            db_stay_date_end = dt.strptime(db_stay_date["end_date"], '%Y-%m-%d')
                            # if temp_travel_window_end < db_stay_date_start or temp_travel_window_start > db_stay_date_end:
                            if ((db_stay_date_start < temp_travel_window_start and db_stay_date_end < temp_travel_window_end) 
                            or (db_stay_date_start > temp_travel_window_start and db_stay_date_end > temp_travel_window_end) 
                            or (db_stay_date_start > temp_travel_window_start and db_stay_date_end < temp_travel_window_end)):
                                flag_travel = True
                    else:
                        raise Exception("Travel Window type not exist")

                    if not flag_travel:
                        raise Exception("Travel Window date is not valid")
                elif (travel_window_start is not None and travel_window_end is None) or (travel_window_start is None and travel_window_end is not None):
                    raise Exception("Required travel_window_start and travel_window_end values")

                if booking_window_date is not None:
                    # booking_dates_option (1 - All dates, no restrictions / 2 - custom dates / 3 - blackout dates)
                    flag_booking = False
                    temp_booking_window_date = dt.strptime(booking_window_date, '%Y-%m-%d')
                    if (data_query.booking_dates_option == 2 or data_query.booking_dates_option == 3) and len(data_query.booking_dates)==0:
                        raise Exception("Booking Window not configured")

                    if data_query.booking_dates_option == 1:
                        flag_booking = True
                    elif data_query.booking_dates_option == 2:
                        for db_booking_date in data_query.booking_dates:
                            db_stay_date_start = dt.strptime(db_booking_date["start_date"], '%Y-%m-%d')
                            db_stay_date_end = dt.strptime(db_booking_date["end_date"], '%Y-%m-%d')
                            if db_stay_date_start <= temp_booking_window_date and temp_booking_window_date <= db_stay_date_end:
                                flag_booking = True
                    elif data_query.booking_dates_option == 3:
                        flag_booking = True
                        for db_booking_date in data_query.booking_dates:
                            db_stay_date_start = dt.strptime(db_booking_date["start_date"], '%Y-%m-%d')
                            db_stay_date_end = dt.strptime(db_booking_date["end_date"], '%Y-%m-%d')
                            if db_stay_date_start <= temp_booking_window_date and temp_booking_window_date <= db_stay_date_end:
                                flag_booking = False
                            # if temp_booking_window_date < db_stay_date_start or temp_booking_window_date > db_stay_date_end:
                            #     flag_booking = True
                    else:
                        raise Exception("Booking Window type not exist")

                    if not flag_booking:
                        raise Exception("Booking Window date is not valid")

                if booking_window_time is not None:
                    flag_booking_time = False
                    temp_booking_window_time = dt.strptime(booking_window_time, '%H:%M')
                    # if (data_query.booking_dates_option == 2 or data_query.booking_dates_option == 3) and len(data_query.booking_times)==0:
                    #     raise Exception("Booking Window not configured")
                    if len(data_query.booking_times)>0:
                        if data_query.booking_dates_option == 1:
                            flag_booking_time = True
                        elif data_query.booking_dates_option == 2:
                            for db_booking_date in data_query.booking_times:
                                db_stay_time_start = dt.strptime(db_booking_date["start_time"], '%H:%M')
                                db_stay_time_end = dt.strptime(db_booking_date["end_time"], '%H:%M')
                                if db_stay_time_start <= temp_booking_window_time and temp_booking_window_time <= db_stay_time_end:
                                    flag_booking_time = True
                        elif data_query.booking_dates_option == 3:
                            flag_booking_time = True
                            for db_booking_date in data_query.booking_times:
                                db_stay_time_start = dt.strptime(db_booking_date["start_time"], '%H:%M')
                                db_stay_time_end = dt.strptime(db_booking_date["end_time"], '%H:%M')
                                if db_stay_time_start <= temp_booking_window_time and temp_booking_window_time <= db_stay_time_end:
                                    flag_booking_time = False
                                # if temp_booking_window_time < db_stay_time_start or temp_booking_window_time > db_stay_time_end:
                                    # flag_booking_time = True
                        else:
                            raise Exception("Booking Window type not exist")
                else:
                    flag_booking_time = True

                    if not flag_booking_time:
                        raise Exception("Booking Window time is not valid")

                min_los = abs((travel_window_end - travel_window_start).days)
                if min_los is not None:
                    if data_query.min_LOS_option == 1:
                        pass
                    elif data_query.min_LOS_option == 2:
                        if int(data_query.min_LOS_value) > int(min_los):
                            raise Exception("min_LOS_value is not valid")

                if min_booking_amount is not None:
                    if data_query.min_booking_amount_option == 1:
                        pass
                    elif data_query.min_booking_amount_option == 2:
                        if float(data_query.min_booking_value) > float(min_booking_amount):
                            raise Exception("min_booking_value is not valid")
                
                if max_booking_amount is not None:
                    if data_query.max_booking_amount_option == 1:
                        pass
                    elif data_query.max_booking_amount_option == 2:
                        if float(data_query.max_booking_value) < float(max_booking_amount):
                            raise Exception("max_booking_value is not valid")

                if data_query.global_sales_limit_option == 2:
                    flag_sales_limit = False
                    count_book = PromoCodeFunctions.search_book_promo_code(promo_code=data_query.code)
                    if int(count_book) > 0:
                        if count_book < data_query.global_sales_limit_value:
                            flag_sales_limit = True
                    else:
                        flag_sales_limit = True
                else:
                    flag_sales_limit = True

                if not flag_sales_limit:
                    raise Exception("Sales limit is not valid")

                result_translate = tlModel.query\
                .filter(tlModel.table_name=="def_promo_code", tlModel.attribute=="description", tlModel.lang_code==lang_code.upper(),
                    tlModel.id_relation==data_query.iddef_promo_code, tlModel.estado==1).first()
                if result_translate is not None:
                    description = result_translate.text

                data = schema.dump(data_query)
                data["description"] = description

                data = PromoCodeFunctions.format_vauchers(data, travel_window_start, travel_window_end, property)

        except Exception as e:
            raise e

        return data

    @staticmethod
    def format_vauchers(promocode_data, travel_window_start,travel_window_end, id_property):
        info_voucher = {
            "code":"",
            "text_only":False,
            "text":"",
            "abs_value":0.0,
            "per_value":0.0,
            "type_amount":0,
            "per_night":{"is_custom":False,"nights":0},
            "currency":"USD",
            "rateplans": [],
            "min_LOS_option":0,
            "min_LOS_value":0.0,
            "min_booking_amount_option":0,
            "min_booking_value":0.0,
            "valid_dates":[],
        }
        list_dates = []

        try:
            info_voucher["code"]=promocode_data["code"]

            if promocode_data["iddef_promo_code_discount_type"] == 2:
                info_voucher["text_only"] = True
                info_voucher["text"] = promocode_data["description"]

            elif promocode_data["iddef_promo_code_discount_type"] == 1:
                if promocode_data["iddef_promo_code_type_amount"] == 4:
                    info_voucher["per_value"]=promocode_data["value_discount"]

                elif promocode_data["iddef_promo_code_type_amount"] == 3:
                    is_custom = True if promocode_data["maximum_nights_option"] == 1 else False
                    maximum_nights_value = promocode_data["maximum_nights_value"] if promocode_data["maximum_nights_option"] == 1 else 0
                    info_voucher["per_night"]={"is_custom":is_custom,"nights":maximum_nights_value}
                    info_voucher["abs_value"] = promocode_data["value_discount"]
                    info_voucher["currency"] = promocode_data["currency_code"]
                    
                else:
                    info_voucher["abs_value"] = promocode_data["value_discount"]
                    info_voucher["currency"] = promocode_data["currency_code"]

                info_voucher["type_amount"] = promocode_data["iddef_promo_code_type_amount"]

            for pc_rp in promocode_data["promo_code_rateplans"]:
                if pc_rp["estado"] == 1:
                    list_rooms = rtcModel.query.filter(rtcModel.iddef_property==pc_rp["iddef_property"],
                        rtcModel.room_code.in_(pc_rp["rooms_rateplan"]),rtcModel.estado==1).all()
                    temp_rateplan = {}
                    temp_rateplan["id_property"] = pc_rp["iddef_property"]
                    temp_rateplan["id_rateplan"] = pc_rp["idop_rateplan"]
                    temp_rateplan["id_rooms"] = [elem_room.iddef_room_type_category for elem_room in list_rooms]
                    info_voucher["rateplans"].append(temp_rateplan)

            info_voucher["min_LOS_option"] = promocode_data["min_LOS_option"]
            info_voucher["min_LOS_value"] = promocode_data["min_LOS_value"]
            info_voucher["min_booking_amount_option"] = promocode_data["min_booking_amount_option"]
            info_voucher["min_booking_value"] = promocode_data["min_booking_value"]

            for dt_travel in PromoCodeFunctions.daterange(travel_window_start, travel_window_end):
                for stay_date in promocode_data["stay_dates"]:
                    info_travel_window_start = dt.strptime(stay_date["start_date"], '%Y-%m-%d').date()
                    info_travel_window_end = dt.strptime(stay_date["end_date"], '%Y-%m-%d').date()

                    if promocode_data["stay_dates_option"] == 1:
                        list_dates.append(dt_travel.strftime('%Y-%m-%d'))
                    elif promocode_data["stay_dates_option"] == 2:
                        if dt_travel >= info_travel_window_start and dt_travel <= info_travel_window_end:
                            list_dates.append(dt_travel.strftime('%Y-%m-%d'))
                    elif promocode_data["stay_dates_option"] == 3:
                        if dt_travel < info_travel_window_start or dt_travel > info_travel_window_end:
                            list_dates.append(dt_travel.strftime('%Y-%m-%d'))
                    else:
                        raise Exception("Travel Window type not exist")
            # Se asigna la lista de fechas sin elementos repetidos y se ordena
            info_voucher["valid_dates"] = sorted(set(list_dates))
        
        except Exception as format_error:
            #print(str(format_error))
            pass

        return info_voucher

    #Metodo para generar una lista de fechas
    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days+1)):
            yield start_date + timedelta(n)

    @staticmethod
    def search_promocode(promo_code):
        data_query = Model.query.filter(Model.code==promo_code, Model.estado==1).first()

        return data_query
    
    #Metodo para crear Promocodes
    @staticmethod
    def create_promocodes(json_data,id_promo_code,user_name=None):
        try:
            dataResponse = []
            schema = ModelSchema(exclude=Util.get_default_excludes())
            if user_name is None:
                user_data = base.get_token_data()
                user_name = user_data['user']['username']

            if int(id_promo_code) == 0:
                model = Model()
                model.name = json_data["name"]
                model.code = json_data["code"]
                model.estado = json_data["estado"]
                #numerical o only text 
                model.iddef_promo_code_discount_type = json_data["iddef_promo_code_discount_type"]
                if json_data["iddef_promo_code_discount_type"] == 1:
                    model.value_discount = json_data["value_discount"]
                    model.iddef_promo_code_type_amount = json_data["iddef_promo_code_type_amount"]
                    if json_data["iddef_promo_code_type_amount"] == 4:
                        model.currency_code = ""
                        model.maximum_nights_option = json_data["maximum_nights_option"]
                        if json_data['maximum_nights_option'] != 0:
                            model.maximum_nights_value = json_data["maximum_nights_value"]
                        else:
                            model.maximum_nights_value = 0.00
                    elif model.iddef_promo_code_type_amount == 3:
                        model.currency_code = json_data["currency_code"]
                        model.maximum_nights_option = json_data["maximum_nights_option"]
                        if json_data['maximum_nights_option'] != 0:
                            model.maximum_nights_value = json_data["maximum_nights_value"]
                        else:
                            model.maximum_nights_value = 0.00
                    else:
                        model.currency_code = json_data["currency_code"]
                        model.maximum_nights_option = 0
                        model.maximum_nights_value = 0.00
                else:
                    model.value_discount = 0.00
                    model.iddef_promo_code_type_amount = 0
                    model.currency_code = ""
                    model.maximum_nights_option = 0
                    model.maximum_nights_value = 0.00                    
                #pendiente maximum aplied nights
                model.min_LOS_option = json_data["min_LOS_option"]
                model.min_LOS_value = json_data["min_LOS_value"]
                model.min_booking_amount_option = json_data["min_booking_amount_option"]
                model.min_booking_value = json_data["min_booking_value"]
                model.max_booking_amount_option = json_data["max_booking_amount_option"]
                model.max_booking_value = json_data["max_booking_value"]
                model.stay_dates_option  = json_data["stay_dates_option"]
                model.stay_dates  = json_data["stay_dates_value"]
                model.booking_dates_option = json_data["booking_dates_option"]
                model.booking_dates  = json_data["booking_dates_value"]
                model.booking_times  = json_data["booking_times_value"]
                model.global_sales_limit_option = json_data["global_sales_limit_option"]
                model.global_sales_limit_value = json_data["global_sales_limit_value"]
                model.cancel_policy_id = json_data["cancel_policy_id"] #Id de la politica de cancelación que se consume de la api de dani
                model.channel_option = json_data["channel_option"]
                #campos pendientes
                model.room_types_option =json_data["room_types_option"]
                model.usuario_creacion = user_name
                db.session.add(model)            
                db.session.flush()
                insert = schema.dump(model)
                insert_iddef_promo_code = insert["iddef_promo_code"]
                dataResponse.append({"iddef_promo_code":insert["iddef_promo_code"]})

                #recorremos las descripciones e insertamos en text_lang
                dataResponseText = []
                for dataDescription in json_data["description"]:
                    Tmodel = tlModel()
                    schemaText = TextModelSchema(exclude=Util.get_default_excludes())
                    Tdata = schemaText.load(dataDescription)

                    Tmodel.lang_code = dataDescription["lang_code"]
                    Tmodel.text = dataDescription["text"]
                    Tmodel.table_name = "def_promo_code"
                    Tmodel.id_relation = insert_iddef_promo_code
                    Tmodel.attribute = "description"
                    Tmodel.estado = 1
                    Tmodel.usuario_creacion = user_name
                    db.session.add(Tmodel)
                    db.session.flush()
                    insertText = schemaText.dump(Tmodel)
                    dataResponseText.append({"iddef_text_lang":insertText["iddef_text_lang"]})
                dataResponse.append({"description":dataResponseText})
                                    
                #guardamos los datos de los canales permitidos o no permitidos promo_code_channel
                dataResponseChannel = []
                if json_data["channel_option"] != 1:                                        
                    for channels in json_data["channel_list"]:
                        pChannelModel = PChanelsModel()
                        schemaPChannel = PChannelsSchema(exclude=Util.get_default_excludes())
                        PChData = schemaPChannel.load(channels, unknown=EXCLUDE)
                        pChannelModel.iddef_promo_code = insert_iddef_promo_code
                        pChannelModel.iddef_channel = channels["iddef_channel"]
                        pChannelModel.estado = 1
                        pChannelModel.usuario_creacion = user_name
                        db.session.add(pChannelModel)
                        db.session.flush()
                        insertChannels = schemaPChannel.dump(pChannelModel)
                        dataResponseChannel.append({"iddef_promo_code_channels":insertChannels["iddef_promo_code_channels"]})
                dataResponse.append({"channel_list":dataResponseChannel})
                
                #insertamos en las tabla de def_promo_code_targeting_country
                schemaPTargeting = pTargetingModelSchema(exclude=Util.get_default_excludes())
                pTargeting = pTargetingModel()
                pTargeting.iddef_promo_code = insert_iddef_promo_code
                pTargeting.market_option = json_data["market_option"]
                pTargeting.market_targeting = json_data["market_targeting"]
                pTargeting.country_option = json_data["country_option"]
                pTargeting.country_targeting = json_data["country_targeting"]
                pTargeting.estado = 1
                pTargeting.usuario_creacion = user_name
                db.session.add(pTargeting)
                db.session.flush()
                insertTargeting = schemaPTargeting.dump(pTargeting)
                dataResponse.append({"iddef_promo_code_targeting_country": insertTargeting["iddef_promo_code_targeting_country"] })

                #Se insertan los datos en la tabla de def_promo_code_rateplan
                #(Esta es la tabla intermedia entre def_promo_code y op_rateplan)
                dataResponseRateplans = []
                for promo_code_property in json_data["promo_code_rateplans"]:
                    iddef_property = promo_code_property["iddef_property"]
                    data_rateplans = []
                    if len(promo_code_property["promo_code_rateplans"]) > 0:
                        for promo_code_rateplan in promo_code_property["promo_code_rateplans"]:
                            if len(promo_code_rateplan["rooms_rateplan"]) > 0:
                                promoCodeRatePlan_model = PromoCodeRatePlan()
                                schemaPromoCodeRatePlan = PromoCodeRatePlanSchema(exclude=Util.get_default_excludes())
                                promoCodeRatePlan_model.iddef_promo_code = insert_iddef_promo_code
                                promoCodeRatePlan_model.iddef_property = iddef_property
                                promoCodeRatePlan_model.idop_rateplan = promo_code_rateplan["idop_rateplan"]
                                promoCodeRatePlan_model.rooms_rateplan = promo_code_rateplan["rooms_rateplan"]
                                promoCodeRatePlan_model.estado = 1
                                promoCodeRatePlan_model.usuario_creacion = user_name
                                db.session.add(promoCodeRatePlan_model)
                                db.session.flush()
                                insertPromoCodeRatePlan = schemaPromoCodeRatePlan.dump(promoCodeRatePlan_model)
                                data_rateplans.append({"idop_rateplan":insertPromoCodeRatePlan["idop_rateplan"],"rooms_rateplan": insertPromoCodeRatePlan["rooms_rateplan"]})
                    dataResponseRateplans.append({"iddef_property": iddef_property,"promo_code_rateplans":data_rateplans})
                dataResponse.append({"promo_code_rateplans": dataResponseRateplans})
                
                db.session.commit()

        except Exception as ex:
            raise Exception("Error al crear promocode: "+str(ex))

        return dataResponse
    
    @staticmethod
    def search_book_promo_code(id_book=None,promo_code=None,isAll=True,count=True):
        conditions = []

        if id_book is not None:
            conditions.append(bpcModel.idbook_hotel==id_book)
        if promo_code is not None:
            conditions.append(bpcModel.promo_code==promo_code)
        if isAll:
            if count:
                data_promo_code = bpcModel.query.filter(and_(*conditions,bpcModel.estado==1)).count()
            else:
                data_promo_code = bpcModel.query.filter(and_(*conditions,bpcModel.estado==1)).all()
        else:
            data_promo_code = bpcModel.query.filter(and_(*conditions,bpcModel.estado==1)).first()

        return data_promo_code
