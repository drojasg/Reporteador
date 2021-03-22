from flask import Flask, request
from flask_restful import Resource
from config import db, base
from models.prueba import PruebaBooking, PruebaBookingSchema
from common.util import Util
from sqlalchemy import or_, and_
from datetime import datetime as dt
from dateutil.parser import parse
from common.public_auth import PublicAuth

class PruebaSearch(Resource):
     def get(self, estado):
        response = {}
        try:
            book_hotel = BookHotel.query.\
                filter(BookHotel.estado == 1).first()

            if book_hotel is None:
                raise Exception(Util.t("en","Booking_estado_not_found", estado))
            
            data = {
                "idbook_hotel": book_hotel.idbook_hotel,
                "code_reservation": book_hotel.code_reservation,
                "iddef_propperty": book_hotel.iddef_property,
                "short_name": def_property.short_name,
                "trade_name": def_property.trade_name,
                "property_code": def_property.property_code,
                "from_date": book_hotel.from_date,
                "to_date": book_hotel.to_date,
                "nights": book_hotel.nights,
                "adults": book_hotel.adults,
                "currency_code": def_market_segment.currency_code,
                "description": def_market_segment.description,
                "iddef_country": book_hotel.iddef_country,
                "name": def_country.name,
                "country_code": def_country.country_code,
                "iddef_channel": def_channel.iddef_channel,
                "name": def_channel.name,
                "iddef_currency": def_currency.iddef_currency,
                "currency_code": def_currency.currency_code,
                "description": def_currency.description,
                "iddef_language": def_language.iddef_language,
                "lang_code": def_language.lang_code,
                "description": def_language.description,
                "exchange_rate": book_hotel.exchange_rate,
                "promo_amount": book_hotel.promo_amount,
                "discount_percent": book_hotel.discount_percent,
                "discount_amount": book_hotel.discount_amount,
                "total_gross": book_hotel.total_gross,
                "fee_amount": book_hotel.fee_amount,
                "country_fee": book_hotel.country_fee,
                "amount_pending_payment": book_hotel.amount_pending_payment,
                "amount_paid": book_hotel.amount_paid,
                "total": book_hotel.total,
                "promotion_amount": book_hotel.promotion_amount,
                "last_refund_amount": book_hotel.last_refund_amount,
                "idbook_status": book_hotel.idbook_status,
                "name": book_status.name,
                "code": book_status.code,
                "description": book_status.description,
                "device_request": book_hotel.device_request,
                "expiry_date": book_hotel.expiry_date,
                "cancelation_date": book_hotel.cancelation_date,
                "modification_date_booking": book_hotel.modification_date_booking,
                "estado": book_hotel.estado,
                "usuario_creacion": book_hotel.usuario_creacion,
                "fecha_creacion": book_hotel.fecha_creacion,
                "usuario_ultima_modificacion": book_hotel.usuario_ultima_modificacion,
                "fecha_ultima_modificacion": book_hotel.fecha_ultima_modificacion
            }
            schema = PruebaBookingSchema()
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

        return responsec