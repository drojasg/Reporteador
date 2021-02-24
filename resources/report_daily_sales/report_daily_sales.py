#**********************
import pandas as pd
import xlwt
import os
import requests
#************************
#****BOTO3***************#
import logging
import boto3
from botocore.exceptions import ClientError
#************************#
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
from datetime import datetime,timedelta
#from datetime import timedelta
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

class reportDailySales(Resource):
    @api.representation(MIME)
    def post(self):
        #agregamos validaciones de parametros
        #params = request.get_json(force=True)
        #conditionals servirá para acumular todos los parametros
        conditionals = []
        conditionals_sheet_2 = []
        #agregamos los estados a los condicionales de cada hoja
        conditionals.append("t.estado = 1")
        conditionals.append("t.idbook_status in (4,5,7,8)")
        conditionals_sheet_2.append("dar.estado = 1")

        #creamos variables de los demás parametros que serán dinámicos y les asignamos un tipo de dato
        now = datetime.now()
        #validamos que los campos vengan como string
        #if isinstance(now, str):

        hoy = datetime.utcnow()
        ayer = hoy - timedelta(days=1)
        anteayer = ayer - timedelta(days=1)
        #print(ayer.replace(hour=23, minute=59, second=59, microsecond=999999))


        #now_datetime = datetime.datetime.now()
        #end_of_day_datetime = now_datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
        #empezar de anteayer a las 11:00
        conditionals.append("CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') between '{now}'".format(now = ayer.replace(hour=00, minute=00, second=00, microsecond=000000)))
        
        conditionals.append("'{to_creation_data}'".format(to_creation_data = ayer.replace(hour=23, minute=59, second=59, microsecond=000000)))
        #Comenzamod a armar el archivo excell

        xlsx_report = os.path.join(
            base.app_config("TMP_PATH"),
            "{}_{}.xlsx".format("report_daily_sales", get_bulk(charsize=7))
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
        df = pd.DataFrame()
        
        #ponemos los querys de todas las hojas
        #hoja 1
        query = "select aux.*,\
        round(aux.total_booking_value/aux.total_room_nights, 2) as avg_daily_rate,\
        round(aux.total_room_nights/aux.bookings, 2) as avg_los\
        from (\
        select \
        p.short_name as hotel_name,\
        round(sum(if(t.iddef_currency = 1, t.total, t.total/t.exchange_rate)),2) as total_booking_value, \
        count(t.idbook_hotel) as bookings, \
        sum(t.total_rooms*t.nights) as total_room_nights\
        from book_hotel t \
        inner join def_property p on p.iddef_property = t.iddef_property\
        inner join def_currency c on c.iddef_currency = t.iddef_currency\
        where  {conditionals}".format(conditionals = " AND ".join(conditionals)) + "group by t.iddef_property) aux;"

        #ejecutamos el query con pandas
        df = pd.read_sql_query(text(query), db.engine)
        
        #sacamos los campos para los reportes:
        bookings = df['bookings'].sum()
        total_room_nights = df['total_room_nights'].sum()
        total_booking_value = df['total_booking_value'].sum()
        total_room_nights = df['total_room_nights'].sum()
        if total_booking_value == 0 or total_room_nights == 0:
            average_daily_rate_on_total_room = 0
        else:
            average_daily_rate_on_total_room = total_booking_value/total_room_nights
        if total_booking_value == 0 or bookings == 0:
            average_LOS = 0
        else:    
            average_LOS = total_room_nights/bookings

        data_sheet2 ={
            'Bookings' : [bookings],
            'Total room nights' : [total_room_nights],
            'Average daily rate on total roomnights': [average_daily_rate_on_total_room],
            'Average LOS': [average_LOS],
            'Total booking value (room only)': [total_booking_value]
        } 

        def format(x):
            return "${:,.2f}".format(x)
        
        df['total_booking_value'] = df['total_booking_value'].apply(format)
        df['avg_daily_rate']= df['avg_daily_rate'].apply(format)

        df_sheet_2 = pd.DataFrame(data_sheet2,columns=['Bookings','Total room nights','Average daily rate on total roomnights', 'Average LOS', 'Total booking value (room only)'] )
        df_sheet_2 = df_sheet_2.T
        #lógica para llenar el DataFsrame
        with pd.ExcelWriter(xlsx_report, engine='xlsxwriter') as writer:

            df.rename(columns=
            {
                'hotel_name':'Hotel name',
                'total_booking_value': 'Total booking value (room only)',
                'bookings': 'Bookings',
                'total_room_nights':'Total room nights',
                'avg_los':'Average LOS',
                'avg_daily_rate':'Average daily rate on total roomnights'
            }, inplace=True)

            workbook = writer.book
            
            #Agregamos una nueva Hoja(solo y solo si es necesario, de lo contrario, comentar este código)
            df_sheet_2.to_excel(writer, sheet_name="KPI", index=True, header = False)
            #Agregamos un titulo a la hoja 2
            #merge_format = workbook.add_format({'bold': 15,'border': 0,'align': 'right','valign': 'vright','fg_color': 'pink'})
            worksheet_2 = writer.sheets['KPI']
            worksheet_2.set_column('A:A', 51)
            #worksheet_2.set_row(1, 30)
            #Agregamos filtros a los encabezados
            #worksheet_2.autofilter('A2:B2')
            #merge_format = workbook.add_format({'bold': 15,'border': 1,'align': 'right','valign': 'vright','fg_color': 'white'})
            #worksheet_2.merge_range('A1:A5',merge_format)

            #Creamos la hoja()
            df.to_excel(writer, sheet_name="Data", index=False, header = True)
            #Editamos el documento para agregarle un título en la hoja seleccionada
            worksheet = writer.sheets['Data']
            #Agregamos un título
            #title= 'Report Daily Sales'
            worksheet.set_column('A:F', 51)
            worksheet.autofilter('A1:G1')
            #worksheet.set_row(1, 30)
            merge_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': 'white'})
            #worksheet.merge_range('A1:G1', title, merge_format)
            

            workbook.close()

            #Obtenemos el response del bucket
            #upload_buck = self.upload_bucket(self,xlsx_report)
            #presigned_url = upload_buck["presigned_url"]
            presigned_url = ""
            #print(upload_buck)

            #Validamos que nos responda el bucket
            

            #SENDING CONSOLIDATED BOOKING EMAIL ******************************
            tb_consolidated = ""
            
            Obj_Daily = df.values.tolist()
            for objDaily in Obj_Daily:
                tb_consolidated = tb_consolidated + "<tr style='background-color: rgba(225,225,225,0.3);'><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(objDaily[0])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(objDaily[1])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(objDaily[2])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(objDaily[3])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(objDaily[4])+"</td><td style='padding: 0.5rem; border: 1px solid lightgrey;'>"+str(objDaily[5])+"</td></tr>"

            btn_download = "<a href="+presigned_url+"><button type='button'id='download-button' style='border: none; border-radius: 0.25rem; text-transform: uppercase; padding: 0.5rem; background-color: #01b0ef; border-color: #01b0ef; color: #ffffff;'>Download</button></a>"
            
            data_booking = {
                "email_list": "",
                "group_validation": True,
                "bookings": int(bookings),
                "total_room_nights": int(total_room_nights),
                "average_daily_rate": f'{average_daily_rate_on_total_room:,.2f}',
                "average_los": f'{average_LOS:,.2f}',
                "booking_value": f'{total_booking_value:,.2f}',
                "data_table": tb_consolidated,
                "btn_download": ""
            }
            files=[
                ('FILE_1', open(xlsx_report,'rb'))
            ]
            Util.send_notification_attachment(data_booking, "NOTIFICATION_BENGINE_CONSOLIDATED_REPORT", 'alejaramos', files)
            
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