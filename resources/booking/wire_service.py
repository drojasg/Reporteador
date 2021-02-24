from config import base
#from common.custom_log_request import CustomLogRequest
#from common.external_credentials import ExternalCredentials

class WireService():
    __messages_code = {
        "GENERAL_UPD_FAILURE": "All the room type blocked has been used",
        "ROOM_UNAVAILABLE": "ROOM UNAVAILABLE",
        "PROPERTY_RESTRICTED": "Property restricted. Not exists availability",
        "INVALID_RATE_CODE":"Invalid rate code",
        "INVALID_ROOM_CATEGORY": "Invalid room type category",
        "INVALID_CURRENCY_CODE": "Invalid currency code"
    }

    def __init__(self):
        self.__url = base.get_url("wire_reservation")
        self.__uri_create_booking = "/reservation/CreateBooking/"
        self.__uri_update_booking = "/reservation/ModifyBooking/"
        self.__uri_cancel_booking = "/reservation/CancelBooking/"
        self.__uri_create_profile = "/name/RegisterName/"
        self.__uri_edit_profile = "/name/UpdateName/"
        self.__external_credentials = ExternalCredentials()
    
    def create_profile(self, first_name, last_name, country_code, email, phonenumber, username):
        '''
            Create customer profile in Opera

            :param first_name: First name customer
            :param last_name: Last name customer
            :param country_code: country code customer
            :param username: Username to log
        '''
        response = {
            "error": True,
            "message": "Error in Opera profile",
            "id_profile": 0
        }
        request = {
            "PersonNameField": {
                "firstNameField": first_name,
                "lastNameField": last_name,
            },
            "PhoneField": [
                {
                    "phoneTypeField": "EMAIL",
                    "phoneRoleField": "EMAIL",
                    "itemField": email
                },
                {
                    "phoneTypeField": "HOME",
                    "phoneRoleField": "PHONE",
                    "itemField": phonenumber
                }
            ],
            "AddressField": {
                "addressTypeField": "HOME",
                "countryCodeField": country_code
            }

        }
        response_data = self.__do_request(self.__uri_create_profile, "POST", request, username)

        if response_data != None:
            ids_field = response_data["resultField"]["iDsField"]
            if ids_field != None:
                response["message"] = "Profile was created"
                response["error"] = False
                response["idProfile"] = ids_field[0]["operaIdField"]
        
        return response

    def edit_profile(self, id_profile, first_name, last_name, country_code, username):
        response = {
            "error": True,
            "message": "Error in the Opera profile edit",
            "id_profile": 0
        }

        request = {
            "NameIDField": {
                "typeField": 1,
                "ValueField": id_profile,
            },
            "PersonNameField": {
                "firstNameField": first_name,
                "lastNameField": last_name,
            },
            "AddressField": {
                "addressTypeField": "HOME",
                "countryCodeField": country_code
            }
        }

        response_data = self.__do_request(self.__uri_edit_profile, "PUT", request, username)

        if response_data != None and response_data["resultField"]:
            response["message"] = "Profile was edited"
            response["error"] = False
            response["idProfile"] = id_profile

        return response
    
    def create_booking(self,request, username):
        response = {"error": False, "message": "", "reservationNumber": 0}
        
        response_data = self.__do_request(self.__uri_create_booking,"POST",request, username)

        if response_data["hotelReservationField"] is not None:
            #La reserva se creo correctamente
            if response_data["hotelReservationField"]["uniqueIDListField"] is not None:
                #regreso un id de reserva
                for uniqueid in response_data["hotelReservationField"]["uniqueIDListField"]:
                    if uniqueid["sourceField"] is None:
                        response["reservationNumber"] = uniqueid["valueField"]
            else:
                response["error"] = True
                response["message"] = "uniqueIDListField no encontrado"
        else:
            #Existe un error
            error_opera_code = response_data["resultField"]["operaErrorCodeField"]
            if response_data["resultField"]["textField"] is not None:
                if len(response_data["resultField"]["textField"]) >=1:
                    msg_error = response_data["resultField"]["textField"][0]
                    if msg_error["valueField"] is not None:
                        error_opera_code = msg_error["valueField"]
                    else:
                        message_code = self.__get_generic_error_message(error_opera_code)

                    self.__try_new_room(request,error_opera_code)

            response['error'] = True
            response['message'] = message_code

        #if response_data["resultField"]["textField"] is None:
        #    booking_info = response_data["hotelReservationField"]["uniqueIDListField"]
        #    """
        #        TODO: validations to get the opera folio
        #    """

        #    response["reservationNumber"] = booking_info

        #else:
        #    error_data = response_data["resultField"]["textField"]
        #    error_data = error_data[0]
        #    error_opera_code = response_data["resultField"]["operaErrorCodeField"]
        #    message_code = error_data["valueField"] if error_data["valueField"] is not None else self.__get_generic_error_message(error_opera_code)

        #    response['error'] = True
        #    response['message'] = message_code

        return response

    def update_booking(self,request, username):
        response = {"error": False, "message": "", "reservationNumber": 0}
        
        response_data = self.__do_request(self.__uri_update_booking,"POST",request, username)

        if response_data["hotelReservationField"] is not None:
            #La reserva se creo correctamente
            if response_data["hotelReservationField"]["uniqueIDListField"] is not None:
                #regreso un id de reserva
                for uniqueid in response_data["hotelReservationField"]["uniqueIDListField"]:
                    if uniqueid["sourceField"] is None:
                        response["reservationNumber"] = uniqueid["valueField"]
            else:
                response["error"] = True
                response["message"] = "uniqueIDListField no encontrado"
        else:
            #Existe un error
            error_opera_code = response_data["resultField"]["operaErrorCodeField"]
            if response_data["resultField"]["textField"] is not None:
                if len(response_data["resultField"]["textField"]) >=1:
                    msg_error = response_data["resultField"]["textField"][0]
                    if msg_error["valueField"] is not None:
                        error_opera_code = msg_error["valueField"]
                    else:        
                        message_code = self.__get_generic_error_message(error_opera_code)

                    self.__try_new_room(request,error_opera_code)

            response['error'] = True
            response['message'] = message_code

        return response
    
    def cancel_booking(self, hotel_code, folio_opera, username, reason_cancellation = ""):
        request_base = {
            "HotelReferenceField": {
                "chainCodeField": "CHA",
                "hotelCodeField": hotel_code,
            },
            "ConfirmationNumberField": {
                "typeField": "INTERNAL",
                "ValueField": folio_opera
            }
        }

        if reason_cancellation:
            request_base["CancelTermField"] = {
                "cancelTypeField":"Cancel",
                "cancelReasonCodeField":"PLAN",
                "CancelReasonField":{
                    "ItemsField": [reason_cancellation]
                }
            }

        response = self.__do_request(self.__uri_cancel_booking,"PUT",request_base, username)
        
        return response

    def __try_new_room(self,request,error_code):
        msg = "Success"
        
        try:
            if error_code.upper() == "ROOM_UNAVAILABLE":
                room_1 = request["HotelReservationField"]["RoomStaysField"][0]["RoomTypesField"][0]["roomTypeCodeField"]
                room_2 = self.__set_room(room_1)
                print(room_2)
                #self.create_booking(new_request,username)
        except Exception as error_data:
            pass

        return msg
    
    def __change_room(self,room_1,room_2):
        pass

    def __set_room(self,room):
        room_try = room

        try:
            position = len(room)
            new_character = 'D'

            if room[-1].upper() == "K":
                temp = list(room)
                temp[position-1] = new_character.upper()
                room_try = "".join(temp)

        except Exception as try_room_error:
            pass


        return room_try

    
    def __get_generic_error_message(self, error_code):
        message = self.__messages_code.get(error_code, None)

        return "" if message is None else message

    def __do_request(self, endpoint, method, data, username):
        '''
            Generic method to do request

            :param endpoint: endpoint API Service
            :param method: HTTP method type (post, get, put, patch, etc...)
            :param data: dictionary data to send to API Service
        '''
        
        url = "{}{}".format(self.__url, endpoint)
        token = self.__external_credentials.get_token(base.system_id)
        timeout = 15
        use_token = False
        response = CustomLogRequest.do_request(url=url, method=method, \
            data=data, timeout=timeout, use_token=use_token, token = token, username = username)
        
        return response

