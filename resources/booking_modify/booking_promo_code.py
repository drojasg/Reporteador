from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_

from config import db, base
from models.book_hotel import BookHotelBaseSchema as ModelBaseSchema, BookHotel
from models.promo_code import GetInternalPromoCodeSchema as ModelPromoCodeSchema, PromoCode
from models.promo_code_type_amount import PromoCodeTypeAmount
from models.text_lang import TextLang
from common.util import Util

from resources.rates.RatesHelper import RatesFunctions as funtions
   
class BookingPromoCodeModify(Resource):
    #api-internal-booking-promocode-get
    # @base.access_middleware
    def get(self, idbooking):
        response = {}
        try:
            
            schema = ModelBaseSchema()

            data = {}

            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbooking, BookHotel.estado == 1).first()
            
            if book_hotel is not None:

                lang_code = book_hotel.language.lang_code
                lang_code = lang_code.upper()

                if len(book_hotel.promo_codes) > 0:
                    for promo_code in book_hotel.promo_codes:
                        if promo_code.estado == 1:

                            in_text, value, discount_type, description = True, 0, "", ""
                            data_promocode = PromoCode.query.filter(PromoCode.estado==1, PromoCode.code==promo_code.promo_code).first()

                            if data_promocode is not None:

                                result_description = TextLang.query\
                                .filter(TextLang.table_name=="def_promo_code", TextLang.attribute=="description", TextLang.lang_code==lang_code,
                                    TextLang.id_relation==data_promocode.iddef_promo_code, TextLang.estado==1).first()
                                if result_description is not None:
                                    description = result_description.text
                                    
                                if data_promocode.iddef_promo_code_type_amount != 0:
                                    in_text = False
                                    value = data_promocode.value_discount
                                    data_amount = PromoCodeTypeAmount.query.get(data_promocode.iddef_promo_code_type_amount)
                                    discount_type = data_amount.name
                                    
                                data = {
                                    "iddef_promo_code": data_promocode.iddef_promo_code,
                                    "promo_code": promo_code.promo_code,
                                    "name": data_promocode.name,
                                    "in_text": in_text,
                                    "value": value,
                                    "voucher_discount_type": discount_type,
                                    "description": description
                                }


            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
    
    #api-internal-booking-promocode-post
    # @base.access_middleware
    def post(self):
        try:
            json_data = request.get_json(force=True)
            load_schema = ModelPromoCodeSchema()
            data = load_schema.load(json_data)
            hotel = data["property_code"]
            date_start = data["date_start"]
            date_end = data["date_end"]
            rateplans = data["rateplans"]
            rooms = data["rooms"]
            market = data["market"]
            if request.json.get("lang_code") != None:
                lang_code = data["lang_code"]
            else:
                lang_code = "EN"
            result = []
            if request.json.get("country") is not None and request.json.get("total_amount") is not None:
                result = funtions.getPromoCode(hotel=hotel,\
                date_start=date_start,date_end=date_end, rateplan=rateplans,\
                room=rooms, market= market, country=data["country"],\
                total_amount=data["booking_amount"], useStay=True, lang_code=lang_code)
            else:
                if request.json.get("country") is not None and  request.json.get("total_amount") is None:
                    result = funtions.getPromoCode(hotel=hotel,\
                    date_start=date_start,date_end=date_end, rateplan=rateplans,\
                    room=rooms, market= market, country=data["country"], useStay=True, lang_code=lang_code)
                elif request.json.get("country") is None and  request.json.get("total_amount") is not None:
                    result = funtions.getPromoCode(hotel=hotel,\
                    date_start=date_start,date_end=date_end, rateplan=rateplans,\
                    room=rooms, market= market, total_amount=data["booking_amount"],\
                    useStay=True, lang_code=lang_code)
                elif request.json.get("country") is None and  request.json.get("total_amount") is None:
                    result = funtions.getPromoCode(hotel=hotel,\
                    date_start=date_start,date_end=date_end, rateplan=rateplans,\
                    room=rooms, market= market, useStay=True, lang_code=lang_code)
            
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