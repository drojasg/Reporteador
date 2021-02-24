from config import base
#from common.external_credentials import ExternalCredentials
#from common.custom_log_request import CustomLogRequest
from models.book_hotel_room import BookHotelRoom

class CleverPaymentService():
    def __init__(self):
        self.__url = base.get_url("payment")
        self.__uri_card_payment = "{}/proxyonlinepayment/postcardpayment".format(self.__url)
        self.__uri_link_payment = "{}/proxypayment/postpaymentgeneral".format(self.__url)
        self.__external_credentials = ExternalCredentials()
    
    def confirm_payment(self, hotel, payment):
        '''
            Do the payment for all the rooms (reservations) in a transaction.

            :param hotel:    BookHotel   hotel & rooms information
            :param payment:  dict        payment information

            :return response: dict       Response information
        '''

        address = hotel.customers[0].customer.address.address if hotel.customers[0].customer.address.address else hotel.customers[0].customer.address.country.alias
        city = hotel.customers[0].customer.address.city if hotel.customers[0].customer.address.city else hotel.customers[0].customer.address.country.alias
        cia = payment["companies"]["MEX"] if hotel.customers[0].customer.address.country.alias == "MEX" else payment["companies"]["DEFAULT"]
        
        request = {
            "usuario_creacion": "",
            "tipo_cambio": hotel.exchange_rate,
            "divisa": payment["currency_code"],
            "reserva": 0,
            "idfin_cliente_interno": 0,
            "pago_general": True,
            "forma_pago": [
                {
                    "idfin_forma_pago": 0,
                    "pago_detalle": [],
                    "pago_SR": {
                        "hotel": hotel.property.property_code,
                        "cia": cia,
                        "tc_nombre": payment["holder_first_name"],
                        "tc_apellido": payment["holder_last_name"],
                        "tc_numero": payment["card_number"],
                        "tc_codigo": payment["cvv"],
                        "tc_mm_exp": payment["expirity_month"],
                        "tc_yy_exp": payment["expirity_year"],
                        "tc_direccion": address,
                        "tc_codigo_postal": hotel.customers[0].customer.address.zip_code,
                        "tc_ciudad": city,
                        "tc_pais": hotel.customers[0].customer.address.country.alias,
                        "tc_tipo_tarjeta": payment["card_type_code_fin"],
                    }
                }
            ]
        }

        response = {
            "error": False,
            "data": {},
            "message": ""
        }

        try:
            credentials = self.__external_credentials.get_credentials_by_system(base.system_id)

            if credentials is None:
                raise Exception("Credential config not found")

            request["usuario_creacion"] = credentials.user
            request["idfin_cliente_interno"] = payment["idfin_cliente_interno"]
            request["forma_pago"][0]["idfin_forma_pago"] = payment["idfin_forma_pago"]

            list_details = []
            for room in hotel.rooms:
                if room.charge_option == BookHotelRoom.charge_option_at_moment:
                    detail = {
                        "idServicioExterno": room.idbook_hotel_room,
                        "importe": room.amount_to_pay,
                        "hotel": hotel.property.property_code,
                        "idconcepto_ingreso": payment["idconcepto_ingreso"]
                    }
                    list_details.append(detail)
            
            request["forma_pago"][0]["pago_detalle"] = list_details            
            response_service = self.__do_request(self.__uri_card_payment, "post", request, hotel.usuario_creacion, True)
            if response_service["error"]:
                raise Exception(response_service["message"])

            response["data"] = response_service["data"]
            response["message"] = response_service["message"]

        except Exception as e:
            response["error"] = True
            response["message"] = str(e)
        finally:
            pass
            #TODO: Save request & response log 
        
        return response

    def confirm_payment_update(self, hotel, payment, rooms_to_pay=[]):
        '''
            Do the payment for all the rooms (reservations) in a transaction.

            :param hotel:    BookHotel   hotel & rooms information
            :param payment:  dict        payment information

            :return response: dict       Response information
        '''

        address = hotel.customers[0].customer.address.address if hotel.customers[0].customer.address.address else hotel.customers[0].customer.address.country.alias
        city = hotel.customers[0].customer.address.city if hotel.customers[0].customer.address.city else hotel.customers[0].customer.address.country.alias
        cia = payment["companies"]["MEX"] if hotel.customers[0].customer.address.country.alias == "MEX" else payment["companies"]["DEFAULT"]

        request = {
            "usuario_creacion": "",
            "tipo_cambio": 1,
            "divisa": payment["currency_code"],
            "reserva": 0,
            "idfin_cliente_interno": 0,
            "pago_general": True,
            "forma_pago": [
                {
                    "idfin_forma_pago": 0,
                    "pago_detalle": [],
                    "pago_SR": {
                        "hotel": hotel.property.property_code,
                        "cia": cia,
                        "tc_nombre": payment["holder_first_name"],
                        "tc_apellido": payment["holder_last_name"],
                        "tc_numero": payment["card_number"],
                        "tc_codigo": payment["cvv"],
                        "tc_mm_exp": payment["expirity_month"],
                        "tc_yy_exp": payment["expirity_year"],
                        "tc_direccion": address,
                        "tc_codigo_postal": hotel.customers[0].customer.address.zip_code,
                        "tc_ciudad": city,
                        "tc_pais": hotel.customers[0].customer.address.country.alias,
                        "tc_tipo_tarjeta": payment["card_type_code_fin"],
                    }
                }
            ]
        }

        response = {
            "error": False,
            "data": {},
            "message": ""
        }

        try:
            credentials = self.__external_credentials.get_credentials_by_system(base.system_id)

            if credentials is None:
                raise Exception("Credential config not found")

            request["usuario_creacion"] = credentials.user
            request["idfin_cliente_interno"] = payment["idfin_cliente_interno"]
            request["forma_pago"][0]["idfin_forma_pago"] = payment["idfin_forma_pago"]

            list_details = []
            for room_pay in rooms_to_pay:
                detail = {
                    "idServicioExterno": room_pay["idbook_hotel_room"],
                    "importe": room_pay["total_to_paid_room"],
                    "hotel": hotel.property.property_code,
                    "idconcepto_ingreso": payment["idconcepto_ingreso"]
                }
                list_details.append(detail)

            if len(list_details) == 0:
                raise Exception("No details")
            
            request["forma_pago"][0]["pago_detalle"] = list_details            
            response_service = self.__do_request(self.__uri_card_payment, "post", request, hotel.usuario_creacion, True)
            if response_service["error"]:
                raise Exception(response_service["message"])

            response["data"] = response_service["data"]
            response["message"] = response_service["message"]

        except Exception as e:
            response["error"] = True
            response["message"] = str(e)
        finally:
            pass
            #TODO: Save request & response log 
        
        return response
    
    def link_room_payment(self, reservation_number, id_payment, username):
        '''
            Relation the payment id with the reservation number for statistics.

            :param reservation_number:   int   reservation number (nowdays Opera folio)
            :param id_payment:           int   id payment (retrive from proxyonlinepayment/postcardpayment response)

            :return response: dict       Response information
        '''

        request = {
            "idpago_detalle_general":id_payment,
            "idReservaOpera":reservation_number
        }

        response = {
            "error": False,
            "data": {},
            "message": ""
        }

        try:
            response_service = self.__do_request(self.__uri_link_payment, "POST", request, username)
            response["data"] = response_service["data"]
            response["message"] = response_service["message"]
        except Exception as e:
            response["error"] = True
            response["message"] = str(e)
        finally:
            pass
            #TODO: Save request & response log 
        
        return response

    def __do_request(self, endpoint, method, data, username, log_request_ignore=False):
        '''
            Generic method to do request

            :param endpoint: endpoint API Service
            :param method: HTTP method type (post, get, put, patch, etc...)
            :param data: dictionary data to send to API Service
        '''
        token = self.__external_credentials.get_token(base.system_id)
        timeout = 15
        use_token = False
        response = CustomLogRequest.do_request(url=endpoint, method=method, \
            data=data, timeout=timeout, use_token=use_token, token = token, username = username, log_request_ignore = log_request_ignore)
        
        return response
