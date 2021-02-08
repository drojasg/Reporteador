# -*- coding: utf-8 -*-
"""
    config.flask
    ~~~~~~~~~~~~~~

    Setup Flask configuration

    :copyright: (c) 2019 by Software Clever, Palace Resorts CEDIS.
    :license: Private.
"""
from flask import Flask
from flask_cors import CORS
from logging.config import dictConfig
from datetime import datetime
from .urls import URLS
from config.extensions.base_controller import BaseController
from celery import Celery
import logging
from kombu.utils.url import safequote
from apscheduler.schedulers.background import BackgroundScheduler
import socket
from flask_compress import Compress
import os

__all__ = ["app", "base", "celery"]

#: Defines project environment dev, qa or pro
ENVIRONMENT = "dev"

#: Logger configuration
LOGGER_FORMAT = (
    "%(asctime)s %(name)-4s %(levelname)-4s in %(module)s: %(message)s"
)

#: Set logging handlers
handlers = {
    #: Send logs to HTTP DTC API
    "http_handler": {
        "class": "logging.handlers.HTTPHandler",
        "formatter": "default",
        "level": "ERROR",
        "host": "127.0.0.1:9010",
        "url": "/logger",
        "secure": False,
        "method": "POST",
    },
    #: Send logs to console
    "wsgi": {
        "class": "logging.StreamHandler",
        "stream": "ext://flask.logging.wsgi_errors_stream",
    },
}
root = {"handlers": ["http_handler", "wsgi"]}

if ENVIRONMENT in ("dev", "qa"):
    #: Send logs to file
    handlers["file_handler"] = {
        "class": "logging.FileHandler",
        "formatter": "default",
        "filename": "app.log",
        "mode": "a",
        "level": "ERROR",
    }
    root["handlers"].append("file_handler")

dictConfig(
    {
        "version": 1,
        "formatters": {"default": {"format": LOGGER_FORMAT}},
        "handlers": handlers,
        "root": root,
    }
)

class CeleryConfig(object):
    enable_iam = True
    aws_access_key = safequote("")
    aws_secret_key = safequote("")
    task_default_queue = "clv-bengine-sqs-qa"
    broker_url = "sqs://" if enable_iam else "sqs://{aws_access_key}:{aws_secret_key}@".format(aws_access_key=aws_access_key, aws_secret_key=aws_secret_key)
    broker_transport_options = {"max_retries": 3, "interval_start": 0, "interval_step": 0.2, "interval_max": 0.5}

class Config(object):
    """Flask configurations"""

    #: Project config values
    APP_NAME = "clv-bengine-core-api"
    SYSTEM_MODULE = "bengine"
    SYSTEM_ID = 24
    TMP_PATH = "/tmp"
    ENABLE_ADMIN_MIDDLEWARE = False
    ENABLE_PUBLIC_MIDDLEWARE = False
     
    DB_HOST = os.getenv('DB_HOST')
    DB_SECRET_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_PARAMS = "?local_infile=1&charset=utf8"

    #: Sqlalchemy config values
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://"+DB_USER+":"+DB_PASS+"@"+DB_HOST+"/"+DB_SECRET_NAME+DB_PARAMS
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DBAPI = "mysql+pymysql"
    SQLALCHEMY_PARAMS = {"local_infile": 1, "charset": "utf8"}

    #: App config values
    ENV = "production"
    DEBUG = False
    TESTING = False

    #: Project's urls
    URLS = URLS


class PROConfig(Config):
    #: App config values
    APP_ENV = "pro"


class QAConfig(Config):
    #: App config values
    APP_ENV = "qa"


class DEVConfig(Config):
    #: App config values
    ENV = "development"
    DEBUG = True
    TESTING = True
    APP_ENV = "dev"



#: Flask app instance
app = Flask(__name__, static_folder="../static")
Compress(app)

@app.route('/static/ping.html')
def ping():
    return app.send_static_file('ping.html')

#: Set Flask configs
if ENVIRONMENT == "pro":
    app.config.from_object(PROConfig)
elif ENVIRONMENT == "qa":
    app.config.from_object(QAConfig)
else:
    app.config.from_object(DEVConfig)
#: Setup CORS
CORS(app)
#: Setup base
base = BaseController(app)

#: Add params to logger object
old_factory = logging.getLogRecordFactory()

def getHostByEnvironment(host_name):
    list_host_names = { 
        "pro": "clv-bengine-core-api_pro16039",
        "qa": "clv-bengine-core-api_qa19006",
        "dev": "host_name_dev",
    } 
    return list_host_names.get(host_name.lower(), None)

def remember_bookings_on_hold():
    with app.test_request_context():
        try:
            url = "{}{}".format(base.get_url("bengine"), "/api/booking/on-hold-reminder")
            base.request(url=url, method="post", data={})
        except Exception as e:
            app.logger.error("Booking on hold remember process Error: "+ str(e))

def cancel_bookings_on_hold():
    with app.test_request_context():
        try:
            url = "{}{}".format(base.get_url("bengine"), "/api/booking/on-hold-cancel")
            base.request(url=url, method="post", data={})
        except Exception as e:
            app.logger.error("Booking on hold cancel process Error: "+ str(e))

def load_exchange_rate():
    with app.test_request_context():
        from common.external_credentials import ExternalCredentials
        try:
            external_credentials = ExternalCredentials()
            token = external_credentials.get_token(base.system_id)

            url = "{}{}".format(base.get_url("bengine"), "/api/exchange-rate/load")
            base.request(url=url, method="post", data={}, use_token=False, token=token)
        except Exception as e:
            app.logger.error("Load exchange rate process Error: "+ str(e))

def link_payments():
    with app.test_request_context():
        try:
            url = "{}{}".format(base.get_url("bengine"), "/api/payments/link-payments")
            base.request(url=url, method="post", data={})
        except Exception as e:
            app.logger.error("Link payments process Error: "+ str(e))

def send_daily_sales_report():
    with app.test_request_context():
        try:
            url = "{}{}".format(base.get_url("bengine"), "/api/reports/get-daily-sales-report")
            base.request(url=url, method="post", data={})
        except Exception as e:
            app.logger.error("Send daily sales report process Error: "+ str(e))

def send_cancel_bookings_report():
    with app.test_request_context():
        try:
            url = "{}{}".format(base.get_url("bengine"), "/api/reports/get-cancelation-report")
            base.request(url=url, method="post", data={})
        except Exception as e:
            app.logger.error("Send canel booking report process Error: "+ str(e))

# Se agregan los jobs
# Por intervalos (cada determinado tiempo):
# scheduler.add_job(remember_bookings_on_hold, 'interval', minutes=5)
# 
# Por cron (hora específica):
# scheduler.add_job(remember_bookings_on_hold, 'cron', year='*', month='*', day="*", week='*', day_of_week='*', hour='6', minute=10, second=0)
scheduler = BackgroundScheduler({'apscheduler.timezone': 'America/Cancun'})
if ENVIRONMENT in ("pro"):
    host_name = socket.gethostname()
    if host_name == getHostByEnvironment(ENVIRONMENT):
        scheduler.add_job(cancel_bookings_on_hold, 'interval', minutes=5)
        scheduler.add_job(remember_bookings_on_hold, 'interval', minutes=5)
        scheduler.add_job(link_payments, 'interval', minutes=10)
        scheduler.add_job(load_exchange_rate, 'cron', year='*', month='*', day="*", week='*', day_of_week='*', hour='10', minute=0, second=0)
        scheduler.add_job(send_daily_sales_report, 'cron', year='*', month='*', day="*", week='*', day_of_week='*', hour='00', minute=25, second=0)
        scheduler.add_job(send_cancel_bookings_report, 'cron', year='*', month='*', day="*", week='*', day_of_week='*', hour='00', minute=30, second=0)
        scheduler.start()

app.logger.error("Host {} is running job process: {}".format(str(socket.gethostname()), str(scheduler.running)))
list_jobs = scheduler.get_jobs()
app.logger.error("***List job process***")
if len(list_jobs) > 0:
    for job in scheduler.get_jobs():
        app.logger.error("    name: {}, trigger: {}, next run: {}, handler: {}".format(str(job.name), str(job.trigger), str(job.next_run_time), str(job.func)))
else:
    job_message = "    No scheduled jobs" if scheduler.running else "    No pending jobs"
    app.logger.error(job_message)

#: Setup Celery
celery = Celery()
celery.config_from_object(CeleryConfig)
app.celery = celery

def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record.username = base.get_username()
    record.environment = base.environment
    record.app_name = base.app_name
    return record


logging.setLogRecordFactory(record_factory)
