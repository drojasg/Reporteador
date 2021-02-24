from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import datetime
from config import db, base
import requests as external_request
import re

class PaymentWire(Resource):

    def get(self):
        url_base = "http://web-test19:8087/WireServiceInterface/service.asmx?op=cobros_regatta_InsertarDinamico"
        headers = {'content-type': 'text/xml'}
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
                            <card_exp xmlns="http://localhost/pr_xmlschemas/wirepr/cobros_regatta.xsd">{exp_card}</card_exp>\
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
        </soap:Envelope>'.format(book_reference="ZRZC-150-BE",pms_folio=12345789456,\
        hotel_code="ZRCZ",check_in_date=datetime.now().isoformat(),amount=1000,\
        currency="usd",card_type="VI",card_number=411111111111111,first_name="luis",\
        last_name="novelo",cvc_card=123,exp_card="12|22",\
        check_out_date=datetime.now().isoformat(),create_date=datetime.now().isoformat())

        #print(xml_base)

        test_request = external_request.post(url_base,data=xml_base,headers=headers)

        response_error = True
        if test_request.status_code == 200:
            x = re.search("<HasErrors>false</HasErrors>", test_request.text)
            txt_response = test_request.text[x.start():x.end()].upper()
            x2 = re.search("TRUE|FALSE",txt_response)
            result = txt_response[x2.start():x2.end()].upper()
            
            if result == "FALSE":
                response_error = False
        # else:
        #     er = re.search('<Message xmlns="http://localhost/pr_xmlschemas/wirepr/ExceptionInfo.xsd">.*</Message>',test_request.text)
        #     #Buscamos el texto de error
        #     pass

        data={
            "code":500,
            "msg":"Succes",
            "data":response_error,
            "error":False
        }

        return data