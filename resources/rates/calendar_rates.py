from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from common.util import Util
from operator import itemgetter
from sqlalchemy import or_, and_
import datetime
from resources.rates.RatesHelper import RatesFunctions as funtions
from resources.age_range.age_range_service import AgeRangeService
from models.rates import CalendarSchema, PublicRatesSchema, RatesWithPromotions
from models.room_type_category import RoomTypeCategory as rtcModel
from models.property import GetDataRatePlanSchema as dialyRateSchema
from models.age_code import AgeCode as agcModel
from models.rateplan import RatePlan as rpModel
#from resources.rateplan import RatePlanPublic as funtions_policy
from common.public_auth import PublicAuth
import copy
from resources.restriction.restricctionHelper import RestricctionFunction as RestFuntions
from resources.promo_code.promocodeHelper import PromoCodeFunctions as vauchersFunctions

class Promotions(Resource):
    @PublicAuth.access_middleware
    def post(self):

        response = {}

        try:

            dataRq = request.get_json(force=True)
            schema = RatesWithPromotions()
            request_data = schema.load(dataRq)

            data = funtions.get_price_with_promotions(request_data["hotel"],request_data["market"],\
            request_data["date_start"],request_data["date_end"],request_data["currency"],request_data["lang_code"],\
            request_data["rooms"],vaucher_code=request_data["promocode"])

            dump_data = schema.dump(data)

            response = {
                "Code":200,
                "Msg":"Success",
                "Error":False,
                "data":dump_data
            }

            if data["error"] == True:
                response["Code"]=501
                response["Msg"]=data["msg"]
                response["Error"]=True

        except ValidationError as error:

            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": None
            }

        except Exception as e:

            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": None
            }

        return response

class PublicRates(Resource):
    #api-public-rates-post
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:

            dataRq = request.get_json(force=True)
            schema = PublicRatesSchema()
            data = schema.load(dataRq)

            #Si no envia las fechas tomamos las fechas por defecto
            #A partir de 15 dias tomamos 5 dias
            if request.json.get("date_start") is None or request.json.get("date_end") is None:
                today = datetime.datetime.now().date()
                date_start = today + datetime.timedelta(days=15)
                date_end = today + datetime.timedelta(days=20)
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

            if request.json.get("promo_applied") is None:
                data["promo_applied"]=True
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
                    only_one=False,market_id=idmarket,country=data["market"],validate_lead_time=True,language=data["lang_code"])
                elif data["rate_plan"] == 0:
                    #Si el rateplan 0 obtenemos todos los rateplans para esta propiedad
                    ratePlans = funtions.getRateplanInfo(property_id=idproperty,\
                    date_start=date_start,date_end=date_end,bookin_window=True,\
                    only_one=False,market_id=idmarket,country=data["market"],validate_lead_time=True,language=data["lang_code"])
                else:
                    rate_plan = funtions.getRateplanInfo(rateplanId=data["rate_plan"],\
                    property_id=idproperty,date_start=date_start,date_end=date_end,\
                    bookin_window=True,market_id=idmarket,country=data["market"],validate_lead_time=True,language=data["lang_code"])
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

                    #Si no se recibe un codigo de habitacion se utilizaran las habitaciones
                    #que tenga el rate plan
                    if request.json.get("room_type") is None:
                        #obtenemos las habitaciones del rate plan
                        roomTypes =  funtions.getRoomTypesForRatePlan(rateplanId,idproperty)

                        #Se obtienen los rooms que estén como room of the house
                        rooms_house = [roomItem for roomItem in roomTypes if roomItem.is_room_of_house == 1]

                        if len(rooms_house) > 0:
                            temp_dataDump = PublicRates.getInfoRatesbyRooms(data,list_rateplans,rooms_house,idproperty,rateplanId,idmarket,
                                get_rooms,adultos,menores,date_start,date_end)
                            if len(temp_dataDump) == 0:
                                dataDump = dataDump + PublicRates.getInfoRatesbyRooms(data,list_rateplans,roomTypes,idproperty,rateplanId,idmarket,
                                    get_rooms,adultos,menores,date_start,date_end)
                            else:
                                dataDump = dataDump + temp_dataDump
                        else:
                            dataDump = dataDump + PublicRates.getInfoRatesbyRooms(data,list_rateplans,roomTypes,idproperty,rateplanId,idmarket,
                                get_rooms,adultos,menores,date_start,date_end)
                            
                    else:
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

                        policies = funtions.get_policy_by_rateplan(rateplanId, date_start,lang_code=data["lang_code"], refundable=not rate_plan.refundable)

                        if get_rooms == False:
                            adultos = roomType.standar_ocupancy
                            menores = 0

                        #Obtenemos la informacion de habitacion
                        roomTypeId = roomType.iddef_room_type_category

                        min_max_los = True

                        date_end_checkout = data["date_end"] - datetime.timedelta(days=1)

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

                                if data["promo_applied"]==False:
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

    @staticmethod
    def getInfoRatesbyRooms(data,list_rateplans,roomTypes,idproperty,rateplanId,idmarket,get_rooms,adultos,menores,date_start,date_end):
        dataDump = []
        for roomItem in roomTypes:

            if get_rooms == False:
                adultos = roomItem.standar_ocupancy
                menores = 0

            #Implementar las restricciones de fechas cerradas por rateplan
            #Implementar las restricciones de minimos y maximos
            min_max_los = True

            date_end_checkout = data["date_end"] - datetime.timedelta(days=1)

            close_info = RestFuntions.getCloseDatesOperaRestriction(\
            date_start,date_end_checkout,idproperty,\
            roomItem.iddef_room_type_category,list_rateplans)

            #Validamos las fechas cerradas
            if len(close_info) >= 1:
                for close in close_info:
                    for close_detail in close["dates"]:
                        if close_detail["close"] == True:
                            min_max_los = False

            min_los = RestFuntions.getMinLosOperaRestriction(\
            date_start,date_start,idproperty,\
            roomItem.iddef_room_type_category,list_rateplans)
            if len(min_los) > 0:
                total_lenght = date_end-date_start
                if min_los[0]["dates"][0]["min_los"] != 0:
                    if total_lenght.days < min_los[0]["dates"][0]["min_los"]:
                        min_max_los = False
                            
            max_los = RestFuntions.getMaxLosOperaRestriction(\
            date_start,date_start,idproperty,\
            roomItem.iddef_room_type_category,list_rateplans)
            if len(max_los) > 0:
                total_lenght = date_end-date_start
                if  max_los[0]["dates"][0]["max_los"] != 0:
                    if total_lenght.days > max_los[0]["dates"][0]["max_los"]:
                        min_max_los = False

            total = 0

            if min_max_los == True:
                #Obtenemos las tarifas necesarias
                rates = funtions.getPricePerDay(idproperty,\
                roomItem.iddef_room_type_category,rateplanId,date_start,date_end,\
                adultos,menores,currency=data["currency"],market=idmarket,\
                country=data["market"])

                total = rates["total"]

            rates_array = []
            if data["promotions"] == True and total > 0:
                try:
                    # rates_promotion = []
                    # rates_promotion.append(rates)

                    promotions = funtions.get_promotions_by_booking(date_start=date_start, 
                    date_end=date_end, market=data["market"], lang_code=data["lang_code"], \
                    hotel=data["property_code"],id_rateplan=rateplanId,\
                    id_room=roomItem.iddef_room_type_category, include_free_room=False)

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

                    #funtions.calcualte_total(rates_aux)

                    rates = rates_aux

                    total = rates["total"]

                except Exception as promo_error:
                    pass

                rates_array.append(rates)

            if total > 0:
                #Aplicamos los tax correspondientes
                try:
                    rates_with_tax = funtions.get_price_with_policy_tax(date_start,\
                    date_end,data["currency"], rates_array)

                    rates_array = rates_with_tax["data"]
                    rates = rates_with_tax["data"][0]

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
                            
            #Seteamos los valores necesarios para el response, el 
            #primero que se encuentre con tarifa diferente a 0
            if total > 0:

                schema2 = PublicRatesSchema(only=("avg_total","avg_total_discount",\
                "total_percent_discount","total"))

                dataDump.append(schema2.dump(rates))

                break

        return dataDump

class CalendarRates(Resource):
    #api-rates-prices-get-calendar
    #@base.access_middleware
    def post(self):

        response = {}

        try:

            requestData = request.get_json(force=True)
            schema = CalendarSchema()
            data = schema.load(requestData)

            room = rtcModel.query.get(data["room_type_code"])

            max_adt = 0
            max_chd = 0
            acept_chd = True
            if room is not None:
                max_adt = room.max_adt
                max_chd = room.max_chd
                acept_chd = bool(room.acept_chd)
            else:
                raise Exception("Habitacion no encontrada")

            if max_adt <= 0:
                raise Exception("Habitacion no contiene una ocupacion de adultos maxima de pax o es 0")

            if acept_chd is True:
                if max_chd <= 0:
                    raise Exception("Habitacion no contiene una ocupacion de menores maxima de pax o es 0")

            schema2 = dialyRateSchema()
            dataResponse = []
            adts = 1
            while adts <= max_adt:

                idPax = funtions.getIdPaxtype(adts)

                if data["currency_code"] != "" or data["country_code"] != "" or data["market_id"] != 0:
                    if data["currency_code"] == "":
                        data_rateplan = rpModel.query.get(data["rate_plan_code"])
                        currency_rateplan = data_rateplan.currency_code
                        currency_code = currency_rateplan.upper()
                    else:
                        currency_code = data["currency_code"]
                    rates_per_day = funtions.getPricePerDay(data["property_code"],\
                    data["room_type_code"],data["rate_plan_code"],data["date_start"],\
                    data["date_end"],adts,0,use_booking_window=False,\
                    currency=currency_code,market=data["market_id"],\
                    country=data["country_code"],apply_crossout=True,show_cero=True)
                else:
                    rates_per_day = funtions.getPricePerDay(data["property_code"],\
                    data["room_type_code"],data["rate_plan_code"],data["date_start"],\
                    data["date_end"],adts,0,use_booking_window=False,apply_crossout=True,\
                    show_cero=True)

                ratesDump = schema2.dump(rates_per_day)

                itemAdult = {
                    "pax":adts,
                    "name":"Adult",
                    "is_adult":True,
                    "pax_id":idPax,
                    "prices":ratesDump["price_per_day"]
                }

                dataResponse.append(itemAdult)

                adts += 1

            if acept_chd is True:
                pax_list = AgeRangeService.get_all_age_range(data["property_code"])
                
                chds = 1
                #while chds <= max_chd:
                for pax_item in pax_list:
                    if pax_item[1] not in ["adults"]:
                        if data["currency_code"] != "" or data["country_code"] != "" or data["market_id"] != 0:
                            if data["currency_code"] == "":
                                data_rateplan = rpModel.query.get(data["rate_plan_code"])
                                currency_rateplan = data_rateplan.currency_code
                                currency_code = currency_rateplan.upper()
                            else:
                                currency_code = data["currency_code"]

                            if pax_item[1] == "infants":
                                rates_per_day = funtions.getFakePricePerDay(data["property_code"],\
                                data["room_type_code"],data["rate_plan_code"],data["date_start"],\
                                data["date_end"],0,chds,use_booking_window=False,\
                                currency=currency_code,market=data["market_id"],country=data["country_code"])
                            else:                                    
                                rates_per_day = funtions.getPricePerDay(data["property_code"],\
                                data["room_type_code"],data["rate_plan_code"],data["date_start"],\
                                data["date_end"],0,chds,use_booking_window=False,\
                                currency=currency_code,market=data["market_id"],country=data["country_code"],\
                                apply_crossout=True,show_cero=True,spp=False)
                        else:
                            if pax_item[1] == "infants":
                                rates_per_day = funtions.getFakePricePerDay(data["property_code"],\
                                data["room_type_code"],data["rate_plan_code"],data["date_start"],\
                                data["date_end"],0,chds,use_booking_window=False)
                            else:        
                                rates_per_day = funtions.getPricePerDay(data["property_code"],\
                                data["room_type_code"],data["rate_plan_code"],data["date_start"],\
                                data["date_end"],0,chds,use_booking_window=False,\
                                apply_crossout=True, show_cero=True,spp=False)
                        
                        ratesDump = schema2.dump(rates_per_day)

                        itemChd = {
                            "pax":chds,
                            "name": pax_item[1] + " ("+ str(pax_item[2]) +"-"+ str(pax_item[3]) +")",
                            "is_adult":False,
                            "pax_id":1,
                            "prices": ratesDump["price_per_day"]
                        }

                        dataResponse.append(itemChd)
                
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