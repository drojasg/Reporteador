from flask import Flask, request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from functools import reduce
from config import db, base
from common.util import Util
from models.book_hotel import BookHotel as Model, BookHotelSchema as bookschema, BookHotelReservationSchema as resschema
from models.prueba import PruebaBookingSchema as bookschema1
import json

class create_dict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value
class PruebaSearch(Resource):
    def get(self):
        try:
            # book_hotel = Model.query.\
            #     filter(Model.estado == 1).first()
            # mydict = create_dict()
            query = """ select 
                        book_hotel.idbook_hotel,\
                        book_hotel.code_reservation,\
                        book_hotel.iddef_property,\
                        pr.trade_name as tr_name,\
                        pr.property_code as pr_code,\
                        book_hotel.from_date,\
                        book_hotel.to_date,\
                        book_hotel.nights,\
                        book_hotel.adults,\
                        book_hotel.child,\
                        book_hotel.total_rooms,\
                        ms.currency_code as ms_code,\
                        ms.description as ms_description,\
                        co.name as co_name,\
                        co.country_code as co_code,\
                        ch.iddef_channel as ch_id,\
                        ch.name as ch_name,\
                        cu.iddef_currency as cu_idcurrency,\
                        cu.currency_code as cu_code,\
                        cu.description as currency_description,\
                        lan.iddef_language as lan_id,\
                        lan.lang_code as lan_code,\
                        lan.description as language_description,\
                        book_hotel.exchange_rate,\
                        book_hotel.promo_amount,\
                        book_hotel.discount_percent,\
                        book_hotel.discount_amount,\
                        book_hotel.total_gross,\
                        book_hotel.fee_amount,\
                        book_hotel.country_fee,\
                        book_hotel.amount_pending_payment,\
                        book_hotel.amount_paid,\
                        book_hotel.total,\
                        book_hotel.promotion_amount,\
                        book_hotel.last_refund_amount,\
                        bs.idbook_status,\
                        bs.name as bs_name,\
                        bs.code as bs_code,\
                        bs.description as bs_description,\
                        book_hotel.expiry_date,\
                        book_hotel.cancelation_date,\
                        book_hotel.modification_date_booking,\
                        book_hotel.estado,\
                        book_hotel.usuario_creacion,\
                        book_hotel.fecha_creacion,\
                        book_hotel.usuario_ultima_modificacion,\
                        book_hotel.fecha_ultima_modificacion\

                        from book_hotel 

                        inner join def_property pr on book_hotel.iddef_property = pr.iddef_property
                        inner join def_market_segment ms on book_hotel.iddef_market_segment = ms.iddef_market_segment
                        inner join def_country co on book_hotel.iddef_country = co.iddef_country
                        inner join def_channel ch on book_hotel.iddef_channel = ch.iddef_channel
                        inner join def_currency cu on book_hotel.iddef_currency  = cu.iddef_currency
                        inner join def_language lan on book_hotel.iddef_language = lan.iddef_language
                        inner join book_status bs on book_hotel.idbook_status = bs.idbook_status

                        where book_hotel.estado=1; 
                    """
            book_hotel = db.session.execute(query).fetchall()
            for row in book_hotel:
                print(row)
                schema = bookschema1(many = True)
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(book_hotel)
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data":{}
            }
        return response