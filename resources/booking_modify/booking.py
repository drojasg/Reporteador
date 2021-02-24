from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_

from config import db, base
from models.book_hotel import BookHotelBaseSchema as ModelBaseSchema, BookHotel
from common.util import Util
   
class BookingModify(Resource):
    #api-internal-booking-get
    #@base.access_middleware
    def get(self, idbooking):
        response = {}
        try:
            
            schema = ModelBaseSchema()

            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbooking, BookHotel.estado == 1).first()

            data = {
                "idbook_hotel": book_hotel.idbook_hotel,
                "code_reservation": book_hotel.code_reservation,
                "iddef_property": book_hotel.iddef_property,
                "property_code": book_hotel.property.property_code,
                "from_date": book_hotel.from_date,
                "to_date": book_hotel.to_date,
                "adults": book_hotel.adults,
                "child": book_hotel.child,
                "nights": book_hotel.nights,
                "total_rooms": book_hotel.total_rooms,
                "iddef_market_segment": book_hotel.iddef_market_segment,
                "market_code": book_hotel.country.country_code,
                "iddef_country": book_hotel.iddef_country,
                "country_code": book_hotel.country.country_code,
                "iddef_language": book_hotel.iddef_language,
                "lang_code": book_hotel.language.lang_code,
                "iddef_channel": book_hotel.iddef_channel,
                "iddef_currency": book_hotel.iddef_currency,
                "currency_code": book_hotel.currency.currency_code,
                "iddef_currency_user": book_hotel.iddef_currency_user,
                "currency_code_user": book_hotel.currency_user.currency_code,
                "discount_percent": book_hotel.discount_percent,
                "discount_amount": book_hotel.discount_amount, 
                "total_gross": book_hotel.total_gross,
                "total": book_hotel.total,
                "idbook_status": book_hotel.idbook_status,
                "status": book_hotel.status_item.name,
                "fecha_creacion": book_hotel.fecha_creacion
            }

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