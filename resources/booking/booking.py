from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from functools import reduce

from config import db, base
from models.book_hotel import BookHotelReservationSchema as ModelSchema, BookHotel,\
BookHotelAdminSchema, EmailReservationSchema, CancelReservationSchema, BookHotelFilterSchema,\
BookHotelReservationDuplicateSchema as BookHotelValidateModelSchema
from models.book_status import BookStatus
from models.payment_method import PaymentMethod
from models.forward_emails import ForwardEmails, ForwardEmailsSchema

from models.market_segment import MarketSegment
from models.languaje import Languaje
from models.currency import Currency
from models.country import Country
from models.property import Property
from models.rateplan import RatePlan
from common.util import Util
from common.card_validation import CardValidation
from .booking_service import BookingService
from .booking_canceled import BookingLetter
from resources.payment.payment_service import PaymentService
from resources.rates.RatesHelper import RatesFunctions
from resources.exchange_rate.exchange_rate_service import ExchangeRateService
from resources.rateplan import RatePlanPublic as FunctionsPolicy
from resources.service.serviceHelper import Search as FunctionsService
from resources.promo_code.promocodeHelper import PromoCodeFunctions as FunctionVoucher
from common.public_auth import PublicAuth
from resources.property.property_service import PropertyService
from .booking_task import BookingTask
from .booking_operation import BookingOperation
#from .booking_promotions import BookingPromo
import json
import copy
from resources.inventory.inventory import Inventory
from unidecode import unidecode
from resources.carta.emailTemplate import EmailTemplate
from resources.carta.carta_util import CartaUtil

class BookingPublic(Resource):
    @PublicAuth.access_middleware
    def get(self, code_reservation, full_name):
        response = {}
        try:
            booking_service = BookingService()
            data = booking_service.get_booking_info_by_code(code_reservation, full_name)
            
            if data["status_code"] not in [BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced, BookStatus.on_hold]:
                raise Exception(Util.t("en", "booking_code_not_found", code_reservation))
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
    
    @PublicAuth.access_middleware
    def post(self):
        response = {}
        message = "Success"
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            data = schema.load(json_data)
            booking_service = BookingService()
            device_request = Util.get_device_request(request.user_agent.string)

            #get api-key data
            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            iddef_channel = credential_data.iddef_channel

            if data["from_date"] <= datetime.today():
                raise Exception(Util.t(data["lang_code"], "booking_today_greater_date"))

            if data["from_date"] > data["to_date"]:
                raise Exception(Util.t(data["lang_code"], "booking_from_date_greater_to_date"))
            
            if len(data["rooms"]) == 0:
                raise Exception(Util.t(data["lang_code"], "booking_rooms_required"))

            if not data["on_hold"]:
                payment_info = booking_service.get_payment_codes(data["payment"])
                        
            data["nights"] = (data["to_date"] - data["from_date"]).days
            market_segment = RatesFunctions.getMarketInfo(data["market_code"],data["lang_code"])
            country_segment = booking_service.get_model_by_code(data["market_code"], "country_code", Country)
            language = booking_service.get_model_by_code(data["lang_code"], "lang_code", Languaje)
            currency_user = booking_service.get_model_by_code(data["currency_code"], "currency_code", Currency)
            country = booking_service.get_model_by_code(data["customer"]["address"]["country_code"], "country_code", Country)            
            property = booking_service.get_model_by_code(data["property_code"], "property_code", Property)
            exchange_rate_amount = 1

            #Para el mercado de México se cobra siempre en MXN, para resto de los mercados USD
            if data["market_code"] == "MX":
                data["currency_code"] = "MXN"
                exchange_rate_user = ExchangeRateService.get_exchange_rate_date(date.today(), data["currency_code"])
                if exchange_rate_user:
                    exchange_rate_amount = exchange_rate_user.amount
            else:
                data["currency_code"] = "USD"
                        
            book_hotel = BookHotel()
            book_hotel.iddef_property = property.iddef_property
            book_hotel.from_date = data["from_date"]
            book_hotel.to_date = data["to_date"]
            book_hotel.nights = data["nights"]
            book_hotel.iddef_market_segment = market_segment.iddef_market_segment
            book_hotel.iddef_country = country_segment.iddef_country
            book_hotel.iddef_language = language.iddef_language
            book_hotel.iddef_currency_user = currency_user.iddef_currency
            book_hotel.iddef_channel = iddef_channel
            book_hotel.exchange_rate = exchange_rate_amount
            book_hotel.device_request = device_request
            book_hotel.estado = 1
            book_hotel.usuario_creacion = username
            age_range_data = booking_service.get_ages_ranges_list(book_hotel.iddef_property)
            booking_currency = data["currency_code"]
            rateplan_list = []
            rooms_list = []
            data_rates = []
            rates_original = []
            total_voucher = 0
            room_order = 0
            for room_data in data["rooms"]:
                #obtenemos ids_rateplan
                rateplan_list.append(room_data["idop_rate_plan"])
                rooms_list.append(room_data["iddef_room_type"])
                    
                room_data["property_code"] = data["property_code"]
                room_data["iddef_property"] = book_hotel.iddef_property
                room_data["from_date"] = book_hotel.from_date
                room_data["to_date"] = book_hotel.to_date
                room_data["currency"] = booking_currency
                room_data["iddef_market"] = book_hotel.iddef_market_segment
                room_data["country_code"] = data["market_code"]
                
                rates_room = RatesFunctions.getPricePerDay(room_data["iddef_property"], room_data["iddef_room_type"], \
                room_data["idop_rate_plan"], room_data["from_date"], room_data["to_date"], currency=room_data["currency"],\
                use_booking_window=True, market=room_data["iddef_market"], country=room_data["country_code"],pax_room=room_data["pax"])
                room_order += 1
                rates_room["room_order"] = room_order
                rates_room["rate_amount"] = rates_room["total"]
                rates_original.append(copy.deepcopy(rates_room))
            
            data_rates = rates_original

            #if apply promotions by free_room
            promotions_rooms = RatesFunctions.get_promotions_by_booking(date_start=data["from_date"].date(), 
            date_end=data["to_date"].date(), market=data["market_code"],hotel=data["property_code"],\
            total_rooms=data["rooms"])
            if len(promotions_rooms) > 0:
                rate_list_aux = []
                for promo in promotions_rooms:
                    rate_list_promotion = copy.deepcopy(data_rates)
                    promo_list = []
                    promo_list.append(promo)

                    aux_rate = RatesFunctions.apply_promotion(rate_list_promotion,\
                    promo_list)

                    rate_list_aux.append(copy.deepcopy(aux_rate["Prices"]))

                cont_room = 0
                list_end = []
                """ generate_vaucher = False
                cont_applies = 0
                room_selected = None
                cont_room_select = 0 """
                for room_item in data["rooms"]: 
                    
                    room_version = []
                    for price_version in rate_list_aux:
                        room_version.append(copy.deepcopy(price_version[cont_room]))

                    rates_aux = RatesFunctions.select_rates_promotion(room_version)
                    list_end.append(copy.deepcopy(rates_aux))

                    price_total = RatesFunctions.calcualte_total_rates(list_end)

                    """ if rates_aux["apply_room_free"] == True:
                        cont_applies += 1
                        if price_total["total"] > 0 and cont_room_select < 1:
                            room_selected = rates_aux
                            cont_room_select += 1

                    if cont_applies % 2 != 0:
                        generate_vaucher = True
                    else:
                        generate_vaucher = False """

                    cont_room += 1

                list_end.sort(key=lambda x: x["room_order"])

                data_rates = list_end

            #if apply tax
            price_tax = RatesFunctions.get_price_with_policy_tax(data["from_date"].date(),\
                data["to_date"].date(),data["currency_code"], data_rates)
            data_rates = price_tax["data"]
            tax_amount = price_tax["total_tax"]
            price_total = RatesFunctions.calcualte_total_rates(data_rates)

            #appy crossout
            data_rates = RatesFunctions.apply_crossout_list(data_rates,\
            book_hotel.iddef_market_segment,data["market_code"],True)
            price_total = RatesFunctions.calcualte_total_rates(data_rates)
            
            #if apply promo_code
            vaucherApplied = False
            is_text = 0
            if data["promo_code"] != "":
                try:
                    date_now = datetime.now().date()
                    vauchers = FunctionVoucher.getValidatePromoCode(data["promo_code"],\
                    property_code=data["property_code"],travel_window_start=data["from_date"].date(),\
                    travel_window_end=data["to_date"].date(),rateplans=rateplan_list,rooms=rooms_list,\
                    market=book_hotel.iddef_market_segment,lang_code=data["lang_code"])

                    vaucher_applied = RatesFunctions.apply_vauchers(data_rates,vauchers,\
                    data["currency_code"],date_now)

                    data_rates = vaucher_applied["Prices"]
                    total_voucher = round(vaucher_applied["Subtotal"],4)
                    vaucherApplied = vaucher_applied["vaucher_applied"]

                    is_text = 0
                    if vauchers != None:
                        if vauchers["text_only"] is True:
                            is_text = 1
                        
                        book_hotel.promo_codes = [booking_service.create_promo_code(is_text,data["promo_code"], vaucher_applied["Subtotal"], vauchers["type_amount"], book_hotel.usuario_creacion)]
                
                except Exception as vaucher_error:
                    pass

            #crear room
            list_rooms = []
            list_services = []
            total_discount_amount = 0
            total_gross = 0
            total_amount = 0
            total_discount_percent = 0
            adults = 0
            child = 0
            promotion_amount = 0
            tax_amount = 0
            list_promotion = []
            count_room = 0
            num = 0
            for room_data in data["rooms"]:
                num += 1
                #iterate the pax values
                pax_list = []
                room_adults = 0
                room_child = 0
                validate_pax_code = True
                for key, value in room_data["pax"].items():
                    iddef_age_range = 0

                    if key == "adults":
                        room_adults = value
                    else:
                        room_child += value

                    if validate_pax_code == True:
                        #looking for the iddef_age_code & validate if exists the code in the property config age_range
                        iddef_age_range = next((item["iddef_age_range"] for item in age_range_data\
                            if item["age_range_age_code"]["code"] == key), None)
                        
                        if iddef_age_range is None:
                            raise Exception("Pax code \"{}\" not exists in the property configuration".format(key))
                    
                    pax_data = {
                        "iddef_age_range": iddef_age_range,
                        "age_code": key,
                        "pax": value,
                        "user": username
                    }

                    pax_list.append(booking_service.create_pax_room(pax_data))
                #validate rates plan currency, must be the same currency
                rate_plan = booking_service.get_model_by_id(room_data["idop_rate_plan"], RatePlan)                

                
                room_data["iddef_room_type"] = room_data["iddef_room_type"]
                room_data["idop_rateplan"] = rate_plan.idop_rateplan
                room_data["rateplan_is_refundable"] = rate_plan.refundable
                room_data["user"] = username
                room_data["paxes"] = pax_list
                room_data["adults"] = room_adults
                room_data["child"] = room_child
                for rate in data_rates:
                    if num == rate["room_order"]:
                        room_data["total"] = rate["total"]
                        room_data["rate_amount"] = rate["rate_amount"]
                        room_data["discount_percent"] = round(rate["total_percent_discount"], 2)
                        room_data["discount_amount"] = round(rate["total_crossout"] - rate["total"], 4)
                        room_data["total_gross"] = rate["total_crossout"]
                        room_data["price_per_day"] = rate["price_per_day"]
                        room_data["vaucher_applied"] = rate["vaucher_applied"]
                        room = booking_service.create_room(room_data,data["promo_code"],vaucherApplied=vaucherApplied,is_text=is_text)
                        count_room += 1
                        total_discount_amount += room.discount_amount
                        total_gross += room.total_gross
                        total_amount += room.total
                        total_discount_percent += room.discount_percent
                        adults += room.adults
                        child += room.child
                        promotion_amount += room.promotion_amount
                        tax_amount += room.country_fee
                        list_rooms.append(room)
            book_hotel.rooms = list_rooms

            #if apply promotions, promotions save
            if promotion_amount > 0:
                list_aux = []
                for itm_room in book_hotel.rooms:
                    for itm_price in itm_room.prices:
                        if itm_price.code_promotions not in list_aux:
                            list_aux.append(itm_price.code_promotions)
                            promotion = RatesFunctions.get_promotions(code=itm_price.code_promotions)
                            if promotion and len(promotion) > 0:
                                idop_promotion = promotion[0]["idop_promotions"]
                                promotion_data = {
                                    "idop_promotions": idop_promotion,
                                    "user": book_hotel.usuario_creacion
                                }
                                list_promotion.append(booking_service.create_promotion(promotion_data))

            book_hotel.promotions = list_promotion

            #if add services, valid exists config. services and save
            FunctionService = FunctionsService()
            if data["services"]:
                config_services = FunctionService.get_service_by_additional(data["services"],book_hotel.from_date, book_hotel.to_date, book_hotel.iddef_market_segment,\
                    property.iddef_property, len(data["rooms"]), (adults + child), data["market_code"])

                for id_service in data["services"]:
                    service_found = next((config_service for config_service in config_services if config_service["iddef_service"] == id_service), None) 
                    if service_found:
                        service_data = {
                            "description": service_found["service_code"],
                            "iddef_service": id_service,
                            "unit_price": service_found["price"],
                            "quantity": 1,
                            "user": username,
                        }
                        
                        total_gross += service_data["unit_price"] * service_data["quantity"]
                        list_services.append(booking_service.create_extra_service(service_data))
                
                book_hotel.services = list_services

            total_paid = 0
            for room in book_hotel.rooms:
                #get total to pay
                pay_data = booking_service.get_payment_guarantee_by_room(room, booking_currency)
                total_paid += room.amount_to_pay
            
            if data["special_request"] != "":
                book_hotel.comments = [booking_service.create_comment(data["special_request"], book_hotel.usuario_creacion)]

            data["customer"]["address"]["iddef_country"] = country.iddef_country
            data["customer"]["user"] = book_hotel.usuario_creacion
            
            currency = booking_service.get_model_by_code(booking_currency, "currency_code", Currency)
            book_hotel.iddef_currency = currency.iddef_currency
            book_hotel.customers = [booking_service.create_customer(data["customer"])]
            book_hotel.promo_amount = total_voucher
            book_hotel.adults = adults
            book_hotel.child = child
            book_hotel.total_rooms = len(data["rooms"])
            book_hotel.discount_percent = round(total_discount_percent/count_room,2)
            book_hotel.discount_amount = total_discount_amount
            book_hotel.total_gross = total_gross
            book_hotel.fee_amount = 0
            book_hotel.promotion_amount = promotion_amount
            book_hotel.promotions = list_promotion
            book_hotel.country_fee = tax_amount
            book_hotel.amount_pending_payment = total_amount - total_paid
            book_hotel.amount_paid = total_paid
            book_hotel.total = total_amount

            if data["on_hold"]:
                book_hotel.idbook_status = BookStatus.on_hold
                book_hotel.amount_pending_payment = total_amount
                book_hotel.amount_paid = 0
                for room in book_hotel.rooms:
                    room.amount_pending_payment = room.total
                    room.amount_paid = 0
            else:
                book_hotel.idbook_status = BookStatus.on_process
            
            if book_hotel.idbook_status == BookStatus.on_hold:
                date_today = datetime.utcnow()
                book_hotel.expiry_date = booking_service.get_on_hold_exp(date_today,\
                data["property_code"],data["from_date"].date(),\
                data["to_date"].date(),data["rooms"])
            
            book_hotel.code_reservation = ""

            db.session.add(book_hotel)
            db.session.commit()
            
            '''
                TODO: 
                - payment process(done)
                - interface Opera
            '''
            book_hotel.code_reservation = booking_service.get_booking_code(book_hotel.idbook_hotel, book_hotel.iddef_property, book_hotel.idbook_status)
            db.session.commit()

            """ #se valida creacion promo_code
            if not data["on_hold"]:
                if generate_vaucher is True:
                    promotion = list(filter(lambda elem: elem["free"][0]["type"] ==3 if len(elem["free"])> 0 else False,promotions_rooms))
                    try:
                        #format promo_code
                        format_promo_code = BookingPromo.booking_create_promocode(book_hotel,\
                        promotion,room_selected)
                        #create promo_code
                        promocode = FunctionVoucher.create_promocodes(format_promo_code,0,user_name=book_hotel.usuario_creacion)

                    except Exception as err:
                        #raise Exception("Error promocode: "+str(err))
                        pass """

            change_status = False
            if not data["on_hold"]:
                payment_data = {
                    "currency_code": currency.currency_code,
                    "card_number": data["payment"]["card_number"],
                    "cvv": data["payment"]["cvv"],
                    "expirity_month": data["payment"]["exp_month"],
                    "expirity_year": data["payment"]["exp_year"],
                    "holder_first_name": data["payment"]["holder_first_name"],
                    "holder_last_name": data["payment"]["holder_last_name"],
                    #"payment_method": PaymentMethod.credit,
                    "card_type_code_fin": payment_info.code_fin,
                    "card_type_code": payment_info.code,
                    "user": book_hotel.usuario_creacion
                }

                payment_service = PaymentService()
                payment_response = payment_service.confirm_payment(book_hotel, payment_data)               
                
                if payment_response["error"]:
                    booking_service.delete_booking(book_hotel, username)
                    raise Exception(Util.t(data["lang_code"], "payment_unprocessed"))
                else:
                    book_hotel.idbook_status = BookStatus.confirmed
                    db.session.add(book_hotel)
                    db.session.commit()
                    #call celery function to send reservation to PMS by sqs
                    #BookingTask.interface_booking(book_hotel.idbook_hotel)
                    booking_service.create_booking(book_hotel=book_hotel,username=username)
                    change_status = True
                    #Mandamos al sistema de cobros de wire y creamos registro payment transaction
                    payment_config = payment_service.payment_auto_charge(self,book_hotel,payment_data)

            #update Inventory
            """
            for date_elem in BookingPublic.daterange(book_hotel.from_date,book_hotel.to_date):
                for room_element in list_rooms:
                    result_inventory = Inventory.manage_inventory(roomid=room_element.iddef_room_type,date_start=date_elem,date_end=date_elem,
                        propertyid=book_hotel.iddef_property)
            """
            if change_status:
                book_hotel.idbook_status = BookStatus.confirmed
            
            #book_hotel.code_reservation = booking_service.get_booking_code(book_hotel.idbook_hotel, book_hotel.iddef_property, book_hotel.idbook_status)
            book_status = booking_service.get_model_by_id(book_hotel.idbook_status, BookStatus)
            book_hotel.status = book_status.name
            book_hotel.payment_currency = currency.currency_code

            total_service = 0
            if len(book_hotel.services) > 0:
                for service in book_hotel.services:
                    if service.estado == 1:
                        total_service += service.total
            book_hotel.total_service = total_service
            
            #call celery function to send email by sqs
            #BookingTask.send_notification(book_hotel.idbook_hotel, book_hotel.usuario_creacion)

            #sending confirmation or on hold email
            booking_data = booking_service.format_booking_info(book_hotel)
            email_template = EmailTemplate()
            subject = email_template.getSubject(booking_data, booking_data["lang_code"])
            email_data = {
                "email_list": book_hotel.customers[0].customer.email,
                "sender": booking_data["sender"],
                "group_validation": False,
                "html": email_template.get(booking_data),
                "email_subject": subject
            }
            files = []
            status = False

            if book_hotel.idbook_status == BookStatus.confirmed:
                files = CartaUtil.get_welcome_letter_file(data["property_code"], data["lang_code"])
                status = True

            
            Util.send_notification_attachment(email_data, email_template.email_tag, book_hotel.usuario_creacion, files)            

            if base.environment == "pro":
                #retrieve email cc to send a email copy
                email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                email_data["email_list"] = email_cc
                if status:
                    files = CartaUtil.get_welcome_letter_file(data["property_code"], data["lang_code"])

                Util.send_notification_attachment(email_data, email_template.email_tag, book_hotel.usuario_creacion, files)
            
            #schema override to dump specific fields
            schema = ModelSchema(only=["code_reservation", "status", "idbook_status", "total", "country_fee", "total_service", "expiry_date", "payment_currency"])

            response = {
                "Code": 200,
                "Msg": message,
                "Error": False,
                "data": schema.dump(book_hotel)
            }
        except ValidationError as error:
            db.session.rollback()
            message = Util.find_nested_error_message(error.messages)
            response = {
                "Code": 500,
                "Msg": message,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

    @PublicAuth.access_middleware
    def put(self, code_reservation):
        response = {}
        prev_booking = None
        new_booking = None
        actual_id_booking = 0
        confirmed_booking = False
        try:
            json_data = request.get_json(force=True)
            schema = ModelSchema(exclude=Util.get_default_excludes())
            request_data = schema.load(json_data)
            booking_service = BookingService()
            device_request = Util.get_device_request(request.user_agent.string)

            #get api-key data
            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            iddef_channel = credential_data.iddef_channel
            
            if request_data["from_date"] <= datetime.today():
                raise Exception(Util.t(request_data["lang_code"], "booking_today_greater_date"))

            if request_data["from_date"] > request_data["to_date"]:
                raise Exception(Util.t(request_data["lang_code"], "booking_from_date_greater_to_date"))

            if len(request_data["rooms"]) == 0:
                raise Exception(Util.t(request_data["lang_code"], "booking_rooms_required"))

            if not request_data["on_hold"]:
                payment_info = booking_service.get_payment_codes(request_data["payment"])
            else:
                raise Exception(Util.t(request_data["lang_code"], "booking_not_save_hold"))

            request_data["nights"] = (request_data["to_date"] - request_data["from_date"]).days
            request_data["user"] = username
            #market_segment = booking_service.get_model_by_code(request_data["market_code"], "code", MarketSegment)
            language = booking_service.get_model_by_code(request_data["lang_code"], "lang_code", Languaje)
            country = booking_service.get_model_by_code(request_data["customer"]["address"]["country_code"], "country_code", Country)
            currency_user = booking_service.get_model_by_code(request_data["currency_code"], "currency_code", Currency)
            exchange_rate = ExchangeRateService.get_exchange_rate_date(date.today(), request_data["currency_code"])          
            
            exchange_rate_amount = 1
            #Para el mercado de México se cobra siempre en MXN, para resto de los mercados USD
            if request_data["market_code"] == "MX":
                request_data["currency_code"] = "MXN"
                exchange_rate_user = ExchangeRateService.get_exchange_rate_date(date.today(), request_data["currency_code"])
                if exchange_rate_user:
                    exchange_rate_amount = exchange_rate_user.amount
            else:
                request_data["currency_code"] = "USD"            
            
            book_hotel = booking_service.get_booking_by_code(code_reservation, "", request_data["lang_code"])
            prev_booking = book_hotel

            if book_hotel is None:
                raise Exception(Util.t(request_data["lang_code"], "booking_code_not_found", code_reservation))

            if book_hotel.idbook_status != BookStatus.on_hold:
                raise Exception(Util.t(request_data["lang_code"], "booking_reservation_not_on_hold", code_reservation))
                                    
            if datetime.utcnow() > book_hotel.expiry_date:
                raise Exception(Util.t(request_data["lang_code"], "booking_on_hold_expired"))

            #Se sustituye el book hotel anterior por uno nuevo, el anterior se quedará como log
            book_hotel, list_info_id_rooms = BookingOperation.create_book_hotel_copy(book_hotel, username)
            actual_id_booking = book_hotel.idbook_hotel
            new_booking = book_hotel

            #book_hotel.iddef_market_segment = market_segment.iddef_market_segment
            book_hotel.iddef_language = language.iddef_language
            book_hotel.iddef_currency_user = currency_user.iddef_currency
            #book_hotel.iddef_channel = request_data["iddef_channel"]
            book_hotel.exchange_rate = exchange_rate_amount
            book_hotel.device_request = device_request
            #new_rooms = list(filter(lambda room: room["idbook_hotel_room"] == 0, request_data["rooms"]))
            age_range_data = booking_service.get_ages_ranges_list(book_hotel.iddef_property)
            booking_currency = request_data["currency_code"]

            #info previous
            previous_from_date = book_hotel.from_date
            previous_to_date = book_hotel.to_date
            previous_iddef_property = book_hotel.iddef_property
            previous_rooms = []
            for room in book_hotel.rooms:
                if room.estado == 1:
                    previous_rooms.append(room)
                room.estado = 0
                room.usuario_ultima_modificacion = username

            rateplan_list = []
            rooms_list = []
            data_rates = []
            rates_original = []
            total_voucher = 0
            room_order = 0
            #saving new rooms
            for room_data in request_data["rooms"]:
                #obtenemos ids_rateplan
                rateplan_list.append(room_data["idop_rate_plan"])
                rooms_list.append(room_data["iddef_room_type"])
                    
                room_data["property_code"] = request_data["property_code"]
                room_data["iddef_property"] = book_hotel.iddef_property
                room_data["from_date"] =request_data["from_date"]
                room_data["to_date"] = request_data["to_date"]
                room_data["currency"] = booking_currency
                room_data["iddef_market"] = book_hotel.iddef_market_segment
                room_data["country_code"] = request_data["market_code"]
                
                rates_room = RatesFunctions.getPricePerDay(room_data["iddef_property"], room_data["iddef_room_type"], \
                room_data["idop_rate_plan"], room_data["from_date"], room_data["to_date"], currency=room_data["currency"],\
                use_booking_window=True, market=room_data["iddef_market"], country=room_data["country_code"],pax_room=room_data["pax"])
                room_order += 1
                rates_room["room_order"] = room_order
                rates_room["rate_amount"] = rates_room["total"]
                rates_original.append(copy.deepcopy(rates_room))
            
            data_rates = rates_original

            #if apply promotions by free_room
            for promotion in book_hotel.promotions:
                promotion.estado = 0
                promotion.usuario_ultima_modificacion = username

            promotions_rooms = RatesFunctions.get_promotions_by_booking(date_start=request_data["from_date"].date(), 
            date_end=request_data["to_date"].date(), market=request_data["market_code"],hotel=request_data["property_code"],\
            total_rooms=request_data["rooms"])
            if len(promotions_rooms) > 0:
                rate_list_aux = []
                for promo in promotions_rooms:
                    rate_list_promotion = copy.deepcopy(data_rates)
                    promo_list = []
                    promo_list.append(promo)

                    aux_rate = RatesFunctions.apply_promotion(rate_list_promotion,\
                    promo_list)

                    rate_list_aux.append(copy.deepcopy(aux_rate["Prices"]))

                cont_room = 0
                list_end = []
                """ generate_vaucher = False
                cont_applies = 0
                room_selected = None
                cont_room_select = 0 """
                for room_item in request_data["rooms"]:
                    
                    room_version = []
                    for price_version in rate_list_aux:
                        room_version.append(copy.deepcopy(price_version[cont_room]))

                    rates_aux = RatesFunctions.select_rates_promotion(room_version)
                    list_end.append(copy.deepcopy(rates_aux))
                    
                    price_total = RatesFunctions.calcualte_total(rates_aux)

                    """ if rates_aux["apply_room_free"] == True:
                        cont_applies += 1
                        if price_total["total"] > 0 and cont_room_select < 1:
                            room_selected = rates_aux
                            cont_room_select += 1

                    if cont_applies % 2 != 0:
                        generate_vaucher = True
                    else:
                        generate_vaucher = False """

                    cont_room += 1
                
                list_end.sort(key=lambda x: x["room_order"])

                data_rates = list_end
            
            #if apply tax
            price_tax = RatesFunctions.get_price_with_policy_tax(request_data["from_date"].date(),\
            request_data["to_date"].date(),request_data["currency_code"], data_rates)
            data_rates = price_tax["data"]
            tax_amount = price_tax["total_tax"]
            price_total = RatesFunctions.calcualte_total_rates(data_rates)

            #appy crossout
            data_rates = RatesFunctions.apply_crossout_list(data_rates,\
            book_hotel.iddef_market_segment,request_data["market_code"],True)
            price_total = RatesFunctions.calcualte_total_rates(data_rates)
            
            #if apply promo_code
            vaucherApplied = False
            is_text = 0

            for promo in book_hotel.promo_codes:
                promo.estado = 0
                promo.usuario_ultima_modificacion = username

            if request_data["promo_code"] != "":
                try:
                    date_now = datetime.now().date()
                    vauchers = FunctionVoucher.getValidatePromoCode(request_data["promo_code"],\
                    property_code=request_data["property_code"],travel_window_start=request_data["from_date"].date(),\
                    travel_window_end=request_data["to_date"].date(),rateplans=rateplan_list,rooms=rooms_list,\
                    market=book_hotel.iddef_market_segment,lang_code=request_data["lang_code"])

                    vaucher_applied = RatesFunctions.apply_vauchers(data_rates,vauchers,\
                    request_data["currency_code"],date_now)

                    data_rates = vaucher_applied["Prices"]
                    total_voucher = round(vaucher_applied["Subtotal"],4)
                    vaucherApplied = vaucher_applied["vaucher_applied"]

                    is_text = 0
                    if vauchers != None:
                        if vauchers["text_only"] is True:
                            is_text = 1
                        
                        book_hotel.promo_codes += [booking_service.create_promo_code(is_text,request_data["promo_code"], vaucher_applied["Subtotal"], vauchers["type_amount"], book_hotel.usuario_creacion)]
                
                except Exception as vaucher_error:
                    pass

            #crear room
            list_rooms = []
            list_services = []
            total_discount_amount = 0
            total_gross = 0
            total_amount = 0
            total_discount_percent = 0
            adults = 0
            child = 0
            promotion_amount = 0
            tax_amount = 0
            list_promotion = []
            count_room = 0
            num = 0
            for room_data in request_data["rooms"]:
                num += 1
                #iterate the pax values
                pax_list = []
                room_adults = 0
                room_child = 0
                validate_pax_code = True
                for key, value in room_data["pax"].items():
                    iddef_age_range = 0

                    if key == "adults":
                        room_adults = value
                    else:
                        room_child += value

                    if validate_pax_code == True:
                        #looking for the iddef_age_code & validate if exists the code in the property config age_range
                        iddef_age_range = next((item["iddef_age_range"] for item in age_range_data\
                            if item["age_range_age_code"]["code"] == key), None)
                        
                        if iddef_age_range is None:
                            raise Exception("Pax code \"{}\" not exists in the property configuration".format(key))
                    
                    pax_data = {
                        "iddef_age_range": iddef_age_range,
                        "age_code": key,
                        "pax": value,
                        "user": username
                    }

                    pax_list.append(booking_service.create_pax_room(pax_data))
                #validate rates plan currency, must be the same currency
                rate_plan = booking_service.get_model_by_id(room_data["idop_rate_plan"], RatePlan)                

                
                room_data["iddef_room_type"] = room_data["iddef_room_type"]
                room_data["idop_rateplan"] = rate_plan.idop_rateplan
                room_data["rateplan_is_refundable"] = rate_plan.refundable
                room_data["user"] = username
                room_data["paxes"] = pax_list
                room_data["adults"] = room_adults
                room_data["child"] = room_child
                for rate in data_rates:
                    if num == rate["room_order"]:
                        room_data["total"] = rate["total"]
                        room_data["rate_amount"] = rate["rate_amount"]
                        room_data["discount_percent"] = round(rate["total_percent_discount"], 2)
                        room_data["discount_amount"] = round(rate["total_crossout"] - rate["total"], 4)
                        room_data["total_gross"] = rate["total_crossout"]
                        room_data["price_per_day"] = rate["price_per_day"]
                        room_data["vaucher_applied"] = rate["vaucher_applied"]
                        room = booking_service.create_room(room_data,request_data["promo_code"],vaucherApplied=vaucherApplied,is_text=is_text)
                        count_room += 1
                        total_discount_amount += room.discount_amount
                        total_gross += room.total_gross
                        total_amount += room.total
                        total_discount_percent += room.discount_percent
                        adults += room.adults
                        child += room.child
                        promotion_amount += room.promotion_amount
                        tax_amount += room.country_fee
                        #list_rooms.append(room)
                        book_hotel.rooms.append(room)

            #if apply promotions, promotions save
            if promotion_amount > 0:
                list_aux = []
                for itm_room in book_hotel.rooms:
                    for itm_price in itm_room.prices:
                        if itm_price.code_promotions not in list_aux:
                            list_aux.append(itm_price.code_promotions)
                            promotion = RatesFunctions.get_promotions(code=itm_price.code_promotions)
                            if promotion and len(promotion) > 0:
                                idop_promotion = promotion[0]["idop_promotions"]
                                promotion_data = {
                                    "idop_promotions": idop_promotion,
                                    "user": book_hotel.usuario_creacion
                                }
                                list_promotion.append(booking_service.create_promotion(promotion_data))
                        
            book_hotel.promotions += list_promotion
            
            for service in book_hotel.services:
                service.estado = 0
                service.usuario_ultima_modificacion = username
            
            #if add services, valid exists config. services and save
            FunctionService = FunctionsService()
            if request_data["services"]:
                config_services = FunctionService.get_service_by_additional(request_data["services"],request_data["from_date"], request_data["to_date"], book_hotel.iddef_market_segment,\
                    book_hotel.property.iddef_property, len(request_data["rooms"]), (adults + child), request_data["market_code"])
                
                for id_service in request_data["services"]:
                    service_found = next((config_service for config_service in config_services if config_service["iddef_service"] == id_service), None) 
                    if service_found:
                        service_data = {
                            "description": service_found["service_code"],
                            "iddef_service": id_service,
                            "unit_price": service_found["price"],
                            "quantity": 1,
                            "user": username,
                        }
                        
                        total_gross += service_data["unit_price"] * service_data["quantity"]
                        list_services.append(booking_service.create_extra_service(service_data))                    
                
                book_hotel.services += list_services
            
            total_paid = 0
            
            #if exists in book_hotel update the first else create
            if request_data["special_request"] != "":
                if book_hotel.comments:
                    book_hotel.comments[0].text = request_data["special_request"]
                    book_hotel.comments[0].usuario_ultima_modificacion = username
                    book_hotel.comments[0].estado = 0
                    book_hotel.comments.append(booking_service.create_comment(request_data["special_request"], username))
                else:
                    book_hotel.comments = [booking_service.create_comment(request_data["special_request"], username)]
            
            customer_data = request_data["customer"]
            #update customer
            book_hotel.customers[0].customer.title = customer_data["title"]
            book_hotel.customers[0].customer.first_name = customer_data["first_name"]
            book_hotel.customers[0].customer.last_name = customer_data["last_name"]
            book_hotel.customers[0].customer.dialling_code = customer_data["dialling_code"]
            book_hotel.customers[0].customer.phone_number = customer_data["phone_number"]
            book_hotel.customers[0].customer.email = customer_data["email"]
            book_hotel.customers[0].customer.birthdate = customer_data["birthdate"]
            book_hotel.customers[0].customer.company = customer_data["company"]
            book_hotel.customers[0].customer.usuario_ultima_modificacion = username
            #update customer address
            book_hotel.customers[0].customer.address.city = customer_data["address"]["city"]
            book_hotel.customers[0].customer.address.iddef_country = country.iddef_country
            book_hotel.customers[0].customer.address.address = customer_data["address"]["address"]
            book_hotel.customers[0].customer.address.street = customer_data["address"]["street"]
            book_hotel.customers[0].customer.address.state = customer_data["address"]["state"]
            book_hotel.customers[0].customer.address.zip_code = customer_data["address"]["zip_code"]
            book_hotel.customers[0].customer.address.usuario_ultima_modificacion = username
            
            currency = booking_service.get_model_by_code(booking_currency, "currency_code", Currency)
            book_hotel.iddef_currency = currency.iddef_currency
            book_hotel.promo_amount = total_voucher
            book_hotel.from_date = request_data["from_date"]
            book_hotel.to_date = request_data["to_date"]
            book_hotel.nights = request_data["nights"]
            book_hotel.usuario_ultima_modificacion = username
            book_hotel.adults = adults
            book_hotel.child = child
            book_hotel.promotion_amount = promotion_amount
            book_hotel.total_rooms = len(request_data["rooms"])
            book_hotel.discount_percent = round(total_discount_percent/count_room,2)
            book_hotel.discount_amount = total_discount_amount
            book_hotel.total_gross = total_gross
            #book_hotel.fee_amount = 0
            book_hotel.country_fee = tax_amount
            book_hotel.amount_pending_payment = total_amount - total_paid
            book_hotel.amount_paid = total_paid
            book_hotel.total = total_amount
            #book_hotel.idbook_status = BookStatus.confirmed

            db.session.add(book_hotel)
            db.session.commit()

            for room in book_hotel.rooms:
                if room.estado == 1:
                    #get total to pay
                    pay_data = booking_service.get_payment_guarantee_by_room(room, booking_currency)
                    total_paid += room.amount_to_pay

            """ #se valida creacion promo_code
            if not request_data["on_hold"]:
                if generate_vaucher is True:
                    promotion = list(filter(lambda elem: elem["free"][0]["type"] ==3 if len(elem["free"])> 0 else False,promotions_rooms))
                    try:
                        #format promo_code
                        format_promo_code = BookingPromo.booking_create_promocode(book_hotel,\
                        promotion,room_selected)
                        #create promo_code
                        promocode = FunctionVoucher.create_promocodes(format_promo_code,0,user_name=book_hotel.usuario_creacion)

                    except Exception as err:
                        pass """
            
            '''
                TODO: 
                - payment process(done)
                - interface Opera
            '''
            if not request_data["on_hold"]:
                currency = booking_service.get_model_by_code(booking_currency, "currency_code", Currency)
                payment_data = {
                    "currency_code": currency.currency_code,
                    "card_number": request_data["payment"]["card_number"],
                    "cvv": request_data["payment"]["cvv"],
                    "expirity_month": request_data["payment"]["exp_month"],
                    "expirity_year": request_data["payment"]["exp_year"],
                    "holder_first_name": request_data["payment"]["holder_first_name"],
                    "holder_last_name": request_data["payment"]["holder_last_name"],
                    "payment_method": PaymentMethod.credit,
                    "card_type_code_fin": payment_info.code_fin,
                    "card_type_code": payment_info.code,
                    "user": username
                }

                payment_service = PaymentService()
                payment_response = payment_service.confirm_payment(book_hotel, payment_data)
                #book_hotel.code_reservation = booking_service.get_booking_code(book_hotel.idbook_hotel, book_hotel.iddef_property, book_hotel.idbook_status)
                
                if payment_response["error"]:
                    booking_service.delete_booking(book_hotel, username)
                    raise Exception(Util.t(request_data["lang_code"], "payment_unprocessed"))
                else:
                    book_hotel.amount_pending_payment = total_amount - total_paid
                    book_hotel.amount_paid = total_paid
                    book_hotel.idbook_status = BookStatus.confirmed
                    db.session.add(book_hotel)
                    db.session.commit()
                    confirmed_booking = True

                    booking_service.create_booking(book_hotel=book_hotel)
                    
                    #Mandamos al sistema de cobros de wire y creamos registro payment transaction
                    payment_config = payment_service.payment_auto_charge(self,book_hotel,payment_data)

                    #update Inventory - add avail_rooms for previous booking
                    """
                    for previous_date_elem in BookingPublic.daterange(previous_from_date,previous_to_date):
                        for room_previous_element in previous_rooms:
                            result_inventory = Inventory.manage_inventory(roomid=room_previous_element.iddef_room_type,date_start=previous_date_elem,date_end=previous_date_elem,
                                propertyid=previous_iddef_property,add_to_inventory=True)
                    """
                    #update Inventory - remove avail_rooms for booking paid
                    """
                    for date_elem in BookingPublic.daterange(book_hotel.from_date,book_hotel.to_date):
                        for room_element in list_rooms:
                            result_inventory = Inventory.manage_inventory(roomid=room_element.iddef_room_type,date_start=date_elem,date_end=date_elem,
                                propertyid=book_hotel.iddef_property)
                    """
                    
                    #sending confirmation or on hold email
                    book_hotel.idbook_status = BookStatus.confirmed
                    booking_data = booking_service.format_booking_info(book_hotel)
                    email_template = EmailTemplate()
                    subject = email_template.getSubject(booking_data, booking_data["lang_code"])
                    email_data = {
                        "email_list": book_hotel.customers[0].customer.email,
                        "sender": booking_data["sender"],
                        "group_validation": False,
                        "html": email_template.get(booking_data),
                        "email_subject": subject
                    }
                    files = CartaUtil.get_welcome_letter_file(booking_data["property_code"], booking_data["lang_code"])
                    
                    Util.send_notification_attachment(email_data, email_template.email_tag, book_hotel.usuario_creacion, files)

                    if base.environment == "pro":
                        #retrieve email cc to send a email copy
                        email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                        email_data["email_list"] = email_cc
                        Util.send_notification_attachment(email_data, email_template.email_tag, book_hotel.usuario_creacion, files)
                    
            #book_hotel.code_reservation = booking_service.get_booking_code(book_hotel.idbook_hotel, book_hotel.iddef_property, book_hotel.idbook_status)
            book_status = booking_service.get_model_by_id(book_hotel.idbook_status, BookStatus)
            book_hotel.status = book_status.name
            
            total_service = 0
            if len(book_hotel.services) > 0:
                for service in book_hotel.services:
                    if service.estado == 1:
                        total_service += service.total
            book_hotel.total_service = total_service

            #schema override to dump specific fields
            schema = ModelSchema(only=["code_reservation", "status", "idbook_status", "total", "country_fee", "total_service", "expiry_date"])

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": schema.dump(book_hotel)
            }
        except ValidationError as error:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": error.messages,
                "Error": True,
                "data": {}
            }
        except Exception as e:
            db.session.rollback()

            if actual_id_booking > 0 and not confirmed_booking:
                try:
                    prev_booking.estado = 1
                    new_booking.estado = 0
                    db.session.commit()
                except Exception as e:
                    pass

            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days+1)):
            yield start_date + timedelta(n)

class BookingPublicValidate(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {}
        try:
            json_data = request.get_json(force=True)
            schema = BookHotelValidateModelSchema()
            data = schema.load(json_data)
            booking_service = BookingService()

            adults, child = 0, 0
            result = {
                "duplicate": False,
                "code_reservation": ""
            }

            today = datetime.now()
            config_param = booking_service.get_config_param_one("interval_looking_duplicate") 
            config_mins = config_param.value  if config_param else 5
            diff_today = today - timedelta(minutes=int(config_mins))
            today = today.strftime("%Y-%m-%d %H:%M:%S")
            diff_today = diff_today.strftime("%Y-%m-%d %H:%M:%S")
            total_rooms = len(data["rooms"])
            market_segment = RatesFunctions.getMarketInfo(data["market_code"],data["lang_code"])
            iddef_market_segment = market_segment.iddef_market_segment
            language = booking_service.get_model_by_code(data["lang_code"], "lang_code", Languaje)
            iddef_language = language.iddef_language
            currency_user = booking_service.get_model_by_code(data["currency_code"], "currency_code", Currency)
            iddef_currency_user = currency_user.iddef_currency
            property = booking_service.get_model_by_code(data["property_code"], "property_code", Property)
            iddef_property = property.iddef_property
            for room in data["rooms"]:
                for key, value in room["pax"].items():
                    if key == "adults":
                        adults += value
                    else:
                        child += value
            query = """            
                SELECT
                t.code_reservation
                FROM book_hotel t
                INNER JOIN book_hotel_room r ON r.idbook_hotel = t.idbook_hotel
                INNER JOIN book_customer_hotel ch ON ch.idbook_hotel = t.idbook_hotel
                INNER JOIN book_customer c ON c.idbook_customer = ch.idbook_customer
                WHERE
                t.from_date = "{from_date}"
                AND t.to_date = "{to_date}"
                AND t.iddef_property = {iddef_property}
                AND t.adults = {adults}
                AND t.child = {child}
                AND t.total_rooms = {total_rooms}
                AND t.iddef_market_segment = {iddef_market_segment}
                AND t.iddef_language = {iddef_language}
                AND t.iddef_currency_user = {iddef_currency_user}
                AND c.first_name = "{first_name}"
                AND c.last_name = "{last_name}"
                AND c.phone_number = "{phone_number}"
                AND c.email = "{email}"
                AND t.estado = 1
                AND t.idbook_status !=2
                AND CONVERT_TZ(t.fecha_creacion, '+00:00', '-05:00') BETWEEN "{diff_today}" AND "{today}"
                ORDER BY
                t.idbook_hotel DESC LIMIT 1;
                """.format(from_date = data["from_date"].date(), to_date = data["to_date"].date(),\
                    iddef_property = iddef_property, adults = adults,child = child,\
                    total_rooms = total_rooms, iddef_market_segment = iddef_market_segment,\
                    iddef_language = iddef_language, iddef_currency_user = iddef_currency_user,\
                    first_name = data["customer"]["first_name"], last_name = data["customer"]["last_name"],
                    phone_number = data["customer"]["phone_number"], email=data["customer"]["email"],
                    today = today, diff_today= diff_today)
            
            book_hotel = db.session.execute(query)
            
            for item in book_hotel:
                result = {
                    "duplicate": True,
                    "code_reservation": item.code_reservation
                }

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": result
            }
        except Exception as e:
            db.session.rollback()
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

class ConfirmationPublic(Resource):
    @PublicAuth.access_middleware
    def post(self):
        response = {
            "Code": 200,
            "Msg": "",
            "Error": False,
            "data": {}
        }

        try:
            json_data = request.get_json(force=True)
            schema = EmailReservationSchema()
            data = schema.load(json_data)
            booking_service = BookingService()

            #get api-key data
            credential_data = PublicAuth.get_credential_data()
            username = credential_data.name
            
            book_hotel = booking_service.get_booking_by_code(data["code_reservation"])

            if book_hotel.idbook_status not in [BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced]:
                raise Exception(Util.t("en", "booking_code_not_found", data["code_reservation"]))
            
            book_hotel.lang_code = book_hotel.language.lang_code
            booking_data = booking_service.format_booking_info(book_hotel)
            email_template = EmailTemplate()
            subject = email_template.getSubject(booking_data, booking_data["lang_code"])
            email_data = {
                "email_list": data["email"],
                "sender": booking_data["sender"],
                "group_validation": False,
                "html": email_template.get(booking_data),
                "email_subject": subject
            }
            service_response = {}
            
            if book_hotel.idbook_status in [BookStatus.confirmed, BookStatus.interfaced, BookStatus.partial_interfaced]:
                files = CartaUtil.get_welcome_letter_file(booking_data["property_code"], booking_data["lang_code"])
                service_response = Util.send_notification_attachment(email_data, email_template.email_tag, username, files)
            else:
                service_response = Util.send_notification(email_data, email_template.email_tag, username)
            
            if service_response["error"]:
                response["Msg"] = "Error sending email"
                response["Error"] = True
            else:
                response["Msg"] = "Confirmation letter was sent"
            
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
    
class Booking(Resource):
    #api-booking-get
    #@base.access_middleware
    def get(self, id):
        response = {}
        try:
            booking_service = BookingService()
            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == id, BookHotel.estado == 1).first()

            if book_hotel is None:
                raise Exception(Util.t("en", "booking_code_not_found", id))
            
            book_hotel.customers[0].customer.address.country_code = book_hotel.customers[0].customer.address.country.country_code
            '''
                format the pax node in rooms
            '''
            services = []
            for room in book_hotel.rooms:
                paxes_code = {}
                
                for pax in room.paxes:
                    paxes_code.update({pax.age_code: pax.total})
                
                room.pax = paxes_code                
                room.trade_name_room = ""            
                #get room category trade name
                text_lang = RatesFunctions.getTextLangInfo("def_room_type_category", "room_name", book_hotel.language.lang_code, room.iddef_room_type)
                if text_lang is not None:
                    room.trade_name_room = text_lang.text
                
                #get cancel policy
                room.polices = []
                cancel_policy = FunctionsPolicy.get_policy_lang(room.iddef_police_cancelation, "en", True)
                if cancel_policy:
                    room.polices = [cancel_policy]
            
            FunctionService = FunctionsService()
            for service in book_hotel.services:
                service_data = FunctionService.get_service_by_lang(service.iddef_service, "en")
                
                if service_data:                    
                    service_info = {
                        "iddef_service": service.iddef_service,
                        "name": service_data["name"],
                        "teaser": service_data["teaser"],
                        "description": service_data["description"]
                    }
                    services.append(service_info)
            
            payment_data = {}
            if book_hotel.idbook_status == BookStatus.confirmed:
                payment = book_hotel.payments[0]
                payment_data["card_type"] = payment.card_code
            
            promotions = []
            data = {
                "iddef_property": book_hotel.iddef_property,
                "trade_name": book_hotel.property.trade_name,
                "from_date": book_hotel.from_date,
                "to_date": book_hotel.to_date,
                "market_code": book_hotel.market_segment.code,
                "iddef_channel": book_hotel.iddef_channel,
                "lang_code": book_hotel.language.lang_code,
                "currency_code": book_hotel.currency.currency_code,
                "promo_code": "",
                "on_hold": book_hotel.idbook_status == BookStatus.on_hold,
                "customer": book_hotel.customers[0].customer,
                "rooms": book_hotel.rooms,
                "code_reservation": booking_service.get_booking_code(book_hotel.idbook_hotel, book_hotel.iddef_property, book_hotel.idbook_status),
                "status": book_hotel.status_item.name,
                "idbook_status": book_hotel.idbook_status,
                "discount_percent": book_hotel.discount_percent,
                "discount_amount": book_hotel.discount_amount, 
                "total_gross": book_hotel.total_gross,
                "total": book_hotel.total,
                "expiry_date": book_hotel.expiry_date if book_hotel.idbook_status == BookStatus.on_hold else None,
                "services_info": services,
                "payment": payment_data,
                "fecha_creacion": book_hotel.fecha_creacion,
                "adults": book_hotel.adults,
                "child": book_hotel.child,
                "nights": book_hotel.nights,
                "comments": book_hotel.comments,
                "promotions": promotions
            }
            
            schema = BookHotelAdminSchema()
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
        
        return response
    
class BookingSearch(Resource):
    #api-booking-get-all
    #@base.access_middleware
    def get(self, iddef_property, idbook_status, code_book_hotel, from_date_travel, to_date_travel,from_date_booking, to_date_booking, limit, offset):
        try:
            if isinstance(code_book_hotel,str):
                if code_book_hotel != "None":
                    iddef_property, idbook_status, from_date_travel, to_date_travel, from_date_booking, to_date_booking = 0, 0, 0, 0, 0, 0
                else:
                    code_book_hotel = 0
                    if isinstance(from_date_travel,str):
                        if from_date_travel == "1900-01-01":
                            from_date_travel = 0
                        else:
                            from_date_travel = datetime.strptime(from_date_travel,'%Y-%m-%d').date()
                    if isinstance(to_date_travel,str):
                        if to_date_travel == "1900-01-01":
                            to_date_travel = 0
                        else:
                            to_date_travel = datetime.strptime(to_date_travel,'%Y-%m-%d').date()
                    if isinstance(from_date_booking,str):
                        if from_date_booking == "1900-01-01":
                            from_date_booking = 0
                        else:
                            from_date_booking = datetime.strptime(from_date_booking,'%Y-%m-%d').date()
                    if isinstance(to_date_booking,str):
                        if to_date_booking == "1900-01-01":
                            to_date_booking = 0
                        else:
                            to_date_booking = datetime.strptime(to_date_booking,'%Y-%m-%d').date()

            limit = 10 if limit == 0 else limit            
            
            data = BookingService.filter_parameter_book_hotel(iddef_property=iddef_property, idbook_status=idbook_status, code_book_hotel=code_book_hotel,
            from_date_travel=from_date_travel,to_date_travel=to_date_travel,from_date_booking=from_date_booking,to_date_booking=to_date_booking,limit=limit, offset=offset)
            
            schema = BookHotelFilterSchema(many=True)

            if data is None:
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
                    "data": schema.dump(data)
                }
        except Exception as e:
            response = {
            "Code": 500,
            "Msg": str(e),
            "Error": True,
            "data": {}
            }

        return response

class BookingSearchTotal(Resource):
    #api-booking-get-count
    #@base.access_middleware
    def get(self, iddef_property, idbook_status, code_book_hotel, from_date_travel, to_date_travel,from_date_booking, to_date_booking):
        try:
            if isinstance(code_book_hotel,str):
                if code_book_hotel != "None":
                    iddef_property, idbook_status, from_date_travel, to_date_travel, from_date_booking, to_date_booking = 0, 0, 0, 0, 0, 0
                else:
                    code_book_hotel = 0
                    if isinstance(from_date_travel,str):
                        if from_date_travel == "1900-01-01":
                            from_date_travel = 0
                        else:
                            from_date_travel = datetime.strptime(from_date_travel,'%Y-%m-%d').date()
                    if isinstance(to_date_travel,str):
                        if to_date_travel == "1900-01-01":
                            to_date_travel = 0
                        else:
                            to_date_travel = datetime.strptime(to_date_travel,'%Y-%m-%d').date()
                    if isinstance(from_date_booking,str):
                        if from_date_booking == "1900-01-01":
                            from_date_booking = 0
                        else:
                            from_date_booking = datetime.strptime(from_date_booking,'%Y-%m-%d').date()
                    if isinstance(to_date_booking,str):
                        if to_date_booking == "1900-01-01":
                            to_date_booking = 0
                        else:
                            to_date_booking = datetime.strptime(to_date_booking,'%Y-%m-%d').date()
            
            total = BookingService.filter_parameter_book_hotel(iddef_property, idbook_status, code_book_hotel,\
            from_date_travel, to_date_travel, from_date_booking, to_date_booking, isCount=True)

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {
                    "total": total
                }
            }
        except Exception as e:
            response = {
            "Code": 500,
            "Msg": str(e),
            "Error": True,
            "data": {}
            }

        return response

class Confirmation(Resource):
    #api-booking-send-confirmation
    #@base.access_middleware
    def post(self, id):
        response = {
            "Code": 200,
            "Msg": "",
            "Error": False,
            "data": {}
        }

        try:
            data_request = request.get_json(force=True)
            user_data = base.get_token_data()
            username = user_data['user']['username']
            booking_service = BookingService()  
            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == id, BookHotel.estado == 1).first()
            
            if book_hotel is None:
                raise Exception(Util.t("en", "booking_not_confirmed"))
                        
            if book_hotel.idbook_status not in [BookStatus.cancel, BookStatus.on_hold, BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced]:
                raise Exception(Util.t("en", "booking_not_confirmed"))

            booking_data = booking_service.format_booking_info(book_hotel)
            email_template = EmailTemplate()
            subject = email_template.getSubject(booking_data, booking_data["lang_code"])
            email_data = {
                "email_list": '',
                "sender": booking_data["sender"],
                "group_validation": False,
                "html": email_template.get(booking_data),
                "email_subject": subject
            }
            files = []
            if book_hotel.idbook_status in [BookStatus.confirmed, BookStatus.interfaced, BookStatus.partial_interfaced]:
                files = CartaUtil.get_welcome_letter_file(booking_data["property_code"], booking_data["lang_code"])
            
            if data_request['is_forward'] == 1 :
                # lista de correos unidos por ;
                array_emails = data_request['email_list']

                if array_emails is not None:
                    emails_forward = ";".join(array_emails)
                    email_data["email_list"] = emails_forward
                    #guardar en tabla de correos reenviados
                    try:
                        schema_forward = ForwardEmailsSchema(exclude=Util.get_default_excludes())
                        model_forward = ForwardEmails()
                        user_data = base.get_token_data()
                        user_name = user_data['user']['username']

                        model_forward.idbook_hotel = book_hotel.idbook_hotel
                        model_forward.reservation = book_hotel.code_reservation
                        model_forward.email = array_emails
                        model_forward.estado = 1
                        model_forward.usuario_creacion = user_name

                        db.session.add(model_forward)
                        db.session.commit()

                        #data_insert = ForwardEmailsSchema.dump(model_forward)
                    
                    except ValidationError as error:
                        db.session.rollback()
                        response = {
                            "Code": 500,
                            "Msg": error.messages,
                            "Error": True,
                            "data": {}
                        }
                    except Exception as e:
                        db.session.rollback()
                        response = {
                            "Code": 500,
                            "Msg": str(e),
                            "Error": True,
                            "data": {}
                        }
                service_response = Util.send_notification_attachment(email_data, email_template.email_tag, username, files)
            
            if base.environment == "pro":
                #retrieve email cc to send a email copy
                email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                email_data["email_list"] = email_cc
                
                service_response = Util.send_notification_attachment(email_data, email_template.email_tag, username, files)
            else: 
                config_param = booking_service.get_config_param_one("internal_emailproperty") 
                email_data["email_list"] = config_param.value  if config_param else ""
                service_response = Util.send_notification_attachment(email_data, email_template.email_tag, username, files)

            if service_response["error"]:
                response["Msg"] = "Error sending email"
                response["Error"] = True
            else:
                response["Msg"] = "Confirmation letter was sent"
            
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class Pms(Resource):
    #api-booking-send-pms
    #@base.access_middleware
    def post(self, id):
        response = {}
        try:
            #user_data = base.get_token_data()
            #username = user_data['user']['username']
            username = "Admin_test"
            booking_service = BookingService()
            #response = booking_service.update_booking(idbook_hotel=id,username=username)
            response = booking_service.create_booking(idbook_hotel=id, username=username)
            response["Code"] = 200            
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response

class BookingDataPdf(Resource):
    @PublicAuth.access_middleware
    def get(self, code_reservation, full_name, language_code):
        response = {}
        try:
            booking_service = BookingService()
            data = booking_service.get_booking_info_by_code(code_reservation, full_name, language_code)

            if data["status_code"] not in [BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced]:
                raise Exception(Util.t(language_code, "booking_code_not_found", code_reservation))
            
            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data
            }
        except Exception as e:
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response
    
class BookingCancel(Resource):
    #api-booking-send-pms
    #@base.access_middleware
    def post(self):
        response = {}
        prev_booking = None
        new_booking = None
        actual_id_booking = 0
        
        try:
            json_data = request.get_json(force=True)
            schema = CancelReservationSchema()
            data = schema.load(json_data)
            booking_service = BookingService()

            user_data = base.get_token_data()
            username = user_data['user']['username']
            date_now = datetime.utcnow()

            book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == data["idbook_hotel"], BookHotel.estado == 1).first()
            prev_booking = book_hotel
            
            property = Property.query.get(data["iddef_property"])
            hotel_code = property.property_code

            #Se sustituye el book hotel anterior por uno nuevo, el anterior se quedará como log
            book_hotel, list_info_id_rooms = BookingOperation.create_book_hotel_copy(book_hotel, username)
            actual_id_booking = book_hotel.idbook_hotel
            new_booking = book_hotel

            cancel_response = booking_service.cancel_booking(book_hotel, hotel_code,\
            book_hotel.idbook_status, username, date_now, data["reason_cancellation"],\
            data["visible_reason_cancellation"])
            response["data"] = cancel_response["data"]
            if cancel_response["error"]:
                response["Code"] = 500
                response["Error"] = True
                response["Msg"] = "Error al cancelar reserva:"+str(data["idbook_hotel"])+", " +str(cancel_response["msg"])
            else:
                response["Code"] = 200
                response["Error"] = False
                response["Msg"] = "Succes"

                try:

                    leatter = BookingLetter.booking_leatter_canceled(book_hotel.code_reservation)

                except Exception as CartaEx:
                    pass #raise Exception ("Error: "+str(CartaEx))
                    
        except Exception as e:
            db.session.rollback()

            if actual_id_booking > 0:
                try:
                    prev_booking.estado = 1
                    new_booking.estado = 0
                    db.session.commit()
                except Exception as e:
                    pass

            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }

        return response