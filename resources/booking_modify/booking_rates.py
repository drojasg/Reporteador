from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_
from resources.rates.RatesHelper import RatesFunctions as funtions, rtSchema,\
vauchersFunctions, datetime, timedelta
from resources.age_range.age_range_service import AgeRangeService
from models.rates import CalendarSchema, PublicRatesSchema, RatesWithPromotions, ModifyBookingRates, ModifyBookingPayment
from models.room_type_category import RoomTypeCategory as rtcModel
from models.property import GetDataRatePlanSchema as dialyRateSchema
from models.age_code import AgeCode as agcModel
from models.rateplan import RatePlan as rpModel, BookingModifyRateplanGet as rtmSchema
from models.book_hotel import BookHotel as bhModel
from models.book_hotel_room import BookHotelRoom as bhrModel
from models.book_hotel_room_prices import BookHotelRoomPrices as bhrpModel
from models.promotions import Promotions
from models.policy import Policy
#from resources.rateplan import RatePlanPublic as funtions_policy
from common.public_auth import PublicAuth
import copy
from resources.restriction.restricctionHelper import RestricctionFunction as RestFuntions
from resources.booking.booking_operation import BookingOperation
from models.promo_code import PromoCode


class BookingModifyRates(Resource):

    #api-internal-booking-rates-get
    # @base.access_middleware
    def post(self):
        response = {}

        try:

            dataRq = request.get_json(force=True)
            schema = PublicRatesSchema()
            data = schema.load(dataRq)

            #Si no envia las fechas tomamos las fechas por defecto
            #A partir de 15 dias tomamos 5 dias
            if request.json.get("date_start") is None or request.json.get("date_end") is None:
                today = datetime.now().date()
                date_start = today + timedelta(days=15)
                date_end = today + timedelta(days=20)
            else:
                date_start = data["date_start"]
                date_end = data["date_end"]

            market_info = funtions.getMarketInfo(data["market"],data["lang_code"])
            idmarket = market_info.iddef_market_segment
            
            if request.json.get("property_code") is None:
                raise Exception("Field missing property_code is required")

            property_info = funtions.getHotelInfo(data["property_code"])
            idproperty = property_info.iddef_property

            if request.json.get("promotions") is None:
                data["promotions"] = True
            
            if request.json.get("room_status") is None:
                data["room_status"] = 1

            if request.json.get("lead_time") is None:
                data["lead_time"] = True

            #Obtenemos el total de pax, si no se envia se tomara el standar ocupancy de la habitacion
            ##Pendiente

            #Verificamos si llega el rate plan en el body del request
            ratePlans = []
            dataDump = []
            if data["room_status"] == 1:
                if request.json.get("rate_plan") is None:
                    #Obtenemos los rate plans disponibles para esta propiedad
                    ratePlans = funtions.getRateplanInfo(property_id=idproperty,\
                    date_start=date_start,date_end=date_end,bookin_window=True,\
                    only_one=False,market_id=idmarket,country=data["market"],\
                    validate_lead_time=data["lead_time"],language=data["lang_code"])
                else:
                    rate_plan = funtions.getRateplanInfo(rateplanId=data["rate_plan"],\
                    property_id=idproperty,date_start=date_start,date_end=date_end,\
                    bookin_window=True,market_id=idmarket,country=data["market"],\
                    validate_lead_time=data["lead_time"],language=data["lang_code"])
                    ratePlans.append(rate_plan)

                adultos = 0
                menores = 0
                get_rooms = False
                if request.json.get("rooms") is not None:
                    get_rooms = True
                    #Esto depende de la tabla
                    agcData = agcModel.query.filter(agcModel.estado==1).all()

                    age_code = [item.code for item in agcData]

                    for paxes in data["rooms"].keys():
                        if paxes in age_code:
                            if paxes.lower() == "adults":
                                adultos += data["rooms"][paxes]
                            elif paxes.lower() != "infants":
                                menores += data["rooms"][paxes]

                for rate_plan in ratePlans:

                    rateplanId = rate_plan.idop_rateplan
                    list_rateplans = []
                    list_rateplans.append(rateplanId)
                    promo_free_room = False

                    #obtenemos el nombre comercial del rateplan
                    txtData = funtions.getTextLangInfo("op_rateplan","commercial_name",\
                    data["lang_code"],rateplanId)

                    if txtData is not None:                        
                        rate_plan_name = txtData.text
                    else:
                        rate_plan_name = ""
                    
                    #utilizamos la informacion de la habitacion
                    roomType = rtcModel.query.get(data["room_type"])

                    if roomType is None:
                        raise Exception("Habitacion no encontrada")

                    roomTypes =  funtions.getRoomTypesForRatePlan(rateplanId,idproperty)
                    
                    if roomTypes is not None:
                        if isinstance(roomTypes,list):
                            idrooms_for_rateplan = [x.iddef_room_type_category for x in roomTypes]
                            if roomType.iddef_room_type_category not in idrooms_for_rateplan:
                                continue

                    #policies = funtions.get_policy_by_rateplan(rateplanId, date_start,lang_code=data["lang_code"], refundable=rate_plan.refundable)
                    policies = funtions.getPolicyDataByRatePlan(rateplanId, date_start)

                    if get_rooms == False:
                        adultos = roomType.standar_ocupancy
                        menores = 0

                    #Obtenemos la informacion de habitacion
                    roomTypeId = roomType.iddef_room_type_category

                    date_end_checkout = data["date_end"] - timedelta(days=1)

                    min_max_los = True

                    close_info = RestFuntions.getCloseDatesOperaRestriction(\
                    date_start,date_end_checkout,idproperty,\
                    roomTypeId,list_rateplans)

                    #Validamos las fechas cerradas
                    if len(close_info) >= 1:
                        for close in close_info:
                            for close_detail in close["dates"]:
                                if close_detail["close"] == True:
                                    min_max_los = False


                    min_los = RestFuntions.getMinLosOperaRestriction(\
                    date_start,date_start,idproperty,\
                    roomTypeId,list_rateplans)
                    if len(min_los) > 0:
                        total_lenght = date_end-date_start
                        if min_los[0]["dates"][0]["min_los"] != 0:
                            if total_lenght.days < min_los[0]["dates"][0]["min_los"]:
                                min_max_los = False
                    
                    max_los = RestFuntions.getMaxLosOperaRestriction(\
                    date_start,date_start,idproperty,\
                    roomTypeId,list_rateplans)
                    if len(max_los) > 0:
                        total_lenght = date_end-date_start
                        if  max_los[0]["dates"][0]["max_los"] != 0:
                            if total_lenght.days > max_los[0]["dates"][0]["max_los"]:
                                min_max_los = False
                        
                    total = 0
                    
                    if min_max_los == True:
                        #Obtenemos las tarifas necesarias
                        rates = funtions.getPricePerDay(idproperty,\
                        roomTypeId,rateplanId,date_start,date_end,\
                        adultos,menores,currency=data["currency"],market=idmarket,\
                        country=data["market"],pax_room=data["rooms"])
                        
                        total = rates["total"]

                        # rate_origin=[]
                        # rate_origin.append(rates)

                    rates_array = []
                    #Aplicamos las promociones(sin 2x1)
                    if data["promotions"] == True and total > 0:
                        try:
                            #rates_promotion.append(rates)
                            #rates_promotion = rate_origin.copy()

                            promotions = funtions.get_promotions_by_booking(date_start=date_start, 
                            date_end=date_end, market=data["market"], lang_code=data["lang_code"], \
                            hotel=data["property_code"],include_free_room=True,\
                            id_rateplan=rateplanId,id_room=roomTypeId)

                            #if data["promo_applied"]==False:
                            for promo in promotions:
                                for free in promo["free"]:
                                    if free["type"]==3:
                                        promo_free_room = True

                            rate_list_aux = []
                            for promo in promotions:
                                rates_promotion = []
                                rates_promotion.append(copy.deepcopy(rates))
                                promo_list = []
                                promo_list.append(promo)

                                aux_rate = funtions.apply_promotion(rates_promotion,\
                                promo_list)

                                rate_list_aux.append(copy.deepcopy(aux_rate["Prices"][0]))
                            
                            rates_aux = funtions.select_rates_promotion(rate_list_aux)

                            #rates_aux = funtions.calcualte_total(rates_aux)

                            funtions.calcualte_total(rates_aux)
                            
                            rates = rates_aux
                            total = rates["total"]

                        except Exception as promo_error:
                            pass

                        rates_array.append(rates)

                    if total > 0:
                        #Aplicamos los impuestos correspondientes(TAX)
                        try:
                            rates_with_tax = funtions.get_price_with_policy_tax(date_start,\
                            date_end,data["currency"], rates_array)

                            rates_array = rates_with_tax["data"]
                            rates = rates_array[0]

                            total = rates["total"]

                        except Exception as tax_error:
                            pass

                        
                    if total > 0:
                        #Aplicamos el inflado de tarifas
                        try:
                            rates_crossouts = funtions.apply_crossout_list(rates_array,\
                            idmarket,data["market"],True)

                            rates_array = rates_crossouts
                            rates = rates_array[0]

                            total = rates["total"]

                        except Exception as apply_cross_error:
                            pass

                    if total > 0:

                        dataDumped = schema.dump(rates)
                        #dataDumped["idop_rate_plan"]=rateplanId
                        dataDumped["rate_plan_name"]=rate_plan_name
                        dataDumped["policies"]=policies
                        dataDumped["promo_free_apply"]=promo_free_room

                        dataDump.append(dataDumped)

            if len(dataDump) > 0:
                dataDump = sorted(dataDump, key = lambda i: i['total'])

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataDump
            }               
            
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": []
            }

        return response

class BookingModifiRateplan(Resource):

    #api-internal-booking-rateplan-post
    # @base.access_middleware
    def post(self):
        response = {}

        try:

            dataRq = request.get_json(force=True)
            schema = rtmSchema()
            data = schema.load(dataRq)

            #Si no envia las fechas tomamos las fechas por defecto
            #A partir de 15 dias tomamos 5 dias
            if request.json.get("date_start") is None or request.json.get("date_end") is None:
                today = datetime.now().date()
                date_start = today + timedelta(days=15)
                date_end = today + timedelta(days=20)
            else:
                date_start = data["date_start"]
                date_end = data["date_end"]

            market_info = funtions.getMarketInfo(data["market"],data["lang_code"])
            idmarket = market_info.iddef_market_segment
            
            if request.json.get("property_code") is None:
                raise Exception("Field missing property_code is required")

            property_info = funtions.getHotelInfo(data["property_code"])
            idproperty = property_info.iddef_property

            if request.json.get("promotions") is None:
                data["promotions"] = True
            
            if request.json.get("room_status") is None:
                data["room_status"] = 1

            #Obtenemos el total de pax, si no se envia se tomara el standar ocupancy de la habitacion
            ##Pendiente

            #Verificamos si llega el rate plan en el body del request
            ratePlans = []
            dataDump = []
            
            if request.json.get("rate_plan") is None:
                #Obtenemos los rate plans disponibles para esta propiedad
                ratePlans = funtions.getRateplanInfo(property_id=idproperty,\
                date_start=date_start,date_end=date_end,bookin_window=True,\
                only_one=False,market_id=idmarket,country=data["market"],language=data["lang_code"])
            else:
                rate_plan = funtions.getRateplanInfo(rateplanId=data["rate_plan"],\
                property_id=idproperty,date_start=date_start,date_end=date_end,\
                bookin_window=True,market_id=idmarket,country=data["market"],language=data["lang_code"])
                ratePlans.append(rate_plan)

            adultos = 0
            menores = 0
            get_rooms = False
            if request.json.get("rooms") is not None:
                get_rooms = True
                #Esto depende de la tabla
                agcData = agcModel.query.filter(agcModel.estado==1).all()

                age_code = [item.code for item in agcData]

                for paxes in data["rooms"].keys():
                    if paxes in age_code:
                        if paxes.lower() == "adults":
                            adultos += data["rooms"][paxes]
                        elif paxes.lower() != "infants":
                            menores += data["rooms"][paxes]

            for rate_plan in ratePlans:

                rateplanId = rate_plan.idop_rateplan

                #obtenemos el nombre comercial del rateplan
                txtData = funtions.getTextLangInfo("op_rateplan","commercial_name",\
                data["lang_code"],rateplanId)

                if txtData is not None:                        
                    rate_plan_name = txtData.text
                else:
                    rate_plan_name = ""
                
                #utilizamos la informacion de la habitacion
                roomType = rtcModel.query.get(data["room_type"])

                if roomType is None:
                    raise Exception("Habitacion no encontrada")

                roomTypes =  funtions.getRoomTypesForRatePlan(rateplanId,idproperty)
                
                if roomTypes is not None:
                    if isinstance(roomTypes,list):
                        idrooms_for_rateplan = [x.iddef_room_type_category for x in roomTypes]
                        if roomType.iddef_room_type_category not in idrooms_for_rateplan:
                            continue

                #policies = funtions.get_policy_by_rateplan(rateplanId, date_start,lang_code=data["lang_code"], refundable=rate_plan.refundable)
                #policies = funtions.getPolicyDataByRatePlan(rateplanId, date_start)

                if get_rooms == False:
                    adultos = roomType.standar_ocupancy
                    menores = 0

                #Obtenemos la informacion de habitacion
                roomTypeId = roomType.iddef_room_type_category

                min_max_los = True
                    
                min_los = RestFuntions.getOperaRestrictions(id_restriction_by=4,\
                id_restriction_type=[2],id_room_type=roomTypeId,\
                id_property=idproperty,id_rateplan=rateplanId,date_start=date_start,\
                date_end=date_start,is_override=True)

                if min_los is not None:
                    for min_item in min_los:
                        total_lenght = date_end-date_start
                        if total_lenght.days < min_item.value:
                            min_max_los = False

                max_los = RestFuntions.getOperaRestrictions(id_restriction_by=4,\
                id_restriction_type=[3],id_room_type=roomTypeId,\
                id_property=idproperty,id_rateplan=rateplanId,date_start=date_start,\
                date_end=date_start,is_override=True)

                if max_los is not None:
                    for max_item in max_los:
                        total_lenght = date_end-date_start
                        if total_lenght.days > max_item.value:
                            min_max_los = False
                
                if min_max_los == True:
                    new_schema = rtSchema(only=("rate_code_clever","idop_rateplan",\
                    "rate_code_base","code","refundable"))
                    dataDumped = new_schema.dump(rate_plan)
                    #dataDumped["idop_rate_plan"]=rateplanId
                    dataDumped["rate_plan_name"]=rate_plan_name
                    #dataDumped["policies"]=policies

                    dataDump.append(dataDumped)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": dataDump
            }               
            
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": []
            }

        return response

class BookingModifyHelper():

    @staticmethod
    def calcualte_total_one(price):
        data={
            "total":0.00,
            "subtotal":0.00
        }
        
        new_total = 0
        new_total_crossout = 0
        for price_night in price["rates"]:
            new_total += price_night["amount"]
            price_night["amount_to_pms"] = price_night["amount"]
            #new_total_crossout += price_night["amount_crossout"]
        
        price["total"] = round(new_total,0)
        #price["total_crossout"] = round(new_total_crossout,0)

        data["total"]= round(price["total"],0)
        #data["subtotal"]= round(price["total_crossout"],0)

        return data
    
    @staticmethod
    def calcualte_total(price_list):
        data={
            "total":0.00,
            "subtotal":0.00
        }
        
        total = 0.00
        subtotal = 0.00
        for price in price_list:
            new_total = 0
            #new_total_crossout = 0
            for price_night in price["rates"]:
                new_total += price_night["amount"]
                price_night["amount_to_pms"] = price_night["amount"]
                #new_total_crossout += price_night["amount_crossout"]
            
            price["total"] = round(new_total,0)
            #price["total_crossout"] = round(new_total_crossout,0)

            total += price["total"]
            #subtotal += price["total_crossout"]

        data["total"]= round(total,0)
        #data["subtotal"]= round(subtotal,0)

        return data
    
    @staticmethod
    def apply_vaucher(prices,vaucher,currency_code,date_totay, idproperty):

        data = {
            "Vaucher_Apply":"",
            "Prices":[],
            "Total":0.00,
            "Subtotal":0.00,
            "vaucher_applied":False,
            "Text_Vaucher":""
        }

        totales = BookingModifyHelper.calcualte_total(prices)

        total = totales["total"]
        #subtotal = totales["subtotal"]
        total_vaucher_discount = 0

        if vaucher is not None:

            data["Vaucher_Apply"]=vaucher["code"]

            if vaucher["text_only"]== True:
                data["Text_Vaucher"] = vaucher["text"]
                data["vaucher_applied"] = True
            else:
                vaucher_value = funtions.convert_to_currency(currency_code,\
                vaucher["currency"],vaucher["abs_value"],date_totay)

                total_rooms = len(prices)
                total_rooms_cont = 0
                total_after = 0
                for price in prices:
                    total_discount_room = 0
                    total_nigth = len(price["rates"])
                    cont_nigth = 0
                    for rateplan_vaucher in vaucher["rateplans"]:
                        if idproperty == rateplan_vaucher["id_property"]:
                            if price["idop_rate_plan"] == rateplan_vaucher["id_rateplan"]:
                                if price["iddef_room_type"] in rateplan_vaucher["id_rooms"]:
                                    total_rooms_cont += 1
                                    for price_item in price["rates"]:
                                        date_str = datetime.strftime(price_item["efective_date"],"%Y-%m-%d")
                                        if date_str in vaucher["valid_dates"]:
                                            cont_nigth += 1
                                            if vaucher["type_amount"]==3:
                                                #Per night 
                                                #Se resta a cada noche de cada habitacion
                                                if vaucher_value > price_item["amount"]:
                                                    vaucher_value = price_item["amount"]
                                                total_vaucher_discount += vaucher_value
                                                total_discount_room += vaucher_value
                                                price_item["amount"] -= vaucher_value
                                                price_item["amount"] = round(price_item["amount"],0)
                                                price_item["amount_to_pms"] = price_item["amount"]
                                                price_item["vaucher_discount"] = vaucher_value
                                                data["vaucher_applied"] = True
                                                data["Text_Vaucher"] = "Se aplico el monto de descuento por dia"

                                            elif vaucher["type_amount"]==4:
                                                #Percent 
                                                #Se aplica un porcentaje a cada noche 
                                                #de cada habitacion
                                                amount_discount = round(price_item["amount"]*(vaucher["per_value"]/100),2)
                                                if amount_discount > price_item["amount"]:
                                                    amount_discount = price_item["amount"]
                                                total_vaucher_discount += amount_discount
                                                total_discount_room += amount_discount
                                                price_item["amount"] -= amount_discount
                                                price_item["amount"] = round(price_item["amount"],0)
                                                price_item["amount_to_pms"] = price_item["amount"]
                                                price_item["vaucher_discount"] = amount_discount
                                                data["vaucher_applied"] = True
                                                data["Text_Vaucher"] = "Se aplico un porcentaje de descuento por dia"

                                    totalroom = BookingModifyHelper.calcualte_total_one(price)
                                    price["total"] = totalroom["total"]
                                    price["discount_room"] = total_discount_room


                    if vaucher["type_amount"]==2 and cont_nigth == total_nigth:
                        #Per room, se resta al total de cada habitacion
                        if vaucher_value > price["total"]:
                            vaucher_value = price["total"]
                        total_vaucher_discount += vaucher_value
                        price["total"] -= vaucher_value
                        price["discount_room"] = vaucher_value
                        price["total"] = round(price["total"],0)
                        total_after += price["total"]

                        vaucher_per_day = vaucher_value/total_nigth
                        for price_item in price["rates"]:
                            price_item["amount_to_pms"] = round(price_item["amount"] - vaucher_per_day,2)
                            price_item["vaucher_discount"]= vaucher_per_day
                        data["vaucher_applied"] = True
                    else:
                        total_after += price["total"]

                totales["total"] = total_after
                
                if vaucher["type_amount"]==1 and total_rooms_cont == total_rooms:
                    vaucher_value /= total_rooms
                    #Per stay, se resta una parte igual al total de cada habitacion 
                    #solo si todas las habitaciones son compatibles con el vaucher
                    total_amount = 0
                    for price in prices:
                        if vaucher_value > price["total"]:
                            vaucher_value = price["total"]
                        total_vaucher_discount += vaucher_value
                        price["total"] -= vaucher_value
                        price["discount_room"] = vaucher_value
                        price["total"] = round(price["total"],0)
                        total_amount += price["total"]
                        vaucher_per_day = vaucher_value/total_nigth
                        for price_item in price["rates"]:
                            price_item["amount_to_pms"] = round(price_item["amount"] - vaucher_per_day,2)
                            price_item["vaucher_discount"]= vaucher_per_day
                        data["vaucher_applied"] = True

                    totales["total"] = total_amount
        
            #totales = RatesFunctions.calcualte_total_rates(prices)

        data["Prices"]=prices
        data["Total"]=round(totales["total"],0)
        data["Subtotal"]=round(total_vaucher_discount,0)
        
        return data


class BookingModifyCalculate(Resource):
    #api-internal-booking-rates-quote-post
    def post(self):

        response = {}

        try:
            dataRq = request.get_json(force=True)
            schema = ModifyBookingRates()
            data = schema.load(dataRq)

            if data["promocode"] != 0:

                prices = data["rooms"]
                promocode_txt = None
                vaucher_applied = False
                vaucher_discount = 0.0
                totales = BookingModifyHelper.calcualte_total(prices)

                try:
                    
                    promo_detail = PromoCode.query.get(data["promocode"])

                    if promo_detail is None:
                        raise Exception("Codigo de promocion no encontrado")

                    market_info = funtions.getMarketInfo(data["market"],data["lang_code"])
                    market_id = market_info.iddef_market_segment

                    property_info = funtions.getHotelInfo(data["hotel"])
                    property_id = property_info.iddef_property

                    rateplan_list = [x["idop_rate_plan"] for x in data["rooms"]]
                    rooms_list = [x["iddef_room_type"] for x in data["rooms"]]

                    vauchers = vauchersFunctions.getValidatePromoCode(promo_detail.code,\
                    property_code=data["hotel"],travel_window_start=data["date_start"],\
                    travel_window_end=data["date_end"],rateplans=rateplan_list,rooms=rooms_list,\
                    market=market_id,lang_code=data["lang_code"])

                    rates = BookingModifyHelper.apply_vaucher(data["rooms"],\
                    vauchers,data["currency"],datetime.now(),property_id)

                    if rates["vaucher_applied"] == True:
                        prices = rates
                        vaucher_applied = True
                        promocode_txt = rates["Text_Vaucher"]
                        vaucher_discount = rates["Subtotal"]

                except Exception as vaucher_error:
                    promocode_txt = str(vaucher_error)

                if vaucher_applied == True:
                    promocode_txt = prices["Text_Vaucher"]
                    vaucher_discount = prices["Subtotal"]
                    totales["total"] = prices["Total"]
                    prices = prices["Prices"]

                response_data = {
                    "rates":prices,
                    "total":totales["total"]+data["service_amount"],
                    "promocode_txt":promocode_txt,
                    "promocode_apply":vaucher_applied,
                    "descount":vaucher_discount,
                    "subtotal":totales["total"]+vaucher_discount-data["service_amount"]
                }

            else:

                # for rooms in data["rooms"]:
                #     for price_item in rooms["rates"]:
                #         price_item["amount_to_pms"]=price_item["amount"]

                totales = BookingModifyHelper.calcualte_total(data["rooms"])

                response_data = {
                    "rates":data["rooms"],
                    "total":totales["total"]+data["service_amount"],
                    "promocode_txt":"No promocode",
                    "promocode_apply":False,
                    "descount":0.0,
                    "subtotal":totales["total"]+0.0+data["service_amount"]
                }
            
            data_payment = BookingOperation.calcualte_payment_booking(rooms=data["rooms"],\
            total_amount=totales["total"],idbook_hotel=data["idbook_hotel"],currency=data["currency"])

            response_data["amount_to_pay"] =data_payment["amount_to_pay"]
            response_data["amount_paid"] =data_payment["amount_paid"]
            response_data["amount_pending_payment"] = data_payment["amount_pending_payment"]
            response_data["amount_to_pending_payment"] = data_payment["amount_to_pending_payment"]
            response_data["amount_refund"] = data_payment["amount_refund"]
            response_data["amount_to_refund"] = data_payment["amount_to_refund"]

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(response_data)
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


class BookingModifyCalculatePayment(Resource):
    #api-internal-booking-payment-get
    def get(self, idbook_hotel):

        response = {}

        try:
            schema = ModifyBookingPayment()
            rooms = []

            model = bhModel.query.filter(bhModel.idbook_hotel==idbook_hotel).first()

            for room in model.rooms:
                elem_room = {
                    "idbook_hotel_room": room.idbook_hotel_room,
                    "policies": {
                        "cancel":room.iddef_police_cancelation,
                        "booking":room.iddef_police_guarantee,
                        "tax":room.iddef_police_tax
                    },
                    "discount_room":room.discount_amount
                }
                prices = []
                for price in room.prices:
                    prices.append({"amount":price.total,"efective_date":price.date})
                elem_room["rates"] = prices
                rooms.append(elem_room)

            totales = BookingModifyHelper.calcualte_total(rooms)

            response_data = {
                "rates":rooms,
                "total":totales["total"],
                "descount":model.discount_amount,
                "subtotal":totales["total"]+0.0
            }
            
            data_payment = BookingOperation.calcualte_payment_booking(rooms=rooms,\
            total_amount=totales["total"],idbook_hotel=idbook_hotel,currency=model.currency.currency_code)

            response_data["amount_to_pay"] =data_payment["amount_to_pay"]
            response_data["amount_paid"] =data_payment["amount_paid"]
            response_data["amount_pending_payment"] = data_payment["amount_pending_payment"]
            response_data["amount_to_pending_payment"] = data_payment["amount_to_pending_payment"]
            response_data["amount_refund"] = data_payment["amount_refund"]
            response_data["amount_to_refund"] = data_payment["amount_to_refund"]

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(response_data)
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


class BookingRoomRatesInfo(Resource):
    #api-booking-room-rates-info-get
    # @base.access_middleware
    def get(self,idbook_hotel_room):
        response = {}

        try:
            result_room = bhrModel.query.get(idbook_hotel_room)

            dataInfoRates = BookingRoomRatesInfo.get_prices_by_room(idbook_hotel_room)
            dataInfoPolicies = BookingRoomRatesInfo.get_policies_info(id_policy_cancel=result_room.iddef_police_cancelation,\
                id_policy_guarantee=result_room.iddef_police_guarantee, id_policy_tax=result_room.iddef_police_tax)

            data_result = {
                "rates":dataInfoRates,
                "policies":dataInfoPolicies
            }

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data_result
            }               
            
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": []
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": []
            }

        return response

    @staticmethod
    def get_prices_by_room(id_room):
        list_rates = []
        list_info_prices = bhrpModel.query.filter(bhrpModel.idbook_hotel_room==id_room, bhrpModel.estado==1).order_by(bhrpModel.date.asc()).all()
        for info_price in list_info_prices:
            promotion_info = None
            if info_price.code_promotions != "":
                promotion_info = BookingRoomRatesInfo.get_promotion_by_code(info_price.code_promotions, info_price.promotion_amount)

            rate = {
                "percent_discount": info_price.discount_percent,
                "efective_date": info_price.date.strftime("%Y-%m-%d"),
                "amount_crossout": info_price.total_gross,
                "amount": info_price.total,
                "promotions": promotion_info,
                "tax_amount": info_price.country_fee,
                "vaucher_discount": info_price.promo_amount,
                "price_pms": info_price.price_to_pms
            }
            list_rates.append(rate)
        return list_rates

    @staticmethod
    def get_promotion_by_code(code_promotions, promotion_amount):
        result_promotion = None
        info_promotion = Promotions.query.filter(Promotions.code==code_promotions).order_by(Promotions.idop_promotions.desc()).first()
        if info_promotion is not None:
            result_promotion = {
                "id_promotion": info_promotion.idop_promotions,
                "value_discount": promotion_amount,
                "code": info_promotion.code
            }

        return result_promotion

    @staticmethod
    def get_policies_info(id_policy_cancel=0, id_policy_guarantee=0, id_policy_tax=0):
        policies = {
            "cancel_policy_detail": None,
            "guarantee_policy": None,
            "tax_policy": None
        }

        if id_policy_cancel > 0:
            policy_cancel = BookingRoomRatesInfo.get_policy(id_policy_cancel, 1)
            if policy_cancel is not None:
                policies["cancel_policy_detail"] = {
                    "id_policy": policy_cancel.iddef_policy,
                    "policy_code": policy_cancel.policy_code
                }
        if id_policy_guarantee > 0:
            policy_guarantee = BookingRoomRatesInfo.get_policy(id_policy_guarantee, 2)
            if policy_guarantee is not None:
                policies["guarantee_policy"] = {
                    "id_policy": policy_guarantee.iddef_policy,
                    "policy_code": policy_guarantee.policy_code
                }
        if id_policy_tax > 0:
            policy_tax = BookingRoomRatesInfo.get_policy(id_policy_tax, 3)
            if policy_tax is not None:
                policies["tax_policy"] = {
                    "id_policy": policy_tax.iddef_policy,
                    "policy_code": policy_tax.policy_code
                }

        return policies

    @staticmethod
    def get_policy(id, id_category):
        policy_model = Policy.query.filter(Policy.iddef_policy==id, Policy.iddef_policy_category==id_category).first()
        return policy_model
