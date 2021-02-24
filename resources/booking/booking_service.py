from datetime import date, timedelta
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy import func
from config import db, base
import htmlmin
import datetime
from datetime import datetime as dt
from models.book_hotel import BookHotelReservationSchema as ModelSchema, BookHotel, BookHotelReservationResponseSchema
from models.book_hotel_room import BookHotelRoom
from models.book_promo_code import BookPromoCode
from models.book_promotion import BookPromotion
from models.book_hotel_comment import BookHotelComment
from models.book_pax_room_hotel import BookPaxRoomHotel
from models.book_customer import BookCustomer
from models.book_customer_hotel import BookCustomerHotel
from models.book_hotel_room_prices import BookHotelRoomPrices
from models.book_address import BookAddress
from models.book_status import BookStatus
from models.book_extra_service import BookExtraService
from models.book_extra_type import BookExtraType
from models.config_booking import ConfigBooking
from models.policy_guarantee_antifraud import PolicyGuaranteeAntifraud

from models.property import Property
from models.age_range import AgeRange, GetAgeRangeSchema
from resources.rates.RatesHelper import RatesFunctions
from resources.media.MediaHelper import MediaFunctions
from resources.media_service import AdminMediaServiceList
from resources.rateplan.rateplan import RatePlanPublic
from common.util import Util
from common.card_validation import CardValidation
from .wire_request import WireRequest, WireService
from resources.rateplan.rateplan import RatePlanPublic as FunctionsPolicy
from resources.service.serviceHelper import Search as FunctionsService
from resources.age_range.age_range_service import AgeRangeService as FunctionsAgeRange
from resources.property.property_service import PropertyService as FunctionsPropertySrv
from resources.policy.policyHelper import PolicyFunctions
from resources.exchange_rate.exchange_rate_service import ExchangeRateService
from resources.policy.policyHelper import PolicyFunctions
from resources.promo_code.promocodeHelper import PromoCodeFunctions

import locale
import copy
from unidecode import unidecode

class BookingService():
    def get_booking_by_code(self, code_reservation, full_name="", lang_code="en"):
        """
            Get book_hotel instance by code_reservation and full name (optional)
            :param code_reservation Code reservation
            :param full_name Fullname owner reservation (optional)
            :param lang_code language code to translate messages

            :return: book_hotel BookHotel instance || exception
        """
        
        lang_code = lang_code.lower()
        book_hotel = BookHotel.query.\
            filter(BookHotel.code_reservation == code_reservation, BookHotel.estado == 1).first()

        if book_hotel is None:
            raise Exception(Util.t(lang_code, "booking_code_not_found", code_reservation))

        """
        if book_hotel.idbook_status not in [BookStatus.on_hold, BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced]:
            raise Exception(Util.t(lang_code, "booking_code_not_found", code_reservation))
        """
        #check if match fullname with customer data
        if full_name != "":
            customer_first_name = book_hotel.customers[0].customer.first_name
            customer_last_name = book_hotel.customers[0].customer.last_name
            book_hotel.customers[0].customer.address.country_code = book_hotel.customers[0].customer.address.country.country_code
            if (unidecode(full_name)).upper() != (unidecode(("{} {}".format(customer_first_name, customer_last_name)))).upper():
                if (unidecode(full_name)).upper() != (unidecode(("{} {}".format(customer_last_name, customer_first_name)))).upper():
                    raise Exception(Util.t(lang_code, "booking_code_not_found", code_reservation))
        
        if lang_code != "":
            book_hotel.lang_code = lang_code
        #book_hotel.idbook_status = BookStatus.confirmed
        
        return book_hotel
    
    def get_booking_info_by_code(self, code_reservation, full_name="", lang_code="en"):
        """
            Get book_hotel instance by code_reservation and full name (optional)
            :param code_reservation Code reservation
            :param full_name Fullname owner reservation (optional)
            :param lang_code language code to translate messages

            :return: dict with booking info (used in confirmation letters)
        """
        book_hotel = self.get_booking_by_code(code_reservation, full_name, lang_code)
        #book_hotel.lang_code = lang_code

        return self.format_booking_info(book_hotel)

    def get_service_media(self, iddef_service, lang_code, iddef_property):
        '''
            Get media service by service id & language code
        '''
        media_data = AdminMediaServiceList.get(self, iddef_service, lang_code, iddef_property, 1)
        result_media = list(filter(lambda elem_selected: elem_selected['selected'] == 1, media_data['data']))

        return result_media
    
    def get_media_property(self,property_code):
        '''
            Get media property by property id
        '''
        media = []
        try:
            media = MediaFunctions.GetMediaProperty(idProperty=property_code,only_one=False,\
            MediaType=1)
        except Exception as ex:
            media = []

        return media
    
    def get_media_room(self,room_code):
        '''
            Get media room by room id
        '''
        media = []
        try:
            media = MediaFunctions.GetMediaRoom(idRoom=room_code, only_one=False, MediaType=1)
        except Exception as ex:
            media = []

        return media
    
    def get_model_by_code(self, code, column_code, model):
        '''
            get model by code or any column value
            :param code: The code to find the register
            :param column_code: The column where will find the code
            :param model: Model table (class reference)

            :return: Object
        '''
        model_data = model.query.filter(getattr(model, column_code) == code, model.estado == 1).first()

        if model_data is None:
            raise Exception("Code {} not exists".format(code))

        return model_data
        
    def get_model_by_id(self, id, model):
        '''
            get model by code
            :param id: ID to find the register
            :param model: Model table (class reference)

            :return: Object
        '''
        return model.query.get(id)
    
    def get_booking_code(self, id, iddef_property, idbook_status):
        '''
            get booking confirm code. This confirm code will be used to send to the customer.
            :param id: ID of booking_hotel register
            :param iddef_property: ID of property
            :param idbook_status: ID ok reservation status (book_status)

            :return: string
        '''
        book_status = self.get_model_by_id(idbook_status, BookStatus)
        
        if book_status is None:
            raise Exception("Cannot save the booking as on hold")
        
        property = self.get_model_by_id(iddef_property, Property)
        
        if property is None:
            raise Exception("Cannot save the booking as on hold")

        #returned format is XXXX-YYYYYYYYYY-ZZZZ
        return "{}-{}-{}".format(property.property_code, str(id), book_status.code)
    
    def get_total_pax(self, rooms):
        '''
            Get total pax of all the booking rooms
            :rooms: list of rooms with pax

            :return: int
        '''
        total = 0
        for room in rooms:
            total += sum(room["pax"].values())
        
        return total
        
    def get_ages_ranges_list(self, iddef_property):
        '''
            get all the age code config of the property
            :param iddef_property: ID of property

            :return: List<Object>
        '''

        data = AgeRange.query\
            .filter(and_(AgeRange.estado == 1, AgeRange.iddef_property == iddef_property)).all()
        
        age_range_schema = GetAgeRangeSchema(exclude=Util.get_default_excludes(), many=True)
        age_range_items = age_range_schema.dump(data, many=True)
        
        return age_range_items
        
    def get_on_hold_exp(self, current_date,property_code,from_date,to_date,data_rooms):
        '''
            Retrieve the expiry date of the on hold booking.

            return Datetime
        '''
        expiry_date = None
        config_booking = FunctionsPropertySrv.get_hold_duration_policy(current_date,property_code,from_date,to_date,data_rooms)
        if len(config_booking) > 0:
            if config_booking[0]['on_hold'] is True:
                expiry_date = config_booking[0]['expiry_date']

        return expiry_date

    def get_code_reservation_value(self, code_reservation, get_value = "iddef_book_hotel"):
        '''
            Splite code_reservation. 
            The structure is : hotel_code-iddef_book_hotel-book_status_code
            :param code_reservation = Reservation code
            :param get_value = The value or field the method return

            :return = Indicated value
        '''
        code_reservation_data = code_reservation.split("-")
        value = ""

        if len(code_reservation_data) != 3:
            raise Exception("code reservation not valid")
        
        if get_value == "hotel_code":
            value = code_reservation_data[0]
        elif get_value == "iddef_book_hotel":
            value = code_reservation_data[1]
        elif get_value == "book_status_code":
            value = code_reservation_data[2]
        
        #book_id = book_id.lstrip("0")#remove 0 in left
        return value
    
    def get_payment_codes(self, data):
        '''
            Valid the credit card data is valid & return card info validation
        '''
        card_info = CardValidation(data["card_number"], data["exp_month"], data["exp_year"])

        if not card_info.is_valid or card_info.code is None:
            raise Exception("Credit card not valid")
        
        if card_info.is_expired:
            raise Exception("Card is expired")
        
        return card_info

    def create_promo_code(self, is_text, promo_code, amount, promo_code_type, user):
        '''
            Map data to new BookPromoCode instance
            TODO: Get promo code amount
        '''

        book_promo_code = BookPromoCode()
        book_promo_code.is_text = is_text
        book_promo_code.promo_code = promo_code
        book_promo_code.amount = amount
        book_promo_code.promo_code_type = promo_code_type
        book_promo_code.usuario_creacion = user
        book_promo_code.estado = 1

        return book_promo_code
    
    def create_promotion(self, data_promotion):
        '''
            Map data to new BookPromotion instance
        '''

        book_promotion = BookPromotion()
        book_promotion.idop_promotions = data_promotion["idop_promotions"]
        #book_promotion.amount = data_promotion["amount"]
        book_promotion.usuario_creacion = data_promotion["user"]
        book_promotion.estado = 1

        return book_promotion

    def create_comment(self, special_request, user, visible_to_guest=True):
        '''
            Map data to new BookHotelComment instance
        '''
        book_hotel_comment = BookHotelComment()
        book_hotel_comment.text = special_request
        book_hotel_comment.visible_to_guest = 1 if visible_to_guest else 0
        book_hotel_comment.source = book_hotel_comment.source_public
        book_hotel_comment.usuario_creacion = user
        book_hotel_comment.estado = 1

        return book_hotel_comment

    def create_room(self, room_data,promo_code,vaucherApplied=False,is_text=0):
        '''        
            Map data to new BookHotelRoom instance
            TODO: find by rate plan the policies
        '''
        police_tax = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 3, room_data["from_date"])
        police_guarantee = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 2, room_data["from_date"])
        police_cancelation = RatePlanPublic.get_policy_cancellation(room_data["idop_rate_plan"], room_data["from_date"], not room_data["rateplan_is_refundable"])

        book_hotel_room = BookHotelRoom()
        book_hotel_room.iddef_room_type = room_data["iddef_room_type"]
        book_hotel_room.idop_rate_plan = room_data["idop_rate_plan"]
        book_hotel_room.refundable = not room_data["rateplan_is_refundable"]
        book_hotel_room.iddef_police_tax = police_tax.iddef_policy if police_tax else 0
        book_hotel_room.iddef_police_guarantee = police_guarantee.iddef_policy if police_guarantee else 0
        book_hotel_room.iddef_police_cancelation = police_cancelation.iddef_policy_cancellation_detail if police_cancelation else 0
        book_hotel_room.iddef_pms = book_hotel_room.pms_opera_default
        book_hotel_room.promo_amount = 0        
        book_hotel_room.usuario_creacion = room_data["user"]
        book_hotel_room.estado = 1

        book_hotel_room.paxes = room_data["paxes"]
        book_hotel_room.adults = room_data["adults"]
        book_hotel_room.child = room_data["child"]

        book_hotel_room.rate_amount = room_data["rate_amount"]
        book_hotel_room.total = room_data["total"]
        if book_hotel_room.total < 0:
            raise Exception("Rate Plan not available")

        book_hotel_room.discount_percent = room_data["discount_percent"]
        book_hotel_room.discount_amount = room_data["discount_amount"]
        book_hotel_room.total_gross = room_data["total_gross"]

        #append room prices to audit
        list_prices = []
        tax_amount = 0
        promotion_amount = 0
        promo_amount = 0
        for room_price_data in room_data["price_per_day"]:
            price_promotion_amount, code_promotion, amount_vaucher = 0, "", 0
            if room_price_data["promotions"] and len(room_price_data["promotions"]) > 0:
                price_promotion_amount = room_price_data["promotions"]["value_discount"]
                code_promotion = room_price_data["promotions"]["code"]
            price = room_price_data["amount"] - room_price_data["tax_amount"]
            price = price + price_promotion_amount
            discount_amount = room_price_data["amount_crossout"] - room_price_data["amount"]
            tax_amount += room_price_data["tax_amount"]
            promotion_amount += price_promotion_amount
            if promo_code != "" and vaucherApplied == True and is_text==0:
                if room_data["vaucher_applied"] == True:
                    amount_vaucher = room_price_data["vaucher_discount"]
            promo_amount += amount_vaucher
            price_data = {
                "date": room_price_data["efective_date"],
                "price": round(price, 4),
                "discount_percent": room_price_data["percent_discount"],
                "discount_amount": round(discount_amount, 4),
                "total_gross": room_price_data["amount_crossout"],
                "promo_amount": amount_vaucher,
                "country_fee": room_price_data["tax_amount"],
                "total": room_price_data["amount"],
                "promotion_amount": price_promotion_amount,
                "code_promotion": code_promotion,
                "price_to_pms": room_price_data["amount_to_pms"],
                "user": book_hotel_room.usuario_creacion,
            }

            list_prices.append(self.create_room_prices(price_data))
        
        book_hotel_room.prices = list_prices
        book_hotel_room.promo_amount = promo_amount
        book_hotel_room.country_fee = tax_amount
        book_hotel_room.promotion_amount = promotion_amount       

        return book_hotel_room

    def create_room_info(self, room_data, validate_pax_code = False, age_range_data = [], is_refund=False):
        '''        
            Map data to new BookHotelRoom instance
            TODO: find by rate plan the policies
        '''
        police_tax = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 3, room_data["from_date"])
        police_guarantee = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 2, room_data["from_date"])
        police_cancelation = RatePlanPublic.get_policy_cancellation(room_data["idop_rate_plan"], room_data["from_date"], not room_data["rateplan_is_refundable"])

        book_hotel_room = BookHotelRoom()
        book_hotel_room.iddef_room_type = room_data["iddef_room_type"]
        book_hotel_room.idop_rate_plan = room_data["idop_rate_plan"]
        book_hotel_room.refundable = not room_data["rateplan_is_refundable"]
        book_hotel_room.iddef_police_tax = police_tax.iddef_policy if police_tax else 0
        book_hotel_room.iddef_police_guarantee = police_guarantee.iddef_policy if police_guarantee else 0
        book_hotel_room.iddef_police_cancelation = police_cancelation.iddef_policy_cancellation_detail if police_cancelation else 0
        book_hotel_room.iddef_pms = book_hotel_room.pms_opera_default
        book_hotel_room.promo_amount = 0        
        book_hotel_room.usuario_creacion = room_data["user"]
        book_hotel_room.estado = 1
                
        pax_list = []
        adults = 0
        child = 0
        #iterate the pax values
        for key, value in room_data["pax"].items():
            iddef_age_range = 0

            if key == "adults":
                adults = value
            else:
                child += value

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
                "user": room_data["user"]
            }

            pax_list.append(self.create_pax_room(pax_data))

        rate = self.info_rates(room_data)

        book_hotel_room.rate_amount = round(rate["total"], 4)

        #promotion_amount, tax_amount = 0.0, 0.0
        #from_date = room_data["from_date"].date()
        #to_date = room_data["to_date"].date()

        book_hotel_room.country_fee = round(rate["country_fee"], 4) if not room_data["rates_fix"] else 0
        if not is_refund:
            book_hotel_room.amount_pending_payment = rate["total"] - room_data["total_to_paid_room"]
            book_hotel_room.amount_paid = room_data["total_to_paid_room"]
        else:
            book_hotel_room.amount_pending_payment = rate["total"]
            book_hotel_room.amount_paid = 0
        book_hotel_room.total = round(rate["total"], 4)
        book_hotel_room.promotion_amount = round(rate["promotion_amount"], 4) if not room_data["rates_fix"] else 0
        book_hotel_room.paxes = pax_list
        book_hotel_room.adults = adults
        book_hotel_room.child = child

        # if book_hotel_room.total <= 0:
        #     raise Exception("Rate Plan not available")
        
        rates_array = []
        rates_array.append(rate)
        # rates_crossouts = RatesFunctions.apply_crossout_list(rates_array,\
        # room_data["iddef_market"], room_data["country_code"],True)

        book_hotel_room.discount_percent = round(rate["total_percent_discount"], 2) if not room_data["rates_fix"] else 0
        book_hotel_room.discount_amount = round(rate["discount_amount"], 4) if not room_data["rates_fix"] else 0
        book_hotel_room.total_gross = round(rate["total_crossout"], 4) if not room_data["rates_fix"] else 0

        #append room prices to audit
        list_prices = []
        for room_price_data in rate["price_per_day"]:
            price_promotion_amount, code_promotion = 0, ""
            if not room_data["rates_fix"] and room_price_data["promotions"] and len(room_price_data["promotions"]) > 0:
                price_promotion_amount = room_price_data["promotions"]["value_discount"]
                code_promotion = room_price_data["promotions"]["code"]
            price = (room_price_data["amount"] - room_price_data["tax_amount"]) if not room_data["rates_fix"] else room_price_data["amount"]
            price = price + price_promotion_amount
            discount_amount = (room_price_data["amount_crossout"] - room_price_data["amount"]) if not room_data["rates_fix"] else 0

            price_data = {
                "date": room_price_data["efective_date"],
                "price": round(price, 4),
                "promo_amount":room_price_data["vaucher_discount"] if not room_data["rates_fix"] else 0,
                "price_to_pms":room_price_data["price_pms"],
                "discount_percent": room_price_data["percent_discount"] if not room_data["rates_fix"] else 0,
                "discount_amount": round(discount_amount, 4),
                "total_gross": room_price_data["amount_crossout"] if not room_data["rates_fix"] else 0,
                "country_fee": room_price_data["tax_amount"] if not room_data["rates_fix"] else 0,
                "total": room_price_data["amount"],
                "promotion_amount": price_promotion_amount,
                "code_promotion": code_promotion,
                "user": book_hotel_room.usuario_creacion,
            }

            temp_room_obj = self.create_room_prices(price_data)
            temp_room_obj.promo_amount = room_price_data["vaucher_discount"] if not room_data["rates_fix"] else 0
            temp_room_obj.price_to_pms = room_price_data["price_pms"]
            list_prices.append(temp_room_obj)
        
        book_hotel_room.prices = list_prices

        return book_hotel_room

    def info_rates(self, room_data):
        aux_sum_discount = 0
        count_rates = 0
        aux_sum_gross = 0
        aux_sum_country_fee = 0
        aux_promotion_amount = 0
        aux_total = 0
        for elem_rate in room_data["rates"]:
            count_rates += 1
            aux_total += elem_rate["amount"]
            aux_sum_discount += elem_rate["percent_discount"]
            aux_sum_gross += elem_rate["amount_crossout"]
            aux_sum_country_fee += elem_rate["tax_amount"]
            if isinstance(elem_rate["promotions"], dict) and len(elem_rate["promotions"]) > 0 and "value_discount" in elem_rate["promotions"].keys():
                aux_promotion_amount += elem_rate["promotions"]["value_discount"]

        discount_percent = round(aux_sum_discount/count_rates,2)
        discount_amount = round(aux_sum_gross-room_data["total_room"],4)
        rate = {
            "total": aux_total,
            "total_percent_discount":discount_percent,
            "discount_amount": discount_amount,
            "total_crossout": round(aux_sum_gross,0),
            "country_fee": aux_sum_country_fee,
            "promotion_amount": aux_promotion_amount,
            "price_per_day":room_data["rates"]
        }
        return rate
    
    def create_pax_room(self, pax_data):
        '''
            Map data to new BookPaxRoomHotel instance
        '''
        book_pax_room = BookPaxRoomHotel()
        book_pax_room.iddef_age_range = pax_data["iddef_age_range"]
        book_pax_room.age_code = pax_data["age_code"]
        book_pax_room.total = pax_data["pax"]
        book_pax_room.usuario_creacion = pax_data["user"]
        book_pax_room.estado = 1

        return book_pax_room

    def create_customer(self, customer_data):
        '''
            Map data to new BookCustomer instance
        '''
        book_customer = BookCustomer()
        book_customer.title = customer_data["title"]
        book_customer.first_name = customer_data["first_name"]
        book_customer.last_name = customer_data["last_name"]
        book_customer.dialling_code = customer_data["dialling_code"]
        book_customer.phone_number = customer_data["phone_number"]
        book_customer.email = customer_data["email"]
        book_customer.birthdate = customer_data["birthdate"]
        book_customer.company = customer_data["company"]
        book_customer.usuario_creacion = customer_data["user"]
        book_customer.estado = 1

        customer_data["address"]["user"] = book_customer.usuario_creacion
        book_customer.address = self.create_customer_address(customer_data["address"])
        
        books_customer_hotel = BookCustomerHotel()
        books_customer_hotel.is_holder = True
        books_customer_hotel.customer = book_customer
        books_customer_hotel.usuario_creacion = customer_data["user"]
        books_customer_hotel.estado = 1

        return books_customer_hotel

    def create_customer_address(self, address_data):
        '''
            Map data to new BookAddress instance
        '''
        book_address = BookAddress()
        book_address.city = address_data["city"]
        book_address.iddef_country = address_data["iddef_country"]
        book_address.address = address_data["address"]
        book_address.street = address_data["street"]
        book_address.state = address_data["state"]
        book_address.zip_code = address_data["zip_code"]
        book_address.usuario_creacion = address_data["user"]
        book_address.estado = 1
        
        return book_address

    def create_room_prices(self, price_data):
        '''
            Map data to new BookHotelRoomPrices instance
        '''
        room_price = BookHotelRoomPrices()
        room_price.date = price_data["date"]
        room_price.price = price_data["price"]
        room_price.price_to_pms = price_data["price_to_pms"]
        room_price.discount_percent = price_data["discount_percent"]
        room_price.discount_amount = price_data["discount_amount"]
        room_price.total_gross = price_data["total_gross"]
        room_price.country_fee = price_data["country_fee"]
        room_price.total = price_data["total"]
        room_price.promotion_amount = price_data["promotion_amount"]
        room_price.code_promotions = price_data["code_promotion"]
        room_price.promo_amount = price_data["promo_amount"]
        room_price.usuario_creacion = price_data["user"]
        room_price.estado = 1

        return room_price

    def create_extra_service(self, service_data):
        '''
            Map data to new BookExtraService instance
        '''
        book_extra_service = BookExtraService()
        book_extra_service.description = service_data["description"]
        book_extra_service.idbook_extra_type = BookExtraType.default_service_booking_engine
        book_extra_service.iddef_service = service_data["iddef_service"]
        book_extra_service.external_folio = ""
        book_extra_service.unit_price = service_data["unit_price"]
        book_extra_service.quantity = service_data["quantity"]
        
        total_gross = book_extra_service.unit_price * book_extra_service.quantity

        book_extra_service.total_gross = total_gross
        book_extra_service.discount_percent = 0
        book_extra_service.discount_amount = 0
        book_extra_service.fee_amount = 0
        book_extra_service.total = total_gross
        book_extra_service.usuario_creacion = service_data["user"]
        book_extra_service.estado = 1

        return book_extra_service

    def update_room(self, book_hotel_room, room_data, validate_pax_code = False, age_range_data = []):
        '''        
            Map data to new BookHotelRoom instance
            TODO: find by rate plan the policies
        '''
        police_tax = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 3, room_data["from_date"])
        police_guarantee = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 2, room_data["from_date"])
        police_cancelation = RatePlanPublic.get_policy_cancellation(room_data["idop_rate_plan"], room_data["from_date"], not room_data["rateplan_is_refundable"])

        if book_hotel_room.idbook_hotel_room != room_data["idbook_hotel_room"]:
            raise Exception("idbook_hotel_room not valid")
        book_hotel_room.iddef_room_type = room_data["iddef_room_type"]
        book_hotel_room.idop_rate_plan = room_data["idop_rate_plan"]
        book_hotel_room.refundable = room_data["rateplan_is_refundable"]
        book_hotel_room.iddef_police_tax = police_tax.iddef_policy if police_tax else 0
        book_hotel_room.iddef_police_guarantee = police_guarantee.iddef_policy if police_guarantee else 0
        book_hotel_room.iddef_police_cancelation = police_cancelation.iddef_policy_cancellation_detail if police_cancelation else 0
        book_hotel_room.iddef_pms = book_hotel_room.pms_opera_default
        book_hotel_room.promo_amount = 0        
        book_hotel_room.usuario_creacion = room_data["user"]
        book_hotel_room.estado = 1

        list_paxes_ranges = [pax_room.age_code for pax_room in book_hotel_room.paxes]
                
        pax_list = []
        adults = 0
        child = 0
        #iterate the pax values
        for key, value in room_data["pax"].items():
            iddef_age_range = 0
            flag_age_range = False

            if key == "adults":
                adults = value
            else:
                child += value

            if validate_pax_code == True:
                #looking for the iddef_age_code & validate if exists the code in the property config age_range
                iddef_age_range = next((item["iddef_age_range"] for item in age_range_data\
                    if item["age_range_age_code"]["code"] == key), None)
                
                if iddef_age_range is None:
                    raise Exception("Pax code \"{}\" not exists in the property configuration".format(key))

            for pax_index, pax_item in enumerate(book_hotel_room.paxes):
                if pax_item.age_code == key:
                    flag_age_range=True
                    book_hotel_room.paxes[pax_index].total = value
                    book_hotel_room.paxes[pax_index].usuario_ultima_modificacion = room_data["user"]
            
            if not flag_age_range:
                pax_data = {
                    "iddef_age_range": iddef_age_range,
                    "age_code": key,
                    "pax": value,
                    "user": room_data["user"]
                }

                pax_room_element = self.create_pax_room(pax_data)
                book_hotel_room.paxes.append(pax_room_element)
        
        #get total price per day
        rate = RatesFunctions.getPricePerDay(room_data["iddef_property"], room_data["iddef_room_type"], \
            room_data["idop_rate_plan"], room_data["from_date"], room_data["to_date"], adults, child, room_data["currency"],\
            True, room_data["iddef_market"], room_data["country_code"])
        
        list_rate = []
        list_rate.append(rate)
        calculate_rate = RatesFunctions.calcualte_total_rates(list_rate)

        book_hotel_room.rate_amount = round(rate["total"], 4)

        promotion_amount, tax_amount = 0.0, 0.0
        from_date = room_data["from_date"].date()
        to_date = room_data["to_date"].date()
        promotions = RatesFunctions.get_promotions_by_booking(date_start=from_date, 
        date_end=to_date, market=room_data["country_code"],\
        hotel=room_data["property_code"], id_rateplan=room_data["idop_rate_plan"],\
        id_room=room_data["iddef_room_type"], include_free_room=False)

        if len(promotions) > 0:
            rate_list_aux = []
            for promo in promotions:
                rates_promotion = []
                rates_promotion.append(copy.deepcopy(rate))
                promo_list = []
                promo_list.append(promo)

                aux_rate = RatesFunctions.apply_promotion(rates_promotion,\
                promo_list)

                rate_list_aux.append(copy.deepcopy(aux_rate["Prices"][0]))
            
            rate = RatesFunctions.select_rates_promotion(rate_list_aux)
            promotion_amount = round(rate["total_crossout"] - rate["total"],4)

        data_tax = PolicyFunctions.getPolicyTaxes(rate["rateplan"],\
        from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d"), isFormat=True)
        if len(data_tax) > 0:
            #tax = RatesFunctions.format_policy_tax(data_tax)
            rate = RatesFunctions.apply_tax(rate, data_tax, room_data["currency"])
            price_total = rate["total"] + promotion_amount
            tax_amount = round(price_total - rate["total_crossout"], 4)

        book_hotel_room.country_fee = tax_amount
        book_hotel_room.total = round(rate["total"], 4)
        book_hotel_room.promotion_amount = round(promotion_amount, 4)
        #book_hotel_room.paxes = pax_list
        book_hotel_room.adults = adults
        book_hotel_room.child = child

        if book_hotel_room.total <= 0:
            raise Exception("Rate Plan not available")
        
        rates_array = []
        rates_array.append(rate)
        rates_crossouts = RatesFunctions.apply_crossout_list(rates_array,\
        room_data["iddef_market"], room_data["country_code"],True)

        book_hotel_room.discount_percent = round(rate["total_percent_discount"], 2)
        book_hotel_room.discount_amount = round(rate["total_crossout"] - rate["total"], 4)
        book_hotel_room.total_gross = round(rate["total_crossout"], 4)

        # Se desactivan todos los precios, en la siguiente sección se reactivan o se crean
        # De otra forma permance desactivado
        for room_price_index, room_price_item in enumerate(book_hotel_room.prices):
            book_hotel_room.prices[room_price_index].estado = 0
            book_hotel_room.prices[room_price_index].usuario_ultima_modificacion = book_hotel_room.usuario_creacion

        #append room prices to audit
        list_prices = []
        for room_price_data in rate["price_per_day"]:
            price_promotion_amount, code_promotion = 0, ""
            if room_price_data["promotions"] and len(room_price_data["promotions"]) > 0:
                price_promotion_amount = room_price_data["promotions"]["value_discount"]
                code_promotion = room_price_data["promotions"]["code"]
            price = room_price_data["amount"] - room_price_data["country_fee"]
            price = price + price_promotion_amount
            discount_amount = room_price_data["amount_crossout"] - room_price_data["amount"]

            flag_price = False
            for room_price_index, room_price_item in enumerate(book_hotel_room.prices):
                if room_price_item.date.strftime('%Y-%m-%d') == room_price_data["efective_date"].strftime('%Y-%m-%d'):
                    flag_price = True
                    book_hotel_room.prices[room_price_index].price = round(price, 4)
                    book_hotel_room.prices[room_price_index].promo_amount = 0,
                    book_hotel_room.prices[room_price_index].discount_percent = room_price_data["percent_discount"]
                    book_hotel_room.prices[room_price_index].discount_amount = round(discount_amount, 4)
                    book_hotel_room.prices[room_price_index].total_gross = room_price_data["amount_crossout"]
                    book_hotel_room.prices[room_price_index].country_fee = room_price_data["country_fee"]
                    book_hotel_room.prices[room_price_index].total = room_price_data["amount"]
                    book_hotel_room.prices[room_price_index].promotion_amount = price_promotion_amount
                    book_hotel_room.prices[room_price_index].code_promotions = code_promotion
                    book_hotel_room.prices[room_price_index].estado = 1
                    book_hotel_room.prices[room_price_index].usuario_ultima_modificacion = book_hotel_room.usuario_creacion

            if not flag_price:
                price_data = {
                    "date": room_price_data["efective_date"],
                    "price": round(price, 4),
                    "discount_percent": room_price_data["percent_discount"],
                    "discount_amount": round(discount_amount, 4),
                    "total_gross": room_price_data["amount_crossout"],
                    "country_fee": room_price_data["country_fee"],
                    "total": room_price_data["amount"],
                    "promotion_amount": price_promotion_amount,
                    "code_promotion": code_promotion,
                    "price_to_pms": room_price_data["amount_to_pms"],
                    "user": book_hotel_room.usuario_creacion,
                }

                book_hotel_room.prices.append(self.create_room_prices(price_data))

        db.session.flush()

        return book_hotel_room

    def update_room_info(self, book_hotel_room, room_data, validate_pax_code = False, age_range_data = [], is_refund=False):
        '''        
            Map data to new BookHotelRoom instance
            TODO: find by rate plan the policies
        '''
        police_tax = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 3, room_data["from_date"])
        police_guarantee = RatePlanPublic.get_policy_by_category(room_data["idop_rate_plan"], 2, room_data["from_date"])
        police_cancelation = RatePlanPublic.get_policy_cancellation(room_data["idop_rate_plan"], room_data["from_date"], not room_data["rateplan_is_refundable"])

        if book_hotel_room.idbook_hotel_room != room_data["idbook_hotel_room"]:
            raise Exception("idbook_hotel_room not valid")
        book_hotel_room.iddef_room_type = room_data["iddef_room_type"]
        book_hotel_room.idop_rate_plan = room_data["idop_rate_plan"]
        book_hotel_room.refundable = room_data["rateplan_is_refundable"]
        book_hotel_room.iddef_police_tax = police_tax.iddef_policy if police_tax else 0
        book_hotel_room.iddef_police_guarantee = police_guarantee.iddef_policy if police_guarantee else 0
        book_hotel_room.iddef_police_cancelation = police_cancelation.iddef_policy_cancellation_detail if police_cancelation else 0
        book_hotel_room.iddef_pms = book_hotel_room.pms_opera_default
        book_hotel_room.promo_amount = 0        
        book_hotel_room.usuario_ultima_modificacion = room_data["user"]
        book_hotel_room.estado = 1

        #list_paxes_ranges = [pax_room.age_code for pax_room in book_hotel_room.paxes]
                
        pax_list = []
        adults = 0
        child = 0
        #iterate the pax values
        for key, value in room_data["pax"].items():
            iddef_age_range = 0
            flag_age_range = False

            if key == "adults":
                adults = value
            else:
                child += value

            if validate_pax_code == True:
                #looking for the iddef_age_code & validate if exists the code in the property config age_range
                iddef_age_range = next((item["iddef_age_range"] for item in age_range_data\
                    if item["age_range_age_code"]["code"] == key), None)
                
                if iddef_age_range is None:
                    raise Exception("Pax code \"{}\" not exists in the property configuration".format(key))

            for pax_index, pax_item in enumerate(book_hotel_room.paxes):
                if pax_item.age_code == key:
                    flag_age_range=True
                    book_hotel_room.paxes[pax_index].total = value
                    book_hotel_room.paxes[pax_index].usuario_ultima_modificacion = room_data["user"]
            
            if not flag_age_range:
                pax_data = {
                    "iddef_age_range": iddef_age_range,
                    "age_code": key,
                    "pax": value,
                    "user": room_data["user"]
                }

                pax_room_element = self.create_pax_room(pax_data)
                book_hotel_room.paxes.append(pax_room_element)
        
        #get total price per day
        rate = self.info_rates(room_data)
        
        # list_rate = []
        # list_rate.append(rate)
        # calculate_rate = RatesFunctions.calcualte_total_rates(list_rate)

        book_hotel_room.rate_amount = round(rate["total"], 4)

        # promotion_amount, tax_amount = 0.0, 0.0
        # from_date = room_data["from_date"].date()
        # to_date = room_data["to_date"].date()

        book_hotel_room.country_fee = round(rate["country_fee"], 4) if not room_data["rates_fix"] else 0
        if not is_refund:
            book_hotel_room.amount_pending_payment = (book_hotel_room.amount_pending_payment - (book_hotel_room.total-rate["total"])) - room_data["total_to_paid_room"]
            book_hotel_room.amount_paid = book_hotel_room.amount_paid + room_data["total_to_paid_room"]
        else:
            #Nota: La modificación de los montos en el reembolso se realiza en el método que guarda los pagos
            #book_hotel_room.amount_pending_payment = rate["total"]
            #book_hotel_room.amount_paid = 0
            pass
        book_hotel_room.total = round(rate["total"], 4)
        book_hotel_room.promotion_amount = round(rate["promotion_amount"], 4) if not room_data["rates_fix"] else 0
        #book_hotel_room.paxes = pax_list
        book_hotel_room.adults = adults
        book_hotel_room.child = child

        # if book_hotel_room.total <= 0:
        #     raise Exception("Rate Plan not available")
        
        rates_array = []
        rates_array.append(rate)

        book_hotel_room.discount_percent = round(rate["total_percent_discount"], 2) if not room_data["rates_fix"] else 0
        book_hotel_room.discount_amount = round(rate["discount_amount"], 4) if not room_data["rates_fix"] else 0
        book_hotel_room.total_gross = round(rate["total_crossout"], 4) if not room_data["rates_fix"] else 0

        # Se desactivan todos los precios, en la siguiente sección se reactivan o se crean
        # De otra forma permance desactivado
        for room_price_index, room_price_item in enumerate(book_hotel_room.prices):
            book_hotel_room.prices[room_price_index].estado = 0
            book_hotel_room.prices[room_price_index].usuario_ultima_modificacion = book_hotel_room.usuario_ultima_modificacion

        #append room prices to audit
        list_prices = []
        for room_price_data in rate["price_per_day"]:
            price_promotion_amount, code_promotion = 0, ""
            if not room_data["rates_fix"] and room_price_data["promotions"] and len(room_price_data["promotions"]) > 0:
                price_promotion_amount = room_price_data["promotions"]["value_discount"]
                code_promotion = room_price_data["promotions"]["code"]
            price = (room_price_data["amount"] - room_price_data["tax_amount"]) if not room_data["rates_fix"] else room_price_data["amount"]
            price = price + price_promotion_amount
            discount_amount = (room_price_data["amount_crossout"] - room_price_data["amount"]) if not room_data["rates_fix"] else 0

            flag_price = False
            for room_price_index, room_price_item in enumerate(book_hotel_room.prices):
                if room_price_item.date.strftime('%Y-%m-%d') == room_price_data["efective_date"].strftime('%Y-%m-%d'):
                    flag_price = True
                    book_hotel_room.prices[room_price_index].price = round(price, 4)
                    book_hotel_room.prices[room_price_index].promo_amount = room_price_data["vaucher_discount"] if not room_data["rates_fix"] else 0
                    book_hotel_room.prices[room_price_index].price_to_pms = room_price_data["price_pms"]
                    book_hotel_room.prices[room_price_index].discount_percent = room_price_data["percent_discount"] if not room_data["rates_fix"] else 0
                    book_hotel_room.prices[room_price_index].discount_amount = round(discount_amount, 4)
                    book_hotel_room.prices[room_price_index].total_gross = room_price_data["amount_crossout"] if not room_data["rates_fix"] else 0
                    book_hotel_room.prices[room_price_index].country_fee = room_price_data["tax_amount"] if not room_data["rates_fix"] else 0
                    book_hotel_room.prices[room_price_index].total = room_price_data["amount"]
                    book_hotel_room.prices[room_price_index].promotion_amount = price_promotion_amount
                    book_hotel_room.prices[room_price_index].code_promotions = code_promotion
                    book_hotel_room.prices[room_price_index].estado = 1
                    book_hotel_room.prices[room_price_index].usuario_ultima_modificacion = book_hotel_room.usuario_ultima_modificacion

            if not flag_price:
                price_data = {
                    "date": room_price_data["efective_date"],
                    "price": round(price, 4),
                    "promo_amount":room_price_data["vaucher_discount"] if not room_data["rates_fix"] else 0,
                    "price_to_pms":room_price_data["price_pms"],
                    "discount_percent": room_price_data["percent_discount"] if not room_data["rates_fix"] else 0,
                    "discount_amount": round(discount_amount, 4),
                    "total_gross": room_price_data["amount_crossout"] if not room_data["rates_fix"] else 0,
                    "country_fee": room_price_data["tax_amount"] if not room_data["rates_fix"] else 0,
                    "total": room_price_data["amount"],
                    "promotion_amount": price_promotion_amount,
                    "code_promotion": code_promotion,
                    "price_to_pms": room_price_data["amount"],
                    "user": book_hotel_room.usuario_ultima_modificacion,
                }

                temp_room_obj = self.create_room_prices(price_data)
                temp_room_obj.promo_amount = room_price_data["vaucher_discount"] if not room_data["rates_fix"] else 0
                temp_room_obj.price_to_pms = room_price_data["price_pms"]
                book_hotel_room.prices.append(temp_room_obj)

        db.session.flush()

        return book_hotel_room
    
    def format_booking_info(self, book_hotel):
        """
            Genrate confirmation data
            :param book_hotel = book_hotel instance
        """
        lang_code = book_hotel.lang_code if book_hotel.lang_code else book_hotel.language.lang_code
        comment = ""
        if book_hotel.comments:
            '''
                check for exist comment
            '''
            book_comment = book_hotel.comments[0]
            comment = book_comment.text if book_comment.source == book_comment.source_public else ""

        '''
            format the pax node in rooms
        '''                
        cancelation_policies = []
        guarantee_policies = []
        tax_policies = []
        services = []
        config_data = {}
        address = ""
        resort_phone = ""
        resort_email = ""
        reservation_email = ""
        promo_code_text = ""
        property_contact = self.get_property_contact_data(book_hotel.iddef_property, lang_code)

        if property_contact:
            address = Util.format_address_property(property_contact)
            resort_phone = Util.format_phone_property(property_contact)
            resort_email = property_contact["email"]
            reservation_email = property_contact["property_email"]

        for room in book_hotel.rooms:
            paxes_code = {}
            
            for pax in room.paxes:
                age_text = ""
                try:
                    age_text = FunctionsAgeRange.get_age_range_lang(iddef_property=book_hotel.iddef_property,\
                    lang_code=lang_code,iddef_age_range=pax.iddef_age_range)
                    if age_text is None or len(age_text) == 0:
                        age_text = pax.age_code
                except Exception as ageEx:
                    pass
                paxes_code.update({pax.age_code: {"value": pax.total, "text": age_text}})
            
            room.pax = paxes_code                
            room.trade_name_room = ""            
            #get room category trade name
            text_lang = RatesFunctions.getTextLangInfo("def_room_type_category", "room_name", lang_code, room.iddef_room_type)
            if text_lang is not None:
                room.trade_name_room = text_lang.text
            
            rateplan_name = RatesFunctions.getTextLangInfo("op_rateplan", "commercial_name", lang_code, room.idop_rate_plan)
            if rateplan_name is not None:
                room.rateplan_name = rateplan_name.text

            room.media = self.get_media_room(room.iddef_room_type)

            #check if exists to avoid getting data again
            police_found = next((policy for policy in cancelation_policies if room.iddef_police_cancelation == policy["iddef_policy"]), None)
            if police_found is None:
                cancel_policy = FunctionsPolicy.get_policy_lang(room.iddef_police_cancelation, lang_code, True)
                if cancel_policy is not None:
                    cancel_policy["iddef_policy"] = room.iddef_police_cancelation
                    cancelation_policies.append(cancel_policy)

            police_guarantee_found = next((policy for policy in guarantee_policies if room.iddef_police_guarantee == policy["iddef_policy"]), None)
            if police_guarantee_found is None:
                guarantee_policy = FunctionsPolicy.get_policy_lang(room.iddef_police_guarantee, lang_code, False)
                if guarantee_policy is not None:
                    guarantee_policy["iddef_policy"] = room.iddef_police_guarantee
                    guarantee_policies.append(guarantee_policy)

            tax_found = next((policy for policy in tax_policies if room.iddef_police_tax == policy["iddef_policy"]), None)
            if tax_found is None:
                tax_policy = FunctionsPolicy.get_policy_lang(room.iddef_police_tax, lang_code, False)
                if tax_policy is not None:
                    tax_policy["iddef_policy"] = room.iddef_police_tax
                    tax_policies.append(tax_policy)

        total_service = 0
        FunctionService = FunctionsService()
        for service in book_hotel.services:
            if service.estado == 1:
                total_service += service.total
            service_data = FunctionService.get_service_by_lang(service.iddef_service, lang_code)
            
            if service_data:
                media = self.get_service_media(service.iddef_service, lang_code, book_hotel.iddef_property)
                
                service_info = {
                    "iddef_service": service.iddef_service,
                    "name": service_data["name"],
                    "teaser": service_data["teaser"],
                    "description": service_data["description"],
                    "icon_description": service_data["name_html_icon"],
                    "media": media
                }
                services.append(service_info)
        
        payment_data = {}
        if book_hotel.idbook_status in [BookStatus.confirmed, BookStatus.changed, BookStatus.interfaced, BookStatus.partial_interfaced]:
            if book_hotel.payments:
                payment = book_hotel.payments[0]
                payment_data["card_type"] = payment.card_code
            
        config_params = self.get_config_params(("check_in", "check_out"))        
        for row in config_params:
            config_data[row.param] = row.value

        if book_hotel.promo_codes:
            if book_hotel.promo_codes[0].is_text:
                promo_code = PromoCodeFunctions.search_promocode(book_hotel.promo_codes[0].promo_code)
                if promo_code:
                    promo_code_text = RatesFunctions.getTextLangInfo("def_promo_code", "description", lang_code, promo_code.iddef_promo_code)
        
        data = {
            "property_code": book_hotel.property.property_code,
            "brand_code": book_hotel.property.brand.code,
            "iddef_brand": book_hotel.property.iddef_brand,
            "trade_name": book_hotel.property.trade_name,
            "web_address": book_hotel.property.web_address,
            "sender": book_hotel.property.sender,
            "address": address,
            "resort_phone": resort_phone,
            "resort_email": resort_email,
            "reservation_email": reservation_email,
            "from_date": book_hotel.from_date,
            "to_date": book_hotel.to_date,
            "nights": book_hotel.nights,
            "total_rooms": book_hotel.total_rooms,
            "market_code": book_hotel.market_segment.code,
            "country_code": book_hotel.country.country_code,
            "iddef_channel": book_hotel.iddef_channel,
            "channel_url": book_hotel.channel.url,
            "lang_code": lang_code,
            "currency_code": book_hotel.currency.currency_code,
            "promo_code": book_hotel.promo_codes[0].promo_code if book_hotel.promo_codes else "",
            "special_request": comment,
            "on_hold": book_hotel.idbook_status == BookStatus.on_hold,
            "customer": book_hotel.customers[0].customer,
            "rooms": book_hotel.rooms,
            "code_reservation": book_hotel.code_reservation,
            "status": book_hotel.status_item.name,
            "idbook_status": book_hotel.idbook_status,
            "exchange_rate": book_hotel.exchange_rate,
            "discount_percent": book_hotel.discount_percent,
            "discount_amount": book_hotel.discount_amount, 
            "total_gross": book_hotel.total_gross,
            "total": book_hotel.total,
            "amount_pending_payment": book_hotel.amount_pending_payment,
            "amount_paid": book_hotel.amount_paid,
            "country_fee": book_hotel.country_fee,
            "total_service": total_service,
            "expiry_date": book_hotel.expiry_date if book_hotel.idbook_status == BookStatus.on_hold else None,
            "property_media":self.get_media_property(book_hotel.iddef_property),
            "cancelation_policies": cancelation_policies,
            "guarantee_policies": guarantee_policies,
            "tax_policies": tax_policies,
            "services_info": services,
            "payment": payment_data,
            "general_data": config_data,
            "promo_amount": book_hotel.promo_amount,
            "fecha_creacion": book_hotel.fecha_creacion,
            "modification_date_booking": book_hotel.modification_date_booking,
            "promo_code_text": promo_code_text,
            "visible_reason_cancellation": book_hotel.visible_reason_cancellation,
            "reason_cancellation" : book_hotel.rooms[0].reason_cancellation
        }
        
        schema = BookHotelReservationResponseSchema(only=["sender","property_code", "brand_code", "trade_name", "iddef_brand", "country_code", "market_code", "iddef_channel", "lang_code",\
            "currency_code", "from_date", "to_date", "promo_code", "payment", "on_hold",\
            "special_request", "customer", "code_reservation", "status", "idbook_status",\
            "exchange_rate", "discount_percent", "discount_amount", "promo_amount", "total_gross", "nights", "total_rooms",\
            "total", "country_fee", "total_service", "expiry_date", "rooms", "property_media", "cancelation_policies", "guarantee_policies", \
            "tax_policies", "services_info", "payment", "general_data", "web_address", "address", "resort_phone", "resort_email", "reservation_email", \
            "channel_url", "amount_pending_payment", "amount_paid", "fecha_creacion", "modification_date_booking", "promo_code_text", "visible_reason_cancellation","reason_cancellation"])

        return schema.dump(data)
  
    @classmethod
    def get_property_contact_data(cls, iddef_property, lang_code = "EN"):
        """
            Contact information by property id
            :param iddef_property = id Property
            :param lang_code = language code
        """
        lang_code = lang_code.upper()
        query = """            
            SELECT c.first_name, c.last_name, a.address, a.zip_code,
            a.city, a.state_code, a.country_code, country.iddef_country,
            cont_phone.country, cont_phone.area,
            cont_phone.number, cont_phone.extension, cont_email.email,
            property_email.email AS property_email
            FROM def_contact_property cp
            INNER JOIN def_contact c on c.iddef_contact = cp.iddef_contact
                AND c.iddef_contact_type = 1 AND c.estado = 1
            INNER JOIN def_address a on a.iddef_contact = c.iddef_contact
                AND c.iddef_contact_type = 1 AND c.estado = 1
            INNER JOIN def_contact_phone cont_phone on cont_phone.iddef_contact = c.iddef_contact
                AND cont_phone.iddef_phone_type = 4 AND cont_phone.estado = 1
            INNER JOIN def_email_contact cont_email on cont_email.iddef_contact = c.iddef_contact
                AND cont_email.email_type = 3 AND cont_email.estado = 1
            LEFT JOIN def_email_contact property_email on property_email.iddef_contact = c.iddef_contact
                AND property_email.email_type = 1 AND property_email.estado = 1   
            INNER JOIN def_country country on country.country_code = a.country_code
            WHERE cp.iddef_property = {iddef_property} AND cp.estado = 1
            """.format(iddef_property = iddef_property)
        result = db.session.execute(query)
        item = {}

        for first_name, last_name, address, zip_code, city, state_code, country_code,\
            iddef_country, country, area, number, extension, email, property_email in result:
            textInfo = RatesFunctions.getTextLangInfo("def_country", "name", lang_code, iddef_country)

            item = {
                "first_name": first_name,
                "last_name": last_name,
                "address": address,
                "zip_code": zip_code,
                "city": city,
                "state_code": state_code,
                "country_code": country_code,
                "country": country,
                "area": area,
                "number": number,
                "extension": extension,
                "email": email,
                "property_email": property_email,
                "country_name": textInfo.text if textInfo else ""
            }
            break
        
        return item

    def formatDate(self, fecha, isHold , lang):
        if isHold == True:
        
            y = fecha.split(" ")
            date = y[0]
            times = y[1] 
            dateSplit = date.split("-")
            dateCast = datetime.datetime(int(dateSplit[0]), int(dateSplit[1]), int(dateSplit[2]))
            try:
                if lang == "ES":
                    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
                else:
                    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
                return times + " " + dateCast.strftime('%d %b, %Y')
            except:
                return times + " " + dateCast.strftime('%d %b, %Y')

        else:
            #fecha = "2020-06-13"
            y = fecha.split("-")
            x = datetime.datetime(int(y[0]), int(y[1]), int(y[2]))
            if lang == "ES":
                locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            else:
                locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            return x.strftime('%d %b, %Y')     

    def format_booking_letter(self, book_hotel, is_remember = False):
        """
            Format booking data for confirmation letter
            :param book_hotel = book_hotel instance
        """
        booking_data = self.format_booking_info(book_hotel)
        #textos por idioma
        subject = ""
        tituloUno = ""
        tituloDos = ""
        tituloClienteUno = ""
        tituloClienteDos = ""
        tituloPagoUno = ""
        tituloPagoDos = ""
        tituloConfirmacionUno = ""
        tituloConfirmacionDos = ""
        tx_nombre = "" 
        tx_numero = ""
        tx_correo = ""
        tx_requerimiento =""
        tx_monto = ""
        tx_cartType = ""
        tx_balance = ""
        tx_deposit = ""
        tx_avisoUno = ""
        tx_avisoDos = ""
        tx_avisoTres = ""
        tx_avisoCuatro = ""
        tx_bookingUno = ""
        tx_bookingDos = ""
        bi_llegadaFecha = ""
        bi_salidaFecha = ""
        bi_llegadaHora = ""
        bi_salidaHora = ""
        bi_noches = ""
        bi_cuartos = ""
        bi_avisoUno = ""
        bi_avisoDos = ""
        serUno = ""
        serDos = ""
        servicio = ""
        servicioDos = ""
        beneUno = ""
        beneDos = ""
        poliUno = ""
        poliDos = ""
        tx_avisoTres_2 = ""

        rateUno = ""
        rateDos = ""
        tx_room = ""

        tx_holdUno = ""
        tx_holdDos = ""
        tx_holdTres = ""

        datos_footer = ""

        propertiMap = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-15-19-22-353011CozumelFinal.png"
        iconLocation = ""
        iconEmail = ""
        iconPhone = ""
        iconWeb = ""
        text_location = booking_data["address"]
        text_web = booking_data["web_address"]
        text_phone = booking_data["resort_phone"]
        text_emailReverva = booking_data["reservation_email"]
        text_emailResort = booking_data["resort_email"]
        imgPurely = ""
        book_email = "bookdirect@palaceresorts.com"
        url_amenities= {
            "moon": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-21-10-11-29-33-142011Servicios_MN-EN.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-21-10-11-30-29-335446Servicios_MN-ES.png" 
                },
            "palace": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-20-10-14-19-18-720395Servicios_pr-EN.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-20-10-14-19-26-846321Servicios_pr-ES.png" 
                },
            "leblanc": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-20-10-14-17-28-589302Servicios_LB-EN.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-20-10-14-18-41-984660Servicios_LB-ES.png" 
                },
        }
        dictHeader = {
            "ZHBP": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-46-25-784679header_BEACHPALACE.png",
            "ZHSP": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-44-09-055169header-sunpalace.png",
            "ZHIM": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-47-53-609018header_IslaMujeres.png",
            "ZRPL": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-50-22-481438header_Playacar.png",
            "ZRCZ": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-47-35-717512header_Cozumel.png",
            "ZMSU": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-49-51-101055header_MoonPalace.png",
            "ZMGR": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-50-49-200988header_TheGrand.png",
            "ZCJG": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-48-08-530524header_jamaica.png",
            "ZHLB": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-48-53-205125header_LBC.png",
            "ZPLB": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-49-36-041442header_LBL.png",
            "ZMNI": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-50-05-218861header_nizuc.png"
            }
        dictFamilia = {
            "ZHBP": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/guestPalace.png",
            "ZHSP": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-46-09-424970img-pareja_SUN.png",
            "ZHIM": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-22-964201img-pareja_ISLA.png",
            "ZRPL": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-44-50-331049img-fam_PLAYACAR.png",
            "ZRCZ": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-38-544572img-pareja_Cozumel.png",
            "ZMSU": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-51-04-189342img-alberca-moon.png",
            "ZMGR": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-51-18-273585img-fam-TheGrand.png",
            "ZCJG": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-44-36-906474img-fam_Jamaica.png",
            "ZHLB": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-21-09-08-53-03-758329img-meditacion-lbC.jpg",
            "ZPLB": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-54-730283img-pareja_LBC.png",
            "ZMNI": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-51-04-189342img-alberca-moon.png"
            }
        dictPurely = {
            "moon": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-21-31-111161Purely_Moon-ES.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-20-58-818237Purely_Moon-EN.png" 
                },
            "palace": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-22-56-562154Purely_PR-ES.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-22-18-098360Purely_PR-EN.png" 
                },
            "leblanc": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-20-31-874344Purely_LBC-ES.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-19-09-844133Purely_LBC-EN.png" 
                },

            }
        appQR = {
            "moon": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-28-09-16-45-26-743628App-Moon-ES.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-28-09-16-45-05-569718App-Moon-EN.png" 
                },
            "palace": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-28-09-16-43-17-065943App-Palace-ES.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-28-09-16-44-11-832487App-Palace-EN.png" 
                },
            "leblanc": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-28-09-16-44-46-722338App-LB-ES.png", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-28-09-16-44-29-923596App-LB-EN.png" 
                },

            }
        footer = {
            "moon": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/footerTwo.png",
            "palace": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/footerDosPalace.png",
            "leblanc": "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/footerTwo.png"
            }   
        

        if booking_data["lang_code"].upper() == "ES":
            
            if booking_data["on_hold"] == True:
                if is_remember == True:
                    tituloUno = "Te queda poco tiempo"
                    tituloDos = "Confirma tu estadía en  "+booking_data["trade_name"]+" antes de que tu reserva expire"
                else:
                    tituloUno = "No olvides completar tu reservación "
                    tituloDos = "Tu reserva para "+booking_data["trade_name"]+" permanecerá en espera por 24 horas." 
            elif booking_data["status_code"] == BookStatus.expired:
                tituloUno = "Qué pena, ya expiró tu reservación en espera"
                tituloDos = "Busca nuestras tarifas actualizadas y haz una nueva reserva para "+booking_data["trade_name"]   
            else:
                tituloUno = "Es momento de hacer tus maletas "
                tituloDos = "Te esperamos en "+booking_data["trade_name"]
            tituloClienteUno = "Información del "
            tituloClienteDos = "huésped"
            tituloPagoUno = "Información de "
            tituloPagoDos = "tarjeta de crédito"
            tituloConfirmacionUno = "Tu Clave de "
            tituloConfirmacionDos = "Confirmación del Hotel"
            tx_nombre = "Nombre:" 
            tx_numero = "Número de teléfono:"
            tx_correo = "Correo electrónico:"
            tx_requerimiento ="Solicitud especial:"
            tx_monto = "Cantidad pagada:"
            tx_cartType = "Tipo de tarjeta:"
            tx_balance = "Saldo pendiente:"
            tx_deposit = "Deposito: "
            tx_avisoUno = "* Las habitaciones se asignan al momento de realizar el check-in y Las solicitudes especiales están sujetas a disponibilidad."
            tx_avisoDos = "Debes proporcionar una tarjeta de crédito en tu check-in, para cubrir cualquier imprevisto."
            btn_reservation_onHold = "COMPLETA TU RESERVA"
            if booking_data["market_code"] != "MEXICO":
                tx_avisoTres = "Todos los pagos solo en dólares estadounidenses."
            tx_avisoTres_1 = "Cualquier tasa de conversión de moneda aplicable es responsabilidad del huésped"
            tx_avisoTres_2 = "Es responsabilidad del huésped notificar y pagar por adelantado a todas las personas en la habitación"
            tx_avisoCuatro = "" #"El huésped es responsable de notificar y pagar la estadía de todas las personas que se hospedan en cada habitación."
            tx_bookingUno = "Información de "
            tx_bookingDos = " la reserva"
            bi_llegadaFecha = "Fecha de llegada:"
            bi_salidaFecha = "Fecha de salida:"
            bi_llegadaHora = "Hora de entrada:"
            bi_salidaHora = "Hora de salida:"
            bi_noches = "Núm. de noches:"
            bi_cuartos = "Núm. de habitaciones:"
            bi_avisoUno = ""
            bi_avisoDos = ""
            serUno = "UN NUEVO NIVEL "
            serDos = "DE TODO INCLUIDO"
            servicio = "Nada será igual después de que experimentes nuestros altos estándares en lujo todo incluido. Disfruta amenidades que rebasan todas tus expectativas, como bebidas de alta gama ilimitadas, servicio a la habitación gourmet las 24 horas, WiFi de alta velocidad gratis, amenidades de baño marca CHI, llamadas gratuitas ilimitadas a los EE. UU. continentales, Canadá y teléfonos fijos de México, y mucho más."
            servicioDos = "Si tienes alguna duda o deseas modificar o cancelar tu reserva, por favor escríbenos a "
            beneUno = "Beneficios "
            beneDos = "adicionales"
            poliUno = "POLÍTICA DE "
            poliDos = "CANCELACIONES"

            tx_holdUno = "TU RESERVA EN " + booking_data["trade_name"].upper() + " ESTÁ EN ESPERA"
            tx_holdDos = "COMPLETE TU RESERVA ANTES DE " #+ self.formatDate(booking_data["expiry_date"], True, booking_data["lang_code"].upper() ) 
            tx_holdTres = "LA RESERVA EXPIRARÁ AUTOMÁTICAMENTE DESPUÉS DE ESTE TIEMPO"
            
            tx_expiredUno = "RESERVA EN ESPERA EXPIRADA"
            tx_expiredDos = "GRACIAS POR SU INTERÉS EN " + booking_data["trade_name"].upper() +". LAMENTAMOS INFORMARLE QUE TU RESERVA EN ESPERA EXPIRÓ."

            rateUno = "Tarifa por "
            rateDos = "noche"
            tx_room = "Habitación"

            if booking_data["on_hold"] == True:                
                if is_remember:
                    subject += "Completa tu reservación antes de que pierdas tus beneficios"
                else:
                    subject += "Recuerda completar tu reserva antes de 24 horas"
            elif booking_data["status_code"] == BookStatus.expired:
                subject = "Oh no, tu reservación ya expiró."
            else:
                subject += "Gracias por reservar en " + booking_data["trade_name"]
        else :

            if booking_data["on_hold"] == True:
                if is_remember == True:
                    tituloUno = "Not long left"
                    tituloDos = "Confirm your stay at "+booking_data["trade_name"]+" before your on-hold reservation expires"
                else:
                    tituloUno = "Don’t forget to complete your booking "
                    tituloDos = "Your reservation at "+booking_data["trade_name"]+" has been placed on hold for 24 hours"  
            
            elif booking_data["status_code"] == BookStatus.expired:
                tituloUno = "Oh dear, your on-hold offer has expired"
                tituloDos = "Browse our updated rates and make a new booking at  "+booking_data["trade_name"]
              
            else:
                tituloUno = "Thank you for choosing "
                tituloDos = "Your unforgettable holidays are already on the way."
            
            tituloClienteUno = "Guest"
            tituloClienteDos = "Information"
            tituloPagoUno = "Credit Card "
            tituloPagoDos = "Information"
            tituloConfirmacionUno = "Your Hotel "
            tituloConfirmacionDos = "Confirmation Code"
            tx_nombre = "Name:" 
            tx_numero = "Phone Number:"
            tx_correo = "Email:"
            tx_requerimiento ="Personalized Request:"
            tx_monto = "Amount Paid:"
            tx_cartType = "Card type:"
            tx_balance = "Outstanding balance:"
            tx_deposit = "Deposit: "
            if booking_data["status_code"] != BookStatus.expired:
                tx_avisoUno = "*Rooms are assigned at check-in and special requests are subject to availability."
                tx_avisoDos = "A credit card must be provided at check-in for room incidentals."
            btn_reservation_onHold = "COMPLETE YOUR RESERVATION"
            if booking_data["market_code"] != "MEXICO":
                tx_avisoTres = "Payments in US dollars only."
            tx_avisoTres_1 = "Guests are responsible for covering any applicable conversion rate and for notifying and paying in advance for all people in room."
            tx_avisoCuatro = "" #"The guest is responsible for notifying and paying for the stay of all the people who stay in each room."
            tx_bookingUno = "Booking "
            tx_bookingDos = " Information"
            bi_llegadaFecha = "Arrival Date:"
            bi_salidaFecha = "Departure Date:"
            bi_llegadaHora = "Check-In Time:"
            bi_salidaHora = "Check-Out Time:"
            bi_noches = "No. of Nights:"
            bi_cuartos = "No. of Rooms:"
            bi_avisoUno = ""
            bi_avisoDos = ""
            serUno = "YOUR AWE-INCLUSIVE "
            serDos = "BENEFITS"
            servicio = "After experiencing our standard of all-inclusive luxury, anything less will be inacceptable. Enjoy signature inclusions of our luxurious accommodations, including top-shelf sips, 24-hour room service, free WiFi, CHI bath amenities, unlimited calls to the Continental US, Canada and Mexico, and much more."
            servicioDos = "If you have any queries or wish to modify or cancel your reservation, please contact "
            beneUno = "Additional"
            beneDos = "Benefits"
            poliUno = "CANCELLATION "
            poliDos = "POLICY"
            tx_holdUno = "YOUR BOOKING AT " + booking_data["trade_name"].upper() + " IS ON HOLD"
            tx_holdDos = "COMPLETE YOUR BOOKING BEFORE " #+ self.formatDate( booking_data["expiry_date"], True, booking_data["lang_code"].upper() ) 
            tx_holdTres = "THE BOOKING WILL AUTOMATICALLY EXPIRE AFTER THIS TIME"
            
            tx_expiredUno = "ON HOLD BOOKING EXPIRED"
            tx_expiredDos = "THANK YOU FOR YOU INTEREST IN " + booking_data["trade_name"].upper() +". WE REGRET TO INFORM YOU THAT YOUR ON HOLD BOOKING HAS EXPIRED."

            rateUno = "Rate per "
            rateDos = "night"
            tx_room = "Room"

            if booking_data["on_hold"] == True:
                if is_remember:
                    subject += "Act quickly before your benefits expire"
                else:
                    subject += "Remember to complete your booking within 24 hours"
            elif booking_data["status_code"] == BookStatus.expired:
                subject = "Oh dear, your on-hold booking just expired"
            else:
                subject += "Thank you for booking at " + booking_data["trade_name"]

        html_footer=""
        html_services=""
        html_rooms = ""
        on_hold = ""
        url_base = booking_data["channel_url"]
        url_on_Hold = url_base+"?name="+booking_data['customer']['first_name']+"%20"+booking_data['customer']['last_name']+"&code="+booking_data['code_reservation']
        on_hold_2 = ""
        colorBtn = ""
        carta = ""

        #Moon(dorado negro)
        if booking_data["iddef_brand"] == 3:
            imgPurely = dictPurely["moon"][booking_data["lang_code"].upper()]
            carta = "NOTIFICATION_BENGINE_CARTA_MOON"
            qr = appQR["moon"][booking_data["lang_code"].upper()]
            footerCarta = footer["moon"]
            colorBtn = "#AA9070"
            iconLocation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-14-45-703787Location.png"
            iconEmail = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-15-00-939158E-mail.png"
            iconPhone = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-14-11-776814Phone_number.png"
            iconWeb = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-13-31-608305web.png"
            amenities = url_amenities["moon"][booking_data["lang_code"].upper()]
            clockIcon = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-23-09-08-58-53-885538Reloj-Dorado.png"            
        #Moon(naranja negro)
        if booking_data["iddef_brand"] == 1:
            imgPurely = dictPurely["leblanc"][booking_data["lang_code"].upper()]
            carta = "NOTIFICATION_BENGINE_CARTA_LEBLANC"
            qr = appQR["leblanc"][booking_data["lang_code"].upper()]
            footerCarta = footer["leblanc"]  
            colorBtn = "#F78F1E"
            iconLocation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-19-21-290643Location_LB.png"
            iconEmail = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-19-37-412912E-mail_LB.png"
            iconPhone = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-19-09-077168Phone_number_LB.png"
            iconWeb = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-18-38-651292web_LB.png"                  
            amenities = url_amenities["leblanc"][booking_data["lang_code"].upper()]
            clockIcon = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-23-09-08-58-28-162277Reloj-Naranja-Morado.png"
         #Palace(verde negro)
        if booking_data["iddef_brand"] == 2:
            imgPurely = dictPurely["palace"][booking_data["lang_code"].upper()]
            carta = "NOTIFICATION_BENGINE_CARTA_PALACE"
            qr = appQR["palace"][booking_data["lang_code"].upper()]
            footerCarta = footer["palace"]
            colorBtn = "#4296c4"
            iconLocation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-06-46-603406Location.png"
            iconEmail = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-06-15-137005E-mail.png"
            iconPhone = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-07-00-658284Phone_number.png"
            iconWeb = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-07-17-273578web.png"       
            amenities = url_amenities["palace"][booking_data["lang_code"].upper()]
            clockIcon = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-22-09-10-23-15-263336Reloj-On_Hold.png"
        #on hold
        if booking_data["on_hold"] == True:                                
            on_hold = "<tr> <td style='font-size:0px;word-break:break-word;'><!--[if mso | IE]> <table role='presentation' border='0' cellpadding='0' cellspacing='0'> <tr> <td height='10' style='vertical-align:top;height:10px;'><![endif]--> <div style='height:10px;'> &nbsp;</div><!--[if mso | IE]> </td></tr></table><![endif]--> </td></tr><tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:gothamLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;line-height:1;text-align:center;color:main-color;'> <h3 style='color:"+colorBtn+";'>"+tx_holdUno+"</h3> </div></td></tr>" + " <tr style='width: 78%;float: left;text-align: justify;'> <td><img src='"+clockIcon+"' style='width: 55px;float: left;height: 43px;' class='img-fluid op7' alt='Responsive image'></td><td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='width: 138%; font-family:gothamLigth, Roboto Condensed, Roboto, Helvetica;font-size:10px;font-weight:bold;line-height:1;text-align:justify;color:#000000;'>"+tx_holdDos + self.formatDate(booking_data["expiry_date"], True, booking_data["lang_code"].upper()) +"<br></br>"+ tx_holdTres+"</div></td></tr>"
            on_hold_2 = "<a href="+url_on_Hold+"><button type='button' style='background-color: "+colorBtn+"; color: white; width: 78%; border: none; height: 40px;'>"+btn_reservation_onHold+"</button></a>"
        elif booking_data["status_code"] == BookStatus.expired:
            on_hold = "<tr> <td style='font-size:0px;word-break:break-word;'><!--[if mso | IE]> <table role='presentation' border='0' cellpadding='0' cellspacing='0'> <tr> <td height='10' style='vertical-align:top;height:10px;'><![endif]--> <div style='height:10px;'> &nbsp;</div><!--[if mso | IE]> </td></tr></table><![endif]--> </td></tr><tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;line-height:1;text-align:center;color:main-color;'> <p>"+tx_expiredUno+"</p></div></td></tr><tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:10px;font-weight:bold;line-height:1;text-align:center;color:#000000;'>"+tx_expiredDos + "</div></td></tr><tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:10px;font-weight:bold;line-height:1;text-align:center;color:main-color;'></div></td></tr>"
        else:
            on_hold = "<tr><td align='center' style='font-size:0px;padding:10px 25px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'><p class='main-color'>"+tituloPagoUno+" <span class='main-color'>"+tituloPagoDos+"</span></p></div></td></tr><tr><td style='font-size:0px;padding:0px;word-break:break-word;'> <!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:300px;' width='300' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:300px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='width:300px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td style='vertical-align:top;width:150px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='left' style='font-size:0px;padding:5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'><p class='grey-color'>"+str(tx_cartType)+"</p></div></td></tr></table></div> <!--[if mso | IE]></td><td style='vertical-align:top;width:150px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='left' style='font-size:0px;padding:5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'><p>"+booking_data['payment']['card_type'].upper() +"</p></div></td></tr></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr><tr><td style='font-size:0px;padding:0px;word-break:break-word;'> <!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:300px;' width='300' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:300px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='width:300px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td style='vertical-align:top;width:150px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='left' style='font-size:0px;padding:5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'><p class='grey-color'>"+str(tx_monto)+"</p></div></td></tr></table></div> <!--[if mso | IE]></td><td style='vertical-align:top;width:150px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='left' style='font-size:0px;padding:5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'><p>"+booking_data['currency_code']+' $'+ str(booking_data['amount_paid'])+"</p></div></td></tr></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr><tr><td style='font-size:0px;padding:0px;word-break:break-word;'> <!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:300px;' width='300' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:300px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='width:300px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td style='vertical-align:top;width:150px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='left' style='font-size:0px;padding:5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'><p class='grey-color'>"+str(tx_balance)+"</p></div></td></tr></table></div> <!--[if mso | IE]></td><td style='vertical-align:top;width:150px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='left' style='font-size:0px;padding:5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'><p style='color:#ff0000;'>"+booking_data['currency_code']+' $'+ str(booking_data['amount_pending_payment'])+"</p></div></td></tr></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr>"

        #footer
        datos_footer= "<tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center; background-color: #e4e4e4;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='vertical-align:middle;width:300px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:middle;' width='100%'><tr><td align='center' style='font-size:0px;padding:10px 5px;word-break:break-word;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'><tbody><tr><td style='width:290px;'></td></tr></tbody></table></td></tr></table></div> <!--[if mso | IE]></td><td class='' style='vertical-align:middle;width:300px;' ><![endif]--><div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:middle;' width='100%'><tr><td align='justify' style='font-size:0px;padding: 5px 10px 5px 0px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:justify;color:#000000;'><p style='display: flex; align-items: center;'><img src='"+iconLocation+"' style='height: 25px; width: auto; margin: 7px;' /> "+text_location+"</p></div></td></tr><tr><td align='justify' style='font-size:0px;padding: 5px 10px 5px 0px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:justify;color:#000000;'><p style='display: flex; align-items: center;'><img src='"+iconWeb+"' style='height: 25px; width: auto; margin: 7px;' /> "+text_web+"</p></div></td></tr><tr><td align='justify' style='font-size:0px;padding: 5px 10px 5px 0px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:justify;color:#000000;'><p style='display: flex; align-items: center;'><img src='"+iconPhone+"' style='height: 25px; width: auto; margin: 7px;' /> "+text_phone+"</p></div></td></tr><tr><td align='justify' style='font-size:0px;padding: 5px 10px 5px 0px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:justify;color:#000000;'><p style='display: flex; align-items: center;'><img src='"+iconEmail+"' style='height: 25px; width: auto; margin: 7px;' /> "+text_emailReverva+"</p></div></td></tr><tr><td align='justify' style='font-size:0px;padding: 5px 10px 5px 0px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:justify;color:#000000;'><p style='display: flex; align-items: center;'><img src='"+iconEmail+"' style='height: 25px; width: auto; margin: 7px;' /> "+text_emailResort+"</p></div></td></tr></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr>"

        html_footer="<div> <!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:600px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='vertical-align:top;width:600px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='center' style='font-size:0px;padding:10px 0px;word-break:break-word;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'><tbody><tr><td style='width:600px;'><img height='auto' src='"+imgPurely+"' style='border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;' width='600'></td></tr></tbody></table></td></tr><tr><td style='font-size:0px;word-break:break-word;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td height='50' style='vertical-align:top;height:50px;'><![endif]--><div style='height:50px;'>&nbsp;</div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr><tr><td align='center' style='font-size:0px;padding:10px 0px;word-break:break-word;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'><tbody><tr><td style='width:300px;'><img height='auto' src='"+qr+"' style='border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;' width='300'></td></tr></tbody></table></td></tr><tr><td style='font-size:0px;word-break:break-word;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td height='50' style='vertical-align:top;height:50px;'><![endif]--><div style='height:50px;'>&nbsp;</div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr><tr><td align='center' style='font-size:0px;padding:10px 0px;word-break:break-word;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'><tbody> "+datos_footer+"<tr><td style='width:600px;'><img height='auto' src='"+footerCarta+"' style='border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;' width='600'></td></tr></tbody></table></td></tr></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></div>"
        #servicios
        columnas_services = ""
        services = booking_data["services_info"]
        inicio = 0
        salida = len(services)
        while inicio < salida:
            i = inicio
            union = ""
            while i < inicio+2:
                                            
                try:
                    if len(services[i]["media"]) > 0:
                        union = union +"<div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:10px 5px;word-break:break-word;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'> <tbody> <tr> <td style='width:290px;'> <img height='auto' src='"+services[i]["media"][0]["url"]+"' width='290' /> </td></tr> </tbody></table> </td></tr><tr><td align='center' style='font-size:0px;padding:10px 25px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'><b><p class='main-color'>Complimentary <span class='main-color'>"+ services[i]["name"] +"</span></p></b></div></td></tr><tr><td align='left' style='font-size:0px;padding:10px 5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'>"+ services[i]["description"] +"</div></td></tr></table></div>"
                    else: 
                        union = union +"<div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:10px 5px;word-break:break-word;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'> <tbody> <tr> <td style='width:290px;'> <img height='auto' src='https://d1.awsstatic.com/case-studies/PALACE-RESORTS.65dfce304db6469e4e2ffb31ba060ebed5dbc9f3.png' width='290' /> </td></tr> </tbody></table> </td></tr><tr><td align='center' style='font-size:0px;padding:10px 25px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'><b><p class='main-color'>Complimentary <span class='main-color'>"+ services[i]["name"] +"</span></p></b></div></td></tr><tr><td align='left' style='font-size:0px;padding:10px 5px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:left;color:#000000;'>"+ services[i]["description"] +"</div></td></tr></table></div>"
                except:
                    union = union + "<div class='mj-column-per-50 mj-outlook-group-fix ' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> </table></div>"
                i += 1
            columnas_services = columnas_services + union 
            inicio += 2
        html_services ="<div style=''><!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' > <tr> <td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--> <div style='margin:0px auto;max-width:600px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody> <tr> <td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr> <td class='' style='vertical-align:top;width:300px;'> <![endif]-->"+ columnas_services +"<!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div><!--[if mso | IE]></td></tr></table><![endif]--></div>"
        if salida > 0 :
            html_services = "<div><!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:600px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='vertical-align:top;width:600px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td style='font-size:0px;padding:10px 25px;word-break:break-word;'><p style='border-top:solid 1px #E0E0E0;font-size:1px;margin:0px auto;width:100%;'></p><!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' style='border-top:solid 1px #E0E0E0;font-size:1px;margin:0px auto;width:550px;' role='presentation' width='550px' ><tr><td style='height:0;line-height:0;'> &nbsp;</td></tr></table><![endif]--></td></tr></table></div><!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div><!--[if mso | IE]></td></tr></table><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:600px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='vertical-align:top;width:600px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='center' style='font-size:0px;padding:10px 25px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'><b><p class='main-color'>"+beneUno+" <span class='main-color'>" + beneDos+" </span></p></b></div></td></tr></table></div><!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div><!--[if mso | IE]></td></tr></table><![endif]--></div>" + html_services

        #cuartos tarifas
        for index, cliente in enumerate(booking_data["rooms"]):
            #datos habitaciones
            paxes = cliente["pax"]

            inicio = 0
            salida = len(paxes)
            columnas_pax = ""
            section_pax = ""

            while inicio < salida:
                i = inicio
                union = ""
                while i < inicio+2:
                    key_pax = list(paxes)
                    try:
                        union = union + "<div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:gothamLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'> <p style='color:grey-color;'>"+ cliente["pax"][key_pax[i]]["text"] +": <span style='color:#000000'>" + str(cliente["pax"][key_pax[i]]["value"]) + "</span></p></div></td></tr></table> </div><!--[if mso | IE]></td><td style='vertical-align:top;width:150px;' ><![endif]-->"
                    except:
                        union = union + "<div class='mj-column-per-50 mj-outlook-group-fix ' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> </table></div>"
                    i += 1
                columnas_pax = columnas_pax + union
                inicio += 2
                

            section_pax = "<tr><td style='font-size:0px;padding:0px;word-break:break-word;'> <!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:300px;' width='300' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:300px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='width:300px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;'> <!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td style='vertical-align:top;width:150px;' ><![endif]--> " + columnas_pax + "</div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div> <!--[if mso | IE]></td></tr></table><![endif]--></td></tr>"
            
            balanceCard = ""
            depositCard = ""
            
            if booking_data["on_hold"] == True:
                balanceCard = str(cliente["amount_pending_payment"])
                depositCard = str(cliente["amount_paid"])
            elif booking_data["status_code"] == BookStatus.expired:
                balanceCard = str(cliente["amount_pending_payment"])
                depositCard = str(cliente["amount_paid"])
            else:
                balanceCard = str(cliente["amount_pending_payment"])
                depositCard = str(cliente["amount_paid"])

            html_rooms = html_rooms + "<div> <table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='background:#ffffff;background-color:#ffffff;width:100%;'> <tbody> <tr> <td><!--[if mso | IE]> <table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' > <tr> <td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--> <div style='margin:0px auto;max-width:600px;'> <table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'> <tbody> <tr> <td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]> <table role='presentation' border='0' cellpadding='0' cellspacing='0'> <tr> <td class='' style='vertical-align:middle;width:300px;' ><![endif]--> <div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:middle;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:10px 0px;word-break:break-word;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='border-collapse:collapse;border-spacing:0px;'> <tbody> <tr> <td style='width:290px;'><img alt='' height='auto' src='"+cliente["media"][0]["url"] + "' style='border:0;display:block;outline:none;text-decoration:none;height:auto;width:100%;font-size:13px;' width='290'></td></tr></tbody> </table> </td></tr></table> </div><!--[if mso | IE]> </td><td class='' style='vertical-align:middle;width:300px;' ><![endif]--> <div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:middle;width:100%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:middle;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:10px 25px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color: main-color;'> <b> <p>"+cliente["rateplan_name"] +"</p></b> </div></td></tr><tr> <td style='font-size:0px;padding:0px;word-break:break-word;'><!--[if mso | IE]> <table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:300px;' width='300' > <tr> <td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--> <div style='margin:0px auto;max-width:300px;'> <table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'> <tbody> <tr> <td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]> <table role='presentation' border='0' cellpadding='0' cellspacing='0'> <tr> <td class='' style='width:300px;' ><![endif]--> <div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;'><!--[if mso | IE]> <table role='presentation' border='0' cellpadding='0' cellspacing='0'> <tr> <td style='vertical-align:top;width:150px;' ><![endif]--> <div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'> <p style='color: grey-color;' >"+tx_room+" "+ str(index+1)+":</p></div></td></tr></table> </div><!--[if mso | IE]> </td><td style='vertical-align:top;width:150px;' ><![endif]--> <div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'> <table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> <tr> <td align='center' style='font-size:0px;padding:5px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'> <p>"+cliente["trade_name_room"] +"</p></div></td></tr></table> </div><!--[if mso | IE]> </td></tr></table><![endif]--> </div><!--[if mso | IE]> </td></tr></table><![endif]--> </td></tr></tbody> </table> </div><!--[if mso | IE]> </td></tr></table><![endif]--> </td></tr>" + section_pax + " <tr> <td align='right' style='font-size:0px;padding:10px 25px;word-break:break-word;'> <div style='font-family:avenirLigth, Roboto Condensed,Roboto, Helvetica, sans-serif;font-size:13px;font-weight:300;line-height:1;text-align:right;color:#000000;'> <p class='grey-color'>Total: <span class='black-color tachado'>" + booking_data["currency_code"] + " $" + str(cliente["total_crossout"]) + "</span></p><p>" + booking_data["currency_code"] + " $" + str(cliente["total"]) + "</p></div></td></tr><tr><td align='right' style='font-size:0px;padding:10px 25px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed,Roboto, Helvetica, sans-serif;font-size:13px;font-weight:300;line-height:1;text-align:right;color:#000000;'><p>"+tx_deposit+" <span>" + booking_data["currency_code"] + " $ "+ depositCard + " </span></p></div></td><tr><tr><td align='right' style='font-size:0px;padding:10px 25px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed,Roboto, Helvetica, sans-serif;font-size:13px;font-weight:300;line-height:1;text-align:right;color:#000000;'><p class='grey-color'>"+tx_balance+" <span style='color: #ff0000 ;'>" + booking_data["currency_code"] + " $ "+ balanceCard + " </span></p></div></td></tr></table> </div><!--[if mso | IE]> </td></tr></table><![endif]--> </td></tr></tbody> </table> </div><!--[if mso | IE]> </td></tr></table><![endif]--> </td></tr></tbody> </table> </div>"
            #titulo tarifario
            html_rooms = html_rooms + "<div><!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' ><tr><td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--><div style='margin:0px auto;max-width:600px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody><tr><td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><td class='' style='vertical-align:top;width:600px;' ><![endif]--><div class='mj-column-per-100 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'><tr><td align='center' style='font-size:0px;padding:10px 25px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'><b><p class='grey-color'>"+rateUno+" <span class='grey-color'>"+rateDos+"</span></p></b></div></td></tr></table></div><!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div><!--[if mso | IE]></td></tr></table><![endif]--></div>"
        
            lista = cliente["prices"]
            inicio = 0
            salida = 6
            columnas = ""
            i = 0
            html_tarifario = ""

            x = 0

            while i < len(lista):
            
                while inicio < salida:
                
                    union = ""
                    while i < inicio+2:
                        try:
                            union = union + "<div class='mj-column-per-50 mj-outlook-group-fix' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:50%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' width='100%'><tbody><tr><td style='border-right:1px solid #eeeeee;vertical-align:top;padding:0px;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='' width='100%'><tr><td align='center' style='font-size:0px;padding:10px 0px 10px 0px;word-break:break-word;'><div style='font-family:avenirLigth, Roboto Condensed, Roboto, Helvetica;font-size:13px;font-weight:300;line-height:1;text-align:center;color:#000000;'><p class='grey-color'>"+ self.formatDate(str(lista[i]["date"]) , False, booking_data["lang_code"].upper() )+"</p><p class='tachado'>"+ booking_data["currency_code"] +" $" +str(lista[i]["total_gross"])+"</p><p>"+ booking_data["currency_code"]  + " $" + str(lista[i]["total"])+"</p></div></td></tr></table></td></tr></tbody></table></div>"
                        except:
                            union = union + "<div class='mj-column-per-50 mj-outlook-group-fix ' style='font-size:0px;text-align:left;direction:ltr;display:inline-block;vertical-align:top;width:100%;'><table border='0' cellpadding='0' cellspacing='0' role='presentation' style='vertical-align:top;' width='100%'> </table></div>"
                        i += 1
                    columnas = columnas + "<div class='mj-column-per-33 mj-outlook-group-fix' style='font-size:0;line-height:0;text-align:left;display:inline-block;width:100%;direction:ltr;'><!--[if mso | IE]><table  role='presentation' border='0' cellpadding='0' cellspacing='0'><tr><![endif]-->"+ union +"<!--[if mso | IE]></tr></table><![endif]--></div>"
                    inicio += 2
            
                html_tarifario = html_tarifario + "<div style=''><!--[if mso | IE]><table align='center' border='0' cellpadding='0' cellspacing='0' class='' style='width:600px;' width='600' > <tr> <td style='line-height:0px;font-size:0px;mso-line-height-rule:exactly;'><![endif]--> <div style='margin:0px auto;max-width:600px;'><table align='center' border='0' cellpadding='0' cellspacing='0' role='presentation' style='width:100%;'><tbody> <tr> <td style='direction:ltr;font-size:0px;padding:0px;text-align:center;'><!--[if mso | IE]><table role='presentation' border='0' cellpadding='0' cellspacing='0'><tr> <td class='' style='vertical-align:top;width:300px;'> <![endif]-->"+ columnas +"<!--[if mso | IE]></td></tr></table><![endif]--></td></tr></tbody></table></div><!--[if mso | IE]></td></tr></table><![endif]--></div>"
            
                columnas = ""
                salida += 6

            
            html_rooms = html_rooms + html_tarifario

        """  politica_cancelacion = ""
        if len(booking_data["cancelation_policies"]) > 0 :
            if len(booking_data["cancelation_policies"][0]["texts"]) != "":
                politica_cancelacion = booking_data["cancelation_policies"][0]["texts"] """

        politica_cancelacion = ""
        if len(booking_data["cancelation_policies"]) > 0 :
            for cancelacion in booking_data["cancelation_policies"]:
                if cancelacion["texts"] != "":
                    politica_cancelacion = politica_cancelacion + cancelacion["texts"]
        
        if len(booking_data["guarantee_policies"]) > 0 :
            for garantia in booking_data["guarantee_policies"]:
                if len(garantia["texts"]) > 0 :
                    for x in garantia["texts"]:
                        politica_cancelacion = politica_cancelacion + x

        if len(booking_data["tax_policies"]) > 0 :
            for tax in booking_data["tax_policies"]:
                if len(tax["texts"]) > 0 :
                    for x in tax["texts"]:
                        politica_cancelacion = politica_cancelacion + x
        
        data = {
            "email_list": "",
            "sender": booking_data["sender"],
            "group_validation": False,
            "propiedad": booking_data["trade_name"],
            "url_banner":dictHeader[booking_data["property_code"]],
            "nombre":booking_data["customer"]["first_name"]+" "+ booking_data["customer"]["last_name"],
            "url_fam": dictFamilia[booking_data["property_code"]],
            "telefono":booking_data["customer"]["phone_number"],
            "correo":booking_data["customer"]["email"],
            "requerimiento_especial":booking_data["special_request"],
            "moneda":booking_data["currency_code"],
            "precio_total":booking_data["total"],
            "codigo_confirmacion": booking_data["code_reservation"],
            "check_in_tiempo": booking_data["general_data"]["check_in"],
            "check_out_tiempo": booking_data["general_data"]["check_out"],
            "check_in_fecha": self.formatDate( booking_data["from_date"], False, booking_data["lang_code"].upper() ),
            "check_out_fecha": self.formatDate( booking_data["to_date"], False, booking_data["lang_code"].upper() ),
            "noches": booking_data["nights"],
            "numeros_cuartos": booking_data["total_rooms"],
            "footer": html_footer ,
            "politica_cancelacion": politica_cancelacion,
            "cuartos": html_rooms,
            "services": html_services,
            "tituloUno":tituloUno,
            "tituloDos":tituloDos,
            "tituloClienteUno":tituloClienteUno,
            "tituloClienteDos":tituloClienteDos,
            "tituloConfirmacionUno":tituloConfirmacionUno,
            "tituloConfirmacionDos":tituloConfirmacionDos,
            "tx_bookingUno":tx_bookingUno,
            "tx_bookingDos":tx_bookingDos,
            "tx_nombre":tx_nombre,
            "tx_numero":tx_numero,
            "tx_correo":tx_correo,
            "tx_requerimiento":tx_requerimiento,
            "tx_monto":tx_monto,
            "tx_avisoUno":tx_avisoUno,
            "tx_avisoDos":tx_avisoDos,
            "tx_avisoTres":tx_avisoTres,
            "tx_avisoTres_1":tx_avisoTres_1,
            "tx_avisoTres_2":tx_avisoTres_2,
            "tx_avisoCuatro":tx_avisoCuatro,
            "bi_llegadaFecha":bi_llegadaFecha,
            "bi_salidaFecha":bi_salidaFecha,
            "bi_llegadaHora":bi_llegadaHora,
            "bi_salidaHora":bi_salidaHora,
            "bi_noches":bi_noches,
            "bi_cuartos":bi_cuartos,
            "bi_avisoUno":" ",
            "bi_avisoDos":" ",
            "serUno":serUno,
            "serDos":serDos,
            "servicio":servicio,
            "servicioDos":servicioDos,
            "book_email":book_email,
            "beneUno":beneUno,
            "beneDos":beneDos,
            "poliUno":poliUno,
            "poliDos":poliDos,
            "carta":carta,
            "on_hold": on_hold,
            "on_hold_2": on_hold_2,
            "email_subject": subject,
            "url_amenities": amenities
        }


        return data
    
    def get_config_params(self, params = ()):
        config_data = ConfigBooking.query.filter(ConfigBooking.param.in_(params), ConfigBooking.estado == 1).all()

        return config_data

    def get_config_param_one(self, param):
        config_data = ConfigBooking.query.filter(ConfigBooking.param == param, ConfigBooking.estado == 1).first()

        return config_data
    
    def _check_customer_profile(self, book_customer, username):
        """
            Check if the customer has a profile, if it doesn't exist it will be created
            param: book_customer Booking Consutomer
            
            return boolean
        """
        
        if not book_customer.id_profile:
            wire_request = WireRequest()
            id_profile = wire_request.get_opera_profile(book_customer, username)
            
            #check if the data was saved in Opera
            if id_profile > 0:
                book_customer.id_profile = id_profile
                book_customer.usuario_ultima_modificacion = username
                
                db.session.commit()
            else:
                return False
        
        return True
    
    def delete_booking(self, book_hotel, username):
        if not book_hotel:
            return False
        
        book_hotel.estado = 0
        book_hotel.usuario_ultima_modificacion = username
        book_hotel.amount_pending_payment = book_hotel.total
        book_hotel.amount_paid = 0

        for room in book_hotel.rooms:
            room.amount_pending_payment = room.total
            room.amount_paid = 0
            room.estado = 0
            room.usuario_ultima_modificacion = username
        
        for service in book_hotel.services:
            #TODO: Liberar servicios
            service.estado = 0
            service.usuario_ultima_modificacion = username
        
        for comment in book_hotel.comments:
            comment.estado = 0
            comment.usuario_ultima_modificacion = username

        #TODO: liberar promociones
        #TODO: liberar vouchers        
        db.session.commit()
    
    def cancel_booking(self, book_hotel, hotel_code, estado, username, date_now,\
    reason_cancellation = "",visible_reason_cancellation=0):
        #cambiar estado reserva
        #cancelar habitacion desde opera
        wire_service = WireService()
        room_data = []
        response = {
            "idbook_hotel":book_hotel.idbook_hotel,
            "error": True,
            "msg":"estado:"+ str(estado),
            "data": room_data
        }
        list_valid_status = [4,5,7,8]
        if estado in(list_valid_status):
            for room in book_hotel.rooms:
                folio_opera = room.pms_confirm_number
                if room.estado == 1 and room.pms_confirm_number != "":
                    wire_response = wire_service.cancel_booking(hotel_code, folio_opera, username, reason_cancellation)
                    if wire_response["resultField"]["operaErrorCodeField"] is not None:
                        ms = wire_response["resultField"]["operaErrorCodeField"]
                        room.pms_message ="idbook_hotel_room:" +str(room.idbook_hotel_room)+ ", " +str(ms)
                        room_response = {
                            "idbook_hotel_room":room.idbook_hotel_room,
                            "error": True,
                            "msg":ms,
                            "folio_opera":folio_opera
                        }
                        response["error"] = True
                        response["msg"] = ms
                    else:
                        room.pms_message = str(wire_response["resultField"]["iDsField"][0]["idTypeField"])
                        room.reason_cancellation = reason_cancellation
                        room_response = {
                            "idbook_hotel_room":room.idbook_hotel_room,
                            "error": False,
                            "msg":"Succes",
                            "folio_opera":wire_response["resultField"]["iDsField"][0]["operaIdField"]
                        }
                        response["error"] = False
                        response["msg"] = "Succes"
                elif room.estado == 1 and room.pms_confirm_number == "":
                    room_response = {
                        "idbook_hotel_room":room.idbook_hotel_room,
                        "error": False,
                        "msg":"Succes",
                        "folio_opera":""
                    }
                    response["error"] = False
                    response["msg"] = "Succes"

                db.session.commit()
                room_data.append(room_response)
            
            if not response["error"]:
                book_hotel.cancelation_date = date_now
                book_hotel.visible_reason_cancellation = visible_reason_cancellation
                book_hotel.idbook_status = 2
                book_hotel.usuario_ultima_modificacion = username
                db.session.commit()
            response["data"] = room_data

        return response

    def get_payment_guarantee_by_room(self, book_hotel_room, currency_code):
        data = {
            "charge_option": BookHotelRoom.charge_option_no_payment,
            "amount": 0
        }
        policy_guarantee = PolicyFunctions.getPolicyConfigData(book_hotel_room.iddef_police_guarantee)

        if not policy_guarantee:
            return data
        
        """
            1. No Payment (implemented)
            2. Credit Card Store as Guarantee (implemented)
            3. Offline Credit Card Payment in own Terminal (implemented)
            4. Bank Transfer (not implemented)
        """
        guarantee_currency_code = policy_guarantee["currency_code"]
        policy_guarantee = policy_guarantee["policy_guarantees"][0]
        if policy_guarantee["iddef_policy_guarantee_type"] == 2:#the payment will be automatic before arrive
            #if the checkin is less than 15 days, charge at the moment. The remaining will be paid at checkin in front desk            
            book_hotel_room_from_date = book_hotel_room.hotel.from_date
            if isinstance(book_hotel_room_from_date,dt):
                book_hotel_room_from_date = date(book_hotel_room.hotel.from_date.year,book_hotel_room.hotel.from_date.month,book_hotel_room.hotel.from_date.day)
            if (book_hotel_room_from_date - date.today()).days < policy_guarantee['nights_applied_antifraud']:
                #if is 1 night, charge 2 usd
                if book_hotel_room.hotel.nights == 1:
                    policy_antifraud = self.get_antifraud_by_nights_type(policy_guarantee["policy_guarantee_antifrauds"], PolicyGuaranteeAntifraud.nights_type_one)                    
                #if is more than 1 night, charge 1 night
                elif book_hotel_room.hotel.nights > 1:
                    policy_antifraud = self.get_antifraud_by_nights_type(policy_guarantee["policy_guarantee_antifrauds"], PolicyGuaranteeAntifraud.nights_type_more_one)
                
                data["amount"] = self.get_amount_by_antifraud_rules(policy_antifraud, currency_code, book_hotel_room.prices)                                    
                
                book_hotel_room.charge_option = BookHotelRoom.charge_option_at_moment
                book_hotel_room.amount_to_pay = data["amount"]
                book_hotel_room.amount_to_pending_payment = 0
                book_hotel_room.amount_pending_payment = book_hotel_room.total - book_hotel_room.amount_to_pay
                book_hotel_room.amount_paid = book_hotel_room.amount_to_pay
            else:
                data["charge_option"] = BookHotelRoom.charge_option_before_arrived
                data["amount"] = 0
                book_hotel_room.charge_option = BookHotelRoom.charge_option_before_arrived
                book_hotel_room.amount_to_pay = data["amount"]
                book_hotel_room.amount_to_pending_payment = book_hotel_room.total
                book_hotel_room.amount_pending_payment = book_hotel_room.amount_to_pending_payment
                book_hotel_room.amount_paid = book_hotel_room.amount_to_pay
            
        elif policy_guarantee["iddef_policy_guarantee_type"] == 3:#the payment (full or partial) will be in the moment save reservation
            data["charge_option"] = BookHotelRoom.charge_option_at_moment
            book_hotel_room.charge_option = BookHotelRoom.charge_option_at_moment
            guarantee_deposit = policy_guarantee["policy_guarantee_deposits"][0]
            """
                iddef_policy_rule options:
                    0. None
                    1. Fixed amount
                    2. Percent
            """
            if guarantee_deposit["iddef_policy_rule"] == 1:
                amount = 0
                if currency_code != guarantee_currency_code:
                    #Convert the currency of guarantee to currency reservation
                    exchange_rate = ExchangeRateService.get_exchange_rate_date(date.today(), guarantee_deposit["currency_code"])
                    if currency_code == "USD" and guarantee_currency_code == "MXN":
                        amount = exchange_rate.amount * guarantee_deposit["fixed_amount"]
                    elif currency_code == "MXN" and guarantee_currency_code == "USD":
                        amount = guarantee_deposit["fixed_amount"] / exchange_rate.amount
                
                if book_hotel_room.total < amount:
                    book_hotel_room.amount_to_pay = book_hotel_room.total
                    data["amount"] = book_hotel_room.total
                else:
                    book_hotel_room.amount_to_pay = round(amount, 2)
                    data["amount"] = round(amount, 2)
                
                book_hotel_room.amount_to_pending_payment = book_hotel_room.total - book_hotel_room.amount_to_pay
                book_hotel_room.amount_pending_payment = book_hotel_room.amount_to_pending_payment
                book_hotel_room.amount_paid = book_hotel_room.amount_to_pay
            elif guarantee_deposit["iddef_policy_rule"] == 2:
                """
                    option_percent options:
                    0. fullstay
                    1. nights
                """
                if guarantee_deposit["option_percent"] == 0:
                    book_hotel_room.amount_to_pay = round(book_hotel_room.total * (float(guarantee_deposit["percent"])/100), 2)
                    data["amount"] = book_hotel_room.amount_to_pay
                    book_hotel_room.amount_to_pending_payment = book_hotel_room.total - book_hotel_room.amount_to_pay
                    book_hotel_room.amount_pending_payment = book_hotel_room.amount_to_pending_payment
                    book_hotel_room.amount_paid = book_hotel_room.amount_to_pay

                elif guarantee_deposit["option_percent"] == 1:

                    #sum the number nights required
                    for i in range(int(guarantee_deposit["number_nights_percent"])):
                        to_pay = book_hotel_room.prices[i].total * (float(guarantee_deposit["percent"])/100)
                        #book_hotel_room.prices[i].amount_to_pay = book_hotel_room.prices[i].total * (float(guarantee_deposit["percent"])/100)
                        """ book_hotel_room.prices[i].amount_pending_payment = book_hotel_room.prices[i].total - to_pay
                        book_hotel_room.prices[i].amount_paid = to_pay """
                        data["amount"] += to_pay
                        
                    data["amount"] = round(data["amount"], 2)
                    book_hotel_room.amount_to_pay = round(data["amount"], 2)
                    book_hotel_room.amount_to_pending_payment = book_hotel_room.total - book_hotel_room.amount_to_pay
                    book_hotel_room.amount_pending_payment = book_hotel_room.amount_to_pending_payment
                    book_hotel_room.amount_paid = book_hotel_room.amount_to_pay
        
        return data

    def get_antifraud_by_nights_type(self, policies_antifraud, type):
        """
            Get antrifraud policy by nights type.
            
            Parameters
            ----------
            policies_antifraud : list of dict
                List of policies antifraud (get of guaranty police)
            type : int
                Type of policy to look for
            
            Returns
            -------
            policy_found: dict
                Policy found
        """
        policy_found = next((item for item in policies_antifraud if item["guarantee_nights_type"] == type), None) 
        return policy_found
    
    def get_amount_by_antifraud_rules(self, policy_antifraud, currency_code, prices):
        """
            Get payment amount based on antifraud rules.
            
            Parameters
            ----------
            policy_antifraud : dict
                Policy antifraud
            currency_code : string
                ISO currency code
            prices : List BookHotelRoomPrices
                List of prices to find the sum of n nights if its the case
            Returns
            -------
            amount: float
                amount calculated
        """
        amount = 0
        default_amount_guarantee_usd = float(policy_antifraud["amount_payment"])        
        
        if policy_antifraud["guarantee_payment_type"] == PolicyGuaranteeAntifraud.payment_type_fixed_amount:
            if currency_code == "MXN":
                exchange_rate = ExchangeRateService.get_exchange_rate_date(date.today(), "MXN")
                amount = exchange_rate.amount * default_amount_guarantee_usd
            else: 
                amount = default_amount_guarantee_usd
        elif policy_antifraud["guarantee_payment_type"] == PolicyGuaranteeAntifraud.payment_type_nights:
            for i in range(int(policy_antifraud["nights_payment"])):
                amount += prices[i].total
        return amount
    
    @classmethod
    def filter_list_book_hotel(cls, iddef_property = 0, idbook_status = 0, code_book_hotel = 0,\
        from_date_travel=0, to_date_travel=0, from_date_booking=0, to_date_booking=0, limit=10, offset=1, isCount=False):
        """
            filter book_hotels by iddef_property, idbook_status, code_book_hotel, from_date_travel, to_date_travel, from_date_booking & to_date_booking
            param: iddef_property (optional)
            param: idbook_status (optional)
            param: code_book_hotel (optional)
            param: from_date_travel (optional)
            param: to_date_travel (optional)
            param: from_date_booking (optional)
            param: to_date_booking (optional)

            return flask_sqlalchemy.BaseQuery
        """
        conditions, conditionsAnd0, conditionsAnd1, conditionsAnd2, conditionsOr0 = [BookHotel.estado == 1], [], [], [], []
        
        if code_book_hotel != 0:
            conditions.append(BookHotel.code_reservation == code_book_hotel)
        else:
            if iddef_property != 0:
                conditions.append(BookHotel.iddef_property == iddef_property)

            if idbook_status != 0:
                conditions.append(BookHotel.idbook_status == idbook_status)
            
            if from_date_travel != 0 and to_date_travel != 0:
                conditionsAnd0.append(BookHotel.from_date >= from_date_travel.strftime("%Y-%m-%d"))
                conditionsAnd0.append(BookHotel.to_date <= to_date_travel.strftime("%Y-%m-%d"))
                conditionsOr0.append(and_(*conditionsAnd0))
                conditionsAnd1.append(BookHotel.from_date < from_date_travel.strftime("%Y-%m-%d"))
                conditionsAnd1.append(BookHotel.to_date > to_date_travel.strftime("%Y-%m-%d"))
                conditionsOr0.append(and_(*conditionsAnd1))
                conditions.append(or_(*conditionsOr0))

            if from_date_booking != 0 and to_date_booking != 0:
                conditionsAnd2.append(func.date(func.convert_tz(BookHotel.fecha_creacion, '+00:00', '-05:00')) >= from_date_booking.strftime("%Y-%m-%d"))
                conditionsAnd2.append(func.date(func.convert_tz(BookHotel.fecha_creacion, '+00:00', '-05:00')) <= to_date_booking.strftime("%Y-%m-%d"))
                conditions.append(and_(*conditionsAnd2))
        
        if isCount == True:
            list_book_hotel = BookHotel.query.filter(and_(*conditions)).count()
        else:
            if code_book_hotel != 0:
                list_book_hotel = BookHotel.query.filter(and_(*conditions)).all()
            else:
                list_book_hotel = BookHotel.query.filter(and_(*conditions)).limit(limit).offset(offset).all()

        return list_book_hotel
    
    @classmethod
    def filter_parameter_book_hotel(cls, iddef_property = 0, idbook_status = 0, code_book_hotel = 0,\
        from_date_travel=0, to_date_travel=0, from_date_booking=0, to_date_booking=0, limit=10, offset=1, isCount=False):
        """
            filter book_hotels by iddef_property, idbook_status, code_book_hotel, from_date_travel, to_date_travel, from_date_booking & to_date_booking
            param: iddef_property (optional)
            param: idbook_status (optional)
            param: code_book_hotel (optional)
            param: from_date_travel (optional)
            param: to_date_travel (optional)
            param: from_date_booking (optional)
            param: to_date_booking (optional)
        """
        result, query_where, query_close, params = None, "\n WHERE b.estado=1 ", ";", {}
        if isCount:
            query = " SELECT COUNT(b.idbook_hotel) AS total FROM book_hotel b "
        else:
            query = " SELECT p.iddef_property,\
                    p.property_code, p.short_name AS property_name, b.idbook_hotel, b.code_reservation, c.currency_code, b.from_date, b.to_date, s.name AS status, b.idbook_status, b.total, GROUP_CONCAT(rc.room_code SEPARATOR ', ') AS codes_rooms,\
                    GROUP_CONCAT( IF(br.pms_confirm_number='', NULL, br.pms_confirm_number)) AS pms_confirm_numbers, CONCAT(bc.last_name, ' ', bc.first_name) AS guest_name, bc.email, dc.country_code AS guest_country, b.adults, b.child, b.nights, b.fecha_creacion\
                    FROM book_hotel b\
                    INNER JOIN def_property p ON p.iddef_property = b.iddef_property AND p.estado = 1\
                    INNER JOIN def_currency c ON c.iddef_currency = b.iddef_currency AND c.estado = 1\
                    INNER JOIN book_status s ON s.idbook_status = b.idbook_status AND s.estado = 1\
                    INNER JOIN  book_customer_hotel bch ON bch.idbook_hotel = b.idbook_hotel AND bch.estado=1\
                    INNER JOIN book_customer bc ON bc.idbook_customer = bch.idbook_customer AND bc.estado=1\
                    INNER JOIN book_address ba ON ba.idbook_customer = bch.idbook_customer AND ba.estado=1\
                    INNER JOIN def_country dc ON dc.iddef_country = ba.iddef_country AND dc.estado=1\
                    INNER JOIN book_hotel_room br ON br.idbook_hotel = b.idbook_hotel AND br.estado = 1\
                    INNER JOIN def_room_type_category rc ON rc.iddef_room_type_category = br.iddef_room_type AND br.estado = 1 "
            query_close = "\n GROUP BY b.idbook_hotel \n LIMIT " +str(limit)+ " OFFSET " +str(offset)+ "; "
        if code_book_hotel != 0:
            query_where += " AND b.code_reservation = :code_book_hotel "
            params["code_book_hotel"] = str(code_book_hotel)
        else:
            if iddef_property != 0:
                query_where += " AND b.iddef_property = :iddef_property "
                params["iddef_property"] = int(iddef_property)
            if idbook_status != 0:
                query_where += " AND b.idbook_status = :idbook_status "
                params["idbook_status"] = int(idbook_status)
            if from_date_travel != 0 and to_date_travel != 0:
                query_where += " AND ((b.from_date >= :from_date_travel AND b.to_date <= :to_date_travel) OR (b.from_date < :from_date_travel AND b.to_date > :to_date_travel)) "
                params["from_date_travel"] = str(from_date_travel) + " 00:00:00"
                params["to_date_travel"] = str(to_date_travel) + " 23:59:59"
            if from_date_booking != 0 and to_date_booking != 0:
                query_where += " AND CONVERT_TZ(b.fecha_creacion, '+00:00', '-05:00') >= :from_date_booking AND CONVERT_TZ(b.fecha_creacion, '+00:00', '-05:00') <= :to_date_booking "
                params["from_date_booking"] = str(from_date_booking) + " 00:00:00"
                params["to_date_booking"] = str(to_date_booking) + " 23:59:59"
        query = query + query_where + query_close
        if isCount:
            result = db.session.execute(query, params).scalar()
        else:
            result = db.session.execute(query, params).fetchall()
        
        return result
        
    def __update_book_status(self,id_book_hotel,book_room_list, username, book_status=None):
    
        try:
            rooms_updated = 0

            for book_room in book_room_list:
                if book_room["error"] == False:
                    book_room_data = BookHotelRoom.query.get(book_room["id_book_room"])
                    
                    if book_room_data is None:
                        raise Exception("Book Hotel Room no encontrado")
                        
                    book_room_data.pms_confirm_number = book_room["opera_folio"]
                    book_room_data.usuario_ultima_modificacion = username

                    db.session.commit()

                    rooms_updated += 1
                elif book_room["opera_folio"] != 0:
                    
                    rooms_updated += 1


            if book_status is None:
                book_status = BookStatus.interfaced
                if rooms_updated != len(book_room_list):
                    book_status = BookStatus.partial_interfaced

            book_hotel_data = BookHotel.query.get(id_book_hotel)
            
            book_hotel_data.idbook_status = book_status
            book_hotel_data.usuario_ultima_modificacion = username

            db.session.commit()

        except Exception as error:
            pass

    @classmethod
    def create_booking(self,book_hotel=None, idbook_hotel=0, channel=None, username=""):

        wire_service = WireService()
        wire_request = WireRequest()

        response = {}

        try:
            if book_hotel is not None:
                if isinstance(book_hotel,BookHotel) == False:
                    raise Exception("Modelo no compatible")
                else:
                    book_hotel = book_hotel
            elif idbook_hotel == 0:
                raise Exception("se necesita de un modelo o un id de reserva valido")
            else:
                book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbook_hotel, BookHotel.estado == 1).first()

            self._check_customer_profile(self, book_hotel.customers[0].customer, username)
            request_list = wire_request.create_request(book_hotel,username=username)

            room_list = []

            if request_list["error"] == False:

                for request in request_list["data"]:

                    idRoom = request["id_room"]

                    try:

                        if request["error"] == False:
                            
                            wire_response = wire_service.create_booking(request["request"], username)

                            if wire_response["error"] == False:
                                room_response = {
                                    "id_book_room":idRoom,
                                    "error": False,
                                    "msg":"Succes",
                                    "opera_folio":wire_response["reservationNumber"]
                                }
                            else:
                                room_response = {
                                    "id_book_room":idRoom,
                                    "error": True,
                                    "msg":wire_response["message"],
                                    "opera_folio":request["folio_opera"]
                                }
                        else:
                            room_response = {
                                "id_book_room":idRoom,
                                "error": True,
                                "msg":request["msg"],
                                "opera_folio":request["folio_opera"]
                            }

                    except Exception as request_error:
                        room_response = {
                            "id_book_room":idRoom,
                            "error": True,
                            "msg":str(request_error),
                            "opera_folio":request["folio_opera"]
                        }

                    room_list.append(room_response)

                self.__update_book_status(self,book_hotel.idbook_hotel,room_list, username)

                response = {
                    "error":False,
                    "msg":"Success",
                    "rooms_status":room_list
                }

            else:
                response = {
                    "error":True,
                    "msg":request_list["msg"],
                    "rooms_status":None
                }

        except Exception as error:
            response = {
                "error":False,
                "msg":str(error),
                "rooms_status":None
            }

        return response

    @classmethod
    def update_booking(self,book_hotel=None, idbook_hotel=0, channel=None, username="", new_id_rooms=[]):

        wire_service = WireService()
        wire_request = WireRequest()

        response = {}

        try:
            if book_hotel is not None:
                if isinstance(book_hotel,BookHotel) == False:
                    raise Exception("Modelo no compatible")
                else:
                    book_hotel = book_hotel
            elif idbook_hotel == 0:
                raise Exception("se necesita de un modelo o un id de reserva valido")
            else:
                book_hotel = BookHotel.query.\
                filter(BookHotel.idbook_hotel == idbook_hotel, BookHotel.estado == 1).first()

            self._check_customer_profile(self, book_hotel.customers[0].customer, username)
            request_list = wire_request.create_request(book_hotel, True)

            room_list = []

            if request_list["error"] == False:

                for request in request_list["data"]:

                    idRoom = request["id_room"]

                    try:

                        if request["error"] == False:
                            if ((len(request["request"]["HotelReservationField"]["UniqueIDListField"]) == 0 
                                or request["request"]["HotelReservationField"]["UniqueIDListField"][0]["valueField"] == "") 
                            and int(idRoom) in new_id_rooms):
                                wire_response = wire_service.create_booking(request["request"], username)
                            else:
                                wire_response = wire_service.update_booking(request["request"], username)

                            if wire_response["error"] == False:
                                room_response = {
                                    "id_book_room":idRoom,
                                    "error": False,
                                    "msg":"Succes",
                                    "opera_folio":wire_response["reservationNumber"]
                                }
                            else:
                                room_response = {
                                    "id_book_room":idRoom,
                                    "error": True,
                                    "msg":wire_response["message"],
                                    "opera_folio":request["folio_opera"]
                                }
                        else:
                            room_response = {
                                "id_book_room":idRoom,
                                "error": True,
                                "msg":request["msg"],
                                "opera_folio":request["folio_opera"]
                            }

                    except Exception as request_error:
                        room_response = {
                            "id_book_room":idRoom,
                            "error": True,
                            "msg":str(request_error),
                            "opera_folio":request["folio_opera"]
                        }

                    room_list.append(room_response)

                self.__update_book_status(self,book_hotel.idbook_hotel,room_list, username, BookStatus.changed)

                response = {
                    "error":False,
                    "msg":"Success",
                    "rooms_status":room_list
                }

            else:
                response = {
                    "error":True,
                    "msg":request_list["msg"],
                    "rooms_status":None
                }

        except Exception as error:
            response = {
                "error":False,
                "msg":str(error),
                "rooms_status":None
            }

        return response