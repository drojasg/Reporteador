from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from functools import reduce
from config import db, base
from common.util import Util
from models.prueba import BookHotel as Model, PruebaBookingSchema
import json

class PruebaSearch(Resource):
    def get(self):
        try:
            book_hotel = Model.query.\
                filter(Model.estado == 1).first()
            print(book_hotel)
            data = {
                "idbook_hotel": book_hotel.idbook_hotel,
                "code_reservation":book_hotel.code_reservation,
                "iddef_property": book_hotel.iddef_property,
                "from_date": book_hotel.from_date,
                "to_date": book_hotel.to_date,
                "adults": book_hotel.adults,
                "child": book_hotel.child,
                "nights": book_hotel.nights,
                "iddef_market_segment":book_hotel.iddef_market_segment,
                "market_code": book_hotel.market_segment.code,
                "iddef_channel": book_hotel.iddef_channel,
                "iddef_country": book_hotel.iddef_country,
                "lang_code": book_hotel.language.lang_code,
                "currency_code": book_hotel.currency.currency_code,
                "status": book_hotel.status_item.name,
                "idbook_status": book_hotel.idbook_status,
                "discount_percent": book_hotel.discount_percent,
                "discount_amount": book_hotel.discount_amount, 
                "total_gross": book_hotel.total_gross,
                "total": book_hotel.total,
                "expiry_date": book_hotel.expiry_date,
                "fecha_creacion": book_hotel.fecha_creacion
            }
            print(data)
            schema = PruebaBookingSchema
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dumps(data, indent = 4, sort_keys = True)
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data":{}
            }
        return response