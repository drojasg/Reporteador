#**********************
import pandas as pd
import xlwt
import os
#************************
from flask import Flask, request
from flask_restful import Resource
from pandas import ExcelWriter
from common.util import Util
from config import base, app, api
from flask import send_file
from sqlalchemy import text
import random
import string
import json
from datetime import datetime
import xlsxwriter
from config import db

MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

#Generamos un alfanúmerico Random

def get_bulk(charsize=12):
    """ Generate a Random hash """
    hash_list = string.ascii_uppercase + string.ascii_lowercase
    code = "".join(
        random.SystemRandom().choice(hash_list) for _ in range(charsize)
    ) + str(datetime.now().strftime("%y%m%d%H%M%S"))
    return code

class reportBookings(Resource):
    @api.representation(MIME)
    def post(self):
        #agregamos validaciones de parametros
        params = request.get_json(force=True)
        conditionals = []
        conditionals2 = []
        conditionals3 = []
        conditionals.append("bh.estado = 1")
        conditionals.append("bes.estado = 1")
        conditionals2.append("bhr.estado =1")
        conditionals3.append("bh.estado = 1")
        conditionals3.append("bp.estado = 1")
        iddef_property, idbook_status, from_date_travel, to_date_travel, from_date_booking, to_date_booking, code_book_hotel = 0, 0, 0, 0, 0, 0,0
        if isinstance(params['code_book_hotel'],str):
            #return params['code_book_hotel']
            if params['code_book_hotel'] != "None":
                code_book_hotel = params['code_book_hotel']
                conditionals.append("code_reservation = '{code_book_hotel}'".format(code_book_hotel = code_book_hotel))
            else:
                code_book_hotel = 0
                #conditionals.append(code_book_hotel)
                if isinstance(params['from_date_travel'],str):
                    if params['from_date_travel'] == "1900-01-01":
                        from_date_travel = 0
                        #conditionals.append(from_date_travel)
                    else:
                        from_date_travel = datetime.strptime(params['from_date_travel'],'%Y-%m-%d')

                        from_date_travel = from_date_travel.replace(hour=00, minute=00, second=00)

                        conditionals.append("bh.from_date between '{from_date_travel}'".format(from_date_travel = from_date_travel))
                if isinstance(params['to_date_travel'],str):
                    if params['to_date_travel'] == "1900-01-01":
                        to_date_travel = 0
                        #conditionals.append(to_date_travel)
                    else:
                        to_date_travel = datetime.strptime(params['to_date_travel'],'%Y-%m-%d')

                        to_date_travel = to_date_travel.replace(hour=23, minute=59, second=59)

                        conditionals.append("'{to_date_travel}'".format(to_date_travel = to_date_travel))
                        #conditionals2.append
                if isinstance(params['from_date_booking'],str):
                    if params['from_date_booking'] == "1900-01-01":
                        from_date_booking = 0
                        #conditionals.append(['from_date_booking'])
                    else:                       
                        from_date_booking = datetime.strptime(params['from_date_booking'],'%Y-%m-%d')
                        
                        from_date_booking = from_date_booking.replace(hour=00, minute=00, second=00)
                        
                        conditionals.append("CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') between '{from_date_booking}'".format(from_date_booking = from_date_booking))
                        conditionals2.append("CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') between '{from_date_booking}'".format(from_date_booking = from_date_booking))
                        conditionals3.append("CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') between '{from_date_booking}'".format(from_date_booking = from_date_booking))
                if isinstance(params['to_date_booking'],str):
                    if params['to_date_booking'] == "1900-01-01":
                        to_date_booking = 0
                        #conditionals.append(['to_date_booking'])
                    else:
                        to_date_booking = datetime.strptime(params['to_date_booking'],'%Y-%m-%d')
                        to_date_booking = to_date_booking.replace(hour=23, minute=59, second=59)
                        conditionals.append("'{to_date_booking}'".format(to_date_booking = to_date_booking))
                        conditionals2.append("'{to_date_booking}'".format(to_date_booking = to_date_booking))
                        conditionals3.append("'{to_date_booking}'".format(to_date_booking = to_date_booking))
                if isinstance(params['iddef_property'],str):
                    if params['iddef_property'] != "None":
                        iddef_property = params['iddef_property']
                        conditionals.append('bh.iddef_property = ' + iddef_property)
                        conditionals2.append('bh.iddef_property = ' + iddef_property)
                        conditionals3.append('bh.iddef_property = ' + iddef_property)
                    else:
                        pass
                if isinstance(params['idbook_status'], str):
                    if params['idbook_status'] != 'None':
                        idbook_status = params['idbook_status']
                        conditionals.append('bh.idbook_status =' + idbook_status)
                    else:
                        pass
                        

            
        #: Tu archivo xlsx
        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}_{}.xlsx".format("bookings_report", get_bulk(charsize=7)),
        )

        #: Antes de tu logica
        #: Se ejecuta despues de cada request
        @app.after_request
        def after_request(response):
            try:
                #: Borrar el archivo
                if os.path.isfile(xlsx_report):
                    os.remove(xlsx_report)
            except Exception:
                pass
            return response

        #: Contruyes el excel
        df = pd.DataFrame()

        query = """select p.property_code, bh.code_reservation, bhr.pms_confirm_number as opera_folio, bs.name as status,\r
        concat_ws(' ', bc.first_name, bc.last_name) as guest_name, CONVERT_TZ(bh.fecha_creacion, '+00:00', '-05:00') as booking_date,\r
        bh.from_date as arrival_date, bh.to_date as departure_date, bhr.adults as adults, bhr.child as children,\r
        bhr.rate_amount as room_stay_amount, bhr.country_fee as tax_fee, bhr.total as total_amount, cu.currency_code,\r
        rtc.room_code, aux_services.services as services, ch.name as channel, bc.email as guest_email, bc.phone_number as guest_phone, customer_country.country_code as guest_country,\r
        bh.device_request as user_device, if(bh.expiry_date != '1900-01-01 00:00:00', pg.hold_duration*24,0) as on_hold_duration,\r
        aux_promotions.promotions_code as booked_promotions, bhr.promotion_amount as discount_amount, c.country_code as user_country,\r
        m.code as user_market, rtc.room_description as room_name, rp.code as rate_plan_name,\r
        '' as services_names, voucher.promo_code as voucher_code from book_hotel_room bhr\r
        inner join book_hotel bh on bhr.idbook_hotel = bh.idbook_hotel and bh.estado = 1\r
        inner join book_customer_hotel bch on bch.idbook_hotel = bh.idbook_hotel\r
        and bch.estado = 1\r
        inner join book_customer bc on bc.idbook_customer = bch.idbook_customer\r
        inner join book_address ba on ba.idbook_customer = bc.idbook_customer\r
        and ba.estado = 1\r
        inner join def_country customer_country on ba.iddef_country = customer_country.iddef_country\r
        inner join def_property p on p.iddef_property = bh.iddef_property\r
        inner join def_market_segment m on m.iddef_market_segment = bh.iddef_market_segment\r
        inner join def_country c on c.iddef_country = bh.iddef_country\r
        inner join def_channel ch on ch.iddef_channel = bh.iddef_channel\r
        inner join def_currency cu on cu.iddef_currency = bh.iddef_currency\r
        inner join def_room_type_category rtc on rtc.iddef_room_type_category = bhr.iddef_room_type\r
        inner join op_rateplan rp on rp.idop_rateplan = bhr.idop_rate_plan\r
        inner join book_status bs on bs.idbook_status = bh.idbook_status\r
        inner join def_policy policy on policy.iddef_policy = bhr.iddef_police_guarantee\r
        inner join def_policy_guarantee pg on pg.iddef_policy = policy.iddef_policy\r
        left join book_promo_code voucher on voucher.idbook_hotel = bh.idbook_hotel\r
        and voucher.estado = 1\r
        left join (\r
        select bh.idbook_hotel, \r
        group_concat(distinct bes.description separator ', ') as services\r
        from book_extra_service bes\r
        inner join book_hotel bh on bh.idbook_hotel = bes.idbook_hotel\r
        where {conditionals}  group by bh.idbook_hotel\r
        ) aux_services on aux_services.idbook_hotel = bh.idbook_hotel\r
        left join( \r
        select bh.idbook_hotel, \r
        group_concat(distinct p.code separator ", ") as promotions_code\r
        from book_promotion bp\r
        inner join book_hotel bh on bh.idbook_hotel = bp.idbook_hotel\r
        inner join op_promotions p on p.idop_promotions = bp.idop_promotions\r
        where {conditionals3})\r
        aux_promotions on aux_promotions.idbook_hotel = bh.idbook_hotel\r
        where {conditionals2};""".format(conditionals = " AND ".join(conditionals), conditionals2 = " AND ".join(conditionals2), conditionals3 = " AND ".join(conditionals3))

        df = pd.read_sql_query(text(query), db.engine)

        #: Logica para llenar el dataframe
        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns=
            {
                'property_code': 'Property Code',
                'code_reservation':'Code Reservation',
                'opera_folio': 'Opera Folio',
                'guest_name': 'Guest Name',
                'booking_date': 'Booking Date',
                'arrival_date':'Arival Date',
                'departure_date': 'Departure Date',
                'adults': 'Adults',
                'children':'Children',
                'room_stay_amount': 'Room Stay Amount',
                'tax_fee': 'Tax Fee',
                'total_amount': 'Total Amount',
                'services': 'Services',
                'guest_email': 'Guest Email',
                'guest_phone': 'Guest Phone',
                'guest_country':'Guest Country',
                'user_device': 'User Device',
                'on_hold_duration': 'On Hold Duration',
                'booked_promotions': 'Booked Promotions',
                'user_country': 'User Country',
                'user_market': 'User Market',
                'room_name': 'Room Name',
                'rate_plan_name':'Rate Plan Name',
                'services_names': 'Services Names',
                'voucher_code': 'Voucher Code',
                'from_date': 'From Date',
                'to_date':'To Date',
                'nights':'Nights',
                'child' : 'Child',
                'total_rooms': 'Total Rooms',
                'market':'Market',
                'country':'Country',
                'lang_code':'Language',
                'channel':'Channel',
                'currency_code':'Currency Code',
                'exchange_rate':'Exchange Rate',
                'room_code':'Room Code',
                'room_code_opera':'Room Code Opera',
                'code':'Code',
                'refundable': 'Refundable',
                'pms_confirm_number':'PMS Confirm Number',
                'rate_amount':'Rate Amount',
                'country_fee':'Country Fee',
                'discount_amount':'Discount Amount',
                'voucher_amount':'Voucher Amount',
                'promotion_amount':'Promotion Amount',
                'total':'Total',
                'expiry_date':'Expiry Date',
                'status':'Status'            
            }, inplace=True)

            #df.write_string(0,0, 'Hola')
            df.to_excel(writer, startrow=1, sheet_name="Bookings", index=False, header = True)
            
            workbook  = writer.book
            worksheet = writer.sheets['Bookings']
        
            title = 'Report Bookings'
            worksheet.set_column('A:G', 12)
            worksheet.set_row(1, 30)
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            worksheet.merge_range('A1:Z1', title, merge_format)
            workbook.close()

        return send_file(xlsx_report, mimetype=MIME)


