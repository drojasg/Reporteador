#**********************
import pandas as pd
import xlwt
import os
import requests
import os
#************************
#****BOTO3***************#
import logging
import boto3
from botocore.exceptions import ClientError
#************************#
from flask import Flask, request
from flask_restful import Resource
from pandas import ExcelWriter
from pandas import DataFrame
from common.util import Util
from config import base, app, api
from flask import send_file
from sqlalchemy import text
import random
import string
import json
from datetime import datetime,timedelta
import xlsxwriter
from config import db

MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#hs = '2020-12-07'


#Generamos un alfanúmerico Random

def get_bulk(charsize=12):
    """ Generate a Random hash """
    hash_list = string.ascii_uppercase + string.ascii_lowercase
    code = "".join(
        random.SystemRandom().choice(hash_list) for _ in range(charsize)
    ) + str(datetime.now().strftime("%y%m%d%H%M%S"))
    return code

class reportCancelations(Resource):
    @api.representation(MIME)
    def post(self):
        #agregamos validaciones de parametros
        #params = request.get_json(force=True)
        #conditionals servirá para acumular todos los parametros
        conditionals = []
        now = datetime.now()
        hoy = datetime.utcnow()
        ayer = hoy - timedelta(days=1)
        conditionals.append("CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') between '{now}'".format(now = ayer.replace(hour=00, minute=00, second=00, microsecond=000000)))
        conditionals.append("'{to_creation_data}'".format(to_creation_data = ayer.replace(hour=23, minute=59, second=59, microsecond=000000)))
        
        ayer = ayer.strftime("%Y-%m-%d")
        #Comenzamod a armar el archivo excell
        

        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}_{}.xlsx".format("report_cancelations", get_bulk(charsize=7))
        )

        #hacemos la lógica para borrar el archivo de los temporales
        #se ejecutará despues de cada request
        @app.after_request
        def after_request(response):
            try:
                #procedemos a borrar el archivo
                if os.path.isfile(xlsx_report):
                    os.remove(xlsx_report)
            except Exception:
                pass
            return response
        #construimos el excell (creamos un dataFrame por cada hoja del documento)
        # df = pd.DataFrame()
        
        #ponemos los querys de todas las hojas
        query = text("""SELECT b.idbook_hotel, b.code_reservation, CONVERT_TZ(b.fecha_creacion, '+00:00', '-05:00') AS fecha_creacion,b.from_date, \r
        b.to_date,DATE_FORMAT(b.modification_date_booking,'%Y-%m-%d') AS fecha_ultima_modificacion,b.adults,b.child, \r
        (IF(b.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), b.total, FORMAT((b.total/exchange_rate),2))) AS total_amount, \r
        (SELECT GROUP_CONCAT(r.room_code) FROM book_hotel_room br \r
        INNER JOIN `def_room_type_category` r \r
        ON br.iddef_room_type = r.iddef_room_type_category \r
        WHERE br.idbook_hotel= b.idbook_hotel AND br.estado=1) AS room_codes, \r
        IFNULL((SELECT GROUP_CONCAT(bs.description) FROM book_extra_service bs \r
        WHERE bs.idbook_hotel= b.idbook_hotel AND bs.estado=1),'') AS services_codes, \r
        IFNULL((SELECT SUM(bs.total) FROM book_extra_service bs \r
        WHERE bs.idbook_hotel= b.idbook_hotel AND bs.estado=1),0) AS service_amount, \r
        (SELECT c.country_code FROM `def_country` c \r
        WHERE c.iddef_country= b.iddef_country AND c.estado=1) AS guest_country, \r
        (IF(b.expiry_date = '1900-01-01 00:00:00',0,TIMESTAMPDIFF(HOUR,b.fecha_creacion,b.expiry_date))) AS on_hold_duration, \r
        (SELECT GROUP_CONCAT(rp.code) FROM `book_hotel_room` br \r
        INNER JOIN op_rateplan rp \r
        ON br.idop_rate_plan = rp.idop_rateplan AND rp.estado=1 \r
        WHERE br.idbook_hotel= b.idbook_hotel AND br.estado=1) AS rate_codes, \r
        IFNULL((SELECT GROUP_CONCAT(p.code) FROM `book_promotion` bp \r
        INNER JOIN `op_promotions` p \r
        ON bp.idop_promotions = p.idop_promotions AND p.estado=1 \r
        WHERE bp.idbook_hotel= b.idbook_hotel AND bp.estado=1),'') AS booked_promotions, \r
        (IF(b.iddef_currency=(SELECT c.iddef_currency FROM `def_currency` c WHERE c.currency_code='USD'), b.discount_amount, FORMAT((b.discount_amount/exchange_rate),2))) AS discount, \r
        (SELECT c.country_code FROM `def_country` c \r
        WHERE c.iddef_country= b.iddef_currency_user AND c.estado=1) AS user_country, \r
        (SELECT GROUP_CONCAT(tl.text) FROM book_hotel_room br \r
        INNER JOIN `def_room_type_category` r \r
        ON br.iddef_room_type = r.iddef_room_type_category AND r.estado=1 \r
        INNER JOIN `def_text_lang` tl \r
        ON r.iddef_room_type_category = tl.id_relation AND tl.table_name='def_room_type_category' AND tl.attribute = 'room_name' AND tl.lang_code='EN' AND tl.estado=1 \r
        WHERE br.idbook_hotel= b.idbook_hotel AND br.estado=1) AS room_names, \r
        (SELECT GROUP_CONCAT(tl.text) FROM `book_hotel_room` br \r
        INNER JOIN op_rateplan rp \r
        ON br.idop_rate_plan = rp.idop_rateplan AND rp.estado=1 \r
        INNER JOIN `def_text_lang` tl \r
        ON rp.idop_rateplan = tl.id_relation AND tl.table_name='op_rateplan' AND tl.attribute = 'commercial_name' AND tl.lang_code='EN' AND tl.estado=1 \r
        WHERE br.idbook_hotel= b.idbook_hotel AND br.estado=1) AS rate_names, \r
        IFNULL((SELECT GROUP_CONCAT(tl.text) FROM book_extra_service bs \r
        INNER JOIN `def_text_lang` tl \r
        ON bs.iddef_service = tl.id_relation AND tl.table_name='def_service' AND tl.attribute = 'Name' AND tl.lang_code='EN' AND tl.estado=1 \r
        WHERE bs.idbook_hotel= b.idbook_hotel AND bs.estado=1),'') AS services_names, \r
        IFNULL((SELECT pc.promo_code FROM `book_promo_code` pc \r
        WHERE pc.idbook_hotel= b.idbook_hotel AND pc.estado=1),'') AS voucher_rule_code, \r
        IFNULL((SELECT pc.promo_code FROM `book_promo_code` pc \r
        INNER JOIN `def_promo_code` v \r
        ON pc.promo_code = v.code AND v.estado=1 \r
        WHERE pc.idbook_hotel= b.idbook_hotel AND pc.estado=1),'') AS voucher_rule_name \r
        FROM `book_hotel` b \r
        WHERE b.idbook_status IN(2) AND b.estado=1 AND ( \r
        DATE_FORMAT(CONVERT_TZ(b.cancelation_date, '+00:00', '-05:00'),'%Y-%m-%d') >='{ayer}' AND DATE_FORMAT(CONVERT_TZ(b.cancelation_date, '+00:00', '-05:00'),'%Y-%m-%d')<='{ayer}');""".format(ayer=ayer))
        
        x = db.session.execute(query)
        
        df = DataFrame(x.fetchall())
        if df.empty:
            df = DataFrame(
                columns=[
                'idbook_hotel',
                'code_reservation',
                'fecha_creacion',
                'from_date',
                'to_date',
                'fecha_ultima_modificacion',
                'adults',
                'child',
                'total_amount',
                'room_codes',
                'services_codes',
                'service_amount',
                'guest_country',
                'on_hold_duration',
                'rate_codes',
                'booked_promotions',
                'discount',
                'user_country',
                'room_names',
                'rate_names',
                'services_names',
                'voucher_rule_code',
                'voucher_rule_name',
            ] 
            )
        else:
            #df = DataFrame(x.fetchall())
            df.columns = x.keys()
        
        #hoja 1
        query1 = text("select\
        count(hr.idbook_hotel_room) as total,\
        sum(round(if(t.iddef_currency=1, hr.total, hr.total/t.exchange_rate),2)) as total_value\
        from book_hotel t\
        inner join book_hotel_room hr on hr.idbook_hotel = t.idbook_hotel\
        and hr.estado = 1\
        where t.idbook_status in (2,4,5,7,8) and t.estado = 1\
        and {conditionals}".format(conditionals = " AND ".join(conditionals)))
        
        query2 = text("""select \r
        count(hr.idbook_hotel_room) as canceled,\r
        sum(round(if(t.iddef_currency=1, hr.total, hr.total/t.exchange_rate),2)) as canceled_total_value\r
        from book_hotel t \r
        inner join book_hotel_room hr on hr.idbook_hotel = t.idbook_hotel\r
        and hr.estado = 1\r
        where t.idbook_status in (2) and t.estado = 1\r
        AND ( \r
        DATE_FORMAT(CONVERT_TZ(t.cancelation_date, '+00:00', '-05:00'),'%Y-%m-%d') >='{ayer}' AND DATE_FORMAT(CONVERT_TZ(t.cancelation_date, '+00:00', '-05:00'),'%Y-%m-%d')<='{ayer}');""".format(ayer=ayer))

        queryGroup = text("""
            select aux.*,
            round(aux.total_booking_value/aux.total_room_nights, 2) as avg_daily_rate,
            round(aux.total_room_nights/aux.bookings, 2) as avg_los
            from (
            select 
            p.short_name as hotel_name,
            round(sum(if(t.iddef_currency = 1, t.total, t.total/t.exchange_rate)),2) as total_booking_value,
            count(t.idbook_hotel) as bookings,
            sum(t.total_rooms*t.nights) as total_room_nights
            from book_hotel t
            inner join def_property p on p.iddef_property = t.iddef_property
            inner join def_currency c on c.iddef_currency = t.iddef_currency
            where t.estado = 1 and t.idbook_status = 2
            and (
            DATE_FORMAT(CONVERT_TZ(t.cancelation_date, '+00:00', '-05:00'),'%Y-%m-%d') >='{ayer}' AND DATE_FORMAT(CONVERT_TZ(t.cancelation_date, '+00:00', '-05:00'),'%Y-%m-%d')<='{ayer}')
            group by t.iddef_property) aux
        """.format(ayer=ayer))

        def format(x):
            return "${}".format(x)
        
        df['total_amount'] = df['total_amount'].apply(format)
        df['service_amount'] = df['service_amount'].apply(format)
        df['discount'] = df['discount'].apply(format)

        #data_hoja1 = db.session.execute(query1)
        data_hoja1 = db.engine.execute(query1)
        r = [row for row in data_hoja1]
        if r[0][0] == None or r[0][1] == None:
            total = 0
            total_value = 0
        else:
            total = r[0][0]
            total_value = r[0][1]
        
        data_hoja1_1 = db.engine.execute(query2)
        r2 = [row for row in data_hoja1_1]
        canceled = r2[0][0]
        canceled_total_value = r2[0][1]

        if canceled == None or canceled_total_value == None:
            canceled = 0
            canceled_total_value = 0
            cancelations_ratio = 0
            canceled_booking_value = 0
        if canceled == 0 or total == None or total == 0 or canceled_total_value == 0:
            cancelations_ratio = 0
            canceled_booking_value = 0
        else:
            cancelations_ratio = (canceled/total)*100
            canceled_booking_value = (canceled_total_value/total_value)*100

        data_hoja1_json =[{
            'cancelled_bookings':'$' +f'{canceled_total_value:,.2f}',
            'cancelled_bookings_value': f'{canceled_booking_value:,.2f}'+'%',
            'cancellations': f'{canceled:,.2f}',
            'cancelations_ratio': f'{cancelations_ratio:,.2f}' + '%'
        }]

        df_sheet1 = pd.DataFrame(data_hoja1_json)
        df_sheet1.rename(columns=
        {
            'cancelled_bookings': 'Cancelled Bookings',
            'cancelled_bookings_value': 'Cancelled bookings value',
            'cancellations': 'Cancellations',
            'cancelations_ratio': 'Cancellations ratio'
        }, inplace=True)
        #df_sheet1 = pd.DataFrame(data_hoja1_json, columns = ['Cancelled bookings', 'Cancelled bookings value', 'Cancellations', 'Cancellations ratio'])
        df_sheet1 = df_sheet1.T
        #lógica para llenar el DataFrame
        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:
            
            df.rename(columns=
            {
                'idbook_hotel': 'Hotel ID' ,
                'code_reservation': 'Reservation ID',
                'fecha_creacion':'Creation date',
                'from_date': 'Arrival date',
                'to_date': 'Departure date',
                'fecha_ultima_modificacion': 'Last modified date',
                'adults': 'Number of adults',
                'child': 'Number of children',
                'total_amount': 'Total amount',
                'room_codes': 'Room codes',
                'services_codes': 'Service codes',
                'service_amount': 'Service amount',
                'guest_country': 'Guest country',
                'on_hold_duration': 'OnHold duration',
                'rate_codes': 'Rate codes',
                'booked_promotions': 'Booked promotions',
                'discount': 'Discount',
                'user_country': 'User country',
                'room_names': 'Room Name(s)',
                'rate_names': 'Rate Name(s)',
                'services_names': 'Service Name(s)',
                'voucher_rule_code': 'Voucher rule code',
                'voucher_rule_name': 'Voucher rule name',
            }, inplace=True)

            """     Last modified date  Room stay amount     Source    Source context
            User device            Promotion code        Contract IDs    Contract names      Net rate """

            workbook = writer.book
            #Creamos la hoja 1
            df_sheet1.to_excel(writer, sheet_name="KPI", index=True, header = False)
            worksheet1 = writer.sheets['KPI']
            worksheet1.set_column('A:B', 51)
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})

            df.to_excel(writer, sheet_name="Data", index=False, header = True)
            worksheet = writer.sheets['Data']
            worksheet.set_column('A:W', 51)
            worksheet.autofilter('A1:G1')
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            
            workbook.close()

            dataGroup = db.engine.execute(queryGroup)
            table_consolidated = ""
            for row in dataGroup:                
                #t = "<tr style='background-color: rgba(225,225,225,0.3);'><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["hotel_name"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["total_booking_value"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["bookings"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["total_room_nights"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["avg_daily_rate"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["avg_los"])+"</td></tr>"
                table_consolidated = table_consolidated + "<tr style='background-color: rgba(225,225,225,0.3);'><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["hotel_name"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+"$"+str(f'{row["total_booking_value"]:,.2f}')+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["bookings"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["total_room_nights"])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+"$"+str(f'{row["avg_daily_rate"]:,.2f}')+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(row["avg_los"])+"</td></tr>"#tb_consolidated
            
           #SEND CANCELATION BOOKING EMAIL ******************************
            #btn_download = "<a href="+presigned_url+"><button type='button'id='download-button' style='border: none; border-radius: 0.25rem; text-transform: uppercase; padding: 0.5rem; background-color: #01B0EF; border-color: #01B0EF; color: #FFFFFF;'>Download</button></a>"
            data_booking = {
                "email_list": "",
                "group_validation": True,
                "cancel_amount_bookings": f'{canceled_total_value:,.2f}',
                "cancel_bookings_value": f'{canceled_booking_value:,.2f}',
                "cancellations": f'{canceled:,.2f}',
                "cancellations_ratio": f'{cancelations_ratio:,.2f}',
                "data_table": table_consolidated,
                "btn_download": ""
            }
            files=[
                ('FILE_1', open(xlsx_report,'rb'))
            ]
            Util.send_notification_attachment(data_booking, "NOTIFICATION_BENGINE_CANCELLATION_BOOKINGS", 'alejaramos', files)
        
        if data_booking is None:        
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {}
            }
        else:
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": "Email Send Successfully"
            }
        
        return response