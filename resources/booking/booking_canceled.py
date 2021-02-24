from flask import Flask, request
from flask_restful import Resource
from marshmallow import ValidationError
from datetime import date, datetime, timedelta
from sqlalchemy.sql.expression import and_
from functools import reduce

from config import db, base
from common.util import Util
from models.book_hotel import BookHotelReservationSchema as ModelSchema, BookHotel, BookHotelAdminSchema, EmailReservationSchema, CancelReservationSchema
from models.book_status import BookStatus
from models.payment_method import PaymentMethod
from .booking_service import BookingService
from resources.log_changes.log_changes_helper import LogChangesHelper
from resources.property.property_service import PropertyService
from resources.carta.emailTemplate import EmailTemplate

class BookingLetter():
    @staticmethod
    def booking_leatter_canceled(code_reservation):
        try:

            book_hotel = BookHotel.query.\
                filter(BookHotel.code_reservation == code_reservation, BookHotel.estado == 1).first()
            
            booking_service = BookingService()
            booking_data = booking_service.format_booking_info(book_hotel)

            if booking_data["status_code"] not in [BookStatus.cancel]:
                raise Exception(Util.t(booking_data["lang_code"], "booking_code_not_found", code_reservation))
            
            email_template = EmailTemplate()
            subject = email_template.getSubject(booking_data, booking_data["lang_code"])
            email_data = {
                "email_list": booking_data["customer"]["email"],
                "sender": booking_data["sender"],
                "group_validation": False,
                "html": email_template.get(booking_data),
                "email_subject": subject
            }

            Util.send_notification(email_data, email_template.email_tag, book_hotel.usuario_creacion)

            if base.environment == "pro":
                #retrieve email cc to send a email copy
                email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                email_data["email_list"] = email_cc
                Util.send_notification(email_data, email_template.email_tag, book_hotel.usuario_creacion)
            
        except Exception as error:
            raise error
        
        return booking_data
    
    @staticmethod
    def booking_leatter_modification(code_reservation):
        try:

            book_hotel = BookHotel.query.\
                filter(BookHotel.code_reservation == code_reservation, BookHotel.estado == 1).first()

            booking_service = BookingService()
            booking_data = booking_service.format_booking_info(book_hotel)

            if booking_data["status_code"] not in [BookStatus.changed]:
                raise Exception(Util.t(booking_data["lang_code"], "booking_code_not_found", code_reservation))
            
            email_template = EmailTemplate()
            subject = email_template.getSubject(booking_data, booking_data["lang_code"])
            email_data = {
                "email_list": booking_data["customer"]["email"],
                "sender": booking_data["sender"],
                "group_validation": False,
                "html": email_template.get(booking_data),
                "email_subject": subject
            }

            Util.send_notification(email_data, email_template.email_tag, book_hotel.usuario_creacion)
            if base.environment == "pro":
                #retrieve email cc to send a email copy
                email_cc = PropertyService.get_email_contact(book_hotel.iddef_property, ";")
                email_data["email_list"] = email_cc
                Util.send_notification(email_data, email_template.email_tag, book_hotel.usuario_creacion)
            
        except Exception as error:
            raise error
        
        return email_data

    @staticmethod
    def format_cancellation_letter(booking_data, data_history):
        """
            Format booking data for cancellation letter
            :param book_hotel = book_hotel instance
        """
        #booking_data = code_reservation        
        tituloBookingCance = ""
        subTitulo = ""
        subTitulo_1 = ""
        tituloSummary = ""
        tituloHistory = ""
        status = ""
        date = ""
        guest = ""
        checkIn = ""
        checkOut = ""
        nights = ""
        price = ""
        tituloBooking = ""
        idBooking = ""
        totalRooms = ""
        propertyName = ""
        bookingLng = ""
        creationDate = ""
        lastModified = ""
        tituloContact = ""
        name = ""
        address = ""
        email = ""
        phone = ""
        tituloPricing = ""
        totalPrice = ""
        tituloGuarantee = ""
        creditCard = ""
        tituloComments = ""
        tituloGuestInfo = ""
        date_checkin = ""
        numNights = ""
        numRooms = ""
        hotel_name = ""
        date_creation = ""
        modification_date = ""
        name_contact = ""
        last_name = ""
        title_name = ""
        zip_code = ""
        city = ""
        state = ""
        email_text = ""
        phone_text = ""
        section_rooms = ""
        rooms_detail = ""
        name_rate_plan = ""
        currency_code = booking_data['currency_code']
        total_res = booking_data['total']
        code_reservation = booking_data['code_reservation']
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

        if booking_data["lang_code"].upper() == "ES":
            tituloBookingCance = "Cancelación de Reserva"
            subTitulo = "La reserva"            
            subTitulo_1 = "ha sido cancelada."
            tituloSummary = "Resumen de la Reserva"
            if data_history != []:
                tituloHistory = "Historial de Reserva"
            status = "Estado"
            date = "Fecha"
            guest = "Huéspedes"
            checkIn = "Llegada"
            checkOut = "Salida"
            nights = "Noches"
            numNights = str(booking_data['nights'])
            price = "Precio"
            tituloBooking = "Reserva"
            idBooking = "ID Reserva"
            date_checkin = str(booking_data['from_date'])
            totalRooms = "Cuartos Totales"
            numRooms = str(booking_data['total_rooms'])
            propertyName = "Hotel"
            hotel_name = booking_data['trade_name']
            bookingLng = "Idioma de la Reserva"
            creationDate = "Fecha de Creación"
            date_creation = str(booking_data['customer']['address']['fecha_creacion'])
            lastModified = "Última modificación"
            modification_date = str(booking_data['customer']['address']['fecha_ultima_modificacion'])
            tituloContact = "Contacto Principal"
            title_name = booking_data['customer']['title']
            name = "Nombre"
            name_contact = booking_data['customer']['first_name']
            last_name = booking_data['customer']['last_name']
            address = "Dirección"
            address_text = booking_data['customer']['address']['address']
            zip_code = str(booking_data['customer']['address']['zip_code'])
            city = booking_data['customer']['address']['city']
            state = booking_data['customer']['address']['state']
            email = "Correo Electrónico"
            email_text = booking_data['customer']['email']
            phone = "Teléfono"
            phone_text = str(booking_data['customer']['phone_number'])
            tituloPricing = "Detalles de Precio"
            totalPrice = "Precio Total"
            tituloGuarantee = "Garantía"
            avisoCreditCard = "Tarjeta de crédito como garantía"
            creditCard = "Tarjeta de Crédito"
            avisoDetails = "Los detalles sobre la (s) garantía (es) de reserva se encuentran en la (s) sección (es) de la habitación."
            tituloComments = "Comentarios"
            tituloGuestInfo = "Información del Huésped"
            confirmedStatus = "Confirmado"
            subject = "Cancelación de reserva" + " " + "-" + " "+ hotel_name + " " + "-" + " " + code_reservation + "," + name_contact+ " " + last_name
        else:
            tituloBookingCance = "Booking Cancellation"
            subTitulo = "The booking"
            subTitulo_1 = "has been cancelled."
            tituloSummary = "Booking Summary"
            if data_history != []:
                tituloHistory = "Booking History"
            status = "Status"
            date = "Date"
            guest = "Guests"
            checkIn = "Check-In"
            checkOut = "Check-Out"
            nights = "Nights"
            numNights = str(booking_data['nights'])
            price = "Price"
            tituloBooking = "Booking"
            idBooking = "Booking ID"
            date_checkin = booking_data['from_date']
            totalRooms = "Total Rooms"
            numRooms = str(booking_data['total_rooms'])
            propertyName = "Property name"
            hotel_name = booking_data['trade_name']
            bookingLng = "Booking Language"
            creationDate = "Creation date"
            date_creation = booking_data['customer']['address']['fecha_creacion']
            lastModified = "Last modified"
            modification_date = booking_data['customer']['address']['fecha_ultima_modificacion']
            tituloContact = "Primary contact"
            title_name = booking_data['customer']['title']
            name = "Name"
            name_contact = booking_data['customer']['first_name']
            last_name = booking_data['customer']['last_name']
            address = "Address"
            address_text = booking_data['customer']['address']['address']
            zip_code = booking_data['customer']['address']['zip_code']
            city = booking_data['customer']['address']['city']
            state = booking_data['customer']['address']['state']
            email = "Email"
            email_text = booking_data['customer']['email']
            phone = "Phone"
            phone_text = booking_data['customer']['phone_number']
            tituloPricing = "Pricing Details"
            totalPrice = "Total Price"
            tituloGuarantee = "Guarantee"
            avisoCreditCard = "Credit Card as Guarantee"
            creditCard = "Credit Card"
            avisoDetails = "Details about the booking guarantee(s) are found in the room section(s)."
            tituloComments = "General Comments"
            tituloGuestInfo = "Guest information"
            confirmedStatus = "Confirmed"
            subject = "Booking cancellation" + " " + "-" + " "+ hotel_name + " " + "-" + " " + code_reservation + "," + name_contact+ " " + last_name
        email_list = ""
        group_validation = False        
        propiedad = "" 
        nombre = ""
        correo=""
        carta = "NOTIFICATION_BENGINE_CANCELLATION_PALACE"
        table_history = ""        

        for rooms in booking_data['rooms']:                     
            dates = ""
            name_guarantee = ""
            text_guarantee = ""
            name_cancellation = ""
            text_cancellation = ""
            prices_section = ""            
            colum_prices = ""
            colum_prices = colum_prices + "<span style='font-size:12px;'>$"+str(rooms['total'])+"</span>"
            prices_section = prices_section + "<td align='right' style='background-color:transparent;padding:3px 0;'> <span style='background-color:transparent;'> <span style='color:#D1322C; font-size:10px'>"+currency_code+" $ "+str(rooms['total_crossout'])+"</span><br/><span color='#222222'>"+currency_code+" $"+str(rooms["total"])+"</span> </span> </td>"
            for prices in rooms['prices']:                
                dates = dates + "<tr><td align='center' style='width:25%;text-align:center;background-color:#DDDDDD;padding:0;border-left:3px solid #28908C; border-right:3px solid #28908C;border-bottom:3px solid #28908C;'> <span style='font-size:12px;background-color:#DDDDDD;'> <div style='background-color:#28908C;padding:0 2px;'> <span style='font-size:12px;background-color:#28908C;color:white'><b>"+prices["date"]+"</b></span> </div><div style='background-color:#FAFCFC;padding:0 2px;'> <span style='font-size:12px;background-color:#FAFCFC;color:white'> <span style='color:#D1322C; font-size:10px'>"+currency_code+"&nbsp; $"+str(prices['total_gross'])+"&nbsp;</span> <span style='font-size:12px;color:#222222'>"+currency_code+"&nbsp; $"+str(prices["total"])+"&nbsp;</span> </span> </div></span> </td></tr>"            
                                
            for guarantee in booking_data['guarantee_policies']:
                name_guarantee = name_guarantee + "<span style='font-size:17px;text-transform:none;color:#005356'><b>"+guarantee['policy_category']+"</b></span>"

                for text in guarantee['texts']:                    
                    text_guarantee = text_guarantee + "<span style='font-size:14px;background-color:white;'> "+text+" </span>"

            for cancellation in booking_data['cancelation_policies']:
                name_cancellation = name_cancellation + "<span style='font-size:17px;text-transform:none;color:#005356'><b>"+cancellation['policy_category']+"</b></span>"
                text_cancellation = text_cancellation + " <span style='font-size:14px;background-color:white;'> "+cancellation['texts']+" </span>"
            
            rooms_detail = rooms_detail + "<tr style='background-color:transparent;'> <td align='left' style='text-align:justify;background-color:transparent;padding:3px 10px 3px 0;'> <span style='background-color:transparent;font-weight:normal;'>"+rooms['trade_name_room']+"</span> </td>"+prices_section+"</tr>"
            section_rooms = section_rooms + "<tr> <td style='padding: 0 0 2px 0; border-color: #28908c; border-bottom-width: 4px; border-bottom-style: solid;'> <table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr> <td style='padding: 0;'> <div align='left' style='text-align: justify; margin: 0; padding: 10px 0 5px 10px;'> <span style='font-size: 20px; text-transform: none; color: #d1a22c;'> <b>"+rooms['trade_name_room']+"</b> </span> </div></td></tr></tbody> </table> </td></tr><tr> <td style='background-color: white; padding: 0;'> <table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr> <td align='left' style='width: 100%; text-align: justify; background-color: white; padding: 10px;'> <span style='font-size: 14px; background-color: white;'> <div align='left' style='text-align: justify; margin: 10px 0;'> <span style='font-size: 17px; text-transform: none; color: #005356;'> <b>Rates / Meal Plan</b> </span> </div><span>"+rooms['rateplan_name']+"</span> <table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> "+dates+" </tbody> </table> <div align='left' style='text-align: justify; margin: 10px 0;'>"+name_guarantee+"</div><table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr> <td align='left' valign='top' style='width:100%;text-align:justify;background-color:white;padding:0;'> "+text_guarantee+" </td></tr></tbody> </table> <div align='left' style='text-align: justify; margin: 10px 0;'>"+name_cancellation+"</div><table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr><td align='left' valign='top' style='width:100%;text-align:justify;background-color:white;padding:0;'> "+text_cancellation+"</td> </tr></tbody> </table> </span> </td></tr></tbody> </table> </td></tr>"
        if data_history != []:
            for logHistory in data_history:
                if logHistory['status_code'] in [4, 7, 8]: 
                    logHistory['status'] = confirmedStatus      
                table_history = table_history + "<tr> <td align='left' style='text-align:justify;padding:2px;'> <span style='font-size:12px;'><a href='' target='_blank' style='text-decoration:underline; color:#28908C'>"+logHistory['status']+"</a></span> </td><td align='left' style='text-align:justify;padding:2px;'> <span style='font-size:12px;'>"+logHistory['fecha_ultima_modificacion']+"</span> </td><td align='right' style='padding:2px;'> <span style='font-size:12px;'>"+str(logHistory['adults']+logHistory['child'])+"</span> </td><td align='right' style='padding:2px;'> <span style='font-size:12px;'>"+logHistory['from_date']+"</span> </td><td align='right' style='padding:2px;'> <span style='font-size:12px;'>"+str(logHistory['nights'])+"</span> </td><td align='right' style='padding:2px;white-space:nowrap;'> "+colum_prices+"</td></tr>"
            table_history = "<tr><td style='background-color:white;padding:0;'><table width='100%' style='border-spacing:0;width:100%;'><tbody><tr><td align='left' style='width:100%;text-align:justify;background-color:white;padding:10px;'><div align='left' style='text-align:justify;margin:10px 0;'><span style='font-size:17px;text-transform:none; color: #005356;'><b>"+tituloHistory+"</b></span></div><table width='100%' style='border-spacing:0;width:100%;'><tbody><tr> <td align='left' style='text-align:justify;background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white;'><b>"+status+"</b></span> </td><td align='left' style='text-align:justify;background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+date+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+guest+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+checkIn+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+nights+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+price+"</b></span> </td></tr>"+table_history+"</tbody></table></td></tr></tbody></table></td></tr>"
        
        data = {
            "email_list": "",
            "url_banner":dictHeader[booking_data["property_code"]],
            "sender":booking_data["sender"],
            "group_validation": False,
            "email_subject": subject,
            "propiedad": "ZMGR",
            "nombre": nombre,
            "correo": correo,
            "carta": carta,                     
            "tituloBookingCance" : tituloBookingCance,
            "subTitulo": subTitulo,
            "subTitulo_1": subTitulo_1,
            "tituloSummary": tituloSummary,
            "tituloHistory": tituloHistory,
            "status": status,
            "date": date,
            "guest": guest,
            "checkIn": checkIn,
            "checkOut": checkOut,
            "nights": nights,
            "price": price,
            "currency_code" : currency_code,
            "tituloBooking": tituloBooking,
            "idBooking": idBooking,
            "rooms_detail": rooms_detail,
            "total_res" : total_res,
            "totalRooms": totalRooms,
            "propertyName": propertyName,
            "bookingLng": bookingLng,
            "creationDate": creationDate,
            "lastModified": lastModified,
            "tituloContact": tituloContact,
            "table_history": table_history,
            "name": name,
            "section_rooms": section_rooms,
            "address": address,
            "email": email,
            "phone": phone,
            "tituloPricing": tituloPricing,
            "totalPrice": totalPrice,
            "tituloGuarantee": tituloGuarantee,
            "creditCard": creditCard,
            "tituloComments": tituloComments,
            "tituloGuestInfo": tituloGuestInfo,
            "code_reservation" : code_reservation,
            "date_checkin" : date_checkin,
            "numNights" : numNights,
            "numRooms" : numRooms,
            "hotel_name": hotel_name,
            "date_creation" : date_creation,
            "modification_date" : modification_date,
            "name_contact" : name_contact,
            "last_name": last_name,
            "title_name" : title_name,
            "zip_code" : zip_code,
            "city" : city,
            "state" : state,
            "email_text" : email_text,
            "phone_text" : phone_text,
            "address_text" : address_text,
            "avisoCreditCard" : avisoCreditCard,
            "avisoDetails" : avisoDetails
        }

        return data
        
    @staticmethod
    def format_modification_letter(booking_data, data_history):
        """
            Format booking data for cancellation letter
            :param book_hotel = book_hotel instance
        """
        #booking_data = code_reservation        
        tituloBookingModi = ""
        subTitulo = ""
        subTitulo_1 = ""
        tituloSummary = ""
        tituloHistory = ""
        status = ""
        date = ""
        guest = ""
        checkIn = ""
        checkOut = ""
        nights = ""
        price = ""
        tituloBooking = ""
        idBooking = ""
        totalRooms = ""
        propertyName = ""
        bookingLng = ""
        creationDate = ""
        lastModified = ""
        tituloContact = ""
        name = ""
        address = ""
        email = ""
        phone = ""
        tituloPricing = ""
        totalPrice = ""
        tituloGuarantee = ""
        creditCard = ""
        tituloComments = ""
        tituloGuestInfo = ""
        code_reservation = booking_data['code_reservation']
        date_checkin = ""
        date_checkout = ""
        numNights = ""
        numRooms = ""
        hotel_name = ""
        date_creation = ""
        modification_date = ""
        name_contact = ""
        last_name = ""
        title_name = ""
        zip_code = ""
        city = ""
        state = ""
        email_text = ""
        phone_text = ""
        section_rooms = ""
        rooms_detail = ""
        name_rate_plan = ""
        services = ""
        currency_code = booking_data['currency_code']
        total_res = booking_data['total']
        description = ""
        quantity = ""
        services_list = ""
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

        if booking_data["lang_code"].upper() == "ES":
            tituloBookingModi = "Modificación de Reserva"
            subTitulo = "La reserva"
            subTitulo_1 = "ha sido modificada."
            tituloSummary = "Resumen de la Reserva"
            if data_history != []:
                tituloHistory = "Historial de Reserva"
            status = "Estado"
            date = "Fecha"
            services = "Servicios"
            guest = "Huéspedes"
            checkIn = "Llegada"
            checkOut = "Salida"
            nights = "Noches"
            numNights = str(booking_data['nights'])
            price = "Precio"
            tituloBooking = "Reserva"
            idBooking = "ID Reserva"
            date_checkin = str(booking_data['from_date'])
            date_checkout = str(booking_data['to_date'])
            totalRooms = "Cuartos Totales"
            numRooms = str(booking_data['total_rooms'])
            propertyName = "Hotel"
            hotel_name = booking_data['trade_name']
            bookingLng = "Idioma de la Reserva"
            creationDate = "Fecha de Creación"
            date_creation = str(booking_data['customer']['address']['fecha_creacion'])
            lastModified = "Última modificación"
            modification_date = str(booking_data['customer']['address']['fecha_ultima_modificacion'])
            tituloContact = "Contacto Principal"
            title_name = booking_data['customer']['title']
            name = "Nombre"
            name_contact = booking_data['customer']['first_name']
            last_name = booking_data['customer']['last_name']
            address = "Dirección"
            address_text = booking_data['customer']['address']['address']
            zip_code = str(booking_data['customer']['address']['zip_code'])
            city = booking_data['customer']['address']['city']
            state = booking_data['customer']['address']['state']
            email = "Correo Electrónico"
            email_text = booking_data['customer']['email']
            phone = "Teléfono"
            phone_text = str(booking_data['customer']['phone_number'])
            tituloPricing = "Detalles de Precio"
            totalPrice = "Precio Total"
            tituloGuarantee = "Garantía"
            avisoCreditCard = "Tarjeta de crédito como garantía"
            creditCard = "Tarjeta de Crédito"
            avisoDetails = "Los detalles sobre la (s) garantía (es) de reserva se encuentran en la (s) sección (es) de la habitación."
            tituloComments = "Comentarios"
            tituloGuestInfo = "Información del Huésped"
            description = "Descripción"
            quantity = "Cantidad"
            confirmedStatus = "Confirmado"
            subject = "Modificación de reserva" + " " + "-" + " "+ hotel_name + " " + "-" + " " + code_reservation + "," + name_contact+ " " + last_name
        else:
            tituloBookingModi = "Booking Modification"
            subTitulo = "The booking"
            subTitulo_1 = "has been modified."
            tituloSummary = "Booking Summary"
            if data_history != []:
                tituloHistory = "Booking History"
            status = "Status"
            date = "Date"
            services = "Services"
            guest = "Guests"
            checkIn = "Check-In"
            checkOut = "Check-Out"
            nights = "Nights"
            numNights = str(booking_data['nights'])
            price = "Price"
            tituloBooking = "Booking"
            idBooking = "Booking ID"
            date_checkin = booking_data['from_date']
            date_checkout = str(booking_data['to_date'])
            totalRooms = "Total Rooms"
            numRooms = str(booking_data['total_rooms'])
            propertyName = "Property name"
            hotel_name = booking_data['trade_name']
            bookingLng = "Booking Language"
            creationDate = "Creation date"
            date_creation = booking_data['customer']['address']['fecha_creacion']
            lastModified = "Last modified"
            modification_date = booking_data['customer']['address']['fecha_ultima_modificacion']
            tituloContact = "Primary contact"
            title_name = booking_data['customer']['title']
            name = "Name"
            name_contact = booking_data['customer']['first_name']
            last_name = booking_data['customer']['last_name']
            address = "Address"
            address_text = booking_data['customer']['address']['address']
            zip_code = booking_data['customer']['address']['zip_code']
            city = booking_data['customer']['address']['city']
            state = booking_data['customer']['address']['state']
            email = "Email"
            email_text = booking_data['customer']['email']
            phone = "Phone"
            phone_text = booking_data['customer']['phone_number']
            tituloPricing = "Pricing Details"
            totalPrice = "Total Price"
            tituloGuarantee = "Guarantee"
            avisoCreditCard = "Credit Card as Guarantee"
            creditCard = "Credit Card"
            avisoDetails = "Details about the booking guarantee(s) are found in the room section(s)."
            tituloComments = "General Comments"
            tituloGuestInfo = "Guest information"
            description = "Description"
            quantity = "Quantity"
            confirmedStatus = "Confirmed"
            subject = "Booking modification" + " " + "-" + " "+ hotel_name + " " + "-" + " " + code_reservation + "," + name_contact+ " " + last_name
        email_list = ""
        group_validation = False
        propiedad = "" 
        correo=""
        nombre = ""
        carta = "NOTIFICATION_BENGINE_MODIFICATION_PALACE"
        table_history = ""        

        for rooms in booking_data['rooms']:                     
            dates = ""
            name_guarantee = ""
            text_guarantee = ""
            name_cancellation = ""
            text_cancellation = ""
            prices_section = ""            
            colum_prices = ""
            colum_prices = colum_prices + "<span style='font-size:12px;'>$"+str(rooms['total'])+"</span>"
            prices_section = prices_section + "<td align='right' style='background-color:transparent;padding:3px 0;'> <span style='background-color:transparent;'> <span style='color:#D1322C; font-size:10px'>"+currency_code+" $ "+str(rooms['total_crossout'])+"</span></br><span color='#222222'>"+currency_code+" $"+str(rooms["total"])+"&nbsp;</span> </span> </td>"
            for prices in rooms['prices']:                
                dates = dates + "<tr><td align='center' style='width:25%;text-align:center;background-color:#DDDDDD;padding:0;border-left:3px solid #28908C; border-right:3px solid #28908C;border-bottom:3px solid #28908C;'> <span style='font-size:12px;background-color:#DDDDDD;'> <div style='background-color:#28908C;padding:0 2px;'> <span style='font-size:12px;background-color:#28908C;color:white'><b>"+prices["date"]+"</b></span> </div><div style='background-color:#FAFCFC;padding:0 2px;'> <span style='font-size:12px;background-color:#FAFCFC;color:white'> <span style='font-size:12px; color:#D1322C;'>"+currency_code+"&nbsp; $"+str(prices['total_gross'])+"&nbsp;</span> <span style='font-size:12px;color:#222222'>"+currency_code+"&nbsp; $"+str(prices["total"])+"&nbsp;</span> </span> </div></span> </td></tr>"            
                                
            for guarantee in booking_data['guarantee_policies']:
                name_guarantee = name_guarantee + "<span style='font-size:17px;text-transform:none;color:#005356'><b>"+guarantee['policy_category']+"</b></span>"

                for text in guarantee['texts']:                    
                    text_guarantee = text_guarantee + "<span style='font-size:14px;background-color:white;'> "+text+" </span>"

            for cancellation in booking_data['cancelation_policies']:
                name_cancellation = name_cancellation + "<span style='font-size:17px;text-transform:none;color:#005356'><b>"+cancellation['policy_category']+"</b></span>"
                text_cancellation = text_cancellation + "<span style='font-size:14px;background-color:white;'> "+cancellation['texts']+" </span>"
            
            rooms_detail = rooms_detail + "<tr style='background-color:transparent;'> <td align='left' style='text-align:justify;background-color:transparent;padding:3px 10px 3px 0;'> <span style='background-color:transparent;font-weight:normal;'>"+rooms['trade_name_room']+"</span> </td>"+prices_section+"</tr>"
            section_rooms = section_rooms + "<tr> <td style='padding: 0 0 2px 0; border-color: #28908c; border-bottom-width: 4px; border-bottom-style: solid;'> <table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr> <td style='padding: 0;'> <div align='left' style='text-align: justify; margin: 0; padding: 10px 0 5px 10px;'> <span style='font-size: 20px; text-transform: none; color: #d1a22c;'> <b>"+rooms['trade_name_room']+"</b> </span> </div></td></tr></tbody> </table> </td></tr><tr> <td style='background-color: white; padding: 0;'> <table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr> <td align='left' style='width: 100%; text-align: justify; background-color: white; padding: 10px;'> <span style='font-size: 14px; background-color: white;'> <div align='left' style='text-align: justify; margin: 10px 0;'> <span style='font-size: 17px; text-transform: none; color: #005356;'> <b>Rates / Meal Plan</b> </span> </div><span>"+rooms['rateplan_name']+"</span> <table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> "+dates+" </tbody> </table> <div align='left' style='text-align: justify; margin: 10px 0;'>"+name_guarantee+"</div><table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr><td align='left' valign='top' style='width:100%;text-align:justify;background-color:white;padding:0;'>  "+text_guarantee+"</td></tr></tbody> </table> <div align='left' style='text-align: justify; margin: 10px 0;'>"+name_cancellation+"</div><table width='100%' style='border-spacing: 0; width: 100%;'> <tbody> <tr><td align='left' valign='top' style='width:100%;text-align:justify;background-color:white;padding:0;'> "+text_cancellation+" </td></tr></tbody> </table> </span> </td></tr></tbody> </table> </td></tr>"
        if data_history != [] :
            for logHistory in data_history :
                if logHistory['status_code'] in [4, 7, 8]: 
                    logHistory['status'] = confirmedStatus
                table_history = table_history + "<tr> <td align='left' style='text-align:justify;padding:2px;'> <span style='font-size:12px;'><a href='' target='_blank' style='text-decoration:underline; color:#28908C'>"+logHistory['status']+"</a></span> </td><td align='left' style='text-align:justify;padding:2px;'> <span style='font-size:12px;'>"+logHistory['fecha_ultima_modificacion']+"</span> </td><td align='right' style='padding:2px;'> <span style='font-size:12px;'>"+str(logHistory['adults']+logHistory['child'])+"</span> </td><td align='right' style='padding:2px;'> <span style='font-size:12px;'>"+logHistory['from_date']+"</span> </td><td align='right' style='padding:2px;'> <span style='font-size:12px;'>"+str(logHistory['nights'])+"</span> </td><td align='right' style='padding:2px;white-space:nowrap;'> "+colum_prices+"</td></tr>"
            table_history = "<tr><td style='background-color:white;padding:0;'><table width='100%' style='border-spacing:0;width:100%;'><tbody><tr><td align='left' style='width:100%;text-align:justify;background-color:white;padding:10px;'><div align='left' style='text-align:justify;margin:10px 0;'><span style='font-size:17px;text-transform:none; color: #005356;'><b>"+tituloHistory+"</b></span></div><table width='100%' style='border-spacing:0;width:100%;'><tbody><tr> <td align='left' style='text-align:justify;background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white;'><b>"+status+"</b></span> </td><td align='left' style='text-align:justify;background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+date+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+guest+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+checkIn+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+nights+"</b></span> </td><td align='right' style='background-color:#28908C;padding:2px;'> <span style='font-size:12px;background-color:#28908C; color:white'><b>"+price+"</b></span> </td></tr>"+table_history+"</tbody></table></td></tr></tbody></table></td></tr>"
        
        for listServices in booking_data['services_info'] :
            services_list = services_list + "<tr> <td align='left' style='text-align:justify;padding:2px;'> <span style='font-size:12px;'><b>"+listServices['name']+"</b></span> </td><td align='center' style='text-align:center;padding:2px;'> <span style='font-size:12px;'>1</span> </td><td align='center' style='text-align:center;padding:2px;white-space:nowrap;'> <span style='font-size:12px;'>Included </span> </td></tr>"
        
        data = {
            "email_list": "",
            "url_banner":dictHeader[booking_data["property_code"]],
            "sender":booking_data["sender"],
            "group_validation": False,
            "email_subject": subject,
            "propiedad": "ZMGR",
            "nombre": nombre,
            "correo": correo,
            "carta": carta,
            "services_list" : services_list,
            "tituloBookingModi" : tituloBookingModi,
            "services": services,
            "description" : description,
            "quantity" : quantity,
            "subTitulo": subTitulo,
            "subTitulo_1": subTitulo_1,
            "tituloSummary": tituloSummary,
            "tituloHistory": tituloHistory,
            "status": status,
            "date_checkout": date_checkout,
            "date": date,
            "guest": guest,
            "checkIn": checkIn,
            "checkOut": checkOut,
            "nights": nights,
            "price": price,
            "currency_code" : currency_code,
            "tituloBooking": tituloBooking,
            "idBooking": idBooking,
            "rooms_detail": rooms_detail,
            "total_res" : total_res,
            "totalRooms": totalRooms,
            "propertyName": propertyName,
            "bookingLng": bookingLng,
            "creationDate": creationDate,
            "lastModified": lastModified,
            "tituloContact": tituloContact,
            "table_history": table_history,
            "name": name,
            "section_rooms": section_rooms,
            "address": address,
            "email": email,
            "phone": phone,
            "tituloPricing": tituloPricing,
            "totalPrice": totalPrice,
            "tituloGuarantee": tituloGuarantee,
            "creditCard": creditCard,
            "tituloComments": tituloComments,
            "tituloGuestInfo": tituloGuestInfo,
            "code_reservation" : code_reservation,
            "date_checkin" : date_checkin,
            "numNights" : numNights,
            "numRooms" : numRooms,
            "hotel_name": hotel_name,
            "date_creation" : date_creation,
            "modification_date" : modification_date,
            "name_contact" : name_contact,
            "last_name": last_name,
            "title_name" : title_name,
            "zip_code" : zip_code,
            "city" : city,
            "state" : state,
            "email_text" : email_text,
            "phone_text" : phone_text,
            "address_text" : address_text,
            "avisoCreditCard" : avisoCreditCard,
            "avisoDetails" : avisoDetails
        }

        return data