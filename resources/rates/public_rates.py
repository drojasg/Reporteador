from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from config import db, base
from common.util import Util
from common.utilities import Utilities
from sqlalchemy import or_, and_
import datetime
from .rates_helper_v2 import Search, Validates, Quotes, Promotions,\
mkfuntion, agcFuntions, prModel, txtFunctions, pfuntions
from common.public_auth import PublicAuth
import copy
from models.rates import CalendarSchema, PublicRatesSchema, RatesWithPromotions
from models.rates_v2.public_promotion import Promotion_Schema as promotionSchema
from resources.restriction.restricctionHelper import RestricctionFunction as RestFuntions
from resources.promo_code.promocodeHelper import PromoCodeFunctions as vauchersFunctions
from resources.rateplan.rate_plan_helper import Rateplans_Helper as rpfuntions
from resources.property.propertyHelper import FilterProperty as prFunctions
from resources.rates.RatesHelper import RatesFunctions as functions_rates
from resources.room_type_category.room_type_helper import Room_Type_Helper as rtcFunctions, rtcModel
class InternalRates_v2(Resource):
    #api-v2-internal-room-rates
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:
            dataRq = request.get_json(force=True)
            schema = PublicRatesSchema()
            data = schema.load(dataRq)

            #Obtenemos la informacion del mercado
            market_info = mkfuntion.getMarketInfo(self,data["market"])
            idmarket = market_info.iddef_market_segment

            if request.json.get("lead_time") is None:
                data["lead_time"] = True

            #Obtenemos la informacion de la propiedad
            idroom = 0
            adults_pax = 0
            property_info = prFunctions.getHotelInfo(self,data["property_code"])
            idproperty = property_info.iddef_property
            
            ratePlans = []
            #Obtenemos la informacion de la habitacion
            roomType = rtcModel.query.get(data["room_type"])
            if roomType is None:
                raise Exception("Room not valid")
            else:
                idroom = roomType.iddef_room_type_category
                adults_pax = roomType.standar_ocupancy

            if request.json.get("rate_plan") is None:
                #Obtenemos los rate plans disponibles para esta propiedad
                ratePlans = rpfuntions.get_rateplan_info(self,property_id=idproperty,\
                date_start=data["date_start"],date_end=data["date_end"],bookin_window=True,\
                only_one=False,market_id=idmarket,country=data["market"],\
                validate_lead_time=data["lead_time"],roomid=idroom,language=data["lang_code"])
            elif data["rate_plan"] == 0:
                #Si el rateplan 0 obtenemos todos los rateplans para esta propiedad
                ratePlans = rpfuntions.get_rateplan_info(self,property_id=idproperty,\
                date_start=data["date_start"],date_end=data["date_end"],bookin_window=True,\
                only_one=False,market_id=idmarket,country=data["market"],\
                validate_lead_time=data["lead_time"],roomid=idroom,language=data["lang_code"])
            else:
                #Obtenemos el rateplan espesifico
                rate_plan = rpfuntions.get_rateplan_info(self,rateplanId=data["rate_plan"],\
                property_id=idproperty,date_start=data["date_start"],date_end=data["date_end"],\
                bookin_window=True,market_id=idmarket,country=data["market"],\
                validate_lead_time=data["lead_time"],roomid=idroom,language=data["lang_code"])
                ratePlans.append(rate_plan)
            
            date_end_checkout = data["date_end"] - datetime.timedelta(days=1)

            idrateplans = [x.idop_rateplan for x in ratePlans]
            
            #Obtenemos las restricciones-fechas cerradas
            close_info = RestFuntions.getCloseDatesOperaRestriction(\
            data["date_start"],date_end_checkout,idproperty,\
            idroom,idrateplans)

            #Obtenemos las restricciones min_los
            min_los = RestFuntions.getMinLosOperaRestriction(\
            data["date_start"],data["date_start"],idproperty,\
            idroom,idrateplans)

            #Obtenemos las restricciones max_los
            max_los = RestFuntions.getMaxLosOperaRestriction(\
            data["date_start"],data["date_start"],idproperty,\
            idroom,idrateplans)

            dataDump = []
            for rateplan in ratePlans:
                rates = None
                rateplanId = rateplan.idop_rateplan

                validations = Validates()

                room_apply = validations.validate_room_rates(rateplanId,data["date_start"],\
                data["date_end"],close_info,min_los,max_los)

                total = 0

                if room_apply == True:
                    try:
                        #Obtenemos las tarifas necesarias
                        get_data = Search()
                        rates = get_data.get_price_per_day(idproperty,idroom,rateplanId,\
                        data["date_start"],data["date_end"],currency=data["currency"],\
                        market=data["market"],paxes=data["rooms"])
                    
                        total = rates["total"]
                    except Exception as error:
                        pass

                if total > 0 and rates is not None:

                    rates_discount = Promotions(rates,data["currency"],\
                    data["market"],idmarket,data["lang_code"],data["date_start"],\
                    data["date_end"],allinone=True)
                    rates = rates_discount.apply_promotions()

                    if rates["total"] > 0:
                        #obtenemos el nombre comercial del rateplan
                        txtData = txtFunctions.getTextLangInfo(self,"op_rateplan",\
                        "commercial_name",data["lang_code"],rateplanId)

                        if txtData is not None:
                            rate_plan_name = txtData.text
                        else:
                            rate_plan_name = ""

                        policies = pfuntions.get_policy_by_rateplan(rateplanId,\
                        data["date_start"],lang_code=data["lang_code"],\
                        refundable=not rateplan.refundable)

                        dataDumped = schema.dump(rates)
                        #dataDumped["idop_rate_plan"]=rateplanId
                        dataDumped["rate_plan_name"]=rate_plan_name
                        dataDumped["policies"]=policies
                        dataDumped["promo_free_apply"]=False

                        dataDump.append(dataDumped)

            if len(dataDump) > 0:
                dataDump = Utilities.sort_dict(self,dataDump,"total",asc=False)
                #dataDump = sorted(dataDump, key = lambda i: i['total'])
            
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

class PublicRates_v2(Resource):

    #api-v2-public-property-rates
    @PublicAuth.access_middleware
    def get(self,hotel_code,country,currency):
        response = {
            "Code": 200,
            "Msg": "Success",
            "Error": False,
            "data": []
        }

        try:
            #Asignamos valores por defecto a los request
            currency_code = currency
            market_info = mkfuntion.getMarketInfo(self,country)
            hotel_info = prFunctions.getHotelInfo(self,hotel_code)

            idmarket = market_info.iddef_market_segment
            
            if hotel_info is None:
                raise Exception("Propiedad no encontrada")
            else:
                hotelid = hotel_info.iddef_property

            #Usamos las fechas por defecto, apartir de 15 dias, 4 noches
            today = datetime.datetime.now().date()
            date_start = today + datetime.timedelta(days=15)
            date_end = today + datetime.timedelta(days=20)

            #Obtenemos la primera habitacion ROH de la propiedad
            #room_info = roommFunction.get_room_type(self,idproperty=hotelid)
            room_info = rtcFunctions.get_room_type(self,idproperty=hotelid)
            idroom = room_info.iddef_room_type_category
            standar_pax = room_info.standar_ocupancy

            #Obtenemos los rateplans disponibles para la habitacion seleccionada, propiedad,
            #mercado,pais, fechas de viaje y fecha de booking
            ratePlans = rpfuntions.get_rateplan_info(self,property_id=hotelid,\
            date_start=date_start,date_end=date_end,bookin_window=True,\
            only_one=False,market_id=idmarket,country=country,\
            validate_lead_time=True,roomid=idroom)
            
            data_response = None
            list_response = []
            for rateplan in ratePlans:
                total = 0
                ratePlanid = rateplan.idop_rateplan
                
                get_rates = Search()
                
                rates = get_rates.get_price_per_day(hotelid,idroom,ratePlanid,date_start,\
                date_end,adult=standar_pax,currency=currency_code,market=idmarket,\
                country=country)

                total = rates["total"]
                
                if total > 0:
                    #Aplicamos las promociones
                    try:
                        rates_discount = Promotions(rates,currency_code,\
                        country,idmarket,"EN",date_start,\
                        date_end,allinone=True)
                        rates_aux = rates_discount.apply_promotions()

                        rates = rates_aux
                        
                        total = rates["total"]
                        
                    except Exception as promo_error:
                        pass
                    
                    schema2 = PublicRatesSchema(only=("avg_total","avg_total_discount",\
                    "total_percent_discount","total"))

                    list_response.append(schema2.dump(rates))

                    #break
            if len(list_response) >= 1:
                list_response = Utilities.sort_dict(self,list_response,"total",asc=False)
                data_response = list_response[0]
            
            response["data"] = data_response

        except Exception as error:
            response["Error"] = True
            response["Msg"] = str(error)

        return response
    
    #api-public-rates-post
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:
            dataRq = request.get_json(force=True)
            schema = PublicRatesSchema()
            data = schema.load(dataRq)

            #Obtenemos la informacion del mercado
            market_info = mkfuntion.getMarketInfo(self,data["market"])
            idmarket = market_info.iddef_market_segment

            #Obtenemos la informacion de la propiedad
            idroom = 0
            adults_pax = 0
            property_info = prFunctions.getHotelInfo(self,data["property_code"])
            idproperty = property_info.iddef_property
            
            ratePlans = []
            #Obtenemos la informacion de la habitacion
            roomType = rtcModel.query.get(data["room_type"])
            if roomType is None:
                raise Exception("Room not valid")
            else:
                idroom = roomType.iddef_room_type_category
                adults_pax = roomType.standar_ocupancy

            if request.json.get("rate_plan") is None:
                #Obtenemos los rate plans disponibles para esta propiedad
                ratePlans = rpfuntions.get_rateplan_info(self,property_id=idproperty,\
                date_start=data["date_start"],date_end=data["date_end"],bookin_window=True,\
                only_one=False,market_id=idmarket,country=data["market"],\
                validate_lead_time=True,roomid=idroom,language=data["lang_code"])
            elif data["rate_plan"] == 0:
                #Si el rateplan 0 obtenemos todos los rateplans para esta propiedad
                ratePlans = rpfuntions.get_rateplan_info(self,property_id=idproperty,\
                date_start=data["date_start"],date_end=data["date_end"],bookin_window=True,\
                only_one=False,market_id=idmarket,country=data["market"],\
                validate_lead_time=True,roomid=idroom,language=data["lang_code"])
            else:
                #Obtenemos el rateplan espesifico
                rate_plan = rpfuntions.get_rateplan_info(self,rateplanId=data["rate_plan"],\
                property_id=idproperty,date_start=data["date_start"],date_end=data["date_end"],\
                bookin_window=True,market_id=idmarket,country=data["market"],\
                validate_lead_time=True,roomid=idroom,language=data["lang_code"])
                ratePlans.append(rate_plan)
            
            date_end_checkout = data["date_end"] - datetime.timedelta(days=1)

            idrateplans = [x.idop_rateplan for x in ratePlans]
            
            #Obtenemos las restricciones-fechas cerradas
            close_info = RestFuntions.getCloseDatesOperaRestriction(\
            data["date_start"],date_end_checkout,idproperty,\
            idroom,idrateplans)

            #Obtenemos las restricciones min_los
            min_los = RestFuntions.getMinLosOperaRestriction(\
            data["date_start"],data["date_start"],idproperty,\
            idroom,idrateplans)

            #Obtenemos las restricciones max_los
            max_los = RestFuntions.getMaxLosOperaRestriction(\
            data["date_start"],data["date_start"],idproperty,\
            idroom,idrateplans)

            dataDump = []
            for rateplan in ratePlans:
                rateplanId = rateplan.idop_rateplan

                validations = Validates()

                room_apply = validations.validate_room_rates(rateplanId,data["date_start"],\
                data["date_end"],close_info,min_los,max_los)

                total = 0

                if room_apply == True:
                    try:
                        #Obtenemos las tarifas necesarias
                        get_data = Search()
                        rates = get_data.get_price_per_day(idproperty,idroom,rateplanId,\
                        data["date_start"],data["date_end"],currency=data["currency"],\
                        market=data["market"],paxes=data["rooms"])
                    
                        total = rates["total"]
                    except Exception as error:
                        print(str(error))

                if total > 0:
                    
                    #obtenemos el nombre comercial del rateplan
                    txtData = txtFunctions.getTextLangInfo(self,"op_rateplan","commercial_name",\
                    data["lang_code"],rateplanId)

                    if txtData is not None:
                        rate_plan_name = txtData.text
                    else:
                        rate_plan_name = ""

                    policies = pfuntions.get_policy_by_rateplan(rateplanId,\
                    data["date_start"],lang_code=data["lang_code"],\
                    refundable=not rateplan.refundable)

                    dataDumped = schema.dump(rates)
                    #dataDumped["idop_rate_plan"]=rateplanId
                    dataDumped["rate_plan_name"]=rate_plan_name
                    dataDumped["policies"]=policies
                    dataDumped["promo_free_apply"]=False

                    dataDump.append(dataDumped)

            if len(dataDump) > 0:
                dataDump = Utilities.sort_dict(self,dataDump,"total",asc=False)
                #dataDump = sorted(dataDump, key = lambda i: i['total'])

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

class PublicDiscounts(Resource):
    #api-v2-public-room-quote
    @PublicAuth.access_middleware
    def post(self):
        response = {}

        try:
            dataRq = request.get_json(force=True)
            schema = promotionSchema()
            data_load = schema.load(dataRq)
            
            market_info = mkfuntion.getMarketInfo(self,data_load["market"])
            idmarket = market_info.iddef_market_segment

            hotel_data = prModel.query.get(data_load["rates"][0]["property"])
            hotel_code = hotel_data.property_code

            if request.json.get("promo_applied") is None:
                data_load["promo_applied"] = False
            
            if request.json.get("promocode") is None:
                data_load["promocode"] = ""

            for item_rates in data_load["rates"]:
                count = 0
                item_rates["vaucher_applied"] = False
                item_rates["paxes"] = data_load["paxes"]
                for item in item_rates["price_per_day"]:
                    count += 1
                    item["night"] = count
                    item["promotion_amount"] = 0.0
                    item["country_fee"] = 0.0
                    item["vaucher_discount"]=0.0
                
                Quotes.get_total_one(self,item_rates)
            
            data_response = []
            vaucher_discount = False
            for data in data_load["rates"]:
                total = data["total"]
                
                if total > 0:
                    #Aplicamos las promociones
                    try:
                        rates_discount = Promotions(data,data_load["currency"],\
                        data_load["market"],idmarket,data_load["lang_code"],data_load["date_start"],\
                        data_load["date_end"],allinone=True,valid2x1= not data_load["promo_applied"])
                        rates_aux = rates_discount.apply_promotions()
                        rates_aux = rates_discount.apply_promocode(promocode=data_load["promocode"])

                        data = rates_aux
                        vaucher_discount = rates_discount.promocode_applied
                        
                        total = data["total"]
                        
                    except Exception as promo_error:
                        pass

                if vaucher_discount == False:
                    if total > 0:
                        dumpSchema = PublicRatesSchema()
                        data_response.append(dumpSchema.dump(data))
                else:
                    dumpSchema = PublicRatesSchema()
                    data_response.append(dumpSchema.dump(data))

            if len(data_response)>0:
                data_response = Utilities.sort_dict(self,data_response,"total",asc=False)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data_response
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