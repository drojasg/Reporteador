from config import app, db, celery, base
#from config.celery import make_celery
from models.pms import Pms
from models.book_hotel import BookHotel
from models.book_status import BookStatus
from resources.property.property_service import PropertyService
from common.util import Util
#celery = make_celery(app)

@celery.task
def interface_pms(name, description):
    with app.app_context():
        try:
            pms = Pms()
            pms.code = "demo"
            pms.name = name
            pms.description = description
            pms.estado = 1
            pms.usuario_creacion = "admin"
            db.session.add(pms)
            db.session.commit()
        except Exception as e:
            print(str(e))
            app.logger.error("Celery Background SQS Error: "+ str(e))

@celery.task
def interface_booking(idbook_hotel):
    with app.app_context():
        from resources.booking.booking_service import BookingService
        try:
            booking_service = BookingService()

            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbook_hotel, BookHotel.estado == 1).first()
            
            if book_hotel is None:
                raise Exception(Util.t("en", "booking_code_not_found", idbook_hotel))

            if book_hotel.idbook_status not in [BookStatus.confirmed]:
                raise Exception(Util.t("en", "booking_not_confirmed"))
                
            booking_service.create_booking(book_hotel=book_hotel)
                
        except Exception as e:
            print(str(e))
            app.logger.error("Celery Background SQS Error: "+ str(e))

@celery.task
def send_notification_async(idbook_hotel, username):
    with app.app_context():
        from resources.booking.booking_service import BookingService
        try:
            booking_service = BookingService()

            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbook_hotel, BookHotel.estado == 1).first()
            
            if book_hotel is None:
                raise Exception(Util.t("en", "booking_code_not_found", idbook_hotel))
            
            #retrieve email cc to send a email copy
            email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")

            #sending confirmation or on hold email
            email_data = booking_service.format_booking_letter(book_hotel)        
            email_data["email_list"] = book_hotel.customers[0].customer.email

            Util.send_notification(email_data, email_data["carta"], username)

            if base.environment == "pro":
                email_data["email_list"] = email_cc
                Util.send_notification(email_data, email_data["carta"], username)
            
        except Exception as e:
            print(str(e))
            app.logger.error("Celery Background SQS Error: "+ str(e))

@celery.task
def get_exchange_rates():
    with app.app_context():
        from resources.exchange_rate.exchange_rate_service import ExchangeRateService
        from datetime import date
        
        try:
            exchange_service = ExchangeRateService()
            response_rates = exchange_service.save_exchange_rate(date.today(), "worker")
            print("load exchange rate")
        except Exception as e:
            print(str(e))
            app.logger.error("Celery Background SQS Error: "+ str(e))

@celery.task
def schedule_pms():
    with app.app_context():
        try:
            print("hello world!!!")
            """
            pms = Pms()
            pms.code = "demo"
            pms.name = "name"
            pms.description = "description"
            pms.estado = 1
            pms.usuario_creacion = "admin"
            db.session.add(pms)
            db.session.commit()
            """
        except Exception as e:
            print(str(e))
            app.logger.error("Celery Background SQS Error: "+ str(e))
