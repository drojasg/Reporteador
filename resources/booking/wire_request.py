from models.book_customer import BookCustomer as customerModel
from models.book_hotel_comment import BookHotelComment as commentModel
from models.book_hotel import BookHotel as bookModel
from models.rateplan import RatePlan as rtpModel
from models.room_type_category import RoomTypeCategory as rtcModel
from models.book_wire import Wire_Request as request_wire
from .wire_service import WireService
from datetime import datetime as datatime
from models.age_range import AgeRange as agModel, AgeCode as acModel
import statistics as stats
from common.util import Util

class WireRequest():

    __list_beds_rooms=[
        {
            "hotel":"ZMSU",
            "room":"G2",
            "beds":["D"]
        },
        {
            "hotel":"ZPLB",
            "room":"OV",
            "beds":["D"]
        },
        {
            "hotel":"ZRCZ",
            "room":"MZK",
            "beds":["D"]
        },
        {
            "hotel":"ZCJG",
            "room":"N1",
            "beds":["D"]
        },
        {
            "hotel":"ZHLB",
            "room":"OV",
            "beds":["D"]
        },
        {
            "hotel":"ZHSP",
            "room":"OSD",
            "beds":["D"]
        }
    ]

    def create_request(self,book_hotel_data,is_update=False,username="",send_notification=True):
        response = {}
        try:
            schema = request_wire()

            book_hotel = None

            request_opera = []

            #obtenemos la informacion de la reserva
            if book_hotel_data is not None:
                if isinstance(book_hotel_data,bookModel) == False:
                    raise Exception("Modelo no compatible")
                else:
                    book_hotel = book_hotel_data
            else:
                raise Exception("Informacion de reserva invalida")
            
            #Obtenemos el perfil del huesped
            customer_profile_id = book_hotel.customers[0].customer.id_profile

            #Creamos el nodo perfil del huesped en opera
            res_guests_field_data = self.res_guests(customer_profile_id, book_hotel.market_segment.pms_profile_id)

            #Creamos el nodo guarantee segun el tipo de pago
            #pendiente sustituir
            guarantee_field_data = self.guarantee("DIR")

            #Creamos el nodo time spam
            time_spam_data = self.time_span(book_hotel.from_date,book_hotel.to_date)

            #Creamos el nodo hotel reference
            hotel_reference_data = self.hotel(book_hotel.property.property_code)

            #Creamos el nodo de comentarios
            comments_data = self.comments(book_hotel.comments)

            #Creamos los comentarios en los comentarios
            promotions_comment = self.promotions_in_comments(book_hotel.promotions)

            #Agregamos los comentarios con la informacion de las promociones
            comments_data.append(promotions_comment)

            #Creamos los comentarios de los servicios
            service_comment = self.service_in_comments(book_hotel.services)

            #Agregamos los servicios como comentarios de la reserva en opera
            comments_data.append(service_comment)

            #Asignamos el currency code
            currency = book_hotel.currency.currency_code
            #currency = "USD"

            #Obtenemos el id de la propiedad
            idProperty = book_hotel.property.iddef_property

            promo_code = None
            if book_hotel.promo_codes:
                promo_code = book_hotel.promo_codes[0].promo_code
            
            count = 1
            #Por cada cuarto se genera un request a opera
            for room in book_hotel.rooms:
                complementary_room = False
                folio = 0

                try:

                    if room.pms_confirm_number != "" and is_update == False:
                        folio = room.pms_confirm_number
                        raise Exception("Ya existe un FOLIO para esta habitacion {}".format(folio))
                    elif room.pms_confirm_number != "" and is_update == True:
                        folio = room.pms_confirm_number
                    # elif room.pms_confirm_number == "" and is_update == True:
                    #     raise Exception("No existe un FOLIO para actualizar esta habitacion")

                    #Obtenemos la informacion del rateplan,seleccionado para esta habitacion
                    ratePlan = rtpModel.query.get(room.idop_rate_plan)
                    if ratePlan is None:
                        raise Exception("Rateplan no encontrado, favor de validar")
                    ratePlan_code = ratePlan.rate_code_base
                    #ratePlan_code = "NETUSA"
                
                    #Obtenemos la informacion del cuarto seleccionado
                    room_type_category = rtcModel.query.get(room.iddef_room_type)
                    if room_type_category is None:
                        raise Exception("Room type category no encontrado, favor de validar")
                    #Obtenemos la informacion necesaria de la habitacion
                    room_type_category_clever = room_type_category.room_code
                    room_type_category_max_pms = room_type_category.max_ocupancy

                    if room_type_category_clever.upper() == "P1" or room_type_category_clever.upper() == "F1":
                        complementary_room = True
                        room_type_category_max_pms = room_type_category.max_ocupancy_pms

                    #Creamos el nodo de pax, segun la maxima ocupacion de la habitacion en el pms
                    guest_count_data = self.createGuestCounts(room.paxes,\
                    idProperty, room_type_category_max_pms)

                    #recorremos el areglo de guest_data para obtener la cantidad de pax
                    adultos = 0
                    menores = 0
                    for guess in guest_count_data["GuestCountField"]:
                        if guess["ageQualifyingCodeField"] == "ADULT":
                            adultos += guess["countField"]
                        else:
                            menores += guess["countField"]

                    room_type_category_opera = room_type_category.room_code_opera
                    if not room_type_category_opera:
                        room_type_category_opera = room_type_category.room_code
                    
                    #asignamos el tipo de cama a la habitacion segun los pax
                    room_type_category_code = self._set_bed_tipe(room_type_category_opera,\
                    adultos,menores,room_type_category.room_code,\
                    book_hotel.property.property_code)
                    room_type_category_code = room_type_category_code.upper()

                    #Creamos el nodo room rates
                    room_rates_data = self.create_room_rates(rates=room.prices,\
                    plan_code=ratePlan_code,room_type=room_type_category_code,\
                    currency_code=currency)

                    #Creamos el nodo room stays
                    room_stay_data = self.create_room_stays_field(guarantee=guarantee_field_data,\
                    time_span=time_spam_data,hotel_reference=hotel_reference_data,\
                    comments_field=comments_data,guest_counts=guest_count_data,\
                    room_rates=room_rates_data,response_rate=ratePlan_code,\
                    room_type=room_type_category_code)

                    if book_hotel.total_rooms > 1:
                        external_format_code = book_hotel.code_reservation + "/" + str(count)
                    else:
                        external_format_code = book_hotel.code_reservation
                    
                    #Creamos la lista de ufs
                    udfs_list = self.user_defined_values(promo_code, ratePlan.rate_code_clever)
                    # if room.total <= 0:
                    #     udfs_list = self.user_defined_values("NORC", "FREE2X1")
                    # else:
                    #     udfs_list = self.user_defined_values(promo_code, ratePlan.rate_code_clever)

                    external_number = self.external_system_number(external_format_code, book_hotel.status_item.code)

                    #Creamos el nodo de unique id list
                    unique_id_list_data = self.create_unique_id_list_field(room.pms_confirm_number) if is_update == True else None

                    #Creamos el nodo hotel reservation
                    request = self.create_base(res_guests_field=res_guests_field_data,\
                    room_stays_field=room_stay_data, udfs_list=udfs_list, external_number=external_number,\
                    unique_id_list_field=unique_id_list_data)

                    #Generamos el json
                    dataDump = schema.dump(request)

                    request = {
                        "id_room":room.idbook_hotel_room,
                        "folio_opera": folio,
                        "request": dataDump, 
                        "msg":"succes",
                        "error":False
                    }

                    request_opera.append(request)

                    if send_notification == True:
                        if complementary_room == True:
                            #Send a notification if the room is P1 or F1
                            tag_notification = "NOTIFICATION_BENGINE_COMPLEMENTARY_ROOMS"
                            total_pax = room.adults + room.child
                            email_data = {
                                "email_list":"",
                                "group_validation": True,
                                "room_type_category": room_type_category_clever,
                                "reservation_code": external_format_code,
                                "pax": total_pax,
                                "pax_adults": room.adults,
                                "pax_minors": room.child
                            }
                            username = username

                            Util.send_notification(email_data, tag_notification, username)

                    count += 1

                except Exception as room_error:
                    request = {
                        "id_room":room.idbook_hotel_room,
                        "folio_opera": folio,
                        "request": None, 
                        "msg":str(room_error),
                        "error":True
                    }

                    request_opera.append(request)

            response = {
                "error":False,
                "msg":"Success",
                "data":request_opera
            }

        except Exception as error:
            response = {
                "error":True,
                "msg":str(error),
                "data":None
            }
            
        return response


    def _verifi_beds_of_room(self,room_code,hotel):
        bed_default = "K"
        only_one_bed = False
        
        for rooms in self.__list_beds_rooms:
            if rooms["hotel"].upper() == hotel.upper():
                if rooms["room"].upper() == room_code.upper():
                    if len(rooms["beds"])==1:
                        only_one_bed = True
                        bed_default = rooms["beds"][0]
                    break
                else:
                    continue
            else:
                continue
        
        return bed_default, only_one_bed

    
    def _set_bed_tipe(self,room_code_base,adults,kids,clever_room,property_code):
        
        bedtype, one_bed = self._verifi_beds_of_room(clever_room,property_code)

        #bedtype = "k"
        if one_bed == False:
            #Si la habitacion es una F1 o P1 se le asigna la K por defecto
            if clever_room != "F1" and clever_room != "P1":
                #Si hay mas de 2 adultos sin menores
                if adults > 2 and kids <= 0:
                    bedtype = "d"        
                #Si hay mas de 2 adultos y almenos 1 menor
                elif adults >= 2 and kids >= 1:
                    bedtype = "d"
                #Si hay maximo 2 adultos y 2 o mas menores
                elif adults <= 2 and kids >= 2:
                    bedtype = "k"
                elif adults <= 2 and kids <= 0:
                    bedtype = "k"

        return room_code_base+bedtype

    
    def get_opera_profile(self,book_customer, username):

        wire = WireService()

        idProfile = 0

        if book_customer is None:
            raise Exception("Informacion de huesped no encontrada")

        if isinstance(book_customer,customerModel) == False:
            raise Exception("Modelo de huesped no compatible")

        wireResponse = wire.create_profile(book_customer.first_name,\
        book_customer.last_name,book_customer.address.country.country_code,\
        book_customer.email,book_customer.dialling_code+book_customer.phone_number,username)

        if wireResponse["error"] == False:
            idProfile = wireResponse["idProfile"]

        return idProfile

    def create_base(self, room_stays_field=None, res_guests_field=None, unique_id_list_field=None, udfs_list = None, external_number = None):
        base_request = {
            'HotelReservationField': {
                'marketSegmentField':"WBPR",
                'UniqueIDListField': unique_id_list_field,
                'RoomStaysField': [room_stays_field],
                'ResGuestsField': res_guests_field,
                'UserDefinedValuesField': udfs_list
            },
            'ExternalSystemNumberField': external_number,
            'xsn': None
        }
        return base_request


    def create_unique_id_list_field(self, folio_opera):
        return [{
            "typeField": "INTERNAL",
            "valueField": folio_opera
        }]
    
    def create_room_stays_field(self, response_rate=None, \
    room_type=None, block_code="", room_rates=None, guest_counts=None, \
    time_span=None, guarantee=None, hotel_reference=None, comments_field=None):
        return {
            'RatePlansField': [
                {"ratePlanCodeField": response_rate}
            ],
            'RoomTypesField': [
                {
                    "roomTypeCodeField": room_type,
                    "numberOfUnitsField": 1,
                    "numberOfUnitsSpecifiedField": True,
                    "invBlockCodeField" :  block_code
                }
            ],
            'RoomRatesField': room_rates,
            'GuestCountsField': guest_counts,
            'TimeSpanField': time_span,
            'GuaranteeField': guarantee,
            'CommentsField': comments_field,
            'HotelReferenceField': hotel_reference,
        }

    def external_system_number(self, number, reference_type):
        return {
            "ReferenceNumberField":number,
            "LegNumberField":"1",
            "ReferenceTypeField":reference_type
        }
    
    def create_room_rates(self, rates=None, plan_code=None, room_type=None, currency_code=None,is_complementary=False):
        room_rate = []

        for value in rates:
            amount = value.price_to_pms
            if is_complementary == True:
                amount = 0
            room = {
                "roomTypeCodeField": room_type,
                "ratePlanCodeField": plan_code,
                "effectiveDateField": value.date,
                "effectiveDateFieldSpecified": True,
                "ratesField": [{
                    "effectiveDateField": value.date,
                    "effectiveDateFieldSpecified": True,
                    "rateOccurrenceField": "DAILY",
                    "baseField":{
                        "currencyTextField": str(amount),
                        "valueField" : amount,
                        "currencyCodeField" : currency_code
                    }
                }]
            }

            room_rate.append(room)

        return room_rate
    
    def createGuestCounts(self, paxes, id_property,max_ocupancy_pms):

        guest_count_data = []

        age_list = agModel.query.with_entities(agModel.iddef_age_range, acModel.code, acModel.age_from, acModel.age_to)\
            .join(acModel)\
            .filter(agModel.iddef_property==id_property, agModel.estado==1)\
            .all()
        
        count_paxes = 0
        for pax in paxes:
            
            if count_paxes >= max_ocupancy_pms:
                break 
                
            if pax.age_code.upper() == "ADULTS":
                occupancy_adults = pax.total
                
                if occupancy_adults > max_ocupancy_pms:
                    occupancy_adults = max_ocupancy_pms

                adult_pax = self.__createGuestCountAdult(occupancy_adults)
                
                guest_count_data.append(adult_pax)

                count_paxes += occupancy_adults
            elif pax.total >= 1:

                code = pax.age_code.lower()

                age_detail = agModel.query.join(acModel,\
                acModel.iddef_age_code == agModel.iddef_age_code).filter(agModel.estado == 1,\
                agModel.iddef_property == id_property, acModel.code.like(code)).first()

                #Si no se encuentra el codigo, se coloca una edad media entre 1 y 17
                #10
                age_detail = next((item for item in age_list if item.code == code), None)

                age_from = 1
                age_to = 17
                if age_detail is not None:

                    age_from = age_detail.age_from
                    age_to = age_detail.age_to

                    if age_from == age_to:
                        age_to += 1

                med = stats.median(range(age_from,age_to))

                for child_pax in range(pax.total):

                    if count_paxes >= max_ocupancy_pms:
                        break

                    child_pax = self.__createGuestCountChildren(med,1)

                    guest_count_data.append(child_pax)
                    count_paxes += 1
            
        return {'GuestCountField': guest_count_data}

    def __createGuestCountAdult(self, adults):
        return {
            "ageQualifyingCodeField": "ADULT",
            "ageQualifyingCodeFieldSpecified": True,
            "ageFieldSpecified": True,
            "countField": adults,
            "countFieldSpecified": True
        }
    
    def __createGuestCountChildren(self, age, count):
        return {
                "ageQualifyingCodeField": "CHILD",
                "ageField": age,
                "ageQualifyingCodeFieldSpecified": True,
                "ageFieldSpecified": True,
                "countField": count,
                "countFieldSpecified": True
            }
    
    def time_span(self, check_in_date, check_out_date):

        if isinstance(check_in_date,datatime) == False:
            check_in_date = datatime.strftime(check_in_date,"%Y-%m-%d")
        if isinstance(check_out_date,datatime) == False:
            check_out_date = datatime.strftime(check_out_date,"%Y-%m-%d")

        return {
            "StartDateField": datatime.strptime(check_in_date,"%Y-%m-%d"),
            "ItemField": datatime.strptime(check_out_date,"%Y-%m-%d")
        }
    
    def guarantee(self, payment_method):

        data = {
           "GuaranteesAcceptedField":[{
               "GuaranteeTravelAgentField":{
                  "sourceField":"0",
                  "typeField":1
               }
           }],
           "guaranteeTypeField":payment_method
        }

        return data
    
    def user_defined_values(self, promo_code = None, clever_code = None):
        udfs = []
        if promo_code:
            udfs.append(self.udf_promo_code(promo_code))
                        
        if clever_code:
            udfs.append(self.udf_clever_code(clever_code))
        
        return udfs
    
    def udf_promo_code(self, promo_code):
        return {
            "valueNameField": "UDFC23_label",
            "itemField": promo_code
        }

    def udf_clever_code(self, clever_code):
        return {
            "valueNameField": "UDFC35_label",
            "itemField": clever_code
        }
    
    def hotel(self, hotel_code, chain_code="CHA"):
        return {
            "chainCodeField": chain_code,
            "hotelCodeField": hotel_code
        }
    
    def res_guests(self, id_profile, company_code):
        data = [{
            "ProfilesField":[{
                "ProfileIDsField":[{
                    "typeField":1,
                    "ValueField":id_profile
                }],
                "ItemField": {
                    "CompanyTypeField": 2,
                    "CompanyIDField": company_code
                },
                "languageCodeField":"E"
            }]
        }]
        return data

    def comments(self, comments):

        comments_list = []
        for comment in comments:
            
            if isinstance(comment,commentModel) == False:
                raise Exception ("Modelo no compatible")

            visible_to_guest = True
            if comment.visible_to_guest == 0:
                visible_to_guest = False

            data = {            
                "CommentTypeField": "RESERVATION",
                "guestViewableField": visible_to_guest,
                "guestViewableFieldSpecified": True,
                "itemsField": [{
                    "valueField": comment.text
                }],
                "ItemsElementNameField": [1]
            }
            comments_list.append(data)

        return comments_list

    def promotions_in_comments(self, promotions_list):

        text_promotions = ""

        for promotion in promotions_list:

            text_promotions += promotion.promotion.code# + " "
            #text_promotions += str(promotion.amount)

            if len(promotions_list)>1:
                text_promotions += " , "
        
        data = {            
            "CommentTypeField": "INF",
            "guestViewableField": True,
            "guestViewableFieldSpecified": True,
            "itemsField": [{
                "valueField": text_promotions
            }],
            "ItemsElementNameField": [1]
        }        

        return data


    def service_in_comments(self, service_list):

        text_service = ""

        for service in service_list:

            text_service += service.description + " Cost: "
            text_service += str(service.total)

            if len(service_list)>1:
                text_service += " , "
        
        data = {            
            "CommentTypeField": "INF",
            "guestViewableField": True,
            "guestViewableFieldSpecified": True,
            "itemsField": [{
                "valueField": text_service
            }],
            "ItemsElementNameField": [1]
        }        

        return data