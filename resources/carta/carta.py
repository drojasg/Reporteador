from flask import Flask, request, make_response
from flask_restful import Resource
from marshmallow import ValidationError
import htmlmin
import datetime
import json, requests
from config import db
from common.util import Util
from jinja2 import Environment, FileSystemLoader
import pdfkit
from resources.booking.booking_service import BookingService
from .carta_util import CartaUtil
import locale
from common.public_auth import PublicAuth

class Carta(Resource):
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



class CartaPdf(Resource):
    #@PublicAuth.access_middleware
    def get(self,  code_reservation, full_name , language_code):

        try:           
            booking_service = BookingService()
            booking_data = booking_service.get_booking_info_by_code(code_reservation, full_name, language_code)
            
            # return booking_data
            url_banner = ""
            url_reservation = ""
            # "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/guestPalace.png"
            if booking_data['property_code'] == "ZRCZ":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-47-35-717512header_Cozumel.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-38-544572img-pareja_Cozumel.png"
            elif booking_data['property_code'] == "ZHBP":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-46-25-784679header_BEACHPALACE.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-04-477370img-fut-beachplaya.png"
            elif booking_data['property_code'] == "ZHSP":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-44-09-055169header-sunpalace.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-46-09-424970img-pareja_SUN.png"
            elif booking_data['property_code'] == "ZHIM":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-47-53-609018header_IslaMujeres.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-22-964201img-pareja_ISLA.png"
            elif booking_data['property_code'] == "ZRPL":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-50-22-481438header_Playacar.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-44-50-331049img-fam_PLAYACAR.png"
            elif booking_data['property_code'] == "ZMSU":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-49-51-101055header_MoonPalace.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-51-04-189342img-alberca-moon.png"
            elif booking_data['property_code'] == "ZMGR":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-50-49-200988header_TheGrand.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-51-18-273585img-fam-TheGrand.png"
            elif booking_data['property_code'] == "ZCJG":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-48-08-530524header_jamaica.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-44-36-906474img-fam_Jamaica.png"
            elif booking_data['property_code'] == "ZHLB":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-48-53-205125header_LBC.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-21-09-08-53-03-758329img-meditacion-lbC.jpg"
            elif booking_data['property_code'] == "ZPLB":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-49-36-041442header_LBL.png"
                url_reservation = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-45-54-730283img-pareja_LBC.png"
            elif booking_data['property_code'] == "ZMNI":
                url_banner = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-19-09-10-50-05-218861header_nizuc.png"
                url_reservation = ""


            #textos por idioma
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
            bi_avisoDos = ""
            serUno = ""
            serDos = ""
            servicio = ""
            beneUno = ""
            beneDos = ""
            poliUno = ""
            poliDos = ""

            rateUno = ""
            rateDos = ""
            tx_room = ""

            tx_holdUno = ""
            tx_holdDos = ""
            tx_holdTres = ""

            img_qr = ''
            img_purely = ''
            img_footer = ''


            if language_code.upper() == "ES":
                tituloUno = "Es momento de hacer tus maletas"
                tituloDos = "Te esperamos en "
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
                tx_monto = "Total:"
                tx_avisoUno = "* Las habitaciones se asignan al momento de realizar el check-in."
                tx_avisoDos = "Las solicitudes especiales están sujetas a disponibilidad. Debes proporcionar una tarjeta de crédito en tu check-in, para cubrir cualquier imprevisto."
                tx_avisoTres = "Los pagos se aplican en dólares estadounidenses."
                tx_avisoCuatro = "El huésped es responsable de cubrir cualquier tasa de conversión monetaria al realizar su pago, así como de notificar y pagar por adelantado por todas las personas que se hospeden en la habitación."
                bi_llegadaFecha = "Fecha de llegada:"
                bi_salidaFecha = "Fecha de salida:"
                bi_llegadaHora = "Hora de entrada:"
                bi_salidaHora = "Hora de salida:"
                bi_noches = "Núm. de noches:"
                tx_deposit = "Deposito: "
                bi_cuartos = "Núm. de habitaciones:"
                bi_avisoDos = "Para disfrutar este beneficio debes proporcionar los detalles de tu vuelo y el número de pasajeros a más tardar siete (7) días antes de tu llegada."
                serUno = "SORPRENDENTES BENEFICIOS "
                serDos = "TODO INCLUIDO"
                servicio = "Nada será igual después de que experimentes nuestros altos estándares en lujo todo incluido. Disfruta amenidades que rebasan todas tus expectativas, como bebidas de alta gama ilimitadas, servicio a la habitación gourmet las 24 horas, WiFi de alta velocidad gratis, amenidades de baño marca CHI, llamadas gratuitas ilimitadas a los EE. UU. continentales, Canadá y teléfonos fijos de México, y mucho más."
                servicio2 = "Si tienes alguna duda o deseas modificar o cancelar tu reserva, por favor escríbenos a "
                servicio3url = "bookdirect@palaceresorts.com"
                beneUno = "Beneficios "
                beneDos = "adicionales"
                poliUno = "POLÍTICA DE "
                poliDos = "CANCELACIONES"

                tx_holdUno = "TU RESERVA EN " + booking_data["trade_name"].upper() + " ESTÁ EN ESPERA"
                tx_holdDos = "COMPLETE TU RESERVA ANTES DE "# + Carta.formatDate(self, booking_data["expiry_date"], True ,language_code.upper() )
                tx_holdTres = "LA RESERVA EXPIRARÁ AUTOMÁTICAMENTE DESPUÉS DE ESTE TIEMPO"
                
                rateUno = "Tarifa por "
                rateDos = "noche"
                tx_room = "Habitación"
                tx_cartType = "Tipo de tarjeta:"
                tx_balance="Saldo pendiente:"

            else :
                tituloUno = "Time to start packing."
                tituloDos = "You are going to"
                tituloClienteUno = "Guest"
                tituloClienteDos = "Information"
                tituloPagoUno = "Credit Card "
                tituloPagoDos = "Information"
                tituloConfirmacionUno = "Your Hotel "
                tituloConfirmacionDos = "Confirmation Code"
                tx_nombre = "Name:" 
                tx_numero = "Phone Number:"
                tx_correo = "Email:"
                tx_deposit = "Deposit: "
                tx_requerimiento ="Personalized Request:"
                tx_monto = "Total:"
                tx_avisoUno = "*Rooms are assigned at check-in and special requests are subject to availability."
                tx_avisoDos = "A credit card must be provided at check-in for room incidentals."
                tx_avisoTres = "Payments in US dollars only. Guests are responsible for covering any applicable conversion"
                tx_avisoCuatro = "rate and for notifying and paying in advance for all people in room."
                bi_llegadaFecha = "Arrival Date:"
                bi_salidaFecha = "Departure Date:"
                bi_llegadaHora = "Check-In Time:"
                bi_salidaHora = "Check-Out Time:"
                bi_noches = "No. of Nights:"
                bi_cuartos = "No. of Rooms:"
                bi_avisoDos = "Please note that in order to enjoy this benefit, guests must provide their flight details and number of passengers no later than 7 days prior to arrival."
                serUno = "YOUR AWE-INCLUSIVE"
                serDos = " BENEFITS"
                servicio = "After experiencing our standard of all-inclusive luxury, anything less will be inacceptable. Enjoy signature inclusions of our luxurious accommodations, including top-shelf sips, 24-hour room service, free WiFi, CHI bath amenities, unlimited calls to the Continental US, Canada and Mexico, and much more."
                servicio2 = "If you have any queries or wish to modify or cancel your reservation, please contact"
                servicio3url = "bookdirect@palaceresorts.com."
                beneUno = "Additional"
                beneDos = "Benefits"
                poliUno = "CANCELLATION "
                poliDos = "POLICY"
                tx_holdUno = "YOUR BOOKING AT " + booking_data["trade_name"].upper() + " IS ON HOLD"
                tx_holdDos = "COMPLETE YOUR BOOKING BEFORE " #+ Carta.formatDate(self, booking_data["expiry_date"], True ,language_code.upper() )
                tx_holdTres = "THE BOOKING WILL AUTOMATICALLY EXPIRE AFTER THIS TIME"



                rateUno = "Rate per "
                rateDos = "night"
                tx_room = "Room"
                tx_cartType = "Card type:"
                tx_balance="Outstanding balance:"


            html_footer=""
            html_services=""
            html_rooms = ""
            EFE = ""
            on_hold = ""
            carta = ""
            use_template = ""

            if booking_data["market_code"] == "MEXICO":
                tx_avisoTres = " "

            cardBooking = ""
            try:
                cardBooking = booking_data["payment"]["card_type"]
            except:
                cardBooking = ""

            #on hold
            if booking_data["on_hold"] == True:
                on_hold = '<div class="row"> <div class="col-xs-12"> <div class="text-left p-2"> <div class="text-main text-center"><p> '+tx_holdUno+' </p></div></div><div class="text-left p-2"> <div class="text-center text-uppercase"><b>'+tx_holdDos+ Carta.formatDate(self, booking_data["expiry_date"], True ,language_code.upper() )+'</b></div></div><div class="text-left p-2"> <div class="text-main text-center"><b>'+tx_holdTres+'</b></div></div></div></div>'
            else:
                on_hold = '<div class="text-center"> <b><p class="text-main">'+tituloPagoUno+' <span class="text-main">'+tituloPagoDos+'</span></p> </b></div><div class="row"><div class="col-xs-6"><div class="text-left p-2"><p class="grey-color">'+ tx_cartType +'</p></div></div><div class="col-xs-6"><div class="text-left p-2"><p>'+cardBooking+'</p></div></div></div><div class="row"><div class="col-xs-6"><div class="text-left p-2"><p class="grey-color">'+ tx_monto +'</p></div></div><div class="col-xs-6"><div class="text-left p-2"><p>'+ booking_data["currency_code"]+' $'+ str(booking_data["total"]) + '</p></div></div></div><div class="row"><div class="col-xs-6"><div class="text-left p-2"><p class="grey-color">'+ tx_deposit +'</p></div></div><div class="col-xs-6"><div class="text-left p-2"><p>'+booking_data["currency_code"]+' $'+str(booking_data["amount_paid"])+'</p></div></div></div><div class="row"><div class="col-xs-6"><div class="text-left p-2"><p class="grey-color">'+ tx_balance +'</p></div></div><div class="col-xs-6"><div class="text-left p-2"><p style="color:red!important;">'+booking_data["currency_code"]+' $'+str(booking_data["amount_pending_payment"])+'</p></div></div></div>'
            
            #Dorado Moon
            if booking_data["iddef_brand"] == 3:
                if booking_data['lang_code'] == "EN":
                    img_purely = "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-20-58-818237Purely_Moon-EN.png"
                else :
                    img_purely = "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-21-31-111161Purely_Moon-ES.png"    
                                
                img_location = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-14-45-703787Location.png"
                img_email = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-15-00-939158E-mail.png"
                img_phone = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-14-11-776814Phone_number.png"
                img_web = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-13-31-608305web.png"
                img_qr = 'https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/qr.png'
                img_footer = 'https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/footerTwo.png'
                use_template = "templateMoon.html"

                   

            #Azul Palace
            if booking_data["iddef_brand"] == 2:
                if booking_data['lang_code'] == "EN":
                    img_purely = "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-22-18-098360Purely_PR-EN.png"
                else :
                    img_purely = "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-22-56-562154Purely_PR-ES.png"
                img_qr = 'https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/qrPalace.png'
                
                                                
                img_location = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-06-46-603406Location.png"
                img_email = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-06-15-137005E-mail.png"
                img_phone = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-07-00-658284Phone_number.png"
                img_web = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-07-17-273578web.png"
                img_footer = 'https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/footerDosPalace.png'
                use_template = "templatePalace.html"
                

            #Naranja LeBlanc
            if booking_data["iddef_brand"] == 1:
                if booking_data['lang_code'] == "EN":
                    img_purely = "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-19-09-844133Purely_LBC-EN.png"
                else :
                    img_purely = "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine//2020-19-10-16-20-31-874344Purely_LBC-ES.png"                
                img_location = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-19-21-290643Location_LB.png"
                img_email = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-19-37-412912E-mail_LB.png"
                img_phone = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-19-09-077168Phone_number_LB.png"
                img_web = "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-18-38-651292web_LB.png"
                img_qr = 'https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/qr.png'
                img_footer = 'https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/footerTwo.png'
                use_template = "templateMoonLeBlanc.html"

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
                            union = union + "<div class='col-xs-6'> <img class='paddingFull my-1 img-fluid' src='"+services[i]["media"][0]["url"]+"' alt=''></img> <div class='text-center' style='padding: 5px;'> <b> <p class='text-main'>"+ services[i]["name"] +"</p></b> </div><div style='padding: 5px;' class='text-justify'> "+ services[i]["description"] +" </div></div>"
                        else:
                            union = union + "<div class='col-xs-6'> <img class='paddingFull my-1 img-fluid' src='https://d1.awsstatic.com/case-studies/PALACE-RESORTS.65dfce304db6469e4e2ffb31ba060ebed5dbc9f3.png' alt=''></img> <div class='text-center' style='padding: 5px;'> <b> <p class='text-main'>"+ services[i]["name"] +"</p></b> </div><div style='padding: 5px;' class='text-justify'> "+ services[i]["description"] +" </div></div>" 
                    except:
                        union = union + "<div class='col-xs-6'></div>"
                    i += 1
                columnas_services = columnas_services + "<div class='row'>" + union + "</div>" 
                inicio += 2
            html_services = columnas_services 
            if salida > 0 :
                html_services = "<div class='row'> <div class='col-xs-12'><div class='text-center' style='padding: 5px;'><b><p class='text-second'>"+beneUno+" <span class='text-main'>"+beneDos+"</span></p></b></div>" + html_services + "</div></div>"
                html_services = html_services + "<div class='row'><br><div class='col-xs-12'><div class='text-center p-2'><br><p style='border-top:solid 1px #E0E0E0;font-size:1px;margin:0px auto;width:100%;'> </p><br></div></div><br></div>"
            
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
                            union = union + "<div class='col-xs-6'><div class='text-center' style='padding:3px;'><p style='margin: 0px !important;'>"+ cliente["pax"][key_pax[i]]["text"] +": " + str(cliente["pax"][key_pax[i]]["value"]) + "</p></div></div>"
                            
                        except:
                            union = union + "<div class='col-xs-6'></div>"
                        i += 1
                    columnas_pax = columnas_pax + "<div class='row'>" + union + "</div>" 
                    inicio += 2
                    

                section_pax = "<div class='text-center' style='padding: 5px;'><b><p>"+cliente["rateplan_name"] +"</p> </b></div><br><div class='row'><div class='col-xs-6'><div class='text-center' style='padding: 5px;'><p> "+tx_room +" "+ str(index+1)+"</p></div></div><div class='col-xs-6'><div class='text-center' style='padding: 5px;'><p>"+cliente["trade_name_room"] +"</p></div></div></div><br>" + columnas_pax + "<br><div class='row'><div class='col-xs-4'><div class='text-center' style='padding: 5px;'></div></div><div class='col-xs-8'><div class='text-rigth' style='padding: 5px;'><p>Total: <span class='tachado grey-color'>" + booking_data["currency_code"] + " $" + str(cliente["total_crossout"]) +" </span></p><p>" + booking_data["currency_code"] + " $" + str(cliente["total"]) +"</p></div><div class='text-rigth' style='padding: 5px;'><p><span>"+tx_deposit+ " </span><span>"+ booking_data["currency_code"] + " $" + str(cliente["amount_paid"]) +"</span></p></div><div class='text-rigth' style='padding: 5px;'><p><span>"+tx_balance+ " </span><span style='color: red!important;'>"+ booking_data["currency_code"] + " $" + str(cliente["amount_pending_payment"]) +"</span></p></div></div></div>"
                html_rooms = html_rooms + "<br><div class='row align-items-center'><div class='col-xs-6'><img class='paddingFull my-1 img-fluid' src='"+cliente["media"][0]["url"] +"' alt=''></img></div><div class='col-xs-6'>" + section_pax + " </div></div>"

                #datos tarifario
                tarifas = cliente["prices"]
                inicio = 0
                salida = len(tarifas)
                columnas_tarifas = ""
                while inicio < salida:
                    i = inicio
                    union = ""
                    while i < inicio+6:
                                                    
                        try:
                            union = union +  "<div class='col-xs-2' style='border-right: 1px solid #eeeeee; padding: 10px 0px 10px 0px ;'><div class='text-center'><p style='margin: 0px !important;'>" + Carta.formatDate(self, str(tarifas[i]["date"]), False, language_code.upper() )  + "</p><p class='tachado grey-color' style='margin: 0px !important;'>"+ booking_data["currency_code"] + " $" + str(tarifas[i]["total_gross"]) + "</p><p style='margin: 0px !important;'>" + booking_data["currency_code"] + " $" + str(tarifas[i]["total"]) +"</p></div></div>" #"C"+tarifas[i]+"C " 
                        except:
                            union = union + "<div class='col-xs-2' style='border-right: 1px solid #eeeeee; padding: 10px 0px 10px 0px ;'> </div>"
                        i += 1
                    columnas_tarifas = columnas_tarifas + "<div class='row'><div class='col-xs-12' style='padding: 10px 0px 10px 0px ;'><br><div class='text-center'> <b><p class='grey-color'>"+rateUno+rateDos+"</p></b> </div><br></div></div> <div class='row' >" + union + " </div>" 
                    inicio += 6

                html_rooms = html_rooms + columnas_tarifas
            

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
                         
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template(use_template)

            datos = {
                'url_banner': url_banner,
                'tituloUno' : tituloUno,
                'tituloDos' : tituloDos,
                'propiedad': booking_data["trade_name"],
                'tituloClienteUno' : tituloClienteUno,
                'tituloClienteDos' : tituloClienteDos,
                'nombre':booking_data["customer"]["first_name"]+" "+ booking_data["customer"]["last_name"],
                'telefono':booking_data["customer"]["phone_number"],
                'correo':booking_data["customer"]["email"],
                'requerimiento_especial':booking_data["special_request"],
                'tx_nombre' : tx_nombre,
                'tx_numero' : tx_numero,
                'tx_correo' : tx_correo,
                'tx_requerimiento' : tx_requerimiento,
                'tx_avisoUno' : tx_avisoUno,
                'tx_avisoDos' : tx_avisoDos,
                'tituloConfirmacionUno' : tituloConfirmacionUno,
                'tituloConfirmacionDos' : tituloConfirmacionDos,
                'tx_avisoTres' : tx_avisoTres,
                'tx_avisoCuatro' : tx_avisoCuatro,
                'codigo_confirmacion': booking_data["code_reservation"],
                'url_reservation' : url_reservation,
                'on_hold' : on_hold,
                'tx_bookingUno' : tx_bookingUno,
                'tx_bookingDos' : tx_bookingDos,
                'bi_llegadaFecha' : bi_llegadaFecha,
                'bi_salidaFecha' : bi_salidaFecha,
                'bi_llegadaHora' : bi_llegadaHora,
                'bi_salidaHora' : bi_salidaHora,
                'bi_noches' : bi_noches,
                'bi_cuartos' : bi_cuartos,
                'check_in_tiempo': booking_data["general_data"]["check_in"],
                'check_out_tiempo': booking_data["general_data"]["check_out"],
                'check_in_fecha': Carta.formatDate(self, booking_data["from_date"], False,language_code.upper() ),
                'check_out_fecha': Carta.formatDate(self, booking_data["to_date"], False,language_code.upper() ),
                'noches': booking_data["nights"],
                'numeros_cuartos': booking_data["total_rooms"],
                'bi_avisoDos' : bi_avisoDos,
                'serUno' : serUno,
                'serDos' : serDos,
                'servicio' : servicio,
                'servicio2' : servicio2,
                'servicio3url' : servicio3url,
                'html_services':html_services,
                'html_rooms' : html_rooms,
                'poliUno' : poliUno,
                'poliDos' : poliDos,
                'politica_cancelacion':  politica_cancelacion ,
                'img_qr' : img_qr,
                'img_purely' : img_purely,
                'img_email' : img_email,
                'img_location' : img_location,
                'img_phone' : img_phone,
                'img_web' : img_web,
                'img_footer' : img_footer,
                'web_address' : booking_data["web_address"],
                'address' : booking_data["address"],
                'resort_phone' : booking_data["resort_phone"],
                'resort_email' : booking_data["resort_email"],
                'reservation_email' : booking_data["reservation_email"]
            }
            options = {
                'page-size': 'Letter',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8"
            }
            html = template.render(datos)

            pdf =  pdfkit.from_string(html, False, options=options, css="templates/bootstrap3.css")

            response = make_response(pdf)

            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename=out.pdf'
            return response 
        
        except Exception as e:          
            
            response = {
                "Code": 500,
                "Msg": str(e),
                "Error": True,
                "data": {}
            }
        
        return response

    def post(self): 
        response = {}
        try:
            dataResponse = []
            lang_code = request.form["lang_code"]
            property_code = request.form['property_code']
            file_data = request.files
                
            if "file" not in file_data:
                raise Exception ("Error: NO FILE PART")
            else:
                file_pdf = file_data["file"]
                if file_pdf.filename == "":
                    raise Exception ("Error: NO SELECT FILE")
                else:
                    file_pdf.filename = "{}-{}.pdf".format(property_code, lang_code)
                    data_response = CartaUtil.upload_bucket_carta(file_pdf)
                    if data_response["success"]:
                        response = {
                            "Code":200,
                            "Msg":"Success",
                            "Error":False,
                            "data": dataResponse
                        }
                    else:
                        raise Exception (str(data_response["message"]))

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
        return response