from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from models.rateplan import RatePlan as rpModel
from models.rateplan_prices import RatePlanPrices as rppModel, RatePlanPricesSchema as rtpSchema
from models.room_type_category import RoomTypeCategory as rtcModel
from models.property import Property as prModel
from models.rate_plan_rooms import RatePlanRooms as rprModel
from models.market_segment import MarketSegment as msModel
from models.restriction import Restriction as ResModel
from models.restriction_detail import RestrictionDetail as ResDetModel
from config import db, base
from models.calendar import calendarData, calendarData2,\
calendarSave as SaveModeSchema, calendarAvailRoom as AvailModeSchema,\
calendarDisabledRoom as disabledModelSchema, calendarMinMaxSchema as MinMaxSchema,\
calendarSaveMinMaxSchema as MinMaxSaveSchema
from common.util import Util
import calendar
import datetime
import random
from datetime import datetime as dt
from resources.rates.RatesHelper import RatesFunctions as functions
from resources.inventory.inventory import Inventory as functionsInventory
from resources.restriction.restricctionHelper import RestricctionFunction as resFuntions
from resources.exchange_rate.exchange_rate_service import ExchangeRateService as funtionsExchange
from common.public_auth import PublicAuth
from resources.restriction.restricctionHelper import RestricctionFunction as restFuntions

class Calendar(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:
            schema = calendarData()
            data = schema.load(request.get_json(force=True))

            #market_code = request.headers.get("market")
            #currency = request.headers.get("currency")
            date_today = dt.today().date()
            date_start = datetime.datetime(data["date_start"].year,data["date_start"].month,1).date() 
            date_end = datetime.datetime(data["date_end"].year,data["date_end"].month,\
            calendar.monthrange(data["date_end"].year,data["date_end"].month)[1]).date()

            if request.json.get("date_specified") is None:
                data["date_specified"] = False

            if data["date_specified"] == False:
                if data["date_start"].year != data["date_end"].year:
                    date_end = datetime.datetime(data["date_end"].year,12,31).date()
                else:
                    date_end = datetime.datetime(data["date_end"].year,12,31).date()

            if data["property_code"] is None:
                property_code = "ZHBP"
            else:
                property_code = data["property_code"]

            #Obtenemos informacion del mercado seleccionado
            msData = functions.getMarketInfo(data["market"])
            msId = msData.iddef_market_segment

            #Obtenemos informacion de las propiedades
            prData = functions.getHotelInfo(property_code)
            prId = prData.iddef_property

            rpData = functions.getRateplanInfo(property_id=prId,date_start=date_start,\
            date_end=date_end,market_id=msId,bookin_window=True,only_one=True,country=data["market"])
            rpId = rpData.idop_rateplan

            #obtenemos currency rateplan
            data_rateplan =  rpModel.query.get(rpId)
            currency_rateplan = data_rateplan.currency_code
            currency_rateplan = currency_rateplan.upper()
            
            currency = data["currency"]
            currency = currency.upper()
            
            Exange_apply = False
            to_usd_amount = 1
            exange_amount = 1
            #Verificamos el tipo de cambimo solicitado sea diferente a su base
            if currency != currency_rateplan:
                Exange_apply = True
                #Si el tipo de cambio del rate plan esta en pesos y se solicita en un tipo de cambio
                #diferente a dolares, es necesario convertir de pesos a dolares primero
                #Y despues de dolares al tipo de cambio solicitado
                if currency_rateplan != "USD":
                    #Siempre vamos a converir a dolares primero
                    exangeDataMx = funtionsExchange.get_exchange_rate_date(date_today,currency_rateplan)
                    to_usd_amount = round(exangeDataMx.amount,2)

                if currency != "USD":
                    exangeData = funtionsExchange.get_exchange_rate_date(date_today,currency)
                    exange_amount = round(exangeData.amount,2)

            rtcData = functions.getRoomTypesForRatePlan(rpId,prId,only_firts=True)
            rtcId = rtcData.iddef_room_type_category
            rtcOcupancy = rtcData.standar_ocupancy

            #Obtenemos el id del standar_ocupancy del cuarto por defecto
            idPax_dft = functions.getIdPaxtype(rtcOcupancy)

            rates_avail = functions.getPrices(prId,rpId,rtcId,idPax_dft,date_start,\
            date_end,order_desc=False)

            ratesItems = []
            ratesOverride = []
            element_date_start = date_start
            element_date_end = date_start
            amount = 0.0
            for rates in rates_avail:

                list_rates = [d for d in ratesItems \
                if rates.is_override == 0 if ((datetime.datetime.strptime(d["date_start"],\
                "%Y-%m-%d").date() <= rates.date_start and datetime.datetime.strptime(d["date_end"],\
                "%Y-%m-%d").date() >= rates.date_end) \
                or (datetime.datetime.strptime(d["date_start"],\
                "%Y-%m-%d").date() >= rates.date_start and datetime.datetime.strptime(d["date_end"],\
                "%Y-%m-%d").date() <= rates.date_end))]

                if len(list_rates)<=0:
                    
                    amount = rates.amount
                    #Si se necesita hacer alguna conversion
                    if Exange_apply == True:
                        #Primero convertimos a dolares
                        amount = round(amount / to_usd_amount,2)

                        #De dolares convertimos al tipo de cambio solicitado
                        amount = round(amount * exange_amount,2)
                    element = {
                        "date_start": rates.date_start.strftime("%Y-%m-%d"),
                        "date_end": rates.date_end.strftime("%Y-%m-%d"),
                        "amount":amount
                    }
                    if rates.is_override == 0:
                        element_date_start = rates.date_start
                        if rates.date_end > element_date_end:
                            element_date_end = rates.date_end
                        ratesItems.append(element)
                    else:
                        ratesOverride.append(element)


            if element_date_end < date_end:
                element_date_start = element_date_end + datetime.timedelta(days=1)
                extra_element = {
                    "date_start":element_date_start.strftime("%Y-%m-%d"),
                    "date_end":date_end.strftime("%Y-%m-%d"),
                    "amount": 0.0
                }
                ratesItems.append(extra_element)


            #Obtenemos las fechas de ofertas
            oferItems = []
            oferts1 = {
                "date_start":datetime.datetime(data["date_start"].year,\
                data["date_start"].month,10).strftime("%Y-%m-%d"),
                "date_end":datetime.datetime(data["date_start"].year,\
                data["date_start"].month,10).strftime("%Y-%m-%d"),
                "ofert":True
            }
            oferItems.append(oferts1)
            oferts2 = {
                "date_start":datetime.datetime(data["date_start"].year,\
                data["date_end"].month,20).strftime("%Y-%m-%d"),
                "date_end":datetime.datetime(data["date_start"].year,\
                data["date_end"].month,20).strftime("%Y-%m-%d"),
                "ofert":True
            }
            oferItems.append(oferts2)

            #Obtenemos las fechas de cierres
            closeItems = []
            rateplans_list = []
            rateplans_list.append(rpId)
            close_dates_v2 = restFuntions.getCloseDatesOperaRestriction(date_start,\
            date_end,prId,rtcId,rateplans_list)
            
            if len(close_dates_v2)>=1:
                for item_close_date in close_dates_v2[0]["dates"]:
                    if item_close_date["close"] == True:
                        item_close = {
                            "date_start": item_close_date["efective_date"],
                            "date_end":item_close_date["efective_date"],
                            "close":True
                        }
                        closeItems.append(item_close)

            # close_dates = restFuntions.getOperaRestrictions(id_restriction_by=5,\
            # id_restriction_type=[1],id_property=prId,date_start=date_start,\
            # date_end=date_end, estado=1)

            # closeItems = []
            # if len(close_dates) >= 1:
            #     for close_date in close_dates:
            #         item_close = {
            #             "date_start": close_date.date_start.strftime("%Y-%m-%d"),
            #             "date_end":close_date.date_end.strftime("%Y-%m-%d"),
            #             "close":True
            #         }
            #         closeItems.append(item_close)

            response = {
                "Code":200,
                "Msg": "Succes",
                "Error":False,
                "data": {
                    "rates":ratesItems,
                    "close_dates":closeItems,
                    "oferts":oferItems,
                    "rates_fix":ratesOverride
                }
            }

        except ValidationError as Error:
            response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
        except Exception as ex:
            response = {
                "Code":500,
                "Msg":str(ex),
                "Error":True,
                "data":{}
            }
        
        return response

class CalendarV2(Resource):

    #api-calendar-get
    def post(self):

        response = {}

        try:
            schema = calendarData()
            data = schema.load(request.get_json(force=True))

            #market_code = request.headers.get("market")
            #currency = request.headers.get("currency")

            dates = []
            if data["date_start"].year != data["date_end"].year:
                count1 = data["date_start"].month
                while count1 <= 12:
                    date_value=datetime.datetime(data["date_start"].year,count1,1).date()
                    dates.append(date_value)
                    count1 += 1
                count2 = data["date_end"].month
                while count2 <= 12:
                    date_value=datetime.datetime(data["date_end"].year,count2,1).date()
                    dates.append(date_value)
                    count2 += 1
            else:
                count1 = data["date_start"].month
                while count1 <= 12:
                    date_value=datetime.datetime(data["date_start"].year,count1,1).date()
                    dates.append(date_value)
                    count1 += 1


            if data["property_code"] is None:
                property_code = "ZHBP"
            else:
                property_code = data["property_code"]


            #Obtenemos informacion del mercado seleccionado
            msData = functions.getMarketInfo(data["market"])
            msId = msData.iddef_market_segment

            #Obtenemos informacion de las propiedades
            prData = functions.getHotelInfo(property_code)
            prId = prData.iddef_property
            
            
            dateResponse = []

            for efective_dates in dates:

                calendarInit = calendar.TextCalendar(calendar.MONDAY)

                cont = 0   
                for fecha in calendarInit.itermonthdays(efective_dates.year,efective_dates.month):
                    dataResponse = calendarData()
                    if fecha != 0:
                        cont = cont + 1
                        dataResponse.efective_date = datetime.datetime(efective_dates.year,efective_dates.month,fecha).date()
                        
                        try:
                            #Obtenemos un rate plan para evaluar
                            rpData = functions.getRateplanInfo(property_id=prId,\
                            bookin_window=True, date_start=dataResponse.efective_date, \
                            date_end=dataResponse.efective_date, market_id=msId,\
                            only_one=True)
                            rpId = rpData.idop_rateplan

                            #Obtenemos la habitacion por defecto del rate plan selecionado
                            rtcData = functions.getRoomTypesForRatePlan(rpId,\
                            prId,only_firts=True)
                            rtcId = rtcData.iddef_room_type_category
                            rtcOcupancy = rtcData.standar_ocupancy

                            #Obtenemos el id del standar_ocupancy del cuarto por defecto
                            idPax_dft = functions.getIdPaxtype(rtcOcupancy)

                            #Con los datos encontrados hasta ahora, buscamos las tarifas correspondientes
                            tarifa = functions.getPrices(prId,rpId,rtcId,idPax_dft,\
                            dataResponse.efective_date,dataResponse.efective_date)

                            if len(tarifa) > 0:
                                dataResponse.dialy_rate = tarifa[0].amount

                            #Conversion de monedas pendiente

                        except Exception as error_detail:
                            dataResponse.dialy_rate = 0                            
                        
                        if cont == 10 or cont == 30:
                            dataResponse.is_close = True                            
                        else:
                            dataResponse.is_close = False

                        if cont == 20 or cont == 26:
                            dataResponse.is_offer = True
                            #dataResponse.dialy_rate = 120.30
                        else:
                            dataResponse.is_offer = False

                        dateResponse.append(dataResponse)
            
            response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": schema.dump(dateResponse,many=True)
                }           

        except ValidationError as Error:
            response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
        except Exception as ex:
            response = {
                "Code":500,
                "Msg":str(ex),
                "Error":True,
                "data":{}
            }

        return response 

class CalendarPrice(Resource):
    #api-calendar-update
    # @base.access_middleware
    def post(self):
        try:
            result = []
            schema = SaveModeSchema()
            schemaRPP = rtpSchema(exclude=Util.get_default_excludes())
            data = schema.load(request.get_json(force=True))
            id_property = data["id_property"]
            id_room = data["id_room"]
            id_rate_plan = data["id_rate_plan"]
            data_prices = data["prices"]
            #Validar si existe propiedad
            data_property = prModel.query.get(id_property)
            data_room = rtcModel.query.get(id_room)
            data_plan = rpModel.query.get(id_rate_plan)
            if data_property is None or data_room is None or data_plan is None:
                return {
                    "Code": 404,
                    "Msg": "data not found",
                    "Error": True,
                    "data": {}
                }
            else:
                #Aqui iterar los prices
                for itemPrice in data_prices:
                    amount = itemPrice["amount"]
                    id_pax = itemPrice["id_pax"]
                    date_start = itemPrice["date_start"]
                    date_end = itemPrice["date_end"]
                    #Validar que las fechas sean de un sólo día
                    if date_start == date_end:
                        #Validar que la tarifa no sea 0
                        if amount < 0:
                            ms = "Error is not allowed negative and zero values: " + str(amount)
                            response = {
                                    "Code":500,
                                    "Msg": ms,
                                    "Error":True,
                                    "data": {}
                                }
                            result.append(response)
                        else:
                            #Se inserta tarifa que sea mayor a 0
                            try:
                                rates_override = functions.getPrices(id_property,id_rate_plan,id_room,\
                                    id_pax,date_start,date_end,order_desc=True)
                                #Actualizar tarifa:
                                if len(rates_override) > 0:
                                    #Filtrar registros encontrados:
                                    data = schemaRPP.dump(rates_override, many=True)
                                    data_rates_override = list(filter(lambda elem_override: elem_override['is_override'] == 1, data))
                                    #Actualizar estado = 0
                                    for xPrice in data_rates_override:
                                        id_price = xPrice["idop_rateplan_prices"]
                                        dataRPP = rppModel.query.get(id_price)
                                        dataRPP.estado = 0
                                        db.session.commit()
                                    #crear nuevo registro
                                    prices = self.create_price(id_property,id_rate_plan,id_room, id_pax,amount,date_start,date_end)
                                else:
                                    prices = self.create_price(id_property,id_rate_plan,id_room,id_pax,amount,date_start,date_end) 
                                result.append(prices)
                            except Exception as exception:
                                response = {
                                        "Code":500,
                                        "Msg":str(exception),
                                        "Error":True,
                                        "data":{}
                                    }
                                result.append(response)
                    else:
                        date_start = date_start.strftime('%m/%d/%Y')
                        date_end = date_end.strftime('%m/%d/%Y')
                        ms = "Date Range Error " + date_start + "-" + date_end
                        response = {
                                "Code":500,
                                "Msg": ms,
                                "Error":True,
                                "data": {}
                            }
                        result.append(response)
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
        except Exception as ex:
            db.session.rollback()
            response = {
                "Code":500,
                "Msg":str(ex),
                "Error":True,
                "data":{}
            }

        return response 

    @staticmethod
    def create_price(id_property,id_rate_plan,id_room, id_pax,amount,date_start,date_end):
        #Crear tarifa
        schemaRPP = rtpSchema(exclude=Util.get_default_excludes())
        user_data = base.get_token_data()
        user_name = user_data['user']['username']
        data = None
        try: 
            rppData = rppModel()
            rppData.idproperty = id_property
            rppData.idrateplan = id_rate_plan
            rppData.idroom_type = id_room
            rppData.idpax_type = id_pax
            rppData.amount = amount
            rppData.date_start = date_start
            rppData.date_end = date_end
            rppData.estado = 1
            rppData.usuario_creacion = user_name
            rppData.is_override = 1
            db.session.add(rppData)
            db.session.commit()
            data = schemaRPP.dump(rppData)
        except Exception as ex:
            raise Exception("Error al crear/actualizar la tarifa "+str(ex))

        return data
    
class CalendarAvail(Resource):
    #api-calendar-get-avail
    # @base.access_middleware
    def post(self):
        try:
            result = []
            schema = AvailModeSchema()
            schemaRPP = rtpSchema(exclude=Util.get_default_excludes())
            data = schema.load(request.get_json(force=True))
            id_property = data["id_property"]
            id_room = data["id_room_type"]
            date_start = data["date_start"]
            date_end = data["date_end"]
            count = 0
            totalDay = date_end - date_start
            band_exist = False
            status = "N/A"
            element_date = date_start
            while count < (totalDay.days + 1):
                #Recorrer las fechas
                try:
                    #Aqui la operacion de busqueda de fecha
                    data_avail = functionsInventory.get_inventory(id_room=id_room,date_start=element_date, id_property=id_property,only_one=True)
                    if data_avail is not None:
                        status = data_avail.avail_rooms
                        band_exist = True
                    else:
                        status = 0
                        band_exist = False

                except Exception as exceptio:
                    pass 
                element_status = {
                    "date": element_date.strftime("%Y-%m-%d"),
                    "avil_room": status,
                    "exist": band_exist
                }
                result.append(element_status)
                count += 1
                element_date = element_date + datetime.timedelta(days=1)
        
            response = {
                    "Code": 200,
                    "Msg": "Success",
                    "Error": False,
                    "data": result
                }
        
        except ValidationError as Error:
            response = {
                    "Code":500,
                    "Msg": Error.messages,
                    "Error":True,
                    "data": {}
                }
        except Exception as ex:
            response = {
                "Code":500,
                "Msg":str(ex),
                "Error":True,
                "data":{}
            }

        return response

class CalendarDisabled(Resource):
    #api-calendar-disabled-room
    # @base.access_middleware
    def post(self):
        try:
            result = []
            rateplans = []
            room_valid = None
            json_data = request.get_json(force=True)
            schema = disabledModelSchema()
            data = schema.load(json_data)
            id_property = data["id_property"]
            id_room = data["id_room_type"]
            try:
                #validacion de habitacion valida
                room_valid = functions.getRoomTypeInfo(idproperty=id_property, idroom_type=id_room)
            
            except Exception as room_error:
                pass

            if room_valid is None:
                raise Exception("Room Type {0:s} no encontrado para la propiedad, favor de verificar que el tipo de habitacion exista: " + str(id_room))
            else:
                for itm in data["rateplans"]:
                    id_rateplan = itm["rateplan_id"]
                    resultClose = []
                    rateplan_valid = None
                    try:
                        #validacion de habitacion valida
                        rateplan_valid = functions.getRateplanPropertyRoomInfo(property_id=id_property,rateplan_id=id_rateplan, roomtype_id=id_room)
                    
                    except Exception as rateplan_error:
                        dataRatePlans = {
                                "Code":500,
                                "Msg": "Error: " + str(rateplan_error),
                                "Error":True,
                                "data": {}
                            }
                        rateplans.append(dataRatePlans)

                    if rateplan_valid is not None:
                        if len(itm["dates"]) > 0:
                            for date in itm["dates"]:
                                bandClose = 1
                                if date["close"] == True:
                                    bandClose = 0
                                data_filter_dates = resFuntions.getOperaRestrictions(id_restriction_by=4,\
                                id_restriction_type=[1], id_room_type=id_room, id_property=id_property,\
                                id_rateplan = id_rateplan, is_override=1, date_start=date["date_start"],\
                                date_end=date["date_end"], is_order=True)
                                if len(data_filter_dates) > 0:
                                    cont = 0
                                    while cont < len(data_filter_dates):
                                        restrictionOperaDelete = resFuntions.updateOPeraRestrictionsbyRoom(model=data_filter_dates[cont], estado=0)
                                        cont += 1
                                    date_start_before = date["date_start"] - datetime.timedelta(days=1)
                                    date_start_after = date["date_start"] + datetime.timedelta(days=1)
                                    date_end_before = date["date_end"] - datetime.timedelta(days=1)
                                    date_end_after = date["date_end"] + datetime.timedelta(days=1)
                                    restrictionOpera = None
                                    for indx, itm in enumerate(data_filter_dates):
                                        if itm.date_start == date["date_start"] and itm.date_end == date["date_end"] and itm.value != bandClose:
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.updateOPeraRestrictionsbyRoom(model=data_filter_dates[indx],\
                                                value=bandClose)
                                        elif itm.date_end < date["date_end"] and itm.date_start == date["date_start"]:
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])
                                        elif itm.date_start < date["date_start"] and itm.date_end > date["date_end"] and itm.value != bandClose: 
                                            restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                            id_rateplan, id_room, itm.value, itm.date_start, date_start_before)
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])
                                            restrictionOpera2 = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                            id_rateplan, id_room, itm.value, date_end_after, itm.date_end)
                                        elif itm.date_end > date["date_end"] and itm.date_start > date["date_start"] and itm.value != bandClose:
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])
                                            restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                            id_rateplan, id_room, itm.value, date_end_after, itm.date_end)
                                        elif itm.date_start == date["date_start"] and itm.date_end > date["date_end"] and itm.value != bandClose:
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])
                                            restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                            id_rateplan, id_room, itm.value, date_end_after, itm.date_end)
                                        elif itm.date_start < date["date_start"] and itm.date_end == date["date_end"] and itm.value != bandClose:
                                            restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                            id_rateplan, id_room, itm.value, itm.date_start, date_start_before)
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])
                                        elif itm.date_end < date["date_end"] and itm.date_start < date["date_start"] and itm.value != bandClose:
                                            restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                            id_rateplan, id_room, itm.value, itm.date_start, date_start_before)
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])
                                        elif itm.date_end < date["date_end"] and itm.date_start < date["date_start"] and itm.value == bandClose:
                                            if restrictionOpera == None:
                                                restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                                id_rateplan, id_room, bandClose, itm.date_start, date["date_end"])
                                        else:
                                            if restrictionOpera == None:
                                                restrictionOperaActive = resFuntions.updateOPeraRestrictionsbyRoom(model=data_filter_dates[indx])
                                else:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(1,id_property,\
                                    id_rateplan, id_room, bandClose, date["date_start"], date["date_end"])

                                if restrictionOpera != None:
                                    response = {
                                            "idop_opera_restrictions": restrictionOpera["idop_opera_restrictions"],
                                            "id_restriction_by": restrictionOpera["id_restriction_by"],
                                            "id_restriction_type": restrictionOpera["id_restriction_type"],
                                            "value": restrictionOpera["value"],
                                            "is_override": restrictionOpera["is_override"],
                                            "date_start": restrictionOpera["date_start"],
                                            "date_end": restrictionOpera["date_end"],
                                            "estado": restrictionOpera["estado"]
                                        }    
                                    resultClose.append(response)
                            
                        dataRatePlans = {
                            "rateplan_id": id_rateplan,
                            "dates": resultClose
                        }
                        rateplans.append(dataRatePlans)

                dataClose = {
                    "id_property": id_property,
                    "id_room_type": id_room,
                    "rateplans": rateplans,
                }
                result.append(dataClose)

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
        except Exception as ex:
            db.session.rollback()
            response = {
                "Code":500,
                "Msg":str(ex),
                "Error":True,
                "data":{}
            }

        return response

class CalendarMinLosMaxLos(Resource):
    #api-calendar-min-max
    # @base.access_middleware
    def post(self):

        response = {}

        try:

            requestData = request.get_json(force=True)
            schema = MinMaxSchema()
            data = schema.load(requestData)
            dataResponseMinLos = []
            dataResponseMaxLos = []
            dataResponse = []

            data_minlos = resFuntions.getMinLosOperaRestriction(\
            data["date_start"],data["date_end"],data["id_property"],\
            data["id_room"],[data["id_rate_plan"]])
            if len(data_minlos) > 0:
                dataResponseMinLos = data_minlos[0]["dates"]
            dates_min_los = {
                "id_restriction_type":2,
                "name":"Min_Los",
                "dates": dataResponseMinLos
            }
            dataResponse.append(dates_min_los)

            data_maxlos = resFuntions.getMaxLosOperaRestriction(\
            data["date_start"],data["date_end"],data["id_property"],\
            data["id_room"],[data["id_rate_plan"]])
            if len(data_maxlos) > 0:
                dataResponseMaxLos = data_maxlos[0]["dates"]
            dates_max_los = {
                "id_restriction_type":3,
                "name":"Max_Los",
                "dates": dataResponseMaxLos
            }
            dataResponse.append(dates_max_los)

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

class CalendarUpdateMinMax(Resource):
    #api-calendar-min-max
    # @base.access_middleware
    def post(self):

        response = {}

        try:

            requestData = request.get_json(force=True)
            schema = MinMaxSaveSchema()
            data = schema.load(requestData)
            dataResponse = []
            dataResponseMinLos = []
            dataResponseMaxLos = []
            id_property = data["id_property"]
            id_room = data["id_room"]
            id_rateplan = data["id_rate_plan"]

            for item in data["data"]:
                id_restriction_type = item["id_restriction_type"]
                for date in item["dates"]:
                    data_filter_dates = resFuntions.getOperaRestrictions(id_restriction_by=4,\
                    id_restriction_type=[id_restriction_type], id_room_type=id_room, id_property=id_property,\
                    id_rateplan = id_rateplan, is_override=1, date_start=date["date_start"], date_end=date["date_end"])
                    if len(data_filter_dates) > 0:
                        cont = 0
                        while cont < len(data_filter_dates):
                            restrictionOperaDelete = resFuntions.updateOPeraRestrictionsbyRoom(model=data_filter_dates[cont], estado=0, id_restriction_type=id_restriction_type)
                            cont += 1
                        date_start_before = date["date_start"] - datetime.timedelta(days=1)
                        date_start_after = date["date_start"] + datetime.timedelta(days=1)
                        date_end_before = date["date_end"] - datetime.timedelta(days=1)
                        date_end_after = date["date_end"] + datetime.timedelta(days=1)
                        restrictionOpera = None
                        for indx, itm in enumerate(data_filter_dates):
                            if itm.date_start == date["date_start"] and itm.date_end == date["date_end"]:
                                #2020-08-10 - 2020-08-12
                                #2020-08-10 = 2020-08-10 and 2020-08-12 = 2020-08-12
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.updateOPeraRestrictionsbyRoom(model=data_filter_dates[indx], value=date["value"], id_restriction_type=id_restriction_type)
                            elif itm.date_start < date["date_start"] and itm.date_end > date["date_end"]: 
                                #2020-08-11 - 2020-08-11
                                #2020-08-10 < 2020-08-11 and 2020-08-12 > 2020-08-11
                                restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                id_rateplan, id_room, itm.value, itm.date_start, date_start_before)
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                    id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                                restrictionOpera2 = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                id_rateplan, id_room, itm.value, date_end_after, itm.date_end)
                            elif itm.date_end > date["date_end"] and itm.date_start > date["date_start"]:
                                #2020-08-09 - 2020-08-11
                                #2020-08-12 < 2020-08-11 and 2020-08-10 > 2020-08-09
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                    id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                                restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                id_rateplan, id_room, itm.value, date_end_after, itm.date_end)
                            elif itm.date_start == date["date_start"] and itm.date_end > date["date_end"]:
                                #2020-08-10 - 2020-08-11
                                #2020-08-10 < 2020-08-10 and 2020-08-12 > 2020-08-11
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                    id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                                restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                id_rateplan, id_room, itm.value, date_end_after, itm.date_end)
                            elif itm.date_start < date["date_start"] and itm.date_end == date["date_end"]:
                                #2020-08-11 - 2020-08-12
                                #2020-08-10 < 2020-08-11 and 2020-08-12 > 2020-08-12
                                restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                id_rateplan, id_room, itm.value, itm.date_start, date_start_before)
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                    id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                            elif itm.date_end < date["date_end"] and itm.date_start == date["date_start"]:
                                #2020-08-10 - 2020-08-13
                                #2020-08-12 < 2020-08-13 and 2020-08-10 > 2020-08-10
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                    id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                            elif itm.date_end < date["date_end"] and itm.date_start < date["date_start"]:
                                #2020-08-11 - 2020-08-13
                                #2020-08-12 < 2020-08-13 and 2020-08-10 > 2020-08-11
                                restrictionOpera1 = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                id_rateplan, id_room, itm.value, itm.date_start, date_start_before)
                                if restrictionOpera == None:
                                    restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                                    id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                    else:
                        restrictionOpera = resFuntions.createOPeraRestrictionsbyRoom(id_restriction_type,id_property,\
                        id_rateplan, id_room, date["value"], date["date_start"], date["date_end"])
                    if restrictionOpera["id_restriction_type"] == 2:
                        responseMinLos = {
                            "idop_opera_restrictions": restrictionOpera["idop_opera_restrictions"],
                            "value": restrictionOpera["value"],
                            "is_override": restrictionOpera["is_override"],
                            "date_start": restrictionOpera["date_start"],
                            "date_end": restrictionOpera["date_end"],
                            "estado": restrictionOpera["estado"]
                        }
                        dataResponseMinLos.append(responseMinLos)
                    else:
                        responseMaxLos = {
                            "idop_opera_restrictions": restrictionOpera["idop_opera_restrictions"],
                            "value": restrictionOpera["value"],
                            "is_override": restrictionOpera["is_override"],
                            "date_start": restrictionOpera["date_start"],
                            "date_end": restrictionOpera["date_end"],
                            "estado": restrictionOpera["estado"]
                        }
                        dataResponseMaxLos.append(responseMaxLos)
                if id_restriction_type == 2:
                    dataMinLos = {
                        "id_restriction_type": id_restriction_type,
                        "dates": dataResponseMinLos
                    }
                    dataResponse.append(dataMinLos)
                else:
                    dataMaxLos = {
                        "id_restriction_type": id_restriction_type,
                        "dates": dataResponseMaxLos
                    }
                    dataResponse.append(dataMaxLos)

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