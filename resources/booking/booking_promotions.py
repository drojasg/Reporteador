from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_

from config import db, base
from common.util import Util
from models.book_hotel import BookHotelReservationSchema as ModelSchema, BookHotel, BookHotelAdminSchema, EmailReservationSchema, CancelReservationSchema
from models.promotions import Promotions as pModel
from models.promotion_restriction import PromotionRestriction as prModel
from models.restriction import Restriction as rModel
from models.restriction_detail import RestrictionDetail as rdModel
from models.room_type_category import RoomTypeCategory as rtcModel
from resources.rates.RatesHelper import RatesFunctions
from resources.promo_code.promocodeHelper import PromoCodeFunctions as vauchersFunctions

class BookingPromo():
    @staticmethod
    def booking_create_promocode(book_hotel, promotion, room_selected):
        try:

            info_vaucher = {
                "iddef_promo_code": 0,
                "estado": 1,
            }

            obj_stay = {}
            obj_booking = {}
            max_amount = room_selected["total"]

            rooms_rateplan = promotion[0]["rates_rooms_avail"][0]["rooms"]
            new_rooms_rateplan = []
            for room in rooms_rateplan:
                data_room = rtcModel.query.get(room)
                new_rooms_rateplan.append(data_room.room_code)

            obj_rates = {
                "iddef_property":book_hotel.iddef_property,
                "promo_code_rateplans": [
                    {
                        "idop_rateplan":promotion[0]["rates_rooms_avail"][0]["rateplan"],
                        "rooms_rateplan":new_rooms_rateplan
                    }
                ]
            }
            
            obj_stay["start_date"] = book_hotel.from_date.strftime("%Y-%m-%d")
            for itm_date in promotion[0]["travel_window"]:
                if book_hotel.to_date.strftime("%Y-%m-%d") <= itm_date["end_date"]:
                    obj_stay["end_date"] = itm_date["end_date"]
            obj_booking["start_date"] = book_hotel.fecha_creacion.strftime("%Y-%m-%d")
            obj_booking["end_date"] = promotion[0]["apply_dates"]["dates_booking"]

            min_LOS_option = 1
            if promotion[0]["length_of_stay"]["minLOS"]["inherit"]==1:
                min_LOS_option = 2

            info_vaucher["name"] =  str(book_hotel.code_reservation) + "_2X1"
            info_vaucher["code"] =  str(book_hotel.code_reservation) + "_2X1"
            info_vaucher["iddef_promo_code_discount_type"] = 1
            info_vaucher["value_discount"] = 100
            info_vaucher["iddef_promo_code_type_amount"] = 4
            info_vaucher["currency_code"] = ""
            info_vaucher["maximum_nights_option"] = 0
            info_vaucher["maximum_nights_value"] = 0
            info_vaucher["description"] = []
            info_vaucher["room_types_option"] = 2
            info_vaucher["promo_code_rateplans"] = [obj_rates]
            info_vaucher["min_LOS_option"] = min_LOS_option
            info_vaucher["min_LOS_value"] = promotion[0]["length_of_stay"]["minLOS"]["value"]
            info_vaucher["min_booking_amount_option"] = 1
            info_vaucher["min_booking_value"] = 0
            info_vaucher["max_booking_amount_option"] = 2
            info_vaucher["max_booking_value"] = max_amount
            info_vaucher["global_sales_limit_option"] = 2
            info_vaucher["global_sales_limit_value"] = 1
            info_vaucher["cancel_policy_id"] = 0
            info_vaucher["market_option"] = 0
            info_vaucher["market_targeting"] = []
            info_vaucher["country_option"] = 0
            info_vaucher["country_targeting"] = []
            info_vaucher["channel_option"] = 0
            info_vaucher["channel_list"] = []
            info_vaucher["stay_dates_option"] = 2
            info_vaucher["stay_dates_value"] = [obj_stay]
            info_vaucher["booking_dates_option"] = 2
            info_vaucher["booking_dates_value"] = [obj_booking]
            info_vaucher["booking_times_value"] = []


        except Exception as error:
            raise error
        
        return info_vaucher