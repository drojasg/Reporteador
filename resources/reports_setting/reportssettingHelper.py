from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta

from config import db, base
from models.reports_setting import ReportSettingSchema as ModelSchema, ReportSetting as Model
from models.reports import ReportsSchema as RModelSchema, Reports as RModel
from common.util import Util
from sqlalchemy import or_, and_, func
import datetime as dt

class ReportSettingFunction():
     #metodo para enviar correos
    @staticmethod
    def reports_setting_leatter(list_reports,user):
        try:
            files = 0
            for item in list_reports:
                email_list = ','.join(aux for aux in item["emails"])
                data_reports = {
                    "email_list": email_list,
                    "group_validation": False,
                    "cancel_amount_bookings": "",
                    "cancel_bookings_value": "",
                    "cancellations": "",
                    "cancellations_ratio": "",
                    "btn_download": "",
                    "email_subject": item["subject_letter"]
                }

                Util.send_notification(data_reports, "NOTIFICATION_BENGINE_CANCELLATION_BOOKINGS", user)

        except Exception as error:
            raise error
        
        return list_reports