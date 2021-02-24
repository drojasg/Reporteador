from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_

from config import db, base
from models.book_hotel import BookHotel
from models.service import GetPublicServiceSchema as GetServiceSchema
from models.age_code import AgeCode as agcModel
from models.currency import Currency as currencyModel
from common.util import Util
from resources.service.serviceHelper import Search as FunctionsService
from resources.property.propertyHelper import FilterProperty as FunctionsProperty
from resources.market_segment.marketHelper import Market as FunctionsMark
from resources.media_service import AdminMediaServiceList
from resources.rates.rates_helper_v2 import Search as ratesFuntions
import datetime as dt
   
class BookingServiceModify(Resource):
    #api-internal-booking-service-get
    # @base.access_middleware
    def get(self, idbooking):
        response = {}
        try:
            FunctionService = FunctionsService()
            ratesHelper = ratesFuntions()
            result = []
            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbooking, BookHotel.estado == 1).first()
            id_property = book_hotel.iddef_property
            data_services = [service_elem.iddef_service for service_elem in book_hotel.services]
            lang_code = book_hotel.language.lang_code
            total_rooms = book_hotel.total_rooms
            total_packs = book_hotel.adults + book_hotel.child
            market_code = book_hotel.country.country_code
            currency_code = book_hotel.currency.currency_code

            try:
                if len(data_services) > 0:
                    data_response = FunctionService.get_service_by_additional(data_services,\
                    book_hotel.from_date, book_hotel.to_date, book_hotel.iddef_market_segment,\
                    id_property, total_rooms, total_packs, market_code)
                    elementos = ["Name","Teaser","Description","icon_description"]
                    if len(data_response)>0:
                        for x in data_response:
                            id_service = x['iddef_service']
                            data_traslate = FunctionService.get_service_by_lang_elements(id_service,elementos,lang_code)
                            x.update(data_traslate)
                            result_media=[]
                            DataMedia = AdminMediaServiceList.get(self,id_service,lang_code,id_property,1)
                            result_media = list(filter(lambda elem_selected: elem_selected['selected'] == 1, DataMedia['data']))
                            x['data_media'] = result_media
                            x['quantity'] = 1
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
    
    #api-internal-booking-service-post
    # @base.access_middleware
    def post(self):
        try:
            FunctionService = FunctionsService()
            FunctionProperty = FunctionsProperty()
            FunctionMark = FunctionsMark()
            ratesHelper = ratesFuntions()
            json_data = request.get_json(force=True)
            load_schema = GetServiceSchema()
            data = load_schema.load(json_data)
            date_start = data["date_start"]
            date_end = data["date_end"]
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
            msData = FunctionMark.getMarketInfo(market)
            msId = msData.iddef_market_segment
            hotel = FunctionProperty.getHotelInfo(data["id_hotel"])
            id_property = hotel.iddef_property
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
                data_services_items = FunctionService.get_service_by_additional(services,\
                date_start,date_end,msId,id_property,total_rooms,total_packs,market)
                elementos = ["Name","Teaser","Description","icon_description"]
                if len(data_services_items)>0:
                    for x in data_services_items:
                        id_service = x['iddef_service']
                        data_traslate = FunctionService.get_service_by_lang_elements(id_service,elementos,lang_code)
                        x.update(data_traslate)
                        result_media=[]
                        DataMedia = AdminMediaServiceList.get(self,id_service,lang_code,id_property,1)
                        result_media = list(filter(lambda elem_selected: elem_selected['selected'] == 1, DataMedia['data']))
                        x['data_media'] = result_media
                        x['quantity'] = 1
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