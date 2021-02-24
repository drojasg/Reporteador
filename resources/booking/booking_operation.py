from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
#from sqlalchemy.orm.session import make_transient


from config import db, base
from models.book_hotel import BookHotel, BookHotelReservationChangeSchema as ModelChangeSchema, BookHotelReservationChangeRSchema as ModelChangeRSchema
from models.book_status import BookStatus
from models.book_address import BookAddress
from models.book_customer import BookCustomer
from models.book_customer_hotel import BookCustomerHotel
from models.book_hotel_comment import BookHotelComment
from models.book_promo_code import BookPromoCode
from models.book_extra_service import BookExtraService
from models.book_promotion import BookPromotion
from models.book_hotel_room import BookHotelRoom
from models.book_hotel_room_prices import BookHotelRoomPrices
from models.payment_transaction import PaymentTransaction
from models.payment_transaction_detail import PaymentTransactionDetail
from models.payment_method import PaymentMethod

from models.currency import Currency
from models.country import Country
from models.rateplan import RatePlan
from common.util import Util
from .booking_service import BookingService
from .booking_canceled import BookingLetter
from resources.payment.payment_service import PaymentService
from resources.rates.RatesHelper import RatesFunctions
from resources.exchange_rate.exchange_rate_service import ExchangeRateService
from resources.policy.policyHelper import PolicyFunctions
from resources.service.serviceHelper import Search as FunctionsService
from resources.promo_code.promocodeHelper import PromoCodeFunctions as FunctionVoucher
from resources.property.property_service import PropertyService
import json
#from resources.inventory.inventory import Inventory

class BookingOperation(Resource):
    #@base.access_middleware
    def put(self, code_reservation):
        response = {}
        prev_booking = None
        new_booking = None
        actual_id_booking = 0
        try:
            json_data = request.get_json(force=True)
            schema = ModelChangeSchema(exclude=Util.get_default_excludes())
            #schema_result = ModelChangeRSchema(exclude=Util.get_default_excludes())
            request_data = schema.load(json_data)
            booking_service = BookingService()

            user_data = base.get_token_data()
            username = user_data['user']['username']

            if request_data["from_date"] <= datetime.today():
                raise Exception(Util.t(request_data["lang_code"], "booking_today_greater_date"))

            if request_data["from_date"] > request_data["to_date"]:
                raise Exception(Util.t(request_data["lang_code"], "booking_from_date_greater_to_date"))

            if len(request_data["rooms"]) == 0:
                raise Exception(Util.t(request_data["lang_code"], "booking_rooms_required"))

            if request_data["is_refund"] is False:
                if not request_data["only_save"] and not request_data["external_payment"] and request.json.get("payment") is None:
                    raise Exception("Payment required")

            if request.json.get("payment") != None:
                payment_info = booking_service.get_payment_codes(request_data["payment"])

            request_data["nights"] = (request_data["to_date"] - request_data["from_date"]).days
            request_data["user"] = username

            country = booking_service.get_model_by_code(request_data["customer"]["address"]["country_code"], "country_code", Country)

            book_hotel = BookHotel.query.\
            filter(BookHotel.code_reservation.like(code_reservation), BookHotel.estado == 1).\
            order_by(BookHotel.idbook_hotel.desc()).first()
            prev_booking = book_hotel

            if book_hotel is None:
                raise Exception(Util.t(request_data["lang_code"], "booking_code_not_found", code_reservation))

            #Se sustituye el book hotel anterior por uno nuevo, el anterior se quedará como log
            book_hotel, list_info_id_rooms = BookingOperation.create_book_hotel_copy(book_hotel, username)
            actual_id_booking = book_hotel.idbook_hotel
            new_booking = book_hotel

            #Se comenta para permitir modificaciones posteriores al pago
            # if book_hotel.idbook_status != BookStatus.on_hold:
            #     raise Exception(Util.t(request_data["lang_code"], "booking_reservation_not_on_hold", code_reservation))

            age_range_data = booking_service.get_ages_ranges_list(book_hotel.iddef_property)
            total_discount_amount = 0
            total_gross = 0
            #total_amount = 0
            total_discount_percent = 0
            adults = 0
            child = 0
            promotion_amount = 0
            tax_amount = 0
            booking_currency = ""
            list_services = []
            list_id_promotions = []
            list_promotion = []
            #rooms_promotions = []
            #rateplan_list = []
            #rooms_list = []
            #data_rates = []
            total_voucher = 0
            count_room = 0
            count_rate_fix = 0

            #list_rooms = []
            list_data_rooms = []
            total_to_pay = 0
            #previous_rooms = []
            new_rooms = []
            new_id_rooms = []
            previous_id_book_rooms = []
            # Se comentan debido a que se retiraron los métodos para modificar el inventario
            # previous_from_date = book_hotel.from_date
            # previous_to_date = book_hotel.to_date
            # previous_iddef_property = book_hotel.iddef_property
            #deleted_id_rooms = []
            # deleted_rooms = []
            request_id_rooms = []
            # for room in book_hotel.rooms:
            #     if room.estado == 1 and room.idbook_hotel_room > 0:
            #         previous_id_book_rooms.append(room.idbook_hotel_room)
                    #previous_rooms.append(room)

            #saving new rooms
            for room_data in request_data["rooms"]:
                #validate rates plan currency, must be the same currency
                rate_plan = booking_service.get_model_by_id(room_data["idop_rate_plan"], RatePlan)
                if not booking_currency:
                    booking_currency = rate_plan.currency_code
                elif booking_currency != rate_plan.currency_code:
                    raise Exception(Util.t(request_data["lang_code"], "booking_rate_plan_same_currency", booking_currency))

                room_data["property_code"] = request_data["property_code"]
                room_data["iddef_property"] = book_hotel.iddef_property
                room_data["from_date"] = request_data["from_date"]
                room_data["to_date"] = request_data["to_date"]
                room_data["currency"] = booking_currency
                room_data["idop_rateplan"] = rate_plan.idop_rateplan
                room_data["rateplan_is_refundable"] = rate_plan.refundable
                room_data["iddef_market"] = book_hotel.iddef_market_segment
                room_data["country_code"] = request_data["market_code"]
                room_data["user"] = username

                if not room_data["rates_fix"]:
                    for elem_rate in room_data["rates"]:
                        if "promotions" in elem_rate.keys() and len(elem_rate["promotions"]) > 0:
                            list_id_promotions.append(elem_rate["promotions"]["id_promotion"])
                        if "vaucher_discount" in elem_rate.keys():
                            total_voucher += elem_rate["vaucher_discount"]

                if room_data["idbook_hotel_room"] == 0:
                    room = booking_service.create_room_info(room_data, True, age_range_data)
                    new_rooms.append(room)
                else:
                    obj_id_room = next((item for item in list_info_id_rooms if item["previous_idbook_hotel_room"] == room_data["idbook_hotel_room"]), None)
                    if obj_id_room is None:
                        raise Exception("id_hotel_room not valid")
                    room_model = BookHotelRoom.query.filter(BookHotelRoom.idbook_hotel_room == obj_id_room["new_idbook_hotel_room"]).first()
                    room_data["idbook_hotel_room"] = obj_id_room["new_idbook_hotel_room"]
                    room = booking_service.update_room_info(room_model, room_data, True, age_range_data)
                    request_id_rooms.append(room.idbook_hotel_room)
                ##obtenemos ids_rateplan
                #rateplan_list.append(room.idop_rate_plan)
                ##obtenemos ids_rooms
                #rooms_list.append(room.iddef_room_type)
                count_room += 1
                count_rate_fix += 1 if room_data["rates_fix"] else 0
                total_discount_amount += room.discount_amount
                total_gross += room.total_gross
                #total_amount += room.total
                total_discount_percent += room.discount_percent
                adults += room.adults
                child += room.child
                promotion_amount += room.promotion_amount
                tax_amount += room.country_fee

                # data_price_per_day = []
                # for nigth in room.prices:
                #     rates_nigth = {
                #         "night": 0,
                #         "amount": nigth.total,
                #         "amount_crossout": round(nigth.total + nigth.discount_amount,2),
                #         "percent_discount": nigth.discount_percent,
                #         "efective_date": nigth.date,
                #         "promotion_amount": nigth.promotion_amount,
                #         "country_fee": nigth.country_fee
                #     }
                #     data_price_per_day.append(rates_nigth)

                # rates_room = {
                #     "property":book_hotel.iddef_property,
                #     "room":room.iddef_room_type,
                #     "rateplan":room.idop_rate_plan,
                #     "paxes":0,
                #     "adults":0,
                #     "minors":0,
                #     "nights":0,
                #     "total": room.total,
                #     "total_crossout": room.total_gross,
                #     "price_per_day":data_price_per_day,
                #     "total_percent_discount":room.discount_percent
                # }
                # data_rates.append(rates_room)

                #list_rooms.append(room)
                list_data_rooms.append({"model_room":room, "data":room_data})

                total_to_pay += room_data["total_to_paid_room"]

                # rooms_item_promotions ={
                #     "iddef_room_type": room.iddef_room_type,
                #     "idop_rate_plan": room.idop_rate_plan,
                #     "adults": adults,
                #     "children": child
                # }
                #rooms_promotions.append(rooms_item_promotions)

                if room.idbook_hotel_room not in (previous_id_book_rooms):
                    book_hotel.rooms.append(room)

            #Se eliminan elementos repetidos de la lista de ids de promociones
            list_id_promotions = list(set(list_id_promotions))

            # Se ponen en estado 0 los rooms que no lleguen en el request
            for room_elem in book_hotel.rooms:
                exist = False
                if room_elem.estado == 1:
                    for request_id_room in request_id_rooms:
                        if request_id_room == room_elem.idbook_hotel_room or room_elem in new_rooms:
                            exist = True
                if not exist:
                    #deleted_id_rooms.append(room_elem.idbook_hotel_room)
                    #deleted_rooms.append(room_elem)
                    room_elem.estado = 0
                    room_elem.usuario_ultima_modificacion = username

            for promotion in book_hotel.promotions:
                promotion.estado = 0
                promotion.usuario_ultima_modificacion = username

            #if apply promotions, promotions save
            if promotion_amount > 0 and count_rate_fix < count_room:
                apply_promotions = RatesFunctions.get_promotions(ids_promotion=list_id_promotions)
                for indx_promotion in apply_promotions:
                    promotion_data = {
                        "idop_promotions": indx_promotion["idop_promotions"],
                        "user": book_hotel.usuario_creacion,
                    }
                    list_promotion.append(booking_service.create_promotion(promotion_data))
                        
            book_hotel.promotions += list_promotion

            for service in book_hotel.services:
                service.estado = 0
                service.usuario_ultima_modificacion = username

            #if add services, valid exists config. services and save
            FunctionService = FunctionsService()
            if request_data["services"]:
                config_services = FunctionService.get_service_by_additional([],request_data["from_date"], request_data["to_date"], book_hotel.iddef_market_segment,\
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
                        
                        #total_gross += service_data["unit_price"] * service_data["quantity"]
                        list_services.append(booking_service.create_extra_service(service_data))                    
                
                book_hotel.services += list_services

            for promo in book_hotel.promo_codes:
                promo.estado = 0
                promo.usuario_ultima_modificacion = username

            #if exists in book_hotel update the first else create            
            if request_data["promo_code"] != "" and count_rate_fix < count_room:
                vauchers = FunctionVoucher.search_promocode(request_data["promo_code"])

                if vauchers != None:
                    is_text = True if vauchers.iddef_promo_code_discount_type == 2 else False

                    book_hotel.promo_codes += [booking_service.create_promo_code(is_text,request_data["promo_code"], total_voucher, vauchers.iddef_promo_code_type_amount, username)]
            else:
                total_voucher = 0

            for comment in book_hotel.comments:
                comment.estado = 0
                comment.usuario_ultima_modificacion = username

            # Create comments
            for comment in request_data["comments"]:
                book_hotel.comments.append(booking_service.create_comment(special_request=comment["text"], user=username,
                    visible_to_guest=comment["visible_to_guest"]))

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

            payment_service = PaymentService()
            info_payment = payment_service.get_payment_info(book_hotel.idbook_hotel)
            #total_paid = 0 #Se retira variable debido a que ya no se utiliza en el proceso
            # for room in book_hotel.rooms:
            #     #get total to pay
            #     pay_data = booking_service.get_payment_guarantee_by_room(room)
            #     total_paid += room.amount_to_pay

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
            if not request_data["is_refund"]:
                book_hotel.amount_pending_payment = (book_hotel.amount_pending_payment - (book_hotel.total - request_data["total"])) - total_to_pay #total_paid
                book_hotel.amount_paid = book_hotel.amount_paid + total_to_pay
            else:
                #to_refund = book_hotel.amount_pending_payment - request_data["amound_refund"]
                book_hotel.amount_pending_payment = 0 #to_refund if to_refund > 0 else 0
                book_hotel.last_refund_amount = request_data["amound_refund"]
                book_hotel.amount_paid = book_hotel.amount_paid - request_data["amound_refund"]
            book_hotel.total = request_data["total"]
            #book_hotel.idbook_status = BookStatus.confirmed

            db.session.add(book_hotel)
            db.session.commit()

            new_id_rooms = [new_room.idbook_hotel_room for new_room in new_rooms]

            diff_amount = 0
            transaction_type = 0 #0 = no_change, 1 = payment, 2 = refund
            if not request_data["only_save"]:
                '''
                    TODO: 
                    - payment process(done)
                    - interface Opera
                '''
                if not request_data["external_payment"]:
                    currency = booking_service.get_model_by_code(booking_currency, "currency_code", Currency)
                    payment_data = {
                        "currency_code": currency.currency_code,
                        "payment_method": PaymentMethod.credit,
                        "card_type_code": "",
                        "user": username
                    }

                    payment_service = PaymentService()
                    #sum_payments = payment_service.get_info_sum_payments(book_hotel.idbook_hotel, book_hotel.from_date)["total_paid"]

                    #Nota: Los reembolsos solo se harán sobre el total
                    if not request_data["is_refund"]:
                        payment_data["card_number"] = request_data["payment"]["card_number"]
                        payment_data["cvv"] = request_data["payment"]["cvv"]
                        payment_data["expirity_month"] = request_data["payment"]["exp_month"]
                        payment_data["expirity_year"] = request_data["payment"]["exp_year"]
                        payment_data["holder_first_name"] = request_data["payment"]["holder_first_name"]
                        payment_data["holder_last_name"] = request_data["payment"]["holder_last_name"]
                        payment_data["card_type_code_fin"] = payment_info.code_fin
                        payment_data["card_type_code"] = payment_info.code
                        is_refund = False
                        transaction_type = 1
                        diff_amount = total_to_pay
                    else:
                        is_refund = True
                        transaction_type = 2
                        diff_amount = request_data["amound_refund"]
                    # else:
                    #     payment_response={"error":False}

                    if is_refund:
                        payment_response = payment_service.update_payment_data(book_hotel, payment_data, is_refund, request_data["amound_refund"], list_data_rooms)
                    else:
                        payment_response = payment_service.confirm_payment_update(book_hotel, payment_data, is_refund, total_to_pay, list_data_rooms)

                    if payment_response["error"]:
                        #booking_service.cancel_booking(book_hotel, username)
                        #message = Util.t(request_data["lang_code"], "payment_unprocessed")
                        booking_service.delete_booking(book_hotel, username)
                        raise Exception(Util.t(request_data["lang_code"], "payment_unprocessed"))
                    else:
                        book_hotel.idbook_status = BookStatus.changed
                        book_hotel.modification_date_booking = datetime.utcnow()
                        db.session.add(book_hotel)
                        db.session.commit()
                        booking_service.update_booking(book_hotel=book_hotel, new_id_rooms=new_id_rooms)

                        """
                        if sum_payments == 0 or book_hotel.total == sum_payments:
                            #update Inventory - add avail_rooms for previous booking
                            for previous_date_elem in BookingOperation.daterange(previous_from_date,previous_to_date):
                                for room_deleted_element in deleted_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_deleted_element.iddef_room_type,date_start=previous_date_elem,date_end=previous_date_elem,
                                        propertyid=previous_iddef_property,add_to_inventory=True)

                            #update Inventory - remove avail_rooms for booking paid
                            for date_elem in BookingOperation.daterange(book_hotel.from_date,book_hotel.to_date):
                                for room_element in new_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_element.iddef_room_type,date_start=date_elem,date_end=date_elem,
                                        propertyid=book_hotel.iddef_property)
                        elif is_refund:
                            #update Inventory - add avail_rooms for previous booking
                            for previous_date_elem in BookingOperation.daterange(previous_from_date,previous_to_date):
                                for room_previous_element in deleted_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_previous_element.iddef_room_type,date_start=previous_date_elem,date_end=previous_date_elem,
                                        propertyid=previous_iddef_property,add_to_inventory=True)
                        elif not is_refund:
                            #update Inventory - remove avail_rooms for booking paid
                            for date_elem in BookingOperation.daterange(book_hotel.from_date,book_hotel.to_date):
                                for room_element in new_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_element.iddef_room_type,date_start=date_elem,date_end=date_elem,
                                        propertyid=book_hotel.iddef_property)
                        """

                        #sending confirmation or on hold email

                        # email_data = booking_service.format_booking_letter(book_hotel)
                        # email_data["email_list"] = book_hotel.customers[0].customer.email

                        # Util.send_notification(email_data, email_data["carta"], book_hotel.usuario_creacion)

                        # if base.environment == "pro":
                        #     #retrieve email cc to send a email copy
                        #     email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                        #     email_data["email_list"] = email_cc
                        #     Util.send_notification(email_data, email_data["carta"], book_hotel.usuario_creacion)

                else:
                    currency = booking_service.get_model_by_code(booking_currency, "currency_code", Currency)
                    if request.json.get("payment") != None:
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
                    else:
                        payment_data = {
                            "currency_code": currency.currency_code,
                            "card_number": 0,
                            "cvv": 0,
                            "expirity_month": 0,
                            "expirity_year": 0,
                            "holder_first_name": "",
                            "holder_last_name": "",
                            "payment_method": PaymentMethod.credit,
                            "card_type_code_fin": 0,
                            "card_type_code": "",
                            "user": username
                        }

                    # payment_service = PaymentService()
                    # payment_response = payment_service.confirm_payment_update(book_hotel, payment_data)
                    # book_hotel.code_reservation = booking_service.get_booking_code(book_hotel.idbook_hotel, book_hotel.iddef_property, book_hotel.idbook_status)
                    payment_service = PaymentService()
                    #sum_payments = payment_service.get_sum_payments(book_hotel.idbook_hotel)

                    #Nota: Los reembolsos solo se harán sobre el total
                    if not request_data["is_refund"]:
                        is_refund = False
                        transaction_type = 1
                        diff_amount = total_to_pay
                    else:
                        is_refund = True
                        transaction_type = 2
                        diff_amount = request_data["amound_refund"]
                    # else:
                    #     payment_response={"error":False}

                    if is_refund:
                        payment_response = payment_service.update_payment_data(book_hotel, payment_data, is_refund, request_data["amound_refund"], list_data_rooms)
                    else:
                        payment_response = payment_service.update_payment_data(book_hotel, payment_data, is_refund, total_to_pay, list_data_rooms)

                    if payment_response["error"]:
                        booking_service.delete_booking(book_hotel, username)
                        raise Exception(Util.t(request_data["lang_code"], "payment_unprocessed"))
                    else:
                        book_hotel.idbook_status = BookStatus.changed
                        book_hotel.modification_date_booking = datetime.utcnow()
                        db.session.add(book_hotel)
                        db.session.commit()
                        booking_service.update_booking(book_hotel=book_hotel, new_id_rooms=new_id_rooms)

                        """
                        if sum_payments == 0 or book_hotel.total == sum_payments:
                            #update Inventory - add avail_rooms for previous booking
                            for previous_date_elem in BookingOperation.daterange(previous_from_date,previous_to_date):
                                for room_deleted_element in deleted_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_deleted_element.iddef_room_type,date_start=previous_date_elem,date_end=previous_date_elem,
                                        propertyid=previous_iddef_property,add_to_inventory=True)

                            #update Inventory - remove avail_rooms for booking paid
                            for date_elem in BookingOperation.daterange(book_hotel.from_date,book_hotel.to_date):
                                for room_element in new_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_element.iddef_room_type,date_start=date_elem,date_end=date_elem,
                                        propertyid=book_hotel.iddef_property)
                        elif is_refund:
                            #update Inventory - add avail_rooms for previous booking
                            for previous_date_elem in BookingOperation.daterange(previous_from_date,previous_to_date):
                                for room_previous_element in deleted_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_previous_element.iddef_room_type,date_start=previous_date_elem,date_end=previous_date_elem,
                                        propertyid=previous_iddef_property,add_to_inventory=True)
                        elif not is_refund:
                            #update Inventory - remove avail_rooms for booking paid
                            for date_elem in BookingOperation.daterange(book_hotel.from_date,book_hotel.to_date):
                                for room_element in new_rooms:
                                    result_inventory = Inventory.manage_inventory(roomid=room_element.iddef_room_type,date_start=date_elem,date_end=date_elem,
                                        propertyid=book_hotel.iddef_property)
                        """

                        #sending confirmation or on hold email
                        # email_data = booking_service.format_booking_letter(book_hotel)        
                        # email_data["email_list"] = book_hotel.customers[0].customer.email

                        # Util.send_notification(email_data, email_data["carta"], book_hotel.usuario_creacion)

                        # if base.environment == "pro":
                            # #retrieve email cc to send a email copy
                            # email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                            # email_data["email_list"] = email_cc
                            # Util.send_notification(email_data, email_data["carta"], book_hotel.usuario_creacion)
            else:
                book_hotel.idbook_status = BookStatus.changed
                book_hotel.modification_date_booking = datetime.utcnow()
                db.session.commit()
                booking_service.update_booking(book_hotel=book_hotel, new_id_rooms=new_id_rooms)

            mail_sent = False
            try:
                leatter = BookingLetter.booking_leatter_modification(book_hotel.code_reservation)
                mail_sent = True
            except Exception as CartaEx:
                mail_sent = False

            book_status = booking_service.get_model_by_id(book_hotel.idbook_status, BookStatus)
            book_hotel.status = book_status.name

            #schema override to dump specific fields
            schema = ModelChangeSchema(only=["idbook_hotel", "code_reservation", "status", "idbook_status", "total", "expiry_date"])
            data_result = schema.dump(book_hotel)
            data_result["difference"] = diff_amount
            data_result["transaction_type"] = transaction_type
            data_result["mail_successful"] = mail_sent

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": data_result
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

            if actual_id_booking > 0:
                try:
                    prev_booking.estado = 1
                    new_booking.estado = 0
                    db.session.commit()
                    actual_id_booking = prev_booking.idbook_hotel
                except Exception as e:
                    pass

            response = {
                "Code": 500,
                "Msg": str(e)+"|"+str(actual_id_booking),
                "Error": True,
                "data": {}
            }
        
        return response

    # Return the cloned model saved in data base
    @staticmethod
    def create_book_hotel_copy(book_hotel_model, username):
        # format [{"idbook_hotel_room_prev":1, "idbook_hotel_room_new":2}]
        #list_rooms = [] #Se comenta variable en desuso
        
        model = BookHotel()
        #model.idbook_hotel = book_hotel_model.idbook_hotel
        model.iddef_property = book_hotel_model.iddef_property
        model.code_reservation = book_hotel_model.code_reservation
        model.from_date = book_hotel_model.from_date
        model.to_date = book_hotel_model.to_date
        model.nights = book_hotel_model.nights
        model.adults = book_hotel_model.adults
        model.child = book_hotel_model.child
        model.total_rooms = book_hotel_model.total_rooms
        model.iddef_market_segment = book_hotel_model.iddef_market_segment
        model.iddef_country = book_hotel_model.iddef_country
        model.iddef_language = book_hotel_model.iddef_language
        model.iddef_currency = book_hotel_model.iddef_currency
        model.iddef_currency_user = book_hotel_model.iddef_currency_user
        model.iddef_channel = book_hotel_model.iddef_channel
        model.exchange_rate = book_hotel_model.exchange_rate
        model.promo_amount = book_hotel_model.promo_amount
        model.discount_percent = book_hotel_model.discount_percent
        model.discount_amount = book_hotel_model.discount_amount
        model.total_gross = book_hotel_model.total_gross
        model.fee_amount = book_hotel_model.fee_amount
        model.country_fee = book_hotel_model.country_fee
        model.amount_pending_payment = book_hotel_model.amount_pending_payment
        model.amount_paid = book_hotel_model.amount_paid
        model.total = book_hotel_model.total
        model.promotion_amount = book_hotel_model.promotion_amount
        model.last_refund_amount = book_hotel_model.last_refund_amount
        model.idbook_status = book_hotel_model.idbook_status
        model.device_request = book_hotel_model.device_request
        model.expiry_date = book_hotel_model.expiry_date
        model.cancelation_date = book_hotel_model.cancelation_date
        model.visible_reason_cancellation = book_hotel_model.visible_reason_cancellation
        model.modification_date_booking = datetime.utcnow()
        model.estado = book_hotel_model.estado
        model.usuario_creacion = username
        model.fecha_creacion = book_hotel_model.fecha_creacion

        for book_customer_hotel in book_hotel_model.customers:
            model_customer_hotel = BookCustomerHotel()
            #model_customer_hotel.idbook_customer_hotel = book_customer_hotel.idbook_customer_hotel
            model_customer_hotel.idbook_hotel = book_customer_hotel.idbook_hotel
            model_customer_hotel.idbook_customer = book_customer_hotel.idbook_customer
            model_customer_hotel.is_holder = book_customer_hotel.is_holder
            model_customer_hotel.estado = book_customer_hotel.estado
            model_customer_hotel.usuario_creacion = username

            model_customer = BookCustomer()
            #model_customer.idbook_customer = book_customer_hotel.customer.idbook_customer
            model_customer.title = book_customer_hotel.customer.title
            model_customer.first_name = book_customer_hotel.customer.first_name
            model_customer.last_name = book_customer_hotel.customer.last_name
            model_customer.dialling_code = book_customer_hotel.customer.dialling_code
            model_customer.phone_number = book_customer_hotel.customer.phone_number
            model_customer.email = book_customer_hotel.customer.email
            model_customer.birthdate = book_customer_hotel.customer.birthdate
            model_customer.company = book_customer_hotel.customer.company
            model_customer.id_profile = book_customer_hotel.customer.id_profile
            model_customer.estado = book_customer_hotel.customer.estado
            model_customer.usuario_creacion = username

            model_address = BookAddress()
            #model_address.idbook_address = book_customer_hotel.customer.address.idbook_address
            model_address.idbook_customer = book_customer_hotel.customer.address.idbook_customer
            model_address.city = book_customer_hotel.customer.address.city
            model_address.iddef_country = book_customer_hotel.customer.address.iddef_country
            model_address.address = book_customer_hotel.customer.address.address
            model_address.street = book_customer_hotel.customer.address.street
            model_address.state = book_customer_hotel.customer.address.state
            model_address.zip_code = book_customer_hotel.customer.address.zip_code
            model_address.estado = book_customer_hotel.customer.address.estado
            model_address.usuario_creacion = username

            model_customer.address = model_address
            model_customer_hotel.customer = model_customer
            model.customers.append(model_customer_hotel)

        for book_hotel_comment in book_hotel_model.comments:
            model_comment = BookHotelComment()
            #model_comment.idbook_hotel_comment = book_hotel_comment.idbook_hotel_comment
            model_comment.idbook_hotel = book_hotel_comment.idbook_hotel
            model_comment.text = book_hotel_comment.text
            model_comment.visible_to_guest = book_hotel_comment.visible_to_guest
            model_comment.source = book_hotel_comment.source
            model_comment.estado = book_hotel_comment.estado
            model_comment.usuario_creacion = username

            model.comments.append(model_comment)


        for book_promo_code in book_hotel_model.promo_codes:
            model_promo_code = BookPromoCode()
            model_promo_code.is_text = book_promo_code.is_text
            model_promo_code.promo_code = book_promo_code.promo_code
            model_promo_code.amount = book_promo_code.amount
            model_promo_code.idbook_hotel = book_promo_code.idbook_hotel
            model_promo_code.estado = book_promo_code.estado
            model_promo_code.promo_code_type = book_promo_code.promo_code_type
            model_promo_code.usuario_creacion = username

            model.promo_codes.append(model_promo_code)

        for book_extra_service in book_hotel_model.services:
            model_extra_service = BookExtraService()
            #model_extra_service.idbook_extra_service = book_extra_service.idbook_extra_service
            model_extra_service.description = book_extra_service.description
            model_extra_service.idbook_extra_type = book_extra_service.idbook_extra_type
            model_extra_service.idbook_hotel = book_extra_service.idbook_hotel
            model_extra_service.iddef_service = book_extra_service.iddef_service
            model_extra_service.external_folio = book_extra_service.external_folio
            model_extra_service.unit_price = book_extra_service.unit_price
            model_extra_service.quantity = book_extra_service.quantity
            model_extra_service.total_gross = book_extra_service.total_gross
            model_extra_service.discount_percent = book_extra_service.discount_percent
            model_extra_service.discount_amount = book_extra_service.discount_amount
            model_extra_service.fee_amount = book_extra_service.fee_amount
            model_extra_service.total = book_extra_service.total
            model_extra_service.estado = book_extra_service.estado
            model_extra_service.usuario_creacion = username

            model.services.append(model_extra_service)

        for book_promotion in book_hotel_model.promotions:
            model_promotion = BookPromotion()
            #model_promotion.idbook_promotion = book_promotion.idbook_promotion
            model_promotion.idbook_hotel = book_promotion.idbook_hotel
            model_promotion.idop_promotions = book_promotion.idop_promotions
            model_promotion.estado = book_promotion.estado
            model_promotion.usuario_creacion = username

            model.promotions.append(model_promotion)

        db.session.add(model)
        db.session.flush()

        list_info_id_rooms = []
        for room_elem in book_hotel_model.rooms:
            hotel_room = BookHotelRoom()
            hotel_room.idbook_hotel = model.idbook_hotel
            hotel_room.iddef_room_type = room_elem.iddef_room_type
            hotel_room.idop_rate_plan = room_elem.idop_rate_plan
            hotel_room.adults = room_elem.adults
            hotel_room.child = room_elem.child
            hotel_room.refundable = room_elem.refundable
            hotel_room.iddef_police_tax = room_elem.iddef_police_tax
            hotel_room.iddef_police_guarantee = room_elem.iddef_police_guarantee
            hotel_room.iddef_police_cancelation = room_elem.iddef_police_cancelation
            hotel_room.iddef_pms = room_elem.iddef_pms
            hotel_room.pms_confirm_number = room_elem.pms_confirm_number
            hotel_room.pms_message = room_elem.pms_message
            hotel_room.reason_cancellation = room_elem.reason_cancellation
            hotel_room.rate_amount = room_elem.rate_amount
            hotel_room.promo_amount = room_elem.promo_amount
            hotel_room.discount_percent = room_elem.discount_percent
            hotel_room.discount_amount = room_elem.discount_amount
            hotel_room.total_gross = room_elem.total_gross
            hotel_room.country_fee = room_elem.country_fee
            hotel_room.amount_pending_payment = room_elem.amount_pending_payment
            hotel_room.amount_paid = room_elem.amount_paid
            hotel_room.total = room_elem.total
            hotel_room.promotion_amount = room_elem.promotion_amount
            hotel_room.paxes = room_elem.paxes
            hotel_room.estado = room_elem.estado
            hotel_room.usuario_creacion = username
            for room_price_elem in room_elem.prices:
                hotel_room_price = BookHotelRoomPrices()
                #hotel_room_price.idbook_hotel_room_prices = room_price_elem.idbook_hotel_room_prices
                #hotel_room_price.idbook_hotel_room = room_price_elem.idbook_hotel_room
                hotel_room_price.date = room_price_elem.date
                hotel_room_price.price = room_price_elem.price
                hotel_room_price.price_to_pms = room_price_elem.price_to_pms
                hotel_room_price.promo_amount = room_price_elem.promo_amount
                hotel_room_price.discount_percent = room_price_elem.discount_percent
                hotel_room_price.discount_amount = room_price_elem.discount_amount
                hotel_room_price.total_gross = room_price_elem.total_gross
                hotel_room_price.country_fee = room_price_elem.country_fee
                hotel_room_price.total = room_price_elem.total
                hotel_room_price.promotion_amount = room_price_elem.promotion_amount
                hotel_room_price.code_promotions = room_price_elem.code_promotions
                hotel_room_price.estado = room_price_elem.estado
                hotel_room_price.usuario_creacion = username

                hotel_room.prices.append(hotel_room_price)

            db.session.add(hotel_room)
            db.session.flush()
            list_info_id_rooms.append({
                "previous_idbook_hotel_room":room_elem.idbook_hotel_room,
                "new_idbook_hotel_room": hotel_room.idbook_hotel_room
            })

        for payment_elem in book_hotel_model.payments:
            hotel_payment_transaction = PaymentTransaction()
            #hotel_payment_transaction.idpayment_transaction = payment_elem.idpayment_transaction
            hotel_payment_transaction.idbook_hotel = model.idbook_hotel
            hotel_payment_transaction.idpayment_method = payment_elem.idpayment_method
            hotel_payment_transaction.idpayment_transaction_type = payment_elem.idpayment_transaction_type
            hotel_payment_transaction.card_code = payment_elem.card_code
            hotel_payment_transaction.authorization_code = payment_elem.authorization_code
            hotel_payment_transaction.merchant_code = payment_elem.merchant_code
            hotel_payment_transaction.ticket_code = payment_elem.ticket_code
            hotel_payment_transaction.idfin_payment = payment_elem.idfin_payment
            hotel_payment_transaction.amount = payment_elem.amount
            hotel_payment_transaction.exchange_rate = payment_elem.exchange_rate
            hotel_payment_transaction.currency_code = payment_elem.currency_code
            hotel_payment_transaction.idop_sistema = payment_elem.idop_sistema
            hotel_payment_transaction.external_code = payment_elem.external_code
            hotel_payment_transaction.estado = payment_elem.estado
            hotel_payment_transaction.usuario_creacion = username
            for payment_detail_elem in payment_elem.details:
                obj_id_room = next((item for item in list_info_id_rooms if item["previous_idbook_hotel_room"] == payment_detail_elem.idbook_hotel_room), None)
                if obj_id_room is not None:
                    hotel_payment_transaction_detail = PaymentTransactionDetail()
                    #hotel_payment_transaction_detail.idpayment_transaction_detail = payment_detail_elem.idpayment_transaction_detail
                    hotel_payment_transaction_detail.idpayment_transaction = payment_detail_elem.idpayment_transaction
                    hotel_payment_transaction_detail.idFin = payment_detail_elem.idFin
                    hotel_payment_transaction_detail.amount = payment_detail_elem.amount
                    hotel_payment_transaction_detail.idbook_hotel_room = obj_id_room["new_idbook_hotel_room"]
                    hotel_payment_transaction_detail.interfaced = payment_detail_elem.interfaced
                    hotel_payment_transaction_detail.estado = payment_detail_elem.estado
                    hotel_payment_transaction_detail.usuario_creacion = username
                    hotel_payment_transaction.details.append(hotel_payment_transaction_detail)
            db.session.add(hotel_payment_transaction)
            db.session.flush()

        book_hotel_model.estado = 2 #Historico
        book_hotel_model.usuario_ultima_modificacion = username
        db.session.commit()

        #Se vuelve a realizar la búsqueda para obtener los datos relacionados del modelo por completo
        model = BookHotel.query.filter(BookHotel.idbook_hotel==model.idbook_hotel).first()

        return model, list_info_id_rooms

    # Return the cloned model saved in data base
    # @staticmethod
    # def prev_create_book_hotel_copy(book_hotel_model, username):
    #     # format [{"idbook_hotel_room_prev":1, "idbook_hotel_room_new":2}]
    #     list_rooms = []
    #     previous_book_hotel_id = book_hotel_model.idbook_hotel
    #     make_transient(book_hotel_model)

    #     #Se limpian los ids y se agrega información del usuario
    #     book_hotel_model.idbook_hotel = 0
    #     book_hotel_model.usuario_creacion = username

    #     for customer_hotel_index, customer_hotel_elem in enumerate(book_hotel_model.customers):
    #         make_transient(book_hotel_model.customers[customer_hotel_index])
    #         book_hotel_model.customers[customer_hotel_index].idbook_customer_hotel = 0
    #         book_hotel_model.customers[customer_hotel_index].usuario_creacion = username
    #         make_transient(book_hotel_model.customers[customer_hotel_index].customer)
    #         book_hotel_model.customers[customer_hotel_index].customer.idbook_customer = 0
    #         book_hotel_model.customers[customer_hotel_index].customer.usuario_creacion = username

    #     for comment_index, comment_elem in enumerate(book_hotel_model.comments):
    #         make_transient(book_hotel_model.comments[comment_index])
    #         book_hotel_model.comments[comment_index].idbook_hotel_comment = 0
    #         book_hotel_model.comments[comment_index].usuario_creacion = username

    #     for promo_code_index, promo_code_elem in enumerate(book_hotel_model.promo_codes):
    #         make_transient(book_hotel_model.promo_codes[promo_code_index])
    #         book_hotel_model.promo_codes[promo_code_index].idbook_promo_code = 0
    #         book_hotel_model.promo_codes[promo_code_index].usuario_creacion = username

    #     temp_rooms = book_hotel_model.rooms
    #     for room_index, room_elem in enumerate(book_hotel_model.rooms):
    #         make_transient(book_hotel_model.rooms[room_index])
    #     book_hotel_model.rooms = []
    #     # for room_index, room_elem in enumerate(book_hotel_model.rooms):
    #     #     book_hotel_model.rooms[room_index].idbook_hotel_room = 0
    #     #     book_hotel_model.rooms[room_index].usuario_creacion = username

    #     for service_index, service_elem in enumerate(book_hotel_model.services):
    #         make_transient(book_hotel_model.services[service_index])
    #         book_hotel_model.services[service_index].idbook_extra_service = 0
    #         book_hotel_model.services[service_index].usuario_creacion = username

    #     temp_payments = book_hotel_model.payments
    #     for payment_index, payment_elem in enumerate(book_hotel_model.payments):
    #         make_transient(book_hotel_model.payments[payment_index])
    #         for payment_detail_index, payment_detail_elem in enumerate(book_hotel_model.payments[payment_index].details):
    #             make_transient(book_hotel_model.payments[payment_index].details[payment_detail_index])
    #     book_hotel_model.payments = []
    #     # for payment_index, payment_elem in enumerate(book_hotel_model.payments):
    #     #     book_hotel_model.payments[payment_index].idpayment_transaction = 0
    #     #     book_hotel_model.payments[payment_index].usuario_creacion = username
    #     #     for payment_detail_index, payment_detail_elem in enumerate(book_hotel_model.payments[payment_index].details):
    #     #         book_hotel_model.payments[payment_index].details[payment_detail_index].idpayment_transaction_detail = 0
    #     #         book_hotel_model.payments[payment_index].details[payment_detail_index].usuario_creacion = username

    #     for promotion_index, promotion_elem in enumerate(book_hotel_model.promotions):
    #         make_transient(book_hotel_model.promotions[promotion_index])
    #         book_hotel_model.promotions[promotion_index].idbook_promotion = 0
    #         book_hotel_model.promotions[promotion_index].usuario_creacion = username

    #     db.session.add(book_hotel_model)
    #     db.session.flush()

    #     raise Exception("Break Point")

    #     list_info_id_rooms = []
    #     for room_index, room_elem in enumerate(temp_rooms):
    #         hotel_room = BookHotelRoom()
    #         hotel_room.idbook_hotel = book_hotel_model.idbook_hotel
    #         hotel_room.iddef_room_type = room_elem.iddef_room_type
    #         hotel_room.idop_rate_plan = room_elem.idop_rate_plan
    #         hotel_room.refundable = room_elem.refundable
    #         hotel_room.iddef_police_tax = room_elem.iddef_police_tax
    #         hotel_room.iddef_police_guarantee = room_elem.iddef_police_guarantee
    #         hotel_room.iddef_police_cancelation = room_elem.iddef_police_cancelation
    #         hotel_room.iddef_pms = room_elem.iddef_pms
    #         hotel_room.pms_confirm_number = room_elem.pms_confirm_number
    #         hotel_room.pms_message = room_elem.pms_message
    #         hotel_room.rate_amount = room_elem.rate_amount
    #         hotel_room.promo_amount = room_elem.promo_amount
    #         hotel_room.discount_percent = room_elem.discount_percent
    #         hotel_room.discount_amount = room_elem.discount_amount
    #         hotel_room.total_gross = room_elem.total_gross
    #         hotel_room.country_fee = room_elem.country_fee
    #         hotel_room.total = room_elem.total
    #         hotel_room.promotion_amount = room_elem.promotion_amount
    #         hotel_room.paxes = room_elem.paxes
    #         hotel_room.usuario_creacion = username
    #         for room_price_index, room_price_elem in enumerate(room_elem.prices):
    #             hotel_room_price = BookHotelRoomPrices()
    #             #hotel_room_price.idbook_hotel_room_prices = room_price_elem.idbook_hotel_room_prices
    #             #hotel_room_price.idbook_hotel_room = room_price_elem.idbook_hotel_room
    #             hotel_room_price.date = room_price_elem.date
    #             hotel_room_price.price = room_price_elem.price
    #             hotel_room_price.promo_amount = room_price_elem.promo_amount
    #             hotel_room_price.discount_percent = room_price_elem.discount_percent
    #             hotel_room_price.discount_amount = room_price_elem.discount_amount
    #             hotel_room_price.total_gross = room_price_elem.total_gross
    #             hotel_room_price.country_fee = room_price_elem.country_fee
    #             hotel_room_price.total = room_price_elem.total
    #             hotel_room_price.promotion_amount = room_price_elem.promotion_amount
    #             hotel_room_price.code_promotions = room_price_elem.code_promotions
    #             hotel_room_price.estado = room_price_elem.estado
    #             hotel_room_price.usuario_creacion = username

    #             hotel_room.prices.append(hotel_room_price)

    #         db.session.add(hotel_room)
    #         db.session.flush()
    #         list_info_id_rooms.append({
    #             "previous_idbook_hotel_room":room_elem.idbook_hotel_room,
    #             "new_idbook_hotel_room": hotel_room.idbook_hotel_room
    #         })

    #     for payment_index, payment_elem in enumerate(temp_payments):
    #         hotel_payment_transaction = PaymentTransaction()
    #         #hotel_payment_transaction.idpayment_transaction = payment_elem.idpayment_transaction
    #         hotel_payment_transaction.idbook_hotel = book_hotel_model.idbook_hotel
    #         hotel_payment_transaction.idpayment_method = payment_elem.idpayment_method
    #         hotel_payment_transaction.idpayment_transaction_type = payment_elem.idpayment_transaction_type
    #         hotel_payment_transaction.card_code = payment_elem.card_code
    #         hotel_payment_transaction.authorization_code = payment_elem.authorization_code
    #         hotel_payment_transaction.merchant_code = payment_elem.merchant_code
    #         hotel_payment_transaction.ticket_code = payment_elem.ticket_code
    #         hotel_payment_transaction.idfin_payment = payment_elem.idfin_payment
    #         hotel_payment_transaction.amount = payment_elem.amount
    #         hotel_payment_transaction.exchange_rate = payment_elem.exchange_rate
    #         hotel_payment_transaction.currency_code = payment_elem.currency_code
    #         hotel_payment_transaction.estado = payment_elem.estado
    #         hotel_payment_transaction.usuario_creacion = username
    #         for payment_detail_index, payment_detail_elem in enumerate(payment_elem):
    #             obj_id_room = next((item for item in list_info_id_rooms if item["previous_idbook_hotel_room"] == payment_detail_elem.idbook_hotel_room), None)
    #             if obj_id_room is not None:
    #                 hotel_payment_transaction_detail = PaymentTransactionDetail()
    #                 #hotel_payment_transaction_detail.idpayment_transaction_detail = payment_detail_elem.idpayment_transaction_detail
    #                 hotel_payment_transaction_detail.idpayment_transaction = payment_detail_elem.idpayment_transaction
    #                 hotel_payment_transaction_detail.idFin = payment_detail_elem.idFin
    #                 hotel_payment_transaction_detail.amount = payment_detail_elem.amount
    #                 hotel_payment_transaction_detail.idbook_hotel_room = obj_id_room["new_idbook_hotel_room"]
    #                 hotel_payment_transaction_detail.interfaced = payment_detail_elem.interfaced
    #                 hotel_payment_transaction_detail.estado = payment_detail_elem.estado
    #                 hotel_payment_transaction_detail.usuario_creacion = username
    #                 hotel_payment_transaction.details.append(hotel_payment_transaction_detail)
    #         db.session.add(hotel_room)
    #         db.session.flush()

    #     previous_book_hotel_model = BookHotel.query.filter(BookHotel.idbook_hotel==previous_book_hotel_id).first()
    #     previous_book_hotel_model.estado = 2 #Estado _________________-
    #     db.session.commit()

    #     #Se vuelve a realizar la búsqueda para obtener los datos relacionados del modelo por completo
    #     book_hotel_model = BookHotel.query.filter(BookHotel.idbook_hotel==book_hotel_model.idbook_hotel).first()


    #     # model = BookHotel()
    #     # model.idbook_hotel = book_hotel_model.idbook_hotel
    #     # model.iddef_property = book_hotel_model.iddef_property
    #     # model.code_reservation = book_hotel_model.code_reservation
    #     # model.from_date = book_hotel_model.from_date
    #     # model.to_date = book_hotel_model.to_date
    #     # model.nights = book_hotel_model.nights
    #     # model.adults = book_hotel_model.adults
    #     # model.child = book_hotel_model.child
    #     # model.total_rooms = book_hotel_model.total_rooms
    #     # model.iddef_market_segment = book_hotel_model.iddef_market_segment
    #     # model.iddef_country = book_hotel_model.iddef_country
    #     # model.iddef_language = book_hotel_model.iddef_language
    #     # model.iddef_currency = book_hotel_model.iddef_currency
    #     # model.iddef_currency_user = book_hotel_model.iddef_currency_user
    #     # model.iddef_channel = book_hotel_model.iddef_channel
    #     # model.exchange_rate = book_hotel_model.exchange_rate
    #     # model.promo_amount = book_hotel_model.promo_amount
    #     # model.discount_percent = book_hotel_model.discount_percent
    #     # model.discount_amount = book_hotel_model.discount_amount
    #     # model.total_gross = book_hotel_model.total_gross
    #     # model.fee_amount = book_hotel_model.fee_amount
    #     # model.country_fee = book_hotel_model.country_fee
    #     # model.total = book_hotel_model.total
    #     # model.promotion_amount = book_hotel_model.promotion_amount
    #     # model.idbook_status = book_hotel_model.idbook_status
    #     # model.expiry_date = book_hotel_model.expiry_date

    #     # #model.property
    #     # model.customers
    #     # model.comments
    #     # model.promo_codes
    #     # #model.market_segment
    #     # #model.country
    #     # #model.language
    #     # #model.currency
    #     # #model.currency_user
    #     # #model.status_item
    #     # model.rooms
    #     # model.services
    #     # model.payments
    #     # model.promotions

    #     return book_hotel_model

    @staticmethod
    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days+1)):
            yield start_date + timedelta(n)
    
    @staticmethod
    def calcualte_payment_booking(rooms=None,total_amount=0,idbook_hotel=0,currency=None):
        data = {
            "total":0.00,
            "amount_paid":0.00,
            "amount_to_pay":0.00,
            "amount_pending_payment":0.00,
            "amount_to_pending_payment":0.00,
            "amount_refund":0.00,
            "amount_to_refund":0.00,
            "rooms":[]
        }
        
        info_payment, info_refund, info_pending_payment = 0, 0, 0
        payment_service = PaymentService()
        info_payment_book = payment_service.get_payment_info(idbook_hotel,[1])
        for payment in info_payment_book:
            if payment.idpayment_transaction_type == 1:
                info_payment += payment.amount
            elif payment.idpayment_transaction_type == 2:
                info_refund += payment.amount
        info_pending_payment_book = payment_service.get_payment_info(idbook_hotel,[2])
        for pending_payment in info_pending_payment_book:
            info_pending_payment += pending_payment.amount

        total_paid, data_room = 0, []
        for room in rooms:
            info_payment_room, info_refund_room, info_pending_payment_room = 0, 0, 0
            for payment in info_payment_book:
                if payment.idpayment_transaction_type == 1:
                    for payment_detail in payment.details:
                        if payment_detail.idbook_hotel_room == room["idbook_hotel_room"]:
                            info_payment_room += payment_detail.amount
                elif payment.idpayment_transaction_type == 2:
                    for payment_detail in payment.details:
                        if payment_detail.idbook_hotel_room == room["idbook_hotel_room"]:
                            info_refund_room += payment_detail.amount
            for pending_payment in info_pending_payment_book:
                for pending_payment_detail in pending_payment.details:
                    if pending_payment_detail.idbook_hotel_room == room["idbook_hotel_room"]:
                        info_pending_payment_room += pending_payment_detail.amount

            policy_guarantee = PolicyFunctions.getPolicyConfigData(room["policies"]["booking"])

            if not policy_guarantee:
                return data
            
            """
                1. No Payment (implemented)
                2. Credit Card Store as Guarantee (implemented)
                3. Offline Credit Card Payment in own Terminal (implemented)
                4. Bank Transfer (not implemented)
            """

            room["amount_refund"] = 0

            guarantee_currency_code = policy_guarantee["currency_code"]
            policy_guarantee = policy_guarantee["policy_guarantees"][0]
            if policy_guarantee["iddef_policy_guarantee_type"] == 2:#the payment will be automatic before arrive
                room["charge_option"] = BookHotelRoom.charge_option_before_arrived
                amount = 0
                room["amount_to_pay"] = amount
                room["amount_paid"] = info_payment_room
                room["amount_pending_payment"] = room["total"] - info_payment_room
                room["amount_to_pending_payment"] = room["total"] - info_payment_room
                if room["total"] > (info_payment_room + info_pending_payment_room):
                    room["amount_to_pending_payment"] = room["total"] - (info_payment_room + info_pending_payment_room)
                elif room["total"] < (info_payment_room + info_pending_payment_room):
                    room["amount_to_pending_payment"] = 0
                    if room["total"] < info_payment_room:
                        room["amount_pending_payment"] = 0
                        room["amount_refund"] = abs(room["total"] - info_payment_room)

            elif policy_guarantee["iddef_policy_guarantee_type"] == 3:#the payment (full or partial) will be in the moment save reservation
                room["charge_option"] = BookHotelRoom.charge_option_at_moment
                guarantee_deposit = policy_guarantee["policy_guarantee_deposits"][0]
                """
                    iddef_policy_rule options:
                        0. None
                        1. Fixed amount
                        2. Percent
                """
                if guarantee_deposit["iddef_policy_rule"] == 1:
                    amount = 0
                    if currency != guarantee_currency_code:
                        #Convert the currency of guarantee to currency reservation
                        exchange_rate = ExchangeRateService.get_exchange_rate_date(date.today(), guarantee_deposit["currency_code"])
                        if currency == "USD" and guarantee_currency_code == "MXN":
                            amount = exchange_rate.amount * guarantee_deposit["fixed_amount"]
                        elif currency == "MXN" and guarantee_currency_code == "USD":
                            amount = guarantee_deposit["fixed_amount"] / exchange_rate.amount
                    
                    room["amount_paid"] = info_payment_room
                    room["amount_pending_payment"] = room["total"] - amount
                    room["amount_to_pending_payment"] = 0
                    if amount < info_payment_room or amount == info_payment_room:
                        room["amount_to_pay"] = 0
                    elif amount > info_payment_room:
                        if room["total"] > (info_payment_room + info_pending_payment_room):
                            room["amount_to_pay"] = round(amount - info_payment_room, 2)
                            room["amount_pending_payment"] = room["total"] - amount
                            room["amount_to_pending_payment"] = room["total"] - (amount + info_payment_room)
                    elif room["total"] < (info_payment_room + info_pending_payment_room):
                        room["amount_to_pending_payment"] = 0
                        if room["total"] < info_payment_room:
                            room["amount_pending_payment"] = 0
                            room["amount_refund"] = abs(room["total"] - info_payment_room)                           

                elif guarantee_deposit["iddef_policy_rule"] == 2:
                    """
                        option_percent options:
                        0. fullstay
                        1. nights
                    """
                    if guarantee_deposit["option_percent"] == 0:
                        amount = 0
                        amount = round(room["total"] * (float(guarantee_deposit["percent"])/100), 2)
                        room["amount_paid"] = info_payment_room
                        room["amount_pending_payment"] = room["total"] - amount
                        room["amount_to_pending_payment"] = 0
                        if amount < info_payment_room or amount == info_payment_room:
                            room["amount_to_pay"] = 0
                        elif amount > info_payment_room:
                            if amount == room["total"]:
                                room["amount_to_pay"] = round(amount - info_payment_room, 2)
                                room["amount_pending_payment"] = 0
                            elif room["total"] > (info_payment_room + info_pending_payment_room):
                                room["amount_to_pay"] = round(amount - info_payment_room, 2)
                                room["amount_pending_payment"] = room["total"] - amount
                                room["amount_to_pending_payment"] = room["total"] - (amount + info_payment_room)
                        elif room["total"] < (info_payment_room + info_pending_payment_room):
                            room["amount_to_pending_payment"] = 0
                            if room["total"] < info_payment_room:
                                room["amount_pending_payment"] = 0
                                room["amount_refund"] = abs(room["total"] - info_payment_room)

                    elif guarantee_deposit["option_percent"] == 1:
                        amount = 0
                        #sum the number nights required
                        for i in range(int(guarantee_deposit["number_nights_percent"])):
                            to_pay = room["rates"][i]["amount"] * (float(guarantee_deposit["percent"])/100)
                            amount += to_pay
                        
                        room["amount_paid"] = info_payment_room
                        room["amount_pending_payment"] = room["total"] - amount
                        room["amount_to_pending_payment"] = 0
                        if amount < info_payment_room or amount == info_payment_room:
                            room["amount_to_pay"] = 0
                        elif amount > info_payment_room:
                            if room["total"] > (info_payment_room + info_pending_payment_room):
                                room["amount_to_pay"] = round(amount - info_payment_room, 2)
                                room["amount_pending_payment"] = room["total"] - amount
                                room["amount_to_pending_payment"] = room["total"] - (amount + info_payment_room)
                        elif room["total"] < (info_payment_room + info_pending_payment_room):
                            room["amount_to_pending_payment"] = 0
                            if room["total"] < info_payment_room:
                                room["amount_pending_payment"] = 0
                                room["amount_refund"] = abs(room["total"] - info_payment_room)

            data_room.append(room)
            total_paid += amount
        data["rooms"] = data_room
        data["amount_refund"] = info_refund
        data["amount_to_refund"] = 0

        data["total"] = total_amount
        data["amount_paid"] = info_payment
        data["amount_pending_payment"] = total_amount - info_payment
        data["amount_to_pending_payment"] = 0
        if total_paid < info_payment or total_paid == info_payment:
            data["amount_to_pay"] = 0
        elif total_paid > info_payment:
            if total_amount > (info_payment+info_pending_payment):
                data["amount_to_pay"] = total_paid - info_payment
                data["amount_pending_payment"] = total_amount - total_paid
                data["amount_to_pending_payment"] = total_amount - (total_paid + info_pending_payment)
        if total_amount < (info_payment+info_pending_payment):
            data["amount_to_pending_payment"] = 0
            if total_amount < (info_payment):
                data["amount_pending_payment"] = 0
                if info_refund < abs(data["total"] - info_payment):
                    data["amount_refund"] = abs(data["total"] - info_payment)
                    data["amount_to_refund"] = (abs(data["total"] - info_payment) - info_refund)
                if info_refund >= abs(data["total"] - info_payment):
                    data["amount_to_refund"] = 0
            
        return data


class BookHotelRoomUpdatePax(Resource):
    #api-booking-room-pax-put
    #@base.access_middleware
    def put(self):
        try:
            # user_data = base.get_token_data()
            # username = user_data['user']['username']

            query = 'UPDATE\
            book_hotel_room bht\
            LEFT JOIN (\
                SELECT t.idbook_hotel_room, SUM(t.total) AS total\
                FROM book_pax_room_hotel t\
                WHERE t.age_code = "adults"\
                AND t.estado = 1\
                GROUP BY t.idbook_hotel_room\
            ) aux_adt ON bht.idbook_hotel_room = aux_adt.idbook_hotel_room\
            LEFT JOIN (\
                SELECT t.idbook_hotel_room, SUM(t.total) AS total\
                FROM book_pax_room_hotel t\
                WHERE t.age_code != "adults"\
                AND t.estado = 1\
                GROUP BY t.idbook_hotel_room\
            ) aux_cdn ON bht.idbook_hotel_room = aux_cdn.idbook_hotel_room\
            SET bht.adults = IF(aux_adt.total IS NOT NULL, aux_adt.total, 0),\
            bht.child = IF(aux_cdn.total IS NOT NULL, aux_cdn.total, 0);'
            
            data = db.session.execute(query)
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {}
            }
        except Exception as e:
            #db.session.rollback()

            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

class BookHotelUpdateCreationModDate(Resource):
    #api-booking-create-mod-date-put
    #@base.access_middleware
    def put(self):
        try:
            # user_data = base.get_token_data()
            # username = user_data['user']['username']

            query = 'UPDATE book_hotel bh\
            INNER JOIN (\
                SELECT * FROM (\
                    SELECT t2.idbook_hotel,\
                    t2.code_reservation,\
                    t2.fecha_creacion\
                    FROM book_hotel t2\
                    WHERE t2.estado IN (1,2)\
                    ORDER BY t2.idbook_hotel ASC\
                ) AS t1 GROUP BY t1.code_reservation\
            ) aux_up ON bh.code_reservation = aux_up.code_reservation\
            SET bh.fecha_creacion = aux_up.fecha_creacion,\
            bh.modification_date_booking = IF(bh.fecha_ultima_modificacion="1900-01-01 00:00:00", aux_up.fecha_creacion, bh.fecha_ultima_modificacion);'
            
            data = db.session.execute(query)
            db.session.commit()

            response = {
                "Code": 200,
                "Msg": "Success",
                "Error": False,
                "data": {}
            }
        except Exception as e:
            #db.session.rollback()

            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response
