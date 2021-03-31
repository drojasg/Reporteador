from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from functools import reduce
from config import db, base
from common.util import Util
from models.book_hotel import BookHotel as Model, BookHotelSchema as bookschema, BookHotelReservationSchema as resschema
from models.prueba import PruebaBookingSchema
import json

class create_dict(dict):
    def __init__(self):
        self = dict()

    def add(self, key, value):
        self[key] = value
class PruebaSearch(Resource):
    def get(self):
        try:
            book_hotel = Model.query.\
                filter(Model.estado == 1).first()
            # mydict = create_dict()
            # query = """ select 
            #             book_hotel.idbook_hotel, 
            #             book_hotel.code_reservation as "Codigo_reservacion",
            #             book_hotel.iddef_property,
            #             def_property.short_name as "Hotel Name",
            #             def_property.trade_name,
            #             def_property.property_code as "Hotel Code",  
            #             book_hotel.from_date,
            #             book_hotel.to_date,
            #             book_hotel.nights,
            #             book_hotel.adults,
            #             book_hotel.child,
            #             book_hotel.total_rooms,
            #             book_hotel.iddef_market_segment,
            #             def_market_segment.currency_code,
            #             def_market_segment.description as "Market Description",
            #             book_hotel.iddef_country,
            #             def_country.name as "Country Name",
            #             def_country.country_code,
            #             def_channel.iddef_channel,
            #             def_channel.name as "Channel Name",
            #             def_currency.iddef_currency,
            #             def_currency.currency_code,
            #             def_currency.description as "Currency description",
            #             def_language.iddef_language,
            #             def_language.lang_code,
            #             def_language.description as "Language description",
            #             book_hotel.exchange_rate,
            #             book_hotel.promo_amount,
            #             book_hotel.discount_percent,
            #             book_hotel.discount_amount,
            #             book_hotel.total_gross,
            #             book_hotel.fee_amount,
            #             book_hotel.country_fee,
            #             book_hotel.amount_pending_payment,
            #             book_hotel.amount_paid,
            #             book_hotel.total,
            #             book_hotel.promotion_amount,
            #             book_hotel.last_refund_amount,
            #             book_hotel.idbook_status,
            #             book_status.name as "Status name",
            #             book_status.code as "Status code",
            #             book_status.description as "Status code",
            #             book_hotel.device_request,
            #             book_hotel.expiry_date,
            #             book_hotel.cancelation_date,
            #             book_hotel.modification_date_booking,
            #             book_hotel.estado,
            #             book_hotel.usuario_creacion,
            #             book_hotel.fecha_creacion,
            #             book_hotel.usuario_ultima_modificacion,
            #             book_hotel.fecha_ultima_modificacion

            #             from book_hotel 

            #             inner join def_property on book_hotel.iddef_property = def_property.iddef_property 
            #             inner join def_market_segment on book_hotel.iddef_market_segment = def_market_segment.iddef_market_segment
            #             inner join def_country on book_hotel.iddef_country = def_country.iddef_country
            #             inner join def_channel on book_hotel.iddef_channel = def_channel.iddef_channel
            #             inner join def_currency on book_hotel.iddef_currency  = def_currency.iddef_currency
            #             inner join def_language on book_hotel.iddef_language = def_language.iddef_language
            #             inner join book_status on book_hotel.idbook_status = book_status.idbook_status

            #             where book_hotel.estado=1; 
            #         """
            # book_hotel = db.session.execute(query)
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
            # schema = bookschema()
            # data = schema.dump(book_hotel)
            # for row in book_hotel: 
            #     mydict.add(row[0],({
            #                "idbook_hotel":row[0],
            #                 "Codigo reservacion":row[1],
            #                 "iddef_property":row[2],
            #                 "short_name":row[3],
            #                 "trade_name":row[4],
            #                 "property_code":row[5],
            #                 "from_date":row[6],
            #                 "to_date":row[7],
            #                 "nights":row[8],
            #                 "adults":row[9],
            #                 "child":row[10],
            #                 "total_rooms":row[11],
            #                 "iddef_market_segment":row[12],
            #                 "code":row[13],
            #                 "currency_code":row[14],
            #                 "description":row[15],
            #                 "iddef_country":row[16],
            #                 "name":row[17],
            #                 "country_code":row[18],
            #                 "iddef_channel":row[19],
            #                 "name":row[20],
            #                 "iddef_currency":row[21],
            #                 "currency_code":row[22],
            #                 "description":row[23],
            #                 "iddef_language":row[24],
            #                 "lang_code":row[25],
            #                 "description":row[26],
            #                 "exchange_rate":row[27],
            #                 "promo_amount":row[28],
            #                 "discount_percent":row[29],
            #                 "discount_amount":row[30],
            #                 "total_gross":row[31],
            #                 "fee_amount":row[32],
            #                 "country_fee":row[33],
            #                 "amount_pending_payment":row[34],
            #                 "amount_paid":row[35],
            #                 "total":row[36],
            #                 "promotion_amount":row[37],
            #                 "last_refund_amount":row[38],
            #                 "idbook_status":row[39],
            #                 "Status name":row[40],
            #                 "Status code":row[41],
            #                 "device_request":row[42],
            #                 "fecha expiracion":row[43],
            #                 "cancelation_date":row[44],
            #                 "modification_date_booking":row[45],
            #                 "estado":row[46],
            #                 "usuario_creacion":row[47],
            #                 "fecha_creacion":row[48],
            #                 "usuario_ultima_modificacion":row[49],
            #                 "fecha_ultima_modificacion":row[50]}))  
            # stud_json = json.dumps(mydict, indent = 2, default = str)
            print(data)
            schema = resschema()
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dumps(book_hotel)
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data":{}
            }
        return response