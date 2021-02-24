from flask import Flask, request, make_response, render_template_string
from resources.booking.booking_service import BookingService
from flask_restful import Resource
import locale
import datetime
import json, requests
from config import api
from common.util import Util
from models.book_status import BookStatus

class EmailTemplate(Resource):
    email_tag = "NOTIFICATION_BENGINE_CARTA_EMPTY"
    
    #@api.representation("text/html")
    # def get(self):
    def get(self, booking_data):
        return self.getHTML(self.getSecciones(booking_data))
    
    def render(self, code_reservation, full_name, language_code):
        booking_service = BookingService()
        booking_data = booking_service.get_booking_info_by_code(code_reservation, full_name, language_code)
        # booking_data = booking_service.get_booking_info_by_code("ZRCZ-320-BE", "VLADIMIR ORTIZ", "EN")
        # booking_data = booking_service.get_booking_info_by_code("ZMGR-96-BE", "Alfonso  Pech", "EN")
        # booking_data = booking_service.get_booking_info_by_code("ZHLB-584-BE", "Francisco Mahay", "EN")

        # booking_data = booking_service.get_booking_info_by_code("ZHLB-641-BE", "wilberth sanchez", "ES")
        # booking_data = booking_service.get_booking_info_by_code("ZHIM-129-BE", "Jessica Huerta", "ES")
        # booking_data = booking_service.get_booking_info_by_code("ZMGR-645-BE", "Alejandro Ramos Celaya", "ES")
        booking_email = self.getSecciones(booking_data)
        
        return make_response(self.getHTML(booking_email), 200)
    
    def getSecciones(self, booking_data):
        #booking_data es la informacion que viene de la api
        #booking_email es el arreglo que enviamos a la api de frm y pega en el html
        booking_email = {}

        booking_data["images"] = self.getImg(booking_data["brand_code"], booking_data["property_code"], booking_data["lang_code"].upper() )
        booking_data["color"] = self.getColorBase(booking_data["brand_code"])
        booking_data["traslate"] = self.getTraslates(booking_data["status_code"], booking_data["lang_code"])
        booking_info_section = self.getBookinInfo(booking_data)
        
        booking_email["header"] = self.getHeader(booking_data)

        # booking_email["guest"] = self.getInfoGuestConfimacion(booking_data)
        if booking_data["status_code"] in( 4,7,8): #Confirmed
            booking_email["guest"] = self.getInfoGuestConfimacion(booking_data)
        if booking_data["status_code"] == 3: #On Hold
            booking_email["guest"] = self.getInfoGuestOnHold(booking_data)
        if booking_data["status_code"] == 5: #Changed
            booking_email["guest"] = self.getInfoGuestModify(booking_data)
        if booking_data["status_code"] == 2: #Cancel
            booking_email["guest"] = self.getInfoGuestCancel(booking_data)
            booking_info_section = self.getBookinInfoCancelation(booking_data)
        
        booking_email["bookin_info"] = booking_info_section
        booking_email["rooms"] = self.getRoomInfo(booking_data)
        booking_email["servicios"] = self.getServices(booking_data)
        booking_email["beneficios"] = self.getBeneficios(booking_data)
        booking_email["politicas_cancelacion"] = self.getPoliticas(booking_data)
        booking_email["footer_img"] =  self.getImagesFooter(booking_data)
        booking_email["footer_info"] =  self.getInfoHotel(booking_data) 
        
        return booking_email
    
    def getPoliticas(self, booking_data):
        politica_cancelacion = ""
        politica_garantia = ""
        politica_tax = ""
        title = ""
        if len(booking_data["cancelation_policies"]) > 0 :
            for cancelacion in booking_data["cancelation_policies"]:
                if cancelacion["texts"] != "":
                    title = booking_data["traslate"]["poliUno"]
                    politica_cancelacion = politica_cancelacion + cancelacion["texts"]
            politica_cancelacion = "<table style='table-layout: fixed; width: 98%; padding-left: 10px;'>"+\
            "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+title+"</span></div><div style='height: 15px;'></div></td></tr></table></td></tr> <tr><td>" +  politica_cancelacion + "</td></tr>"+\
            "</table>"

        if len(booking_data["guarantee_policies"]) > 0 :
            for garantia in booking_data["guarantee_policies"]:
                if len(garantia["texts"]) > 0 :
                    title = booking_data["traslate"]["poliDos"]
                    for x in garantia["texts"]:
                        politica_garantia = politica_garantia + x
            politica_garantia = "<table style='table-layout: fixed; width: 98%; padding-left: 10px;'>"+\
            "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>" +\
            "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+title+"</span></div><div style='height: 15px;'></div></td></tr></table></td></tr> <tr><td>" + politica_garantia + "</td></tr>"+\
            "</table>"

        if len(booking_data["tax_policies"]) > 0 :
            for tax in booking_data["tax_policies"]:
                if len(tax["texts"]) > 0 :
                    title = booking_data["traslate"]["poliTres"]
                    for x in tax["texts"]:
                        politica_tax = politica_tax + x
            politica_tax = "<table style='table-layout: fixed; width: 98%; padding-left: 10px;'>"+\
            "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>"+\
            "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+title+"</span></div><div style='height: 15px;'></div></td></tr></table></td></tr> <tr></td>" + politica_tax+ "<td></tr>"+\
            "</table>"
        
        politicasReturn = politica_cancelacion + politica_garantia +politica_tax
        endMessage = ""

        if politicasReturn != "":
            endMessage  = "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>"+politica_cancelacion + politica_garantia +politica_tax + "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tbody><tr><td><div style='text-align: center; font-size: 12px;'>"+booking_data["traslate"]["tx_consulta"]+"</div><div style='text-align: center; font-size: 12px; color: "+booking_data["color"]["base"]+";'>bookdirect@palaceresorts.com.</div><div style='height: 15px;'></div></td></tr></tbody></table></td></tr>"
        
        return endMessage

    def getColorBase(self, brand):
        color_footer = "#E4E4E4"
        if brand == 'moon_palace':
            base = "#AA9070"
            booking_info = "#000000"
            tx_info = "#9a7243"
            value_info = "#ffffff"
            color_footer = "#000000"
        elif brand == 'le_blanc':
            base = "#F78F1E"
            booking_info = "#c6c6c6"
            tx_info = "#ffffff"
            value_info = "#000000"
        else:
            base = "#4296c3"
            booking_info = "#4296c3"
            tx_info = "#ffffff"
            value_info = "#000000"

        data = {
            "base": base,
            "booking_info": booking_info,
            "tx_info": tx_info,
            "value_info": value_info,
            "color_footer": color_footer,
        }
        return data
    
    def formatDate(self, fecha, isHold , lang):
        global x
        x  =  2
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

    def formatMoney(self, amount):
        currency = "${:,.0f}".format(amount)
        return(currency)

    def getImg(self, brand, property, lang):
        imgHeader = {
            "ZHBP": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-30-10-15-13-21-992303image.png",
            "ZHSP": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-03-06-018995Sun-Palace-Header.jpg",
            "ZHIM": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-04-52-129222Isla-Mujeres-Palace-Header.jpg",
            "ZRPL": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-03-17-694394Playacar-Palace-Header.jpg",
            "ZRCZ": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-05-06-175633Cozumel-Palace-Header.jpg",
            "ZMSU": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-03-53-474004Moon-Palace-Cancun-Header.jpg",
            "ZMGR": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-02-53-662038THG-Moon-Cancn-Header.jpg",
            "ZCJG": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-03-34-825409Moon-Palace-Jamaica-Header.jpg",
            "ZHLB": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-04-39-584980Le-Blanc-Cancun-Header.jpg",
            "ZPLB": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-04-17-644566Le-Blanc-Los-Cabos-Header.jpg",
            "ZMNI": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-12-03-53-474004Moon-Palace-Cancun-Header.jpg"
            }
        imgAmenidades= {
            "moon_palace": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-23-11-09-52-30-715907Beneficios-MN-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-23-11-09-52-18-536465Beneficios-MN-EN.jpg" 
                },
            "palace_resorts": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-23-11-09-50-23-670398Beneficios-PR-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-23-11-09-50-07-452626Beneficios-PR-EN.jpg" 
                },
            "le_blanc": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-23-11-09-53-00-130919Beneficios-LB-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-23-11-09-52-49-091741Beneficios-LB-EN.jpg" 
                },
        }
        
        imgPurely = {
            "moon_palace": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-26-26-998955Purely_Palace-Banner-MOON-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-25-59-981191Purely_Palace-Banner-MOON-EN.jpg" 
                },
            "palace_resorts": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-27-13-407692Purely_Palace-Banner-PR-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-26-52-777936Purely_Palace-Banner-PR-EN.jpg" 
                },
            "le_blanc": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-27-44-791292Purely_Palace-Banner-LB-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-27-28-625818Purely_Palace-Banner-LB-EN.jpg"
            },

            }
        imgQr = {
            "moon_palace": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-24-13-360950Moon-App-QR-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-24-26-615404Moon-App-QR-EN.jpg" 
                },
            "palace_resorts": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-24-37-970490Palace-App-QR-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-25-01-729443Palace-App-QR-EN.jpg" 
                },
            "le_blanc": {
                "ES": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-25-25-815926LeBlanc-App-QR-ES.jpg", 
                "EN": "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-15-25-42-712803LeBlanc-App-QR-EN.jpg" 
                },

            }
        iconFooter={
            "moon_palace": {
                "iconLocation" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-14-45-703787Location.png",
                "iconEmail" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-15-00-939158E-mail.png",
                "iconPhone" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-14-11-776814Phone_number.png",
                "iconWeb" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-30-09-16-13-31-608305web.png",
                "iconClock" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-28-12-12-05-58-019690reloj_on_hold_dorado.png" 
                },
            "palace_resorts": {
                "iconLocation" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-06-46-603406Location.png",
                "iconEmail" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-06-15-137005E-mail.png",
                "iconPhone" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-07-00-658284Phone_number.png",
                "iconWeb" : "https://s3.amazonaws.com/webfiles_palace/clever-qa/booking_engine/2020-18-09-13-07-17-273578web.png",
                "iconClock" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-28-12-12-04-51-635022reloj_on_hold_azul.png"
                },
            "le_blanc": {
                "iconLocation" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-16-07-59-874568Location.png",
                "iconEmail" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-16-07-39-066521E-mail.png",
                "iconPhone" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-16-08-13-730509Phone_number.png",
                "iconWeb" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-10-11-16-05-55-082332web.png" ,       
                "iconClock" : "https://s3.amazonaws.com/webfiles_palace/clever/booking_engine/2020-28-12-12-06-29-679509reloj_on_hold_naranja.png"
                },

            }
        urlPurely = {
            "EN": "https://www.palaceresorts.com/en/purely-palace",
            "ES": "https://www.palaceresorts.com/es/purely-palace"
            }
        images = {
            "imgHeader": imgHeader[property],
            "imgAmenidades": imgAmenidades[brand][lang],
            "imgPurely": imgPurely[brand][lang],
            "imgQr": imgQr[brand][lang],
            "iconFooter": iconFooter[brand],
            "urlPurely": urlPurely[lang]
        }

        return images

    def getRoomInfo(self, booking_data):
        html_room = ""
        
        for index, cliente in enumerate(booking_data["rooms"]):
            paxes = cliente["pax"]
            wrap_col = ""
            content_img = ""
            content_room_info = ""

            #columna izquierda Imagen
            content_img = "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'>" +\
                          "<tr> <img src='"+cliente["media"][0]["url"]+"' style='width: 100%;'></img>" +\
                          "</tr></table></td></tr></table>"
            
            #columna derecha Info de habitacion
            ##se generala columna de paxes dinamicos

            col_pax = ""
            key_pax = list(cliente["pax"])
            totalPax = 0
            for pax_label in key_pax:
                totalPax = totalPax + cliente["pax"][pax_label]["value"]
                col_pax = col_pax + "<div style='text-align: right;'> <span style='color: #848484;'>"+cliente["pax"][pax_label]["text"] +": </span>"+str(cliente["pax"][pax_label]["value"])+"</div>"
            
            wrap_pax = "<td style='width: 50%; font-size: 12px;'>" +\
                        col_pax +\
                        "</td>"
            #se pegalos pax a la columna derecha
            content_room_info = "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px; width: 284px;'>" + \
                                "<tr><td style='width: 100%; text-align: left;' colspan='2'><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+cliente["trade_name_room"]+"</span></div></td></tr>" +\
                                "<tr><td style='width: 100%; text-align: left;' colspan='2'><div> <span style='color: #000000; font-weight: bold; font-size: 12px;'>"+cliente["rateplan_name"]+"</span></div><div style='height: 10px;'></div></td></tr>" +\
                                "<tr><td style='width: 50%; font-size: 12px;'><div style='text-align: left;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_guests"]+": </span>"+ str(totalPax)+" Pax</div><div style='text-align: left;'> Total: <span style='color: #848484; text-decoration: line-through;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(cliente["total_crossout"])+"</span></div><div> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(cliente["total"])+"</div></td>" + wrap_pax + "</tr>" +\
                                "<tr><td style='width: 100%;' colspan='2'><div style='width: 100%; padding: 0px 0px;'><div style='height: 8px;'></div><p style='border-top:dashed 1px "+booking_data["color"]["base"]+";font-size:1;margin:0px auto;width:100%; '></p><div style='height: 8px;'></div></div></td></tr>"+\
                                "<tr><td style='width: 100%; font-size: 12px;' colspan='2'><div><div style='text-align: left;width: 142px; float: left;'> <span>"+booking_data["traslate"]["tx_deposit"]+": </span></div><div style='text-align: right;width: 135px;float: left;'> <span> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> " + self.formatMoney(cliente["amount_paid"]) +"</span></div></div><div><div style='text-align: left;width: 142px; float: left;'> <span>"+booking_data["traslate"]["tx_balance"]+" </span></div><div style='text-align: right;width: 135px;float: left;'> <span style=' font-weight: bold;'> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(cliente["amount_pending_payment"])+"</span></div></div></td></tr>"+\
                                "</table></td></tr></table>"

            #Es el row que envuelve las 2 columnas
            wrap_col = "<tr> <td style='width: 100%;'> <table style='width: 100%;'> <tr> <td style='padding-top: 10px; text-align: center;'>" + \
                       content_img + content_room_info +\
                       "</td></tr></table> </td></tr>"

            #Precio por noche
            tituloPrecioNoche = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='font-size: 12px; font-weight: bold;'>"+booking_data["traslate"]["rateUno"]+"</span></div></td></tr></table></td></tr>"

            #PRECIO POR NOCHE 
            lista = cliente["prices"]
            inicio = 0
            salida = 6
            columnas = ""
            i = 0
            htmlTarifario = ""
            x = 0

            while i < len(lista):  
                while inicio < salida:
                    
                    union = ""
                    while i < inicio+3:
                        try:
                            #union = union + lista[i]
                            union = union + "<td style='width: 96.666px;'><div><span style='font-weight: bold;'>"+ self.formatDate(str(lista[i]["date"]) , False, booking_data["lang_code"].upper() ) +"</span></div><div><span style='color: #848484; text-decoration: line-through; font-size: 10px;'><span style='font-size: 9px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(lista[i]["total_gross"])+"</span></div><div><span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(lista[i]["total"])+"</div></td>"
                        except:
                            union = union + " <td style='width: 96.666px;'></td>"
                        i += 1
                    columnas = columnas + "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tr>"+union+"</tr></table></td></tr></table>"
                    inicio += 3
                
                htmlTarifario = htmlTarifario + "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style='padding-bottom: 10px; text-align: center;'> "+ columnas +" </td></tr></table></td></tr>"
                
                columnas = ""
                
                salida += 6

            html_room = html_room + wrap_col + tituloPrecioNoche + htmlTarifario
        
        return html_room

    def getServices(self, booking_data):

        columnas_services = ""
        services = booking_data["services_info"]
        html_services = ""
        salida = len(services)
        for serviceFor in services:
            union = ""
            if len(serviceFor["media"]) > 0:
                union = union + "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'><tr> <img src='"+serviceFor["media"][0]["url"]+"' style='width: 100%;'></img></tr></table></td></tr></table>"
            else:
                union = union + "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'><tr> <img src='' style='width: 100%;'></img></tr></table></td></tr></table>"
            
            union = union + "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'><tr><td style='width: 100%;'><div style=' text-align: center; color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'> "+serviceFor["name"]+"</div><div style='height: 15px;'></div></td></tr><tr><td style='width: 100%;'><div style='text-align: justify; font-size: 12px;'> "+serviceFor["description"]+"</div><div style='height: 10px;'></div></td></tr></table></td></tr></table>" 
            
            html_services = html_services + "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'>"+ union +"</td></tr></table></td></tr>"

        html_services

        """ 
        POR SI LO QUIEREN DE REGRESO xd
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
                        union = union +"<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'><tr> <img src='"+services[i]["media"][0]["url"]+"' style='width: 100%;'></img></tr><tr><td style='width: 100%;'><div style='height: 15px;'></div><div style=' text-align: center; color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'> "+services[i]["name"]+"</div><div style='height: 15px;'></div></td></tr><tr><td style='width: 100%;'><div style='text-align: justify; font-size: 12px;'> "+services[i]["description"]+"</div><div style='height: 10px;'></div></td></tr></table></td></tr></table>"
                    else: 
                        union = union +"<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'><tr> <img src='' style='width: 100%;'></img></tr><tr><td style='width: 100%;'><div style='height: 15px;'></div><div style=' text-align: center; color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'> "+services[i]["name"]+"</div><div style='height: 15px;'></div></td></tr><tr><td style='width: 100%;'><div style='text-align: justify; font-size: 12px;'> "+services[i]["description"]+"</div><div style='height: 10px;'></div></td></tr></table></td></tr></table>"
                except:
                    union = union + "<table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 14px;'></table></td></tr></table>"
                i += 1
            columnas_services = columnas_services + union 
            inicio += 2
        html_services ="<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: left;'>"+ columnas_services +"</td></tr></table></td></tr>"
        """
        if salida > 0 :
            html_services = "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr><tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+booking_data["traslate"]["beneUno"].upper()+"</span></div><div style='height: 15px;'></div></td></tr></table></td></tr>" + html_services
        

        return html_services

    def getInfoGuestConfimacion(self, booking_data):
        htmlGuest = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 22px;'>"+booking_data["traslate"]["tituloUno"]+"</span></div><div> <span style='font-size: 18px;'>"+booking_data["traslate"]["tituloDos"]+" "+booking_data["trade_name"]+"</span></div></td></tr></table></td></tr><tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 600px; display: inline; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 100%;'><table style='width: 100%; max-width: 570px; display: inline-block; vertical-align: top; border: solid "+booking_data["color"]["base"]+" 2px;'><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+booking_data["traslate"]["tituloConfirmacion"]+":</span></div><div> <span style='color: #000000; font-weight: bold; font-size: 16px;'>"+booking_data["code_reservation"]+"</span></div></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>" +\
                    "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 50%;'><div style='text-align: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tituloCliente"]+"</span></div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_nombre"]+" </span>"+booking_data["customer"]["first_name"]+" "+ booking_data["customer"]["last_name"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_numero"]+" </span>"+booking_data["customer"]["phone_number"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_correo"]+" </span>"+booking_data["customer"]["email"]+"</div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_requerimiento"]+" </span><br> "+booking_data["special_request"]+"</div></td></tr></table></td></tr></table><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 145px; font-size: 16px;'><div style='text-align: left;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>Total: </span></div></td><td style='width: 100%; font-size: 12px;'><div style='text-align: right;'> <span style='color: #848484; text-decoration: line-through;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> " + self.formatMoney(booking_data["total"] + booking_data["promo_amount"]) + " </span></div></td></tr><tr> <td style='width: 50%; font-size: 14px;'><div style='text-align: left;'> <span style='font-weight: bold;'>Promocode: "+ booking_data["promo_code"]+" </span></div></td><td style='width: 50%; font-size: 12px;'><div style='text-align: right;'> <span> <span style='font-size: 10px;'> - "+ booking_data["currency_code"]+"</span> "+self.formatMoney(booking_data["promo_amount"])+"</span></div></td></tr><tr>    <td style='width: 50%; font-size: 14px;'><div style='text-align: left;'> <span style='font-size: 12px; color: #848484;'>"+booking_data["promo_code_text"]+"</span></div></td>     <td style='width: 50%; font-size: 14px;' colspan='2'><div style='text-align: right;'> <span style='font-weight: bold;'> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(( booking_data["total"] ))+"</span></div></td></tr><tr><td colspan='2'><div><div style='text-align: left;width: 100%; float: left;'><div style='height: 8px;'></div><p style='border-top:dashed 1px "+booking_data["color"]["base"]+";font-size:1;margin:0px auto;width:100%; '></p><div style='height: 8px;'></div></div></div></td></tr><tr><td style='width: 50%; font-size: 12px;'><div style='text-align: left;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_monto"]+" </span></div></td><td style='width: 50%; font-size: 12px;'><div style='text-align: right;'> <span> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(booking_data["amount_paid"])+"</span></div></td></tr><tr><td style='width: 50%; font-size: 12px;'><div style='text-align: left;'> <span style='color: #848484;'> "+booking_data["traslate"]["tx_balance"]+"</span></div></td><td style='width: 50%; font-size: 14px;'><div style='text-align: right;'> <span style='font-weight: bold;'> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(booking_data["amount_pending_payment"])+"</span></div></td></tr></table></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style='text-align: justify;'><table style='width: 100%; max-width: 600px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 10%;'><div style='font-size: 10px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_avisoUno"]+booking_data["traslate"]["tx_avisoDos"]+"</span></div></td></tr></table></td></tr></table></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>"
                    
        return htmlGuest
        
    def getInfoGuestOnHold(self, booking_data):
        url_base = booking_data["channel_url"]
        url_on_Hold = url_base+"?name="+booking_data['customer']['first_name'].replace(' ', '%20')+"%20"+booking_data['customer']['last_name'].replace(' ', '%20')+"&code="+booking_data['code_reservation']

        htmlGuest = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 22px;'> "+booking_data["traslate"]["tituloUno_on"]+" </span></div><div> <span style='font-size: 18px;'>"+booking_data["traslate"]["sub_titulo1"]+" "+booking_data["trade_name"]+" "+booking_data["traslate"]["sub_titulo2"]+"</span></div></td></tr></table></td></tr>" + \
                    "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 600px; display: inline; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 100%;'><table style='width: 100%; max-width: 570px; display: inline-block; vertical-align: top; border: solid "+booking_data["color"]["base"]+" 2px;'><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+booking_data["traslate"]["tituloConfirmacion"]+":</span></div><div> <span style='color: #000000; font-weight: bold; font-size: 16px;'>"+booking_data["code_reservation"]+"</span></div></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>" +\
                    "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'> "+booking_data["traslate"]["tx_holdUno"]+" "+booking_data["trade_name"].upper()+" "+booking_data["traslate"]["tx_holdDos"]+" </span></div></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 50%;'><div style='text-align: left;'><p style='display: flex; margin: 0px; align-items: center;'> <img src='"+booking_data["images"]["iconFooter"]["iconClock"]+"' style='height: 26px; width: auto;' alt=''> &nbsp; <span>"+booking_data["traslate"]["tx_holdClock"]+":<br> <span style='font-weight: bold;'>"+str(booking_data["expiry_date"])+"</span></span></p><div style='height: 10px;'></div><div style='font-size: 12px;'> <span >"+booking_data["traslate"]["tx_holdTres"]+"</span></div></div></td></tr></table></td></tr></table><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style='font-size: 14px; width: 284px;'><tr><td> <a href="+url_on_Hold+"><button type='button' style='background-color:"+booking_data["color"]["base"]+"; color:#ffffff; border:1px solid "+booking_data["color"]["base"]+"; width:100%; height:35px'> "+booking_data["traslate"]["btn_reservation_onHold"]+"</button></a> </td></tr></table></td></tr></table></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div> <span style='color: #848484; font-weight: bold; font-size: 10px;'> "+booking_data["traslate"]["tx_avisoUno"]+" </span></div></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 50%;'><div style='text-align: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tituloCliente"]+"</span></div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_nombre"]+" </span>"+booking_data["customer"]["first_name"]+" "+ booking_data["customer"]["last_name"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_numero"]+" </span>"+booking_data["customer"]["phone_number"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_correo"]+" </span>"+booking_data["customer"]["email"]+"</div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_requerimiento"]+" </span><br> "+booking_data["special_request"]+"</div></td></tr></table></td></tr></table><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style='font-size: 14px; width: 284px;'><tr><td><div><div style='text-align: left;width: 142px; float: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tx_balance"]+" </span></div><div style='text-align: right;width: 135px;float: left; font-size: 14px;'> <span> <span style='font-size: 10px;'>"+ booking_data["currency_code"]+"</span> "+self.formatMoney(booking_data["total"])+"</span></div></div></td></tr></table><table style='font-size: 14px; width: 284px;'><tr><td><div style='height: 8px;'></div><div style='font-size: 10px; text-align: justify;'> <span style='color: #848484;'>* "+booking_data["traslate"]["tx_provide_card"]+"</span></div></td></tr></table></td></tr></table></td></tr></table></td></tr>" 
        
        
        return htmlGuest

    def getInfoGuestModify(self, booking_data):
        #se pegalos pax a la columna derecha
        for index, rooms in enumerate(booking_data["rooms"]):
            content_summary = "<table style='font-size: 14px; width: 284px; border: 2px solid "+booking_data["color"]["base"]+"; padding: 10px;'><tr><td colspan='2'><div style='height: 8px;'></div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tx_Booking_summary"]+"</span></td></tr><tr><td style='width: 50%; font-size: 12px;'><div style='text-align: left;'> <span style='color: #848484;'>"+rooms["trade_name_room"]+"</span></div></td><td style='width: 50%; font-size: 12px;'><div style='text-align: right;'> <span style='color: #848484; text-decoration: line-through;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+" </span>"+self.formatMoney(rooms["total_crossout"])+"</span> </div></td></tr><tr>"+\
            "<td style='width: 50%; font-size: 12px;' colspan='2'><div style='text-align: right;'> <span style='color: #848484;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+" </span>"+self.formatMoney(rooms["total"])+"</span></div></td></tr><tr><td colspan='2'><div><div style='text-align: left;width: 100%; float: left;'><div style='height: 8px;'></div><p style='border-top:dashed 1px "+booking_data["color"]["base"]+";font-size:1;margin:0px auto;width:100%; '></p><div style='height: 8px;'></div></div></div></td></tr><tr><td style='width: 50%; font-size: 12px;'><div style='text-align: left;'> <span style='color: #848484;'>"+booking_data["traslate"]["total_price"]+":</span></div></td><td style='width: 50%; font-size: 12px;'><div style='text-align: right;'> <span style='color: #848484;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+" </span>"+self.formatMoney(rooms["total"])+"</span></div></td></tr></table>"

        htmlGuest = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 22px;'> "+booking_data["traslate"]["tx_title_modify"]+" </span></div><div> <span style='font-size: 16px;'>"+booking_data["traslate"]["tx_Subtitle_modify"]+"</span></div></td></tr></table></td></tr><tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div style='height: 15px;'></div><div> <span style='font-size: 16px;'> "+booking_data["traslate"]["tx_Subtitle_uno"]+" <span style='font-weight: bold;'>"+booking_data["code_reservation"]+"</span> "+booking_data["traslate"]["tx_Subtitle_dos"]+"</span></div></td></tr></table></td></tr><tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div>" +\
        "<p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr><tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 50%;'><div style='text-align: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tituloCliente"]+"</span></div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_nombre"]+" </span>"+booking_data["customer"]["first_name"]+" "+ booking_data["customer"]["last_name"]+"</div>" +\
        "<div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_numero"]+" </span>"+booking_data["customer"]["phone_number"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_correo"]+" </span>"+booking_data["customer"]["email"]+"</div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_requerimiento"]+" </span><br>"+booking_data["special_request"]+"</div></td></tr><tr><td style='width: 50%;'><div style='height: 15px;'></div><div style='text-align: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tx_Booking_summary"]+"</span></div><div style='height: 15px;'></div>" +\
        "<div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["id_reserva"]+": </span>"+booking_data["code_reservation"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["name_property"]+": </span>"+booking_data["trade_name"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["lang_reservation"]+": </span>"+booking_data["lang_code"]+"</div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["date_creation"]+": </span> "+booking_data["fecha_creacion"].replace('-', '/')+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["last_modified"]+": </span> "+booking_data["modification_date_booking"].replace('-', '/')+"</div>" +\
        "<div style='height: 8px;'></div></td></tr></table></td></tr></table><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style='font-size: 14px; width: 284px;'><tr><td><div><div style='text-align: left;width: 142px; float: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tx_balance"]+" </span></div></div></td></tr></table><table style='font-size: 14px; width: 284px;'><tr><td><div style='height: 8px;'></div><div><div style='text-align: left;width: 142px; float: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_monto"]+" </span></div><div style='text-align: right;width: 135px;float: left; font-size: 12px;'> " +\
        "<span> <span style='font-size: 10px;'>"+booking_data["currency_code"]+"</span> "+self.formatMoney(booking_data["amount_paid"])+"</span></div></div></td></tr></table><div style='height: 15px;'></div>"+content_summary+" " +\
        "</td></tr></table></td></tr></table></td></tr><tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'>" +\
        "</div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>"

        return htmlGuest

    def getInfoGuestCancel(self, booking_data):
        #se pegalos pax a la columna derecha
        if booking_data["lang_code"].upper() == "ES":
            refund_Process_dos = "Se ha iniciado la gestión de su reembolso por la cantidad de <span style='font-weight: bold;'> "+booking_data["currency_code"]+" "+self.formatMoney(booking_data["amount_paid"])+"</span>."
        else:
            refund_Process_dos = "The sum of <span style='font-weight: bold;'> "+booking_data["currency_code"]+" "+self.formatMoney(booking_data["amount_paid"])+"</span> is being processed and will be refund."
        
        content_summary = ""
        # summary_total = 0
        for index, rooms in enumerate(booking_data["rooms"]):
            # summary_total = summary_total + rooms["total"]
            content_summary = content_summary +  "<tr><td style='width: 50%; font-size: 12px;'><div style='text-align: left;'> <span style='color: #848484;'>"+rooms["trade_name_room"]+"</span></div></td><td style='width: 50%; font-size: 12px;'><div style='text-align: right;'> <span style='color: #848484; text-decoration: line-through;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+" </span>"+self.formatMoney(rooms["total_crossout"])+"</span></div></td></tr><tr><td style='width: 50%; font-size: 12px;' colspan='2'><div style='text-align: right;'> <span style='color: #848484;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+" </span>"+self.formatMoney(rooms["total"])+"</span></div></td></tr>"
        
        textCancel = ""
        razon_cancelacion = ""
        text_razon_cancelacion = ""
        if booking_data["amount_paid"] != 0:
            textCancel = booking_data["traslate"]["refund_Process_tres"]
        if booking_data["visible_reason_cancellation"] == 1:
            text_razon_cancelacion = booking_data["reason_cancellation"]
            
            razon_cancelacion = "<div style='text-align: left; font-size: 12px;'><span style='color: #848484;'>"+booking_data["traslate"]["tx_reason_cancel"]+": </span>"+text_razon_cancelacion+"</div><div style='height: 8px;'></div>"

        htmlGuest = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 22px;'> "+booking_data["traslate"]["tx_title_cancelation"]+" </span>" +\
                    "</div><div> <span style='font-size: 16px;'>"+booking_data["traslate"]["tx_Subtitle_cancelation"]+"</span></div></td></tr></table></td></tr><tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td style='width: 50%;'><div style='height: 15px;'>" +\
                    "</div><div> <span style='font-size: 16px;'> "+booking_data["traslate"]["tx_Subtitle_bookingUno"]+" <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["code_reservation"]+"</span> "+booking_data["traslate"]["tx_Subtitle_bookingDos"]+"</span></div></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr><tr><td style='width: 100%;'><table style='width: 100%;'>" +\
                    "<tr><td style=' text-align: center;'><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td style='width: 50%;'><div style='text-align: left; font-size: 16px;'>" +\
                    "<span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["tituloCliente"]+"</span></div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'>" +\
                    "<span style='color: #848484;'>"+booking_data["traslate"]["tx_nombre"]+" </span>"+booking_data["customer"]["first_name"]+" "+ booking_data["customer"]["last_name"]+"</div><div style='text-align: left; font-size: 12px;'>" +\
                    "<span style='color: #848484;'>"+booking_data["traslate"]["tx_numero"]+" </span>"+booking_data["customer"]["phone_number"]+"</div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["tx_correo"]+" </span>" +\
                    ""+booking_data["customer"]["email"]+"</div><div style='height: 15px;'></div></td></tr><tr><td style='width: 50%;'><div style='height: 15px;'></div><div style='text-align: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>" +\
                    ""+booking_data["traslate"]["tx_Booking_summary"]+"</span></div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["id_reserva"]+": </span>"+booking_data["code_reservation"]+"</div>" +\
                    "<div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["name_property"]+": </span>"+booking_data["trade_name"]+"</div><div style='height: 15px;'></div><div style='text-align: left; font-size: 12px;'>" +\
                    "<span style='color: #848484;'>"+booking_data["traslate"]["date_creation"]+": </span> "+booking_data["fecha_creacion"].replace("-", "/")+"</div><div style='text-align: left; font-size: 12px;'>" +\
                    "<span style='color: #848484;'>Check-In: </span>"+booking_data["general_data"]["check_in"].replace("-", "/")+"</div>" +\
                    "<div style='height: 8px;'></div> <div style='text-align: left; font-size: 12px;'> <span style='color: #848484;'>"+booking_data["traslate"]["bi_noches_dos"]+": </span>"+str(booking_data["nights"])+"</div> <div style='height: 8px;'></div><div style='text-align: left; font-size: 12px;'>" +\
                    "<span style='color: #848484;'>"+booking_data["traslate"]["Tx_total_room"]+": </span>"+str(booking_data["total_rooms"])+"</div><div style='height: 8px;'></div>"+razon_cancelacion+"</td></tr></table></td></tr></table><table style='width: 100%; max-width: 290px; display: inline-block; vertical-align: top;'>" +\
                    "<tr><td style='width: 100%;'><table style='font-size: 14px; width: 284px;'><tr><td><div><div style='text-align: left;width: 284px; float: left; font-size: 16px;'> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["refund_Process"]+"</span>" +\
                    "</div></div></td></tr></table><table style='font-size: 14px; width: 284px;'><tr><td><div style='height: 8px;'></div><div><div style='text-align: left;width: 284px; font-size: 12px;'> <span style='color: #848484;'>"+refund_Process_dos+" </span>" +\
                    "</div></div></td></tr><tr><td><div style='text-align: left;width: 284px; font-size: 12px;'><span style='color: #848484;'> "+textCancel+"</span></div></td></tr></table>      <table><tr><td> </td></tr><tr><td> </td></tr><tr><td> </td></tr><tr><td> </td></tr></table>" +\
                    "<div><table style='font-size: 14px; width: 284px; border: 2px solid "+booking_data["color"]["base"]+"; padding: 10px;'><tr><td colspan='2'><div style='height: 8px;'></div><span style='color: "+booking_data["color"]["base"]+"; font-weight: bold;'>"+booking_data["traslate"]["desglose_precio"]+"</span></td></tr>" +\
                    ""+content_summary+"<tr><td colspan='2'><div><div style='text-align: left;width: 100%; float: left;'><div style='height: 8px;'></div><p style='border-top:dashed 1px "+booking_data["color"]["base"]+";font-size:1;margin:0px auto;width:100%; '></p><div style='height: 8px;'></div></div></div></td></tr><tr><td style='width: 50%; font-size: 12px;'>" +\
                    "<div style='text-align: left;'> <span style='color: #848484;'>"+booking_data["traslate"]["total_price"]+":</span></div></td><td style='width: 50%; font-size: 12px;'><div style='text-align: right;'> <span style='color: #848484;'><span style='font-size: 10px;'>"+ booking_data["currency_code"]+" </span>"+self.formatMoney(booking_data["total"])+"</span></div></td></tr></table>" +\
                    "</div></td></tr></table></td></tr></table></td></tr> <tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '>" +\
                    "</p><div style='height: 15px;'></div></td></tr>"

        return htmlGuest

    def getImagesFooter(self, booking_data):
        footerImages = "<tr><td style='width: 100%;'><table style='width: 100%;'><tbody><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 600px; display: inline-block; vertical-align: top;'><tbody><tr><td style='width: 100%;'><table><tbody><tr><td><div> <a href='"+booking_data["images"]["urlPurely"]+"'> <img src='"+booking_data["images"]["imgPurely"]+"' style='width: 100%;'> </a> </div><div style='height: 15px;'></div></td></tr><tr><td><div> <img src='"+booking_data["images"]["imgQr"]+"' style='width: 100%;'></div><div style='height: 15px;'></div></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></td></tr>"
        return footerImages

    def getInfoHotel(self, booking_data):
        ##fila uno y dos son correspondientes a columnas 1 y 2 respectivamente
        if booking_data["lang_code"].upper() == "ES":
            privacy_url = "<a href='https://www.palaceresorts.com/en/privacy-users' style='color:"+booking_data["color"]["value_info"]+"'>*"+booking_data["traslate"]["tx_privacyUno"]+"</a>"
            EU_Privacy = "<a href='https://www.palaceresorts.com/en/privacy-users' style='color:"+booking_data["color"]["value_info"]+"'>*"+booking_data["traslate"]["tx_privacyDos"]+"</a>"
        else:
            privacy_url = "<a href='https://www.palaceresorts.com/es/usuarios' style='color:"+booking_data["color"]["value_info"]+"'>*"+booking_data["traslate"]["tx_privacyUno"]+"</a>"
            EU_Privacy = "<a href='https://www.palaceresorts.com/es/usuarios' style='color:"+booking_data["color"]["value_info"]+"'>*"+booking_data["traslate"]["tx_privacyDos"]+"</a>"
        
        footerInfo = "<tr><td style='width: 100%;'><table style='width: 100%;'><tbody><tr><td style='padding: 5px; text-align: center;'><div style='background-color: "+booking_data["color"]["color_footer"]+"; padding: 10px;'><table style='width: 100%; max-width: 278px; display: inline-block; vertical-align: top;'><tbody><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tbody><tr><td style='width: 100%;'><div style='text-align: left;'><p style='display: flex; margin: 0px; align-items: center;'> <img src='"+booking_data["images"]["iconFooter"]["iconLocation"]+"' style='height: 26px; width: auto;' alt=''> &nbsp; <span style='color: "+booking_data["color"]["value_info"]+"'>"+booking_data["address"]+"</span></p><div style='height: 10px;'></div></div></td></tr><tr><td style='width: 100%;'><div style='text-align: left;'><p style='display: flex; margin: 0px; align-items: center;'> <img src='"+booking_data["images"]["iconFooter"]["iconPhone"]+"' style='height: 26px; width: auto;' alt=''> &nbsp; <span style='color: "+booking_data["color"]["value_info"]+"'>"+booking_data["resort_phone"]+"</span></p><div style='height: 10px;'></div></div></td></tr><tr><td style='width: 100%;'><div style='text-align: left;'><p style='display: flex; margin: 0px; align-items: center;'> <img src='"+booking_data["images"]["iconFooter"]["iconWeb"]+"' style='height: 26px; width: auto;' alt=''> &nbsp; <span style='color: "+booking_data["color"]["value_info"]+"'> <a href="+booking_data["web_address"]+" target='_blank' rel='noopener noreferrer' style='color: "+booking_data["color"]["value_info"]+"'>"+booking_data["web_address"]+"</a></span></p><div style='height: 10px;'></div></div></td></tr></tbody></table></td></tr></tbody></table>" +\
                    "<table style='width: 100%; max-width: 278px; display: inline-block; vertical-align: top;'><tbody><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tbody><tr><td style='width: 100%;'><div style='text-align: left;'><p style='display: flex; margin: 0px; align-items: center;'> <img src='"+booking_data["images"]["iconFooter"]["iconEmail"]+"' style='height: 26px; width: auto;' alt=''> &nbsp; <span style='color: "+booking_data["color"]["value_info"]+"'>Reservations:<br> <a style='color:"+booking_data["color"]["value_info"]+"' href='mailto:"+booking_data["reservation_email"]+"' target='_blank'>"+booking_data["reservation_email"]+"</a></span></p><div style='height: 10px;'></div></div></td></tr><tr><td style='width: 100%;'><div style='text-align: left;'><p style='display: flex; margin: 0px; align-items: center;'> <img src='"+booking_data["images"]["iconFooter"]["iconEmail"]+"' style='height: 26px; width: auto;' alt=''> &nbsp; <span style='color: "+booking_data["color"]["value_info"]+"'>Resort E-mail:<br> <a style='color:"+booking_data["color"]["value_info"]+"' href='mailto:"+booking_data["resort_email"]+"' target='_blank'>"+booking_data["resort_email"]+"</a></span></p><div style='height: 10px;'></div></div></td></tr><tr><td style='width: 100%;font-size: 12px;'><table><tbody><tr><td style='width: 100px;font-size: 12px;'><div style='text-align: left;'> <span> "+privacy_url+" </span></div></td><td style='font-size: 12px;'><div style='text-align: right;'> <span> "+EU_Privacy+" </span></div></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table></div></td></tr></tbody></table></td></tr>" +\
                    "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tbody><tr><td><div> <span>Palace Resorts Reservation, Km 21 Carretera Cancun-Puerto Morelos, Q. Roo, México 77500.</span></div></td></tr></tbody></table></td></tr>"
        
        return footerInfo 

    def getHeader(self, booking_data):
        header = "<tr><td style='width: 100%;'> <img src='"+booking_data["images"]["imgHeader"]+"' style='width: 100%;'></td></tr>"
        return header

    def getHTML(self, booking_email):
        html = "<!DOCTYPE html><html lang='en'><head><meta http-equiv='X-UA-Compatible' content='IE=edge'><meta http-equiv='Content-Type' content='text/html; charset=UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Document</title></head><body style='font-family: Arial, Helvetica, sans-serif, Verdana; font-size: 12px;'><div style='background-color: white; max-width: 600px; margin:0px auto;'><table style='max-width: 600px;'>" +\
            booking_email["header"] +\
            booking_email["guest"] +\
            booking_email["bookin_info"] +\
            booking_email["rooms"] +\
            booking_email["servicios"] +\
            booking_email["beneficios"] +\
            booking_email["politicas_cancelacion"] +\
            booking_email["footer_img"] +\
            booking_email["footer_info"]  +\
        "</table></div></body></html>"
        return html

    def getBeneficios(self, booking_data):
        #Titulo
        #Contenido
        beneficios = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+booking_data["traslate"]["beneDos"].upper()+"</span></div><div style='height: 15px;'></div></td></tr></table></td></tr>" +\
                    "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 600px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table><tr><td><div> <img src='"+booking_data["images"]["imgAmenidades"]+"' style='width: 100%;'></img></div><div style='height: 15px;'></div></td></tr><tr><td style='width: 10%;'><div style='text-align: center; font-size: 12px;'> "+booking_data["traslate"]["servicio"]+"</div><div style='height: 15px;'></div></td></tr></table></td></tr></table></td></tr></table></td></tr>"
        return beneficios

    def getBookinInfo(self, booking_data):
        info = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div> <span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'>"+booking_data["traslate"]["tx_information"].upper()+"</span></div></td></tr></table></td></tr>" +\
            "<tr><td style='width: 100%;'><table style='width: 100%;'><tr><td style=' text-align: center;'><table style='width: 100%; max-width: 600px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style='background-color: "+booking_data["color"]["booking_info"]+";'><tr><td style='width: 100%;'><table style='width: 100%; max-width: 286px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tr><td style='width: 95px;'><div> <span style='color: "+booking_data["color"]["tx_info"]+";'>"+booking_data["traslate"]["bi_llegadaFecha_uno"]+" <br> "+booking_data["traslate"]["bi_llegadaFecha_dos"]+":</span></div><div style='color: "+booking_data["color"]["value_info"]+"'>"+booking_data["from_date"]+"</div></td><td style='width: 95px;'><div> <span style='color: "+booking_data["color"]["tx_info"]+";'>"+booking_data["traslate"]["bi_salidaFecha_uno"]+" <br> "+booking_data["traslate"]["bi_salidaFecha_dos"]+":</span></div><div style='color: "+booking_data["color"]["value_info"]+"'>"+booking_data["to_date"]+"</div></td><td style='width: 95px;'><div> <span style='color: "+booking_data["color"]["tx_info"]+";'>"+booking_data["traslate"]["bi_llegadaHora_uno"]+" <br> "+booking_data["traslate"]["bi_llegadaHora_dos"]+":</span></div><div style='color: "+booking_data["color"]["value_info"]+"'>"+booking_data["general_data"]["check_in"]+"</div></td></tr></table></td></tr></table><table style='width: 100%; max-width: 286px; display: inline-block; vertical-align: top;'><tr><td style='width: 100%;'><table style=' font-size: 12px;'><tr><td style='width: 95px;'><div> <span style='color: "+booking_data["color"]["tx_info"]+";'>"+booking_data["traslate"]["bi_salidaHora_uno"]+" <br> "+booking_data["traslate"]["bi_salidaHora_dos"]+":</span></div><div style='color: "+booking_data["color"]["value_info"]+"' >"+booking_data["general_data"]["check_out"]+"</div></td><td style='width: 95px;'><div> <span style='color: "+booking_data["color"]["tx_info"]+";'>"+booking_data["traslate"]["bi_noches_uno"]+" <br> "+booking_data["traslate"]["bi_noches_dos"]+":</span></div><div style='color: "+booking_data["color"]["value_info"]+"'>"+str(booking_data["nights"])+"</div></td><td style='width: 95px;'><div> <span style='color: "+booking_data["color"]["tx_info"]+";'>"+booking_data["traslate"]["bi_cuartos_uno"]+" <br> "+booking_data["traslate"]["bi_cuartos_dos"]+":</span></div><div style='color: "+booking_data["color"]["value_info"]+"'>"+str(booking_data["total_rooms"])+"</div></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr></table></td></tr>" +\
            "<tr><td style='width: 100%; padding: 0px 32px;'><div style='height: 15px;'></div><p style='border-top:solid 1px #e0e0e0;font-size:1;margin:0px auto;width:100%; '></p><div style='height: 15px;'></div></td></tr>"
        return info

    def getBookinInfoCancelation(self, booking_data):
        info_cancel = "<tr><td style='width: 100%; text-align: center;'><table style='width: 100%;'><tr><td><div>" +\
            "<span style='color: "+booking_data["color"]["base"]+"; font-weight: bold; font-size: 16px;'> "+booking_data["traslate"]["booking_history"]+" </span></div></td></tr></table></td></tr>"
        return info_cancel
    
    def getTraslates(self, status_code, lang):

        if lang.upper() == "ES":
            tituloUno = "¡Llegó el momento de preparar las maletas!"
            tituloDos = "Te esperamos en "
            tituloConfirmacion = "Tu Clave de Confirmación del Hotel"
            tituloCliente = "Información del huésped"
            tx_nombre = "Nombre:" 
            tx_numero = "Número de teléfono:"
            tx_correo = "Correo electrónico:"
            tx_requerimiento ="Solicitud especial:"
            tx_monto = "Cantidad pagada:"
            tx_balance = "Saldo pendiente:"
            tx_avisoUno = "* Las habitaciones se asignan al momento de realizar el check-in y las solicitudes especiales están sujetas a disponibilidad. "
            tx_avisoDos = "Debes proporcionar una tarjeta de crédito en tu check-in, para cubrir cualquier imprevisto."
            tx_information = "Información de la reserva."
            tx_deposit = "Deposito"
            rateUno = "Tarifa por noches"
            beneUno = "Beneficios adicionales"
            beneDos = "UN TODO INCLUIDO A UN NIVEL SORPRENDENTE"
            servicio = "Nada será igual después de que experimentes nuestros altos estándares en lujo todo incluido. Disfruta amenidades que rebasan todas tus expectativas, como bebidas de alta gama ilimitadas, servicio a la habitación gourmet las 24 horas, WiFi de alta velocidad gratis, amenidades de marca exclusiva, llamadas gratuitas ilimitadas a los EE. UU. continentales, Canadá y teléfonos fijos de México, y mucho más."
            tx_poli = "POLÍTICA DE CANCELACIONES"
            bi_llegadaFecha_uno = "Fecha de"
            bi_llegadaFecha_dos = "llegada"
            bi_salidaFecha_uno = "Fecha de"
            bi_salidaFecha_dos = "salida"
            bi_llegadaHora_uno = "Hora de"
            bi_llegadaHora_dos = "entrada"
            bi_salidaHora_uno = "Hora de"
            bi_salidaHora_dos = "salida"
            bi_noches_uno = "Núm. de"
            bi_noches_dos = "Noches"
            bi_cuartos_uno = "Núm. de"
            bi_cuartos_dos = "habitaciones"
            tx_guests = "Invitados"
            tx_consulta = "Si tienes alguna duda o deseas modificar o cancelar tu reserva, por favor escríbenos a"
            #text On Hold
            tituloUno_on = "No olvides completar tu reservación."
            sub_titulo1 = "Tu reserva para"
            sub_titulo2 = "ha quedado pendiente."
            tx_holdUno = "TU RESERVA EN"
            tx_holdDos = "PERMANECERÁ EN ESPERA POR 24 HORAS."
            tx_holdClock = "COMPLETA TU RESERVA ANTES DE "
            btn_reservation_onHold = "COMPLETA TU RESERVA"
            tx_holdTres = "LA RESERVA EXPIRARÁ AUTOMÁTICAMENTE EN ESE MOMENTO."
            poliUno = "POLÍTICA DE CANCELACIONES"
            poliDos = "GARANTÍA DE RESERVA"
            poliTres = "GRUPO DE REGLAS FISCALES"
            tx_provide_card =  "Se debe proporcionar una tarjeta de crédito al momento del check-in para imprevistos en la habitación. Cualquier tasa de conversión de moneda aplicable es responsabilidad del huésped. Es responsabilidad del huésped notificar y pagar por adelantado a todas las personas en la habitación."
            tx_privacyUno = "Politicas de privacidad"
            tx_privacyDos = "Privacidad EU"
            #Modificacion
            tx_title_modify = "MODIFICACIÓN DE RESERVA"
            tx_Subtitle_modify = "Gracias por actualizar tu información."
            tx_Subtitle_uno = "Por favor corrobora que los datos sean correctos en la reservación"
            tx_Subtitle_dos = "a continuación"
            tx_Booking_summary = "Resumen de reserva"
            id_reserva = "ID de reserva"
            name_property = "Nombre de la propiedad"
            lang_reservation = "Idioma de reserva"
            date_creation = "Creado en"
            last_modified = "Última modificación"
            total_price = "Precio Total"
            #Cancelaciones
            tx_title_cancelation = "LAMENTAMOS QUE TUS PLANES HAYAN CAMBIADO, "
            tx_Subtitle_cancelation = "pero esperamos poder darte la bienvenida muy pronto."
            tx_Subtitle_bookingUno = "La reservación "
            tx_Subtitle_bookingDos = " ha sido cancelada."
            Tx_total_room = "Total habitaciones"
            refund_Process = "Estatus del reembolso"
            refund_Process_tres = "(Este proceso puede tardar entre 15 y 30 días hábiles)"
            desglose_precio = "DESGLOSE DEL PRECIO"
            booking_history = "HISTORIAL DE LA RESERVA"
            tx_reason_cancel = "Razón de la cancelación"
            
        else:
            tituloUno = "Time to start packing!"
            tituloDos = "You are going to"
            tituloConfirmacion = "Your Hotel Confirmation Code"
            tituloCliente = "Guest Information"
            tx_nombre = "Name:" 
            tx_numero = "Phone Number:"
            tx_correo = "Email:"
            tx_requerimiento ="Personalized Request:"
            tx_monto = "Amount Paid:"
            tx_balance = "Outstanding balance:"
            tx_avisoUno = "*Rooms are assigned at check-in and special requests are subject to availability. "
            tx_avisoDos = "A credit card must be provided at check-in for room incidentals."
            tx_information = "Booking Information"
            tx_deposit = "Deposit"
            rateUno = "Rate per night"
            beneUno = "Additional Benefits"
            beneDos = "A WHOLE NEW LEVEL OF ALL INCLUSIVE"
            servicio = "After experiencing our standard of all-inclusive luxury, anything less will be inacceptable. Enjoy signature inclusions of our luxurious accommodations, including top-shelf sips, 24-hour room service, free WiFi, signature in-room amenities, unlimited calls to the Continental US, Canada and Mexico, and much more."
            tx_poli = "CANCELLATION POLICY"
            bi_llegadaFecha_uno = "Arrival"
            bi_llegadaFecha_dos = "Date"
            bi_salidaFecha_uno = "Departure"
            bi_salidaFecha_dos = "Date"
            bi_llegadaHora_uno = "Check-In"
            bi_llegadaHora_dos = "Time"
            bi_salidaHora_uno = "Check-Out"
            bi_salidaHora_dos = "Time"
            bi_noches_uno = "No. of"
            bi_noches_dos = "Nights"
            bi_cuartos_uno = "No. of"
            bi_cuartos_dos = "Rooms"
            tx_guests = "Guests"
            tx_consulta = "If you have any queries or wish to modify or cancel your reservation, please contact"
            #text On Hold
            tituloUno_on = "Don’t forget to complete your booking"
            sub_titulo1 = "Your reservation at"
            sub_titulo2 = "has been placed on hold for 24 hours."
            tx_holdUno = "YOUR BOOKING AT"
            tx_holdDos = "IS ON HOLD FOR 24 HOURS"
            tx_holdClock = "COMPLETE YOUR BOOKING BEFORE "
            btn_reservation_onHold = "COMPLETE YOUR RESERVATION"
            tx_holdTres = "THE BOOKING WILL AUTOMATICALLY EXPIRE AFTER THIS TIME."
            poliUno = "CANCELLATION POLICY"
            poliDos = "BOOKING GUARANTEE"
            poliTres = "TAX RULE GROUP"
            tx_provide_card =  "A credit card must be provided at check-in for any incidentals. Guests are responsible for any applicable currency exchange rates. Guests must notify of and pay in advance for all room occupants."
            tx_privacyUno = "Privacy Policy"
            tx_privacyDos = "EU Privacy"
            #Modificacion
            tx_title_modify = "BOOKING MODIFICATION"
            tx_Subtitle_modify = "Thank you for confirming your changes."
            tx_Subtitle_uno = "Please find the modified details for reservation"
            tx_Subtitle_dos = "below:"
            tx_Booking_summary = "Booking Details"
            id_reserva = "Booking ID"
            name_property = "Property Name"
            lang_reservation = "Booking Language"
            date_creation = "Created on"
            last_modified = "Last Modified"
            total_price = "Total Price"
            #Cancelaciones
            tx_title_cancelation = "WE ARE SORRY TO HEAR YOUR PLANS HAVE CHANGED"
            tx_Subtitle_cancelation = " and look forward to welcoming you in the near future."
            tx_Subtitle_bookingUno = "Booking "
            tx_Subtitle_bookingDos = " has been cancelled."
            Tx_total_room = "Total rooms"
            refund_Process = "Refund Process"
            refund_Process_tres = "(Please note that this may take between 15 to 30 business days)."
            desglose_precio = "PRICING DETAILS"
            booking_history = "BOOKING HISTORY"
            tx_reason_cancel = "Reason for cancellation"




        traslates = {
            "tituloUno": tituloUno,
            "tituloDos": tituloDos,
            "tituloConfirmacion": tituloConfirmacion,
            "tituloCliente": tituloCliente,
            "tx_nombre": tx_nombre, 
            "tx_numero": tx_numero,
            "tx_correo": tx_correo,
            "tx_deposit": tx_deposit,
            "tx_requerimiento": tx_requerimiento,
            "tx_monto": tx_monto,
            "tx_balance": tx_balance,
            "tx_avisoUno": tx_avisoUno,
            "tx_avisoDos": tx_avisoDos,
            "tx_information": tx_information,
            "tx_deposit": tx_deposit,
            "rateUno": rateUno,
            "beneUno": beneUno,
            "beneDos": beneDos,
            "servicio": servicio,
            "tx_poli": tx_poli,
            "bi_llegadaFecha_uno": bi_llegadaFecha_uno,
            "bi_llegadaFecha_dos": bi_llegadaFecha_dos,
            "bi_salidaFecha_uno": bi_salidaFecha_uno,
            "bi_salidaFecha_dos": bi_salidaFecha_dos,
            "bi_llegadaHora_uno": bi_llegadaHora_uno,
            "bi_llegadaHora_dos": bi_llegadaHora_dos,
            "bi_salidaHora_uno": bi_salidaHora_uno,
            "bi_salidaHora_dos": bi_salidaHora_dos,
            "bi_noches_uno": bi_noches_uno,
            "bi_noches_dos": bi_noches_dos,
            "bi_cuartos_uno": bi_cuartos_uno,
            "bi_cuartos_dos": bi_cuartos_dos,
            "tx_guests": tx_guests,
            "tituloUno_on": tituloUno_on,
            "sub_titulo1": sub_titulo1,
            "sub_titulo2": sub_titulo2,
            "tx_holdUno": tx_holdUno,
            "tx_holdDos": tx_holdDos,
            "tx_holdClock": tx_holdClock,
            "btn_reservation_onHold": btn_reservation_onHold,
            "tx_holdTres": tx_holdTres,
            "poliUno": poliUno,
            "poliDos": poliDos,
            "poliTres": poliTres,
            "tx_provide_card": tx_provide_card,
            "tx_privacyUno": tx_privacyUno,
            "tx_privacyDos": tx_privacyDos,
            "tx_title_modify": tx_title_modify,
            "tx_Subtitle_modify": tx_Subtitle_modify,
            "tx_Subtitle_uno": tx_Subtitle_uno,
            "tx_Subtitle_dos": tx_Subtitle_dos,
            "tx_Booking_summary": tx_Booking_summary,
            "id_reserva": id_reserva,
            "name_property": name_property,
            "lang_reservation": lang_reservation,
            "date_creation": date_creation,
            "last_modified": last_modified,
            "total_price": total_price,
            "tx_consulta": tx_consulta,
            "tx_title_cancelation": tx_title_cancelation,
            "tx_Subtitle_cancelation": tx_Subtitle_cancelation,
            "tx_Subtitle_bookingUno": tx_Subtitle_bookingUno,
            "tx_Subtitle_bookingDos": tx_Subtitle_bookingDos,
            "Tx_total_room": Tx_total_room,
            "refund_Process": refund_Process,
            "refund_Process_tres": refund_Process_tres,
            "desglose_precio": desglose_precio,
            "booking_history": booking_history,
            "tx_reason_cancel": tx_reason_cancel
        }

        return traslates

    def getSubject(self, booking_data, lang_code = "EN", is_remember = False):
        subject = ""

        if booking_data["lang_code"].upper() == "ES":
            if booking_data["on_hold"] == True:
                if is_remember:
                    subject = "Completa tu reservación antes de que pierdas tus beneficios"
                else:
                    subject = "Recuerda completar tu reserva antes de 24 horas"
            elif booking_data["status_code"] == BookStatus.expired:
                subject = "Oh no, tu reservación ya expiró."
            elif booking_data["status_code"] == BookStatus.cancel:
                subject = "Ha sido cancelada tu reserva en {}".format(booking_data["trade_name"])
            else:
                subject = "Gracias por reservar en " + booking_data["trade_name"]
        else:            
            if booking_data["on_hold"] == True:
                if is_remember:
                    subject = "Act quickly before your benefits expire"
                else:
                    subject = "Remember to complete your booking within 24 hours"
            elif booking_data["status_code"] == BookStatus.expired:
                subject = "Oh dear, your on-hold booking just expired"
            elif booking_data["status_code"] == BookStatus.cancel:
                subject = "Your booking at {} has been cancelled".format(booking_data["trade_name"])
            else:
                subject = "Thank you for booking at " + booking_data["trade_name"]
        
        return subject
    