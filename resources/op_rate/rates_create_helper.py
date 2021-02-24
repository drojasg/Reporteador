from resources.rateplan.rate_plan_helper import Rateplans_Helper as rpHelper
from models.rateplan_prices import RatePlanPrices as rtpModel
from resources.room_type_category.room_type_helper import Room_Type_Helper as rtcHelper
from models.category_type_pax import CategoryTypePax as ctpModel
from resources.property.propertyHelper import FilterProperty as prHelper
from common.utilities import Utilities as util
from config import db
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

class Process_Rate():
    rate_code = None
    rate_code_id = 0
    property_code = None
    property_id = 1
    room_code = None
    room_code_id = 0
    currency = "USD"
    max_ocupancy = 0
    update_rateplan = False
    include_kids = False
    __paxes = None
    rate_code_base = ""
    __query_base_insert = "insert into op_rateplan_prices (idproperty,idrateplan,idroom_type,\
    idpax_type,amount,date_start,date_end,estado,usuario_creacion,fecha_creacion,\
    usuario_ultima_modificacion,fecha_ultima_modificacion,is_override) values {qr};"
    __query_delete = "delete from op_rateplan_prices where idop_rateplan_prices in ({ids})"
    __price_extra = 0
    __adults_price = []
    __childs_price = []
    rate_extra = None
    __last_adult = {}
    __last_child = {}
    rtpdata = None
    __usuario = "Clever Layers"
    __values_insert = []
    __rates_id_delete = []
    Warnings = []
    Data_str = []
    Errors = []

    def __init__(self,rate_code,property_code,room_code,currency_code,include_kids,rate_code_base,max_ocupancy=0):
        self.max_ocupancy = max_ocupancy
        self.include_kids = include_kids
        self.validate_property(property_code)
        self.validate_room(room_code,self.property_id)
        self.validate_rateplan(rate_code,self.property_id,rate_code_base,idroom=self.room_code_id)

    def validate_property(self,code_property):
        prData = prHelper.getHotelInfo(self,code_property)
        self.property_id = prData.iddef_property
        self.property_code = code_property
    
    def validate_rateplan(self,rateplan_code,property,rate_base,idroom=None):

        rp_data = rpHelper.get_rateplan_info(self,rate_code=self.rate_code,\
        property_id=self.property_id,only_rateplan=True,validate_estado=False,roomid=idroom)
        self.rate_code = rateplan_code
        self.rate_code_base = rate_base
        currency_avail = self.validate_currency(rp_data.currency_code,self.currency)
        if currency_avail == False:
            raise Exception("Currency not avail")        
        self.update_rateplan = not self.valid_rate_code_base(rp_data.rate_code_base,\
        self.rate_code_base)
        self.rate_code_id = rp_data.idop_rateplan

    def set_category_pax(self,max_ocupancy):
        self.__paxes = ctpModel.query.filter(ctpModel.pax_number<=max_ocupancy,\
        ctpModel.estado==1).all()
    
    def validate_room(self,room,property):

        rtc_data = rtcHelper.get_room_type(self,idproperty=self.property_id,\
        room_type_code=self.room_code,property_name=self.property_code)

        self.room_code_id = rtc_data.iddef_room_type_category
        self.room_code = rtc_data.room_code
        self.max_ocupancy = rtc_data.max_ocupancy
        self.set_category_pax(self.max_ocupancy)

    def validate_currency(self,currency_rateplan,currency_request):
        return currency_rateplan.upper() == currency_request.upper()

    def valid_rate_code_base(self,rate_base_rq,rate_base_now):
        return rate_base_now.upper() == rate_base_rq.upper()

    def __get_pax_id_item(self,group="EXTRA",number_pax = 0):
        id = 0
        for pax_item in self.__paxes:
            if pax_item.group_pax.upper() == group.upper():
                if pax_item.pax_number == number_pax:
                    id = pax_item.iddef_category_type_pax
                    break
        return id
    
    def __set_price_extra(self,price):
        idpax_type = self.__get_pax_id_item(price["group_pax"],price["pax_number"])
        self.rate_extra = {
            "type":idpax_type,
            "amount":price["amount_final"],
            "pax_number":price["pax_number"]
        }

    def __set_price_adults(self,price):
        idpax_type = self.__get_pax_id_item(price["group_pax"],price["pax_number"])
        item_adult = {
            "type":idpax_type,
            "amount":price["amount_final"],
            "pax_number":price["pax_number"]
        }
        self.__adults_price.append(item_adult)
        return item_adult

    def __set_price_childs(self,price):
        idpax_type = self.__get_pax_id_item(price["group_pax"],price["pax_number"])
        item_child = {
            "type":idpax_type,
            "amount":price["amount_final"],
            "pax_number":price["pax_number"]
        }
        self.__childs_price.append(item_child)
        return item_child

    def __set_prices(self,price_list,date_start,date_end,include_childs=True):
        cont = 0
        cont_item = 0
        for price in price_list:
            try:
                if price["rate_exists"] == True:
                    if price["group_pax"].upper() == "EXTRA":
                        self.__set_price_extra(price)
                        self.__price_extra = self.rate_extra["amount"]
                    else:
                        cont_item += 1
                        if price["group_pax"].upper() == "CHILD" and include_childs == False:
                            continue

                        item_rate = None
                        rtpdata = rtpModel()
                        rtpdata.idproperty = self.property_id
                        rtpdata.idrateplan = self.rate_code_id
                        rtpdata.idroom_type = self.room_code_id
                        rtpdata.date_start = date_start
                        rtpdata.date_end = date_end
                        rtpdata.is_override = 0
                        rtpdata.estado = 1
                        rtpdata.fecha_creacion = datetime.today()
                        rtpdata.usuario_ultima_modificacion = ''
                        rtpdata.fecha_ultima_modificacion = datetime(1900,1,1,00,00,00)
                        rtpdata.usuario_creacion = self.__usuario
                        if price["group_pax"].upper() == "ADULT":
                            item_rate = self.__set_price_adults(price)
                            cont += 1
                        elif price["group_pax"].upper() == "CHILD":
                            item_rate = self.__set_price_childs(price)
                        if item_rate is not None:
                            rtpdata.amount = item_rate["amount"]
                            rtpdata.idpax_type = item_rate["type"]
                        str_info = "Tarifa {amount} del {date_start} al {date_end} para \
                        la habitacion {room} del rateplan {ratecode} {type_pax} {number_pax}"
                        self.__release_rates(rtpdata)
                        self.__values_insert.append(self.format_query_insert(rtpdata))
                        self.Data_str.append(str_info.format(amount=item_rate["amount"],\
                        date_start=date_start,date_end=date_end,room=self.room_code,\
                        ratecode=self.rate_code,type_pax=price["group_pax"].upper(),\
                        number_pax=price["pax_number"]))
            except Exception as item_rate_error:
                self.Errors.append(str(item_rate_error))

        self.__adults_price = util.sort_dict(self,self.__adults_price,key_sort="pax_number")
        self.__last_adult = self.__adults_price[0]
        
        if include_childs:
            self.__childs_price = util.sort_dict(self,self.__childs_price,key_sort="pax_number")
            self.__last_child = self.__childs_price[0]
    
        return cont
    
    def process_rate(self,price_list,date_start,date_end):
        cont_pax = 0
        try:
            cont_pax = self.__set_prices(price_list,date_start,date_end)
            while cont_pax < self.max_ocupancy:
                try:
                    cont_pax += 1
                    if self.rate_extra is not None:
                        amount = self.calculate_rate(cont_pax)
                        idpax = self.__get_pax_id_item("ADULT",cont_pax)
                        rtpdata = rtpModel()
                        rtpdata.idproperty = self.property_id
                        rtpdata.idrateplan = self.rate_code_id
                        rtpdata.idroom_type = self.room_code_id
                        rtpdata.date_start = date_start
                        rtpdata.date_end = date_end
                        rtpdata.is_override = 0
                        rtpdata.estado = 1
                        rtpdata.usuario_creacion = self.__usuario
                        rtpdata.amount = amount
                        rtpdata.idpax_type = idpax
                        rtpdata.fecha_creacion = datetime.today()
                        rtpdata.usuario_ultima_modificacion = ''
                        rtpdata.fecha_ultima_modificacion = datetime(1900,1,1,00,00,00)
                        str_info = "Tarifa {amount} del {date_start} al {date_end} para \
                        la habitacion {room} del rateplan {ratecode} {type_pax} {number_pax}"
                        self.__release_rates(rtpdata)
                        self.__values_insert.append(self.format_query_insert(rtpdata))
                        self.Data_str.append(str_info.format(amount=amount,date_start=date_start,\
                        date_end=date_end,room=self.room_code,ratecode=self.rate_code,\
                        type_pax="ADULT",number_pax=cont_pax))
                    else:
                        self.Warnings.append("Tarifa para pax extra no encontrado")
                except Exception as item_rate_error:
                    self.Errors.append(str(item_rate_error))
        except Exception as rate_error:
            self.Errors.append(str(rate_error))
    
    def __release_rates(self,rtpData):

        rtpAux = rtpModel.query.filter(rtpModel.estado == 1, \
        and_(or_
        (and_(rtpModel.date_start <= rtpData.date_start,\
        rtpModel.date_end >= rtpData.date_end),\
        and_(rtpModel.date_start >= rtpData.date_start,\
        rtpModel.date_end <= rtpData.date_end),
        and_(rtpModel.date_start <= rtpData.date_start,\
        rtpModel.date_end <= rtpData.date_end, rtpModel.date_end >= rtpData.date_start))),
        rtpModel.idpax_type == rtpData.idpax_type, \
        rtpModel.idproperty == rtpData.idproperty, \
        rtpModel.idrateplan == rtpData.idrateplan, \
        rtpModel.idroom_type == rtpData.idroom_type,
        rtpModel.is_override == 0).all()

        date_end_before = rtpData.date_start - timedelta(days=1)
        date_start_after = rtpData.date_end + timedelta(days=1)

        for item in rtpAux:
            str_info = "{estado} al crear las mover tarifas para {fecha_inicio} hasta {fecha_fin}"
            try:
                self.__rates_id_delete.append(str(item.idop_rateplan_prices))
            
                date_start = item.date_start
                date_end = item.date_end

                if date_start < rtpData.date_start and date_end > rtpData.date_end:

                    new_rtp_before = rtpModel()
                    new_rtp_before.is_override = 0
                    new_rtp_before.estado = 1
                    new_rtp_before.usuario_creacion = self.__usuario
                    new_rtp_before.date_start = date_start
                    new_rtp_before.idpax_type = rtpData.idpax_type
                    new_rtp_before.idproperty = rtpData.idproperty
                    new_rtp_before.idroom_type = rtpData.idroom_type
                    new_rtp_before.idrateplan = rtpData.idrateplan
                    new_rtp_before.amount = item.amount
                    new_rtp_before.date_end = date_end_before
                    new_rtp_before.fecha_creacion = datetime.today()
                    new_rtp_before.usuario_ultima_modificacion = ''
                    new_rtp_before.fecha_ultima_modificacion = datetime(1900,1,1,00,00,00)
                    self.__values_insert.append(self.format_query_insert(new_rtp_before))

                    new_rtp_after = rtpModel()
                    new_rtp_after.is_override = 0
                    new_rtp_after.estado = 1
                    new_rtp_after.usuario_creacion = self.__usuario
                    new_rtp_after.date_start = date_start_after
                    new_rtp_after.idpax_type = rtpData.idpax_type
                    new_rtp_after.idproperty = rtpData.idproperty
                    new_rtp_after.idroom_type = rtpData.idroom_type
                    new_rtp_after.idrateplan = rtpData.idrateplan
                    new_rtp_after.amount = item.amount
                    new_rtp_after.date_end = date_end
                    new_rtp_after.fecha_creacion = datetime.today()
                    new_rtp_after.usuario_ultima_modificacion = ''
                    new_rtp_after.fecha_ultima_modificacion = datetime(1900,1,1,00,00,00)
                    self.__values_insert.append(self.format_query_insert(new_rtp_after))

                elif date_end > rtpData.date_end and date_start >= rtpData.date_start:

                    new_rtp = rtpModel()
                    new_rtp.is_override = 0
                    new_rtp.estado = 1
                    new_rtp.usuario_creacion = self.__usuario
                    new_rtp.date_start = date_start_after
                    new_rtp.idpax_type = rtpData.idpax_type
                    new_rtp.idproperty = rtpData.idproperty
                    new_rtp.idroom_type = rtpData.idroom_type
                    new_rtp.idrateplan = rtpData.idrateplan
                    new_rtp.amount = item.amount
                    new_rtp.date_end = date_end
                    new_rtp.fecha_creacion = datetime.today()
                    new_rtp.usuario_ultima_modificacion = ''
                    new_rtp.fecha_ultima_modificacion = datetime(1900,1,1,00,00,00)
                    self.__values_insert.append(self.format_query_insert(new_rtp))
                
                elif date_start < rtpData.date_start and date_end <= rtpData.date_end:
                    #Creamos un registro para las fechas anteriores
                    new_rtp = rtpModel()
                    new_rtp.is_override = 0
                    new_rtp.estado = 1
                    new_rtp.usuario_creacion = self.__usuario
                    new_rtp.date_start = date_start
                    new_rtp.idpax_type = rtpData.idpax_type
                    new_rtp.idproperty = rtpData.idproperty
                    new_rtp.idroom_type = rtpData.idroom_type
                    new_rtp.idrateplan = rtpData.idrateplan
                    new_rtp.amount = item.amount
                    new_rtp.date_end = date_end_before
                    new_rtp.fecha_creacion = datetime.today()
                    new_rtp.usuario_ultima_modificacion = ''
                    new_rtp.fecha_ultima_modificacion = datetime(1900,1,1,00,00,00)
                    self.__values_insert.append(self.format_query_insert(new_rtp))

            except Exception as rate_item_error:
                self.Errors.append(str_info.format(estado="Error",\
                fecha_inicio=item.date_start,fecha_fin=item.date_end))

    def __delete_rates(self):
        if len(self.__rates_id_delete)>0:
            str_ids = ','.join(self.__rates_id_delete)
            final_query = self.__query_delete.format(ids=str_ids)
            data = db.session.execute(final_query)
            db.session.commit()
    
    def __update_ratecode(self):
        updated_rate_code, msg_rate_update = rpHelper.update_ratecode_rateplan(self,\
        self.rate_code_id,self.rate_code_base)

        if updated_rate_code == False:
            self.Warnings.append(msg_rate_update)
    
    def calculate_rate(self,number_pax):
        amount = 0
        
        last_amount = self.__last_adult["amount"]
        amount = last_amount + ((number_pax-len(self.__adults_price))*self.__price_extra)

        return amount
    
    def process(self,ratelist):
        for rate in ratelist:
            self.reset_fields()
            self.process_rate(rate["prices"],rate["date_from"],rate["date_to"])
        
        self.__delete_rates()
        self.create_rate()
        if self.update_rateplan:
            self.__update_ratecode()
               
    def create_rate(self):
        values = ','.join(self.__values_insert)
        final_query = self.__query_base_insert.format(qr=values)
        data = db.session.execute(final_query)
        db.session.commit()

    def format_query_insert(self,rtpdata):
        qr_str = '({rtp.idproperty},{rtp.idrateplan},{rtp.idroom_type},{rtp.idpax_type},\
        {rtp.amount},"{rtp.date_start}","{rtp.date_end}",{rtp.estado},\
        "{rtp.usuario_creacion}","{rtp.fecha_creacion:%Y-%m-%d %H:%M:%S}",\
        "{rtp.usuario_ultima_modificacion}","{rtp.fecha_ultima_modificacion}",\
        {rtp.is_override})'.format(rtp=rtpdata)

        return qr_str
    
    def reset_fields(self):
        self.rate_extra = {}
        self.__price_extra = 0
        self.__adults_price = []
        self.__childs_price = []
        self.__last_adult = {}
        self.__last_child = {}