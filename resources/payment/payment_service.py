from datetime import date
from config import base, db, app

from resources.payment.clever_payment_service import CleverPaymentService
from models.payment_method import PaymentMethod
from models.payment_transaction import PaymentTransaction
from models.payment_transaction_detail import PaymentTransactionDetail
from models.payment_transaction_type import PaymentTransactionType
from datetime import date, datetime, timedelta
import requests as external_request
import re
from models.book_hotel_room import BookHotelRoom

class PaymentService():
    @staticmethod
    def get_config(payment_method_id):
        '''
            Retrieve the payment method config.
            :param: payment_method_id 
        '''
        config = None

        payment_method = PaymentMethod.query.filter(
            PaymentMethod.idpayment_method == payment_method_id, PaymentMethod.has_config == 1, PaymentMethod.estado == 1).first()
        
        if payment_method is not None:
            config = payment_method.config

        return config
    
    @staticmethod
    def format_info(self,book_hotel,payment):
        data = []

        for room in book_hotel.book_hotel_room:
            
            data_item = {
                'referencia_regatta': book_hotel.code_reservation,
                'no_reserva': room.pms_confirm_number,
                'hotel': book_hotel.property.property_code,
                'checkin_original': book_hotel.from_date,
                'monto_original': room.amount_pending_payment,
                'moneda_original': payment["currency_code"],
                'card_type': self.get_card_type(payment["card_type_code"]),
                'card_num': payment["card_number"],
                'card_first_name': payment["holder_first_name"],
                'card_last_name': payment["holder_last_name"],
                'card_cvc': payment["cvv"],
                'card_exp': payment["expirity_month"] + "|" + payment["expirity_year"],
                'checkin_actualizado': book_hotel.to_date,
                "estatus_cobro": "Pendiente",
                "estatus": "NoCobrado",
                "estatus_opera": "Pendiente",
                'ent_user': "Booking Engine",
                'ent_date': datetime.now(),
                'ent_time': "12:00",
                'pci': 0                        
            }

            data.append(data_item)

        return data
    
    @staticmethod
    def get_card_type(card_code):
        """
            Return card type to charges web service.
            param: card_code String Card code of Booking Engine (exists in payment_card_type table)
        """
        if card_code == "amex":
            return "AX"
        if card_code == "visa":
            return "VI"
        if card_code == "mastercard":
            return "MC"
        
        return ""
    
    @staticmethod
    def payment_auto_charge(self, book_hotel_info,payment_data_card):

        payment_response = PaymentService.payment_auto_config(self,book_hotel_info,payment_data_card)

        if not payment_response["error"]:

            for item in payment_response["data"]:

                if item["procesed"] == True:

                    payment = PaymentTransaction()

                    payment.idbook_hotel = book_hotel_info.idbook_hotel
                    payment.idpayment_method = PaymentMethod.charge_before_arrived
                    payment.idpayment_transaction_type = PaymentTransactionType.payment_type
                    payment.card_code = payment_data_card["card_type_code"]
                    payment.authorization_code = 0
                    payment.merchant_code = 0
                    payment.ticket_code = 0
                    payment.idfin_payment = 0
                    payment.amount = book_hotel_info.amount_pending_payment
                    payment.exchange_rate = 1
                    payment.currency_code = payment_data_card["currency_code"]
                    payment.idop_sistema = 5
                    payment.external_code = item["recnum"]
                    payment.estado = 2
                    payment.usuario_creacion = payment_data_card["user"]

                    payment_details = []
                    payment_detail = PaymentTransactionDetail()
                    payment_detail.idFin = 0
                    payment_detail.amount = item["amount"]
                    payment_detail.idbook_hotel_room = item["idroom"]
                    payment_detail.interfaced = 1
                    payment_detail.estado = 1
                    payment_detail.usuario_creacion = payment_data_card["user"]
                    payment_details.append(payment_detail)
                    payment.details = payment_details

                    db.session.add(payment)
            db.session.commit()
        
        return ""

    @staticmethod
    def payment_auto_config(self,book_hotel_info,payment_data_card):

        list_response_room = []
        try:
            url_base = "{}?op=cobros_regatta_InsertarDinamico".format(base.get_url("charges_service"))
            #url_base = "http://web-test19:8087/WireServiceInterface/service.asmx?op=cobros_regatta_InsertarDinamico"
            headers = {'content-type': 'text/xml'}

            exp_m_str = str(payment_data_card["expirity_month"])
            str_date=str(payment_data_card["expirity_year"])+"-"+exp_m_str+"-01"
            exp_date = datetime.strptime(str_date,"%Y-%m-%d")

            xml_base = '<?xml version="1.0" encoding="utf-8"?>\
            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">\
                <soap:Body>\
                    <cobros_regatta_InsertarDinamico xmlns="http://localhost/pr_xmlschemas/wirepr/">\
                        <cobros_regattaRequest xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regattaRequest.xsd">\
                            <Data>\
                                <referencia_regatta xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{book_reference}</referencia_regatta>\
                                <no_reserva xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{pms_folio}</no_reserva>\
                                <hotel xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{hotel_code}</hotel>\
                                <checkin_original xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{check_in_date}</checkin_original>\
                                <monto_original xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{amount}</monto_original>\
                                <moneda_original xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{currency}</moneda_original>\
                                <card_type xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{card_type}</card_type>\
                                <card_num xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{card_number}</card_num>\
                                <card_first_name xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{first_name}</card_first_name>\
                                <card_last_name xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{last_name}</card_last_name>\
                                <card_cvc xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{cvc_card}</card_cvc>\
                                <card_exp xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{exp_card:%m|%y}</card_exp>\
                                <checkin_actualizado xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{check_out_date}</checkin_actualizado>\
                                <estatus_cobro xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">Pendiente</estatus_cobro>\
                                <estatus xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">NoCobrado</estatus>\
                                <estatus_opera xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">Pendiente</estatus_opera>\
                                <ent_user xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">BookingEngine</ent_user>\
                                <ent_date xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{create_date}</ent_date>\
                                <ent_time xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">12:00</ent_time>\
                                <pci xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">0</pci>\
                            </Data>\
                        </cobros_regattaRequest>\
                    </cobros_regatta_InsertarDinamico>\
                </soap:Body>\
            </soap:Envelope>'
        
            for room in book_hotel_info.book_hotel_room:
                if room.estado == 1:
                    item = {
                        "idroom":room.idbook_hotel_room,
                        "amount":room.amount_to_pending_payment,
                        "procesed":False,
                        "msg":"La reserva se cobrara un dia antes de la reserva",
                        "recnum":0
                    }

                    try:
                        
                        if room.charge_option == 2 or room.charge_option == 3:

                            if room.amount_to_pending_payment > 0:
                                request = xml_base.format(book_reference=book_hotel_info.code_reservation,\
                                pms_folio=room.pms_confirm_number,\
                                hotel_code=book_hotel_info.property.property_code,\
                                check_in_date=book_hotel_info.from_date.isoformat(),\
                                amount=room.amount_to_pending_payment,\
                                currency=payment_data_card["currency_code"],\
                                card_type=PaymentService.get_card_type(payment_data_card["card_type_code"]),\
                                card_number=payment_data_card["card_number"],\
                                first_name=payment_data_card["holder_first_name"],\
                                last_name=payment_data_card["holder_last_name"],\
                                cvc_card=payment_data_card["cvv"],\
                                exp_card=exp_date,\
                                check_out_date=book_hotel_info.from_date.isoformat(),\
                                create_date=datetime.now().isoformat())
                            
                                #print(request)

                                try:
                                    response_wire = external_request.post(url_base,data=request,headers=headers)
                                    
                                    if response_wire.status_code == 200:
                                        x = re.search("<HasErrors>false</HasErrors>", response_wire.text)
                                        if x is not None:
                                            txt_response = response_wire.text[x.start():x.end()].upper()
                                            x2 = re.search("TRUE|FALSE",txt_response)
                                            if x2 is not None:
                                                result = txt_response[x2.start():x2.end()].upper()
                                                if result == "FALSE":
                                                    item["procesed"] = True
                                                    recnum_get = re.search('<recnum xmlns="http:\/\/localhost\/pr_xmlschemas\/wirepr\/cobros_regatta.xsd">\d+<\/recnum>',\
                                                    response_wire.text)
                                                    if recnum_get is not None:
                                                        recnum1 = response_wire.text[recnum_get.start():recnum_get.end()]
                                                        recnum = re.search("\d+",recnum1)
                                                        if recnum is not None:
                                                            item["recnum"]=recnum1[recnum.start():recnum.end()]
                                                        else:
                                                            item["msg"]="Recnum no encontrado"
                                                    else:
                                                        item["msg"]="Recnum no encontrado"
                                                else:
                                                    item["msg"] = "La habitacion no se pudo enviar al sistema de pagos"
                                    else:
                                        item["msg"] = "La habitacion no pudo ser procesada correctamente, wire error"
                                except Exception as request_error:
                                        item["msg"]=str(request_error)
                            else:
                                item["msg"] = "La habitacion no tiene saldo pendiente a cobrar"
                        else:
                            item["msg"]="La habitacion no requiere cobrar antes de su llegada"

                    except Exception as room_process_error:
                        item["msg"]="Se produjo un error inesperado al procesar la habitacion"

                    list_response_room.append(item)

            data={
                "code":200,
                "msg":"Success",
                "data":list_response_room,
                "error":False
            }

        except Exception as wire_payment_error:
            data={
                "code":500,
                "msg":str(wire_payment_error),
                "data":list_response_room,
                "error":True
            }

        return data
    
    def confirm_payment(self, book_hotel, payment_data):
        response = {
            "error": False,
            "data": {},
            "message": ""
        }

        total_charge_at_moment = 0
        #total_charge_before_arrived = 0

        for room in book_hotel.rooms:
            if room.charge_option == BookHotelRoom.charge_option_at_moment:
                total_charge_at_moment += 1
            #elif room.charge_option == BookHotelRoom.charge_option_before_arrived:
            #    total_charge_before_arrived += 1
        
        if total_charge_at_moment > 0:
            response = self.card_charge(book_hotel, payment_data)
        
        """
        if total_charge_before_arrived > 0:
            response = self.before_arrival_charge(book_hotel, payment_data):
        """
        return response
    
    @staticmethod
    def card_charge(book_hotel, payment_data):
        """
        docstring
        """
        response = {
            "error": False,
            "data": {},
            "message": ""
        }
        config = PaymentService.get_config(PaymentMethod.credit)
        
        if config is None:
            raise Exception("Payment method without config")

        payment_data["idfin_cliente_interno"] = config["idfin_cliente_interno"]
        payment_data["idfin_forma_pago"] = config["idfin_forma_pago"]
        payment_data["idconcepto_ingreso"] = config["idconcepto_ingreso"]
        payment_data["payment_method"] = PaymentMethod.credit
        payment_data["companies"] = config["companies"]
        
        payment_service = CleverPaymentService()
        payment_response = payment_service.confirm_payment(book_hotel, payment_data)

        if not payment_response["error"]:
            payment = PaymentTransaction()
            payment.idbook_hotel = book_hotel.idbook_hotel
            payment.idpayment_method = payment_data["payment_method"]
            payment.idpayment_transaction_type = PaymentTransactionType.payment_type
            payment.card_code = payment_data["card_type_code"]
            payment.authorization_code = payment_response["data"]["authorization"]
            payment.merchant_code = payment_response["data"]["merchant"]
            payment.ticket_code = payment_response["data"]["ticket"]
            payment.idfin_payment = payment_response["data"]["payment"]
            payment.amount = payment_response["data"]["amount_charged"]
            payment.exchange_rate = book_hotel.exchange_rate
            payment.currency_code = payment_response["data"]["currency"]
            payment.estado = 1
            payment.usuario_creacion = payment_data["user"]
            
            #Saving the distribution to re send to Clever Finance API with Opera folio
            payment_details = []
            for detail in payment_response["data"]["detalle"]["data"]:
                payment_detail = PaymentTransactionDetail()
                payment_detail.idFin = detail["idFin"]
                payment_detail.amount = detail["monto"]
                payment_detail.idbook_hotel_room = detail["idServicioExterno"]
                payment_detail.interfaced = 0
                payment_detail.estado = 1
                payment_detail.usuario_creacion = payment_data["user"]
                payment_details.append(payment_detail)

            payment.details = payment_details
            
            db.session.add(payment)
            db.session.commit()
        else:
            response["error"] = True
            response["message"] = payment_response["message"]
        
        return response

    def confirm_payment_update(self, book_hotel, payment_data, is_refund=False, total_amount=0, list_rooms=[]):
        response = {
            "error": False,
            "data": {},
            "message": ""
        }

        try:
            if total_amount == 0:
                return response

            if is_refund:
                raise Exception("Refund transaction is not valid")
            payment_transaction_type = PaymentTransactionType.refund_type if is_refund else PaymentTransactionType.payment_type
            if payment_transaction_type == PaymentTransactionType.refund_type:
                raise Exception("Refund transaction is not valid")

            config = self.get_config(payment_data["payment_method"])
        
            if config is None:
                raise Exception("Payment method without config")

            payment_data["idfin_cliente_interno"] = config["idfin_cliente_interno"]
            payment_data["idfin_forma_pago"] = config["idfin_forma_pago"]
            payment_data["idconcepto_ingreso"] = config["idconcepto_ingreso"]
            payment_data["companies"] = config["companies"]

            #Se obtiene listado de pagos por cuarto
            list_rooms_pay = []
            for elem_data in list_rooms:
                room = elem_data["model_room"]
                data = elem_data["data"]
                if data["total_to_paid_room"] > 0:
                    list_rooms_pay.append({"idbook_hotel_room":room.idbook_hotel_room, "total_to_paid_room":data["total_to_paid_room"]})

            payment_service = CleverPaymentService()
            payment_response = payment_service.confirm_payment_update(hotel=book_hotel, payment=payment_data, rooms_to_pay=list_rooms_pay)

            if not payment_response["error"]:
                payment = PaymentTransaction()
                payment.idbook_hotel = book_hotel.idbook_hotel
                payment.idpayment_method = payment_data["payment_method"]
                payment.idpayment_transaction_type = PaymentTransactionType.payment_type
                payment.card_code = payment_data["card_type_code"]
                payment.authorization_code = payment_response["data"]["authorization"]
                payment.merchant_code = payment_response["data"]["merchant"]
                payment.ticket_code = payment_response["data"]["ticket"]
                payment.idfin_payment = payment_response["data"]["payment"]
                payment.amount = payment_response["data"]["amount_charged"]
                payment.exchange_rate = 1
                payment.currency_code = payment_response["data"]["currency"]
                payment.estado = 1
                payment.usuario_creacion = payment_data["user"]

                #Saving the distribution to re send to Clever Finance API with Opera folio
                payment_details = []
                for detail in payment_response["data"]["detalle"]["data"]:
                    payment_detail = PaymentTransactionDetail()
                    payment_detail.idFin = detail["idFin"]
                    payment_detail.amount = detail["monto"]
                    payment_detail.idbook_hotel_room = detail["idServicioExterno"]
                    payment_detail.interfaced = 0
                    payment_detail.estado = 1
                    payment_detail.usuario_creacion = payment_data["user"]
                    payment_details.append(payment_detail)

                payment.details = payment_details

                db.session.add(payment)
                db.session.commit()
            else:
                response["error"] = True
                response["message"] = payment_response["message"]

        except Exception as ex:
            response["error"] = True
            response["message"] = str(ex)
        
        return response

    def update_payment_data(self, book_hotel, payment_data, is_refund=False, total_amount=0, list_data_rooms=[]):
        response = {
            "error": False,
            "data": {},
            "message": ""
        }

        try:
            if total_amount == 0:
                return response

            payment_transaction_type = PaymentTransactionType.refund_type if is_refund else PaymentTransactionType.payment_type

            payment = PaymentTransaction()
            payment.idbook_hotel = book_hotel.idbook_hotel
            payment.idpayment_method = payment_data["payment_method"]
            payment.idpayment_transaction_type = payment_transaction_type
            payment.card_code = payment_data["card_type_code"]
            payment.authorization_code = 0
            payment.merchant_code = 0
            payment.ticket_code = 0
            payment.idfin_payment = 0
            payment.amount = total_amount
            payment.exchange_rate = 1
            payment.currency_code = payment_data["currency_code"]
            payment.estado = 3 # External payment
            payment.usuario_creacion = payment_data["user"]

            #Saving the distribution to re send to Clever Finance API with Opera folio
            payment_details = []
            for data_room in list_data_rooms:
                room = data_room["model_room"]
                data = data_room["data"]
                if payment_transaction_type == PaymentTransactionType.refund_type:
                    if room.amount_paid > 0:
                        payment_detail = PaymentTransactionDetail()
                        payment_detail.idFin = 0
                        payment_detail.amount = room.amount_paid
                        payment_detail.idbook_hotel_room = room.idbook_hotel_room
                        payment_detail.interfaced = 1
                        payment_detail.estado = 1
                        payment_detail.usuario_creacion = payment_data["user"]
                        payment_details.append(payment_detail)

                        room.amount_pending_payment = room.total
                        room.amount_paid = 0
                else:
                    if data["total_to_paid_room"] > 0:
                        payment_detail = PaymentTransactionDetail()
                        payment_detail.idFin = 0
                        payment_detail.amount = data["total_to_paid_room"]
                        payment_detail.idbook_hotel_room = room.idbook_hotel_room
                        payment_detail.interfaced = 1
                        payment_detail.estado = 1
                        payment_detail.usuario_creacion = payment_data["user"]
                        payment_details.append(payment_detail)

            payment.details = payment_details
            
            db.session.add(payment)
            db.session.commit()

        except Exception as ex:
            response["error"] = True
            response["message"] = str(ex)

        return response

    def get_payment_info(self, idbook_hotel, idpayment_methods=[]):
        if isinstance(idpayment_methods, list) and len(idpayment_methods)==0:
            result = PaymentTransaction.query.filter(PaymentTransaction.idbook_hotel==idbook_hotel, PaymentTransaction.estado>0).all()
        elif isinstance(idpayment_methods, list) and len(idpayment_methods)>0:
            result = PaymentTransaction.query.filter(PaymentTransaction.idbook_hotel==idbook_hotel, PaymentTransaction.estado>0,
                PaymentTransaction.idpayment_method.in_(idpayment_methods)).all()
        else:
            raise Exception("idpayment_methods is not valid")

        return result

    def get_payment_detail_by_room(self, idbook_hotel_room):
        result = PaymentTransactionDetail.query.filter(PaymentTransactionDetail.idbook_hotel_room==idbook_hotel_room, PaymentTransactionDetail.estado>0).all()

        return result

    def get_sum_payments(self, idbook_hotel, idpayment_methods=[]):
        total = 0

        payments = self.get_payment_info(idbook_hotel, idpayment_methods)

        for payment in payments:
            if payment.idpayment_transaction_type == PaymentTransactionType.payment_type:
                total += payment.amount
            elif payment.idpayment_transaction_type == PaymentTransactionType.refund_type:
                total -= payment.amount

        return total

    def get_sum_payments_by_room(self, idbook_hotel_room):
        total = 0

        payment_details = self.get_payment_detail_by_room(idbook_hotel_room)

        for payment_detail in payment_details:
            total += payment_detail.amount

        return total

    def get_info_sum_payments(self, idbook_hotel, check_in_date):
        total_paid = 0
        total_pending = 0

        #se obtiene la fecha actual y la fecha que se debe realizar el cargo a tarjeta (un día antes de check-in)
        actual_date = datetime.now().date()
        charge_date = check_in_date - timedelta(days=1)

        #Se especifica si se toma lo inviado a wire como cobrado
        wire_is_paid = True if actual_date >= charge_date else False
        payments_paid, payments_pending = self.get_payment_info_complete(idbook_hotel, wire_is_paid)

        for payment in payments_paid:
            if payment.idpayment_transaction_type == PaymentTransactionType.payment_type:
                total_paid += payment.amount
            elif payment.idpayment_transaction_type == PaymentTransactionType.refund_type:
                total_paid -= payment.amount

        for payment in payments_pending:
            if payment.idpayment_transaction_type == PaymentTransactionType.payment_type:
                total_pending += payment.amount
            elif payment.idpayment_transaction_type == PaymentTransactionType.refund_type:
                total_pending -= payment.amount

        return {"total_paid":total_paid, "total_pending":total_pending}

    def get_payment_info_complete(self, idbook_hotel, wire_is_paid=False):
        if not wire_is_paid:
            payments_paid = PaymentTransaction.query.filter(PaymentTransaction.idbook_hotel==idbook_hotel, PaymentTransaction.estado>0,
                PaymentTransaction.idpayment_method != PaymentMethod.charge_before_arrived).all()
            payments_pending = PaymentTransaction.query.filter(PaymentTransaction.idbook_hotel==idbook_hotel, PaymentTransaction.estado>0,
                PaymentTransaction.idpayment_method == PaymentMethod.charge_before_arrived).all()
        else:
            payments_paid = PaymentTransaction.query.filter(PaymentTransaction.idbook_hotel==idbook_hotel, PaymentTransaction.estado>0).all()
            payments_pending = []

        return payments_paid, payments_pending

    
    @staticmethod
    def before_arrival_charge(book_hotel, payment_data):
        """
        docstring
        """
        response = {
            "error": False,
            "data": {},
            "message": ""
        }
        #TODO: Change for paredes SOAP Service
        payment_service = CleverPaymentService()
        for room in book_hotel.rooms:
            if room.charge_option == BookHotelRoom.charge_option_before_arrived:
                payment_response = payment_service.confirm_payment(book_hotel, payment_data)

                if not payment_response["error"]:
                    payment = PaymentTransaction()
                    payment.idbook_hotel = book_hotel.idbook_hotel
                    payment.idpayment_method = PaymentMethod.charge_before_arrived
                    payment.idpayment_transaction_type = PaymentTransactionType.payment_type
                    payment.card_code = payment_data["card_type_code"]
                    payment.amount = payment_response["data"]["amount_charged"]
                    #payment.idop_sistema = ""
                    #payment.external_code = payment_response[""]
                    payment.exchange_rate = 1
                    payment.currency_code = payment_response["data"]["currency"]
                    payment.estado = 1
                    payment.usuario_creacion = payment_data["user"]
                    
                    db.session.add(payment)
                    db.session.commit()
                else:
                    response["error"] = True
                    response["message"] = payment_response["message"]
                
        return response

    def link_room_payment(self, transaction_details, username):
        """
            :param transaction_details: List PaymentTransactionDetail List de detail payments
            :param username: string Username
            :return int Total interfaced values

            Save payment relation with pms confirmation number in Clever Finanzas
        """
        

        payment_service = CleverPaymentService()
        count = 0
        for idpayment_transaction_detail, idFin, pms_confirm_number in transaction_details:
            #send to clever finanzas
            payment_response = payment_service.link_room_payment(pms_confirm_number, idFin, username)

            if not payment_response["error"]:
                #search row
                transaction_detail = PaymentTransactionDetail.query.\
                    filter(PaymentTransactionDetail.idpayment_transaction_detail == idpayment_transaction_detail,\
                        PaymentTransactionDetail.estado == 1).first()
                
                #save changes
                transaction_detail.interfaced = 1
                transaction_detail.usuario_ultima_modificacion = username
                db.session.add(transaction_detail)
                db.session.commit()
                count += 1
        
        return count