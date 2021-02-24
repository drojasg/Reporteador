from sqlalchemy import or_, and_, func
import datetime
import copy
from models.rateplan import RatePlan as rpModel
from models.property import Property as prModel
from models.category_type_pax import CategoryTypePax as ctpModel
from models.room_type_category import RoomTypeCategory as rtcModel
from common.utilities import Utilities as utilFuntions
from models.rateplan_prices import RatePlanPrices as rtpModel
from resources.age_code.age_code_helper import age_helper as agcFuntions
from resources.exchange_rate.exchange_rate_service import ExchangeRateService as funtionsExchange
from resources.text_lang.textlangHelper import Filter as txtFunctions
from resources.market_segment.marketHelper import Market as mkfuntion
from resources.cross_out_config.crossouts_helper import Crossout_Functions as crsFuntions
from resources.policy.policyHelper import PolicyFunctions as pfuntions
from resources.promotions.promotionsHelper_v2 import FilterPublic as promotionsFuntions
from resources.promo_code.promocodeHelper import PromoCodeFunctions as vhFunctions
class Promotions():
    rates = None
    rates_copy = None
    promotions = []
    market_info = None
    currency_code = "USD"
    country_code = "US"
    lang_code = "EN"
    today = datetime.datetime.now().date()
    date_start = today + datetime.timedelta(days=15)
    date_end = today + datetime.timedelta(days=20)
    hotel_id = 0
    hotel_code = None
    market_id = 0
    only_one = False
    __valid_free_rooms = False
    promo_free_apply = False
    generate_free_room = False
    tax_apply = []
    crossouts = []
    all_in_one = False
    rateplan_info = []
    room_info = []
    book_total = 0
    promocode = None
    promocode_applied = False
    promocode_is_txt = False
    promocode_txt = ""
    total_discount_promotion = 0
    total_discount_vaucher = 0

    def __init__(self,rates,currency,country,market,lang_code,\
        date_start,date_end,paxes=None,allinone=False,valid2x1=False):

        if rates is None:
            raise Exception("Rates can't be null")

        if isinstance(rates,list):
            self.rates = utilFuntions.sort_dict(self,rates,key_sort="total")
            self.rates_copy = copy.deepcopy(self.rates)
            self.only_one = False
        else:
            rates_aux = []
            rates_aux.append(rates)
            self.rates = utilFuntions.sort_dict(self,rates_aux,key_sort="total")
            self.rates_copy = copy.deepcopy(self.rates)
            self.only_one = True

        if len(rates)>0:
            self.__set_general_items(currency,country,market,lang_code,\
            self.rates[0]["property"],date_start,date_end,paxes,allinone)
        else:
            raise Exception("Rates can't be null")

        self.__valid_free_rooms = valid2x1
        self.promotions = Search.get_promotions(self,self.date_start,self.date_end,\
        self.country_code,self.hotel_code,self.lang_code,rateplan_info=self.rateplan_info,\
        room_info=self.room_info)
        

    def __set_general_items(self,currency,country,market,lang_code,hotel,date_start,\
        date_end,paxes,allinone):

        self.currency_code = currency
        self.market_id = market
        self.country_code = country
        self.lang_code = lang_code
        self.hotel_id = hotel
        self.date_start = date_start
        self.date_end = date_end
        self.tax_apply = []
        self.all_in_one = allinone
        self.rateplan_info = []
        self.room_info = []

        hotel_info = prModel.query.get(self.hotel_id)
        if hotel_info is not None:
            self.hotel_code = hotel_info.property_code

        if self.all_in_one == True:
            for item in self.rates:

                #Set information of crossouts
                crossout_aux = Search.get_crossout_info(self,item["rateplan"],self.date_start,\
                self.date_end,self.market_id,self.country_code)

                self.crossouts.append(crossout_aux)
                
                #Set informacion de politicas tax
                tax_aux = Search.get_polici_tax(self,self.date_start,\
                self.date_end,item["rateplan"])
                
                self.tax_apply.append(tax_aux)

                #set informacion de rateplan
                self.rateplan_info.append(item["rateplan"])
                #set informacion de room
                self.room_info.append(item["room"])

                self.book_total += item["total"]

    #Aplica promociones
    def apply_promotions(self):
        if self.promotions is not None:

            if len(self.promotions)<=0:
                #Si no se encontraron promociones validas
                self.__apply_rate_up()
            
            for promotion in self.promotions:
                aux_rates = copy.deepcopy(self.rates_copy)

                avail_room_rates_promotion = promotion["rates_rooms_avail"]
                avail_dates_promotion = promotion["apply_dates"]
                idpromotion = promotion["idop_promotions"]
                codepromotion = promotion["code"]
                percent_cross_out = promotion["percent_cross_out"]
                
                for discount in promotion["free"]:
                    #Aplicamos las promociones 2x1
                    if discount["type"] == 3:
                        if self.__valid_free_rooms:
                            self.promo_free_apply = True
                        #Unicamente si hay mas de 1 habitacion
                        #if len(self.rates)>1:
                        aux_rates = self.__apply_free_rooms_promotion(discount,avail_dates_promotion,\
                        avail_room_rates_promotion,idpromotion,codepromotion,aux_rates\
                        ,percent_crossout=percent_cross_out)
                    #Aplicamos las noches gratis
                    if discount["type"] == 2:
                        aux_rates = self.__apply_free_night_promotion(discount,avail_dates_promotion,\
                        avail_room_rates_promotion,idpromotion,codepromotion,aux_rates,\
                        percent_crossout=percent_cross_out)
                    #Aplicamos el descuento de menores
                    if discount["type"]== 1:
                        #obtenemos los pax para la propiedad
                        property_pax = agcFuntions.get_age_codes_property_valid(self,\
                        self.hotel_id,discount["min"])

                        age_codes = [item.code for item in property_pax]
                        
                        aux_rates = self.__apply_free_childs_promotion(discount,\
                        age_codes,avail_dates_promotion,\
                        avail_room_rates_promotion,idpromotion,codepromotion,aux_rates,\
                        percent_crossout=percent_cross_out)

                #Aplicamos el porcentaje de descuento
                if promotion["per_discount"]>0.0:
                    aux_rates = self.__apply_percent_discount(promotion["per_discount"],\
                    avail_dates_promotion,avail_room_rates_promotion,idpromotion,\
                    codepromotion,aux_rates,percent_crossout=percent_cross_out)

                #Aplicamos el descuento absoluto/monto
                if promotion["abs_discount"]>0.0:
                    aux_rates = self.__apply_abs_discount(promotion["abs_discount"],\
                    avail_dates_promotion,avail_room_rates_promotion,idpromotion,\
                    codepromotion,aux_rates,percent_crossout=percent_cross_out)

                selected = self.__compare_rates(aux_rates)
                
                if promotion["timer_config"]["timer"]==1 and selected == True:
                    self.__verifi_timer(promotion["timer_config"],\
                    avail_dates_promotion,avail_room_rates_promotion)

                if self.promo_free_apply:
                    self.__verifi_promotion2x1(avail_room_rates_promotion)

            #End For, se compara con el anterior
            quote = Quotes()
            quote.get_total_list(self.rates)

            if self.all_in_one == True:
                self.tax_update_room(self.rates)

        return Functions.get_response(self,self.rates,self.only_one)

    def __apply_rate_up(self):
        total_room = len(self.rates)
        i = 0
        for item in self.rates:
            j = 0
            if self.all_in_one == True:
                policy = Search.get_policy_rateplan(self,item["rateplan"],self.tax_apply)
            for rate in item["price_per_day"]:    
                if self.all_in_one == True:
                    #aplicamos los tax
                    if policy is not None:
                        self.tax_update_item(policy,i,j,(item["adults"]+item["minors"]),total_room)
                    #aplicamos los crossouts
                    self.__apply_crossout(i,j)
                j += 1
            i += 1
    
    def __verifi_promotion2x1(self,avail_rooms):
        for item in self.rates:
            avail = Validates.validate_room_promotion(self,item,avail_rooms)
            if avail:
                item["promo_free_apply"] = True

    #Verifica si la promocion tiene una configuracion de timer
    def __verifi_timer(self,timer_config,avail_dates_promotion,avail_rates_room):
        for rate in self.rates:
            room_apply = Validates.validate_room_promotion(self,rate,avail_rates_room)
            if room_apply == True:
                if avail_dates_promotion["dates_booking"] != "1900-01-01":
                    
                    date_apply_str = avail_dates_promotion["dates_booking"]+" "+avail_dates_promotion["times_booking"]+":00"
                    date_end_bookin = datetime.datetime.strptime(date_apply_str,"%Y-%m-%d %H:%M:%S")
                    
                    date_offset_str = str(timer_config["days_offset"])+" "+timer_config["time_offset"]
                    date_offset = datetime.datetime.strptime(date_offset_str,"%d %H:%M:%S")
                    
                    date_offset_1 = datetime.timedelta(days = date_offset.day, \
                    hours = date_offset.hour, minutes = date_offset.minute, \
                    seconds = date_offset.second)
                    
                    date_now = datetime.datetime.now()
                    dif_date = date_end_bookin - date_now

                    if dif_date <= date_offset_1:
                        rate["timer_on"] = True
                        rate["date_end_promotion"] = date_end_bookin
    
    #Cuartos gratis
    def __apply_free_rooms_promotion(self,discount_detail,avail_dates_promotion,\
        avail_rates_room,promotionid,promotioncode,rates_aux,percent_crossout=0):
        
        try:
            pivot = discount_detail["max"]
            pivot_free = discount_detail["min"]
            apply_once = discount_detail["value"]
            rooms_cont = 0
            apply_discount = False
            free_room_count = 0

            cont_room = 0
            position_room = 0
            for rooms_rates in rates_aux:
                room_avail = Validates.validate_room_promotion(self,rooms_rates,avail_rates_room)

                #Si la habitacion es aplicable a la promocion 2x1, se coloca la bandera
                rooms_rates["apply_room_free"] = room_avail

                #if room_apply == True:
                #price_day = len(price["price_per_day"])
                if apply_discount == True:
                    room_apply = Validates.validate_room_promotion(self,self.rates[cont_room],\
                    avail_rates_room)

                    if room_apply == True:
                        self.generate_free_room = False
                        #data["generate_free_room"] = False
                        #prices[cont_room]["total_crossout"]=prices[cont_room]["total"]
                        self.rates[cont_room]["total"]=0.00
                        #prices[cont_room]["apply_room_free"] = True
                        #prices[cont_room]["total_percent_discount"]=100
                        for price_nigth in self.rates[cont_room]["price_per_day"]:
                            #price_nigth["amount_crossout"]=price_nigth["amount"]
                            total_promotion_discount += price_nigth["amount"]
                            promo_detail = {
                                "id_promotion":promotionid,
                                "code":promotioncode,
                                "value_discount":price_nigth["amount"],
                                "crossout":percent_crossout
                            }
                            price_nigth["promotions"] = promo_detail
                            price_nigth["promotion_amount"] = price_nigth["amount"]
                            price_nigth["amount"]=0.00
                            price_nigth["amount_to_pms"]=price_nigth["amount"]
                            #price_nigth["percent_discount"]=100

                        free_room_count += 1
                        if free_room_count >= pivot_free:
                            if apply_once == False:
                                apply_discount = False
                            else:
                                break

                    cont_room += 1
                else:
                    room_apply = Validates.validate_room_promotion(self,self.rates[cont_room],\
                    avail_rates_room)

                    if room_apply == True:            
                        rooms_cont +=1
                        #prices[cont_room]["apply_room_free"] = True
                        if rooms_cont >= pivot:
                            apply_discount = True
                            rooms_cont = 0 
                            free_room_count = 0
                    else:
                        cont_room += 1

            if free_room_count % 2 == 0:
                self.generate_free_room = True

        except Exception as promotion_error:
            pass

        return rates_aux

    #Noches gratis
    def __apply_free_night_promotion(self,discount_detail,avail_dates_promotion,\
        avail_rates_room,promotionid,promotioncode,rates_aux,percent_crossout=0):
        total_discount = 0
        
        try:
            pivot = discount_detail["max"]
            pivot_free = discount_detail["min"]
            apply_once = discount_detail["value"]

            for room in rates_aux:
                room_apply = Validates.validate_room_promotion(self,room,avail_rates_room)

                if room_apply == True:
                    nigths_cont = 0
                    apply_discount = False
                    free_nights_count = 0
                    price_discount = 0
                    for price_nigth in room["price_per_day"]:
                        date_str = datetime.datetime.strftime(price_nigth["efective_date"],"%Y-%m-%d")
                        if date_str in avail_dates_promotion["dates_travel"]:

                            if apply_discount == True:
                                #price_nigth["amount_crossout"]=price_nigth["amount"]
                                price_discount += price_nigth["amount"]
                                price_nigth["amount"]=0.00
                                price_nigth["amount_to_pms"] = price_nigth["amount"]
                                #total_promotion_discount += price_nigth["amount"]
                                promo_detail = {
                                    "id_promotion":promotionid,
                                    "code":promotioncode,
                                    "value_discount":price_nigth["amount"],
                                    "crossout":percent_crossout
                                }
                                price_nigth["promotions"] = promo_detail
                                price_nigth["promotion_amount"] = price_nigth["amount"]
                                #price_nigth["percent_discount"]=100
                                free_nights_count += 1
                                if free_nights_count >= pivot_free:
                                    if apply_once == 1:
                                        apply_discount = False
                                    else:
                                        break
                            else:
                                nigths_cont +=1
                                if nigths_cont >= pivot:
                                    apply_discount = True
                                    nigths_cont = 0 
                                    free_nights_count = 0

                    #room["total"] = room["total"]-price_discount
        except Exception as error:
            pass

        return rates_aux

    #Menores gratis
    def __apply_free_childs_promotion(self,discount_detail,property_pax_avail,\
        avail_dates_promotion,avail_rates_room,promotionid,promotioncode,rates_aux,percent_crossout=0):
        total_discount = 0
        try:
            pivot_free = discount_detail["max"]
            property_pax = property_pax_avail #Obtener lista de pax disponibles para la propiedad
            for room in rates_aux:

                room_aply = Validates.validate_room_promotion(self,room,avail_rates_room)

                if room_aply == True:
                    apply_minors = 0
                    
                    #Validar si la habitacion incluye menores
                    apply = Validates.validate_apply_menors_promotion(self,property_pax,\
                    room["paxes"],pivot=discount_detail["min"])
                    
                    price_discount = 0
                    if apply == True:
                        #obtenemos la informacion de la habitacion
                        room_detail = rtcModel.query.get(room["room"])
                        if room_detail.acept_chd == 1 and room["minors"]>=1:
                            while apply_minors < pivot_free and apply_minors < room["minors"]:
                                discount_applied = 0
                                for price_night in room["price_per_day"]:
                                    if price_night["amount"] > 0:
                                        date_str = datetime.datetime.strftime(price_night["efective_date"],\
                                        "%Y-%m-%d")
                                        if date_str in avail_dates_promotion["dates_travel"]:

                                            #obtenemos el precio de los menores
                                            child_data = Search.get_price(self,\
                                            self.hotel_id,room["rateplan"],room["room"],1,\
                                            price_night["efective_date"],\
                                            price_night["efective_date"])

                                            if len(child_data) >= 1:
                                                discount_applied = child_data[0].amount
                                                price_night["amount"] -= child_data[0].amount
                                                price_night["amount"] = round(price_night["amount"],0)
                                                price_night["amount_to_pms"] = price_night["amount"]
                                                total_promotion_discount += discount_applied
                                                promo_detail = {
                                                    "id_promotion":promotionid,
                                                    "code":promotioncode,
                                                    "value_discount":discount_applied,
                                                    "crossout":percent_crossout
                                                }
                                                price_night["promotions"] = promo_detail
                                                price_night["promotion_amount"] = discount_applied
                                apply_minors += 1
                                price_discount += discount_applied
        except Exception as error:
            pass

        return rates_aux

    #Descuento porcentajes
    def __apply_percent_discount(self,discount_percent_value,\
        avail_dates_promotion,avail_rates_room,promotionid,promotioncode,rates_aux,percent_crossout=0):

        total_promotion_discount = 0
        
        try:
            for room in rates_aux:
                dif_total = 0
                for price_item in room["price_per_day"]:
                    date_str = datetime.datetime.strftime(price_item["efective_date"],"%Y-%m-%d")
                    if date_str in avail_dates_promotion["dates_travel"]:
                        if price_item["amount"]>0:
                            aux = price_item["amount"]
                            price_discount=price_item["amount"]-(price_item["amount"]*discount_percent_value)
                            price_item["amount"]=round(price_discount,0)
                            price_item["amount_to_pms"] = price_item["amount"]
                            dif = aux - price_item["amount"]
                            total_promotion_discount += dif
                            promo_detail = {
                                "id_promotion":promotionid,
                                "code":promotioncode,
                                "value_discount":dif,
                                "crossout":percent_crossout
                            }
                            price_item["promotion_amount"] = dif
                            price_item["promotions"] = promo_detail
                            dif_total += dif
        except Exception as percent_eror:
            pass

        return rates_aux

    #Descuento montos
    def __apply_abs_discount(self,discount_abs_value,\
        avail_dates_promotion,avail_rates_room,promotionid,promotioncode,rates_aux,percent_crossout=0):

        try:
            for room in rates_aux:
                for price_item in room["price_per_day"]:
                    date_str = datetime.datetime.strftime(price_item["efective_date"],"%Y-%m-%d")
                    if date_str in avail_dates_promotion["dates_travel"]:
                        #price_item["amount_crossout"] += round(price_item["amount"],2)
                        if price_item["amount"]>0:
                            total_promotion_discount += discount_abs_value
                            promo_detail = {
                                "id_promotion":promotionid,
                                "code":promotioncode,
                                "value_discount":discount_abs_value,
                                "crossout":percent_crossout
                            }
                            price_item["promotion_amount"] = discount_abs_value
                            price_item["promotions"] = promo_detail
                            price_item["amount"]=round(price_item["total"]-discount_abs_value,0)
                            price_item["amount_to_pms"] = price_item["amount"]
        except Exception as amount_error:
            pass

        return rates_aux

    #Actualiza las tarifas
    def __compare_rates(self,rate_promotion):
        promo_selected = False
        total_room = len(rate_promotion)
        i = 0
        for item in rate_promotion:
            j = 0
            if self.all_in_one == True:
                policy = Search.get_policy_rateplan(self,item["rateplan"],self.tax_apply)
            for rate in item["price_per_day"]:
                if rate["amount"] <= self.rates[i]["price_per_day"][j]["amount"]:
                    self.rates[i]["price_per_day"][j]["amount"] = rate["amount"]
                    self.rates[i]["price_per_day"][j]["amount_to_pms"] = rate["amount_to_pms"]
                    crossout_promotion = 0
                    if rate["promotions"] is not None:
                        self.rates[i]["price_per_day"][j]["promotions"] = rate["promotions"]
                        self.rates[i]["price_per_day"][j]["promotion_amount"] = rate["promotion_amount"]
                        crossout_promotion = self.rates[i]["price_per_day"][j]["promotions"]["crossout"]
                    promo_selected = True
                    
                    if self.all_in_one == True:
                        #aplicamos los tax
                        if policy is not None:
                            self.tax_update_item(policy,i,j,(item["adults"]+item["minors"]),total_room)
                        #aplicamos los crossouts
                        self.__apply_crossout(i,j,promotion_crossout=crossout_promotion)
                j += 1
            i += 1

        return promo_selected

    #Aplica impuestos de politicas
    def apply_taxes(self):
        response = self.rates

        try:
            aux_rate = rtfuntions.get_price_with_policy_tax(self.date_start,\
            self.date_end,self.currency_code,self.rates)

            self.rates = aux_rate["data"]
            
        except Exception as tax_error:
            pass
        
        if self.only_one == True:
            if len(self.rates)>=1:
                response = self.rates[0]

        return response

    def __apply_crossout(self,item_rate,item_night,promotion_crossout=0):
        idrateplan = self.rates[item_rate]["rateplan"]
        efective_date = self.rates[item_rate]["price_per_day"][item_night]["efective_date"]
        value = self.rates[item_rate]["price_per_day"][item_night]["amount"]
        #promotion_crossout = self.rates[item_rate]["price_per_day"][item_night]["promotions"]["crossouts"]
        
        if promotion_crossout is not None:
            if promotion_crossout > 0:
                crossout_percent = promotion_crossout
            else:
                crossout_percent = Search.get_crossout_in_date(self,\
                idrateplan,self.crossouts,efective_date)
        else:
            crossout_percent = Search.get_crossout_in_date(self,\
            idrateplan,self.crossouts,efective_date)

        amount_crossout = Quotes.get_rate_crossout(self,crossout_percent,amount=value)

        self.rates[item_rate]["price_per_day"][item_night]["amount_crossout"] = amount_crossout
        self.rates[item_rate]["price_per_day"][item_night]["percent_discount"] = crossout_percent

    #Aplica vauchers
    def apply_promocode(self,promocode="",validate_2x1=True):

        if promocode != "":
            if validate_2x1 == True:
                avail_promo2x1 = Validates.valid_promocode_2x1(self,promocode)
                if avail_promo2x1 == True:
                    try:
                        self.promocode = Search.get_promocode_detail(self,promocode,\
                        self.hotel_code,self.date_start,self.date_end,self.rateplan_info,\
                        self.room_info,self.market_id,self.country_code,self.lang_code,\
                        amount=self.book_total)
                    except Exception as promocode_error:
                        pass
            else:
                try:
                    self.promocode = Search.get_promocode_detail(self,promocode,\
                    self.hotel_code,self.date_start,self.date_end,self.rateplan_info,\
                    self.room_info,self.market_id,self.country_code,self.lang_code,\
                    amount=self.book_total)
                except Exception as promocode_error:
                    pass

        if self.promocode is not None:
            quotes = Quotes()

            vaucher = self.promocode
            if vaucher["text_only"]== True:
                self.promocode_is_txt = True
                self.promocode_txt = vaucher["text"]
                self.promocode_applied = True

                for price in self.rates:
                    self.promocode_applied = True

            else:
                vaucher_value = quotes.currency_convert(self.currency_code,\
                vaucher["currency"],vaucher["abs_value"])

                total_rooms = len(self.rates)
                avail_room = 0
                total_after = 0
                item_rate = 0
                for price in self.rates:
                    #Validamos si la habitacion es aplicable
                    valid_room = Validates.validate_room_promocode(self,price["property"],\
                    price["rateplan"],price["room"],vaucher["rateplans"])

                    if valid_room == True:
                        if vaucher["type_amount"] == 1:
                            #Descuento por estancia, el valor se divide entre el total
                            #de habitaciones y por dia, solo si todas las habitaciones
                            #son validas para este codigo de promocion
                            avail_room += 1
                        elif vaucher["type_amount"] == 2:
                            #Descuento por habitacion, el valor se divide entre todos los
                            #dias, solo si todos los dias son validos para este codigo
                            #de promocion
                            avail_dates = self.__apply_promocode_per_day(0,\
                            vaucher["valid_dates"],item_rate,only_dates=True)

                            total_dates = len(price["price_per_day"])
                            if avail_dates == total_dates:
                                
                                if vaucher_value > price["total"]:
                                    vaucher_value = price["total"]

                                price["total"] -= vaucher_value
                                discount_value = quotes.get_amount_to_discount_day(vaucher["type_amount"],\
                                total_dates,price["total"])

                                self.__apply_promocode_per_day(discount_value,\
                                vaucher["valid_dates"],item_rate,only_pms=True)

                                total_after += price["total"]

                        elif vaucher["type_amount"] == 3:
                            #El descuento se aplica por noche

                            #Obtenemos el valor a aplicar
                            value = quotes.get_amount_to_discount_day(vaucher["type_amount"],\
                            0,vaucher_value)

                            #Aplicamos los descuentos
                            self.__apply_promocode_per_day(value,\
                            vaucher["valid_dates"],item_rate)

                            totales = quotes.get_total_one(price)
                            total_after += totales["total"]

                        elif vaucher["type_amount"] == 4:
                            #Aplican los descuentos de porcentaje por noche
                            
                            #Aplicamos los descuentos
                            self.__apply_promocode_per_day(vaucher["per_value"],\
                            vaucher["valid_dates"],item_rate,percent=True)

                            totales = quotes.get_total_one(price)
                            total_after += totales["total"]

                    item_rate += 1
                
                if vaucher["type_amount"] == 1 and avail_room == total_rooms:
                    
                    value_room = quotes.get_amount_to_discount_day(vaucher["type_amount"],\
                    total_rooms,vaucher_value)

                    item = 0
                    for price in self.rates:
                        item += 1
                        if price["total"] > value_room:
                            value_room = price["total"]
                        price["total"] = round(price["total"]-value_room,0)
                        total_after += price["total"]

                        value = quotes.get_amount_to_discount_day(vaucher["type_amount"],\
                        len(price["price_per_day"]),price["total"])

                        self.__apply_promocode_per_day(value,vaucher["valid_dates"],\
                        item,only_pms=True)

            # if vaucher["type"] == 2:
            quotes.get_total_list(self.rates,to_pms=True)

        return Functions.get_response(self,self.rates,self.only_one)

    #Aplica los descuentos de los promocodes por dia
    def __apply_promocode_per_day(self,vaucher_per_day,vaucher_dates,room,\
        only_pms=False,percent=False,only_dates=False):
        dates_avail = 0
        vaucher_discount_aux = vaucher_per_day
        for price_item in self.rates[room]["price_per_day"]:

            date_str = utilFuntions.get_valid_dates_str(self,price_item["efective_date"])
            valid_date = Validates.validte_dates_promocodes(self,vaucher_dates,date_str)

            if percent == True:
                vaucher_per_day = Quotes.get_amount_to_discount_day(self,4,\
                price_item["amount"],vaucher_discount_aux)
            
            if valid_date == True:
                if only_dates == True:
                    dates_avail += 1
                else:
                    if vaucher_per_day > price_item["amount"]:
                        vaucher_per_day = price_item["amount"]
                    if only_pms == True:
                        price_item["vaucher_discount"] = round(price_item["amount"] - vaucher_per_day,2)
                        price_item["amount_to_pms"] = round(vaucher_per_day,2)
                        self.total_discount_vaucher += price_item["vaucher_discount"] 
                        self.promocode_applied = True
                    else:
                        price_item["amount"] = round(price_item["amount"] - vaucher_per_day,0)
                        price_item["amount_to_pms"] = round(price_item["amount"],2)
                        price_item["vaucher_discount"] = vaucher_per_day
                        self.promocode_applied = True
                        self.total_discount_vaucher += price_item["vaucher_discount"]

        return dates_avail
    
    def tax_update_item(self,policy,item_rate,item_day,pax,room):
        if policy["type"] == 3 or policy["type"] == 4:
            pass
        else:
            efective_date = self.rates[item_rate]["price_per_day"][item_day]["efective_date"]
            amount_aux = self.rates[item_rate]["price_per_day"][item_day]["amount"]
            apply_date = Validates.validate_apply_dates_ranges_tax(self,efective_date,\
            efective_date,policy["apply_dates"],policy["dates"])
            apply_maximun = Validates.validate_apply_maximun_tax(self,policy["apply_max"],amount_aux,policy["max_amount"])
            if apply_date and apply_maximun:
                amount_tax = self.convert_amount_tax(policy["value"],policy["tax_currency"],amount_aux,self.currency_code) if policy["type"] != 2 else policy["value"]
                amount_tax = self.value_policy_tax(policy["type"],amount_tax,amount_aux,pax,room)
                self.tax_update(item_rate,item_day,policy["type"],amount_tax,amount_aux)
    
    def tax_update_room(self, rates):
        total_room = len(rates)
        i = 0
        for item in rates:
            j = 0
            info_tax = Search.get_policy_rateplan(self,item["rateplan"],self.tax_apply)
            if info_tax is not None:
                if info_tax["type"] == 3 or info_tax["type"] == 4:
                    apply_date = Validates.validate_apply_dates_ranges_tax(self,self.date_start,self.date_end,\
                    info_tax["apply_dates"],info_tax["dates"])
                    apply_maximun = Validates.validate_apply_maximun_tax(self,info_tax["apply_max"],\
                    item["total"],info_tax["max_amount"])
                    if apply_date and apply_maximun:
                        amount_tax = self.convert_amount_tax(info_tax["value"],info_tax["tax_currency"],item["total"],self.currency_code) if info_tax["type"] != 2 else info_tax["value"]
                        amount_tax = self.value_policy_tax(info_tax["type"],amount_tax,item["total"],(item["adults"]+item["minors"]),total_room)
                        self.rates[i]["total_tax"] = amount_tax
                        self.rates[i]["total"] = self.apply_policy_tax(amount_tax,item["total"])
                        amount_tax_aux = round((amount_tax/(self.date_end - self.date_start).days),0)
            for rate in item["price_per_day"]:
                if info_tax is not None:
                    if info_tax["type"] == 3 or info_tax["type"] == 4:
                        amount_aux = self.rates[i]["price_per_day"][j]["amount"]
                        if apply_date and apply_maximun:
                            self.tax_update(i,j,info_tax["type"],amount_tax_aux,amount_aux)
                j += 1
            i += 1
    
    #obtenemos valor tax_amount
    def convert_amount_tax(self,amount_tax,tax_currency,amount,currency):
        #Obtenemos los datos de tipo de cambio
        exange_apply, to_usd_amount, exange_amount, exange_amount_tag = Search.get_currency_rate(self,currency,tax_currency)
        if exange_apply == True:
            #Primero convertimos a dolares
            amount_tax = round(amount_tax / to_usd_amount,2)
            #De dolares convertimos al tipo de cambio solicitado
            amount_tax = round(amount_tax * exange_amount,2)

        return amount_tax

    def tax_update(self,item_rate,item_day,type,amount_tax,amount_aux):
        if type == 3 or type == 4:
            self.rates[item_rate]["price_per_day"][item_day]["amount_to_pms"] = self.apply_policy_tax(amount_tax,amount_aux)
        else:
            self.rates[item_rate]["price_per_day"][item_day]["tax_amount"] = amount_tax
            self.rates[item_rate]["price_per_day"][item_day]["amount"] = self.apply_policy_tax(amount_tax,amount_aux)
            self.rates[item_rate]["price_per_day"][item_day]["amount_to_pms"] = self.rates[item_rate]["price_per_day"][item_day]["amount"]
    
    #get validate policy_tax
    def value_policy_tax(self,type,amount_tax,amount,pax,room):
        if type == 1:
            return round((pax * amount_tax),0)
        elif type == 2:
            return round(((amount * amount_tax) / 100),0)
        elif type == 3:
            return round((amount_tax),0)
        elif type == 4:
            return round((pax * amount_tax),0)
        elif type == 5:
            return round((room * amount_tax),0)

    #Aplicamos policy tax
    def apply_policy_tax(self,amount_tax,amount):

        amount = round(amount + amount_tax,0)

        return amount

class Quotes():

    def currency_convert(self,currency_select,currency_vaucher,value_vaucher):
        to_usd_amount = 1
        exange_amount = 1
        currency_vaucher = currency_vaucher.upper()
        currency_select = currency_select.upper()
        date_now = datetime.datetime.today().date()

        try:
            if currency_vaucher != currency_select:
                Exange_apply = True
                if currency_vaucher != "USD":
                    exangeDataMx = funtionsExchange.get_exchange_rate_date(date_now,currency_vaucher)
                    to_usd_amount = round(exangeDataMx.amount,2)

                if currency_select != "USD":
                    exangeData = funtionsExchange.get_exchange_rate_date(date_now,currency_select)
                    exange_amount = round(exangeData.amount,2)
                
            if Exange_apply == True:
                value_vaucher = round(value_vaucher / to_usd_amount,2)
                value_vaucher = round(value_vaucher * exange_amount,2)

        except Exception as error:
            pass

        return value_vaucher

    def get_amount_to_discount_day(self,type_vaucher,items_div,value):
        total = 0
        
        if type_vaucher == 1:
            total = value/items_div
        elif type_vaucher == 2:
            total = value/items_div
        elif type_vaucher == 3:
            total = value
        elif type_vaucher == 4:
            total = round(items_div*(value/100),2)

        return total

    def get_rate_crossout(self,percent_discount,amount=0):

        if percent_discount == 0:
            amount_final = 0
        else:
            percent_dif = 100 - percent_discount

            amount_final = (amount * 100) / percent_dif

        return round(amount_final,0)

    def get_percent(self,amount,amout_discount):

        if amout_discount == 0:        
            percent_total = 0
        else: 
            percent_apply = (amount * 100) / amout_discount
            percent_total = 100 - percent_apply

        return int(round(percent_total))

    #Calcula el total de la habitacion y su respectiva sumatoria
    def get_total_one(self,price,key="price_per_day",to_pms=False):
        data={
            "total":0.00,
            "subtotal":0.00
        }
        
        new_total = 0
        new_total_crossout = 0
        for price_night in price[key]:
            if to_pms == True:
                new_total += price_night["amount_to_pms"]
            else:
                new_total += price_night["amount"]
            new_total_crossout += price_night["amount_crossout"]
        
        price["total"] = round(new_total,0)
        price["total_crossout"] = round(new_total_crossout,0)

        data["total"]= round(price["total"],0)
        data["subtotal"]= round(price["total_crossout"],0)

        return data

    #Calcula el total de todas las habitaciones
    def get_total_list(self,price_list,to_pms=False):
        data={
            "total":0.00,
            "subtotal":0.00
        }
        
        total = 0.00
        subtotal = 0.00
        quote = Quotes()
        for price in price_list:
            new_total = 0
            new_total_crossout = 0
            for price_night in price["price_per_day"]:
                if to_pms == True:
                    new_total += price_night["amount_to_pms"]
                else:
                    new_total += price_night["amount"]
                new_total_crossout += price_night["amount_crossout"]
            
            price["total"] = round(new_total,0)
            price["total_crossout"] = round(new_total_crossout,0)

            if to_pms == False:
                price["total_percent_discount"] = quote.get_percent(price["total"],price["total_crossout"])
                price["avg_total"] = quote.get_avg(price["total"],price["nights"])
                price["avg_total_discount"] = quote.get_avg(price["total_crossout"],price["nights"])

            total += price["total"]
            subtotal += price["total_crossout"]

        data["total"]= round(total,0)
        data["subtotal"]= round(subtotal,0)

        return data

    #Obtiene el promedio de un conjunto de datos
    def get_avg(self,amount,divisor):
        avg = 0

        avg = int(round(float(amount/divisor),0))

        return avg

class Validates():

    def valid_promocode_2x1(self,promocode):
        valid_promocode = False
        
        try:
            if promocode != "":
                promocode_str = promocode.split("_")
                if len(promocode_str) >= 2:
                    if promocode_str[1] == "FREE2X1":
                        valid_promocode = True
        except Exception as str_error:
            pass
        
        return valid_promocode


    def validte_dates_promocodes(self,vaucher_dates,date):
        valid_date = False

        if date in vaucher_dates:
            valid_date = True

        return valid_date

    def validate_room_promocode(self,property_id,rateplan,room,vaucher_rateplan_info):
        valid_room = False

        for rateplan_vaucher in vaucher_rateplan_info:
            if property_id == rateplan_vaucher["id_property"]:
                if rateplan == rateplan_vaucher["id_rateplan"]:
                    if room in rateplan_vaucher["id_rooms"]:
                        valid_room = True
                        break

        return valid_room

    #Valida fechas cerradas
    def _validate_close_dates(self,close_dates,id_rateplan):
        avail_room = True 
        
        if len(close_dates) >= 1:
            for close in close_dates:
                if close["id_rateplan"] == id_rateplan:
                    for close_detail in close["dates"]:
                        if close_detail["close"] == True:
                            avail_room = False
                            break

        return avail_room

    #Valida max of stay
    def _validate_max_los(self,max_los,id_rateplan,lenght_stay):
        avail_room = True
        
        if len(max_los) > 0:
            for max_detail in max_los:
                if max_detail["id_rateplan"] == id_rateplan:
                    if max_detail["dates"][0]["max_los"] != 0:
                        if lenght_stay > max_detail["dates"][0]["max_los"]:
                            avail_room = False
                            break

        return avail_room

    #Valida min of stay
    def _validate_min_los(self,min_los,id_rateplan,lenght_stay):
        avail_room = True
        
        if len(min_los) > 0:
            for min_detail in min_los:
                if min_detail["id_rateplan"] == id_rateplan:
                    if min_detail["dates"][0]["min_los"] != 0:
                        if lenght_stay < min_detail["dates"][0]["min_los"]:
                            avail_room = False
                            break

        return avail_room

    #Valida restricciones de opera
    def validate_room_rates(self,id_rateplan,date_start,date_end,close_dates,min_los,max_los):
        avail_room = True

        if avail_room == True:
            avail_room = self._validate_close_dates(close_dates,id_rateplan)

        total_lenght = None
        if total_lenght is None:
            total_lenght = date_end-date_start
        
        if avail_room == True:
            avail_room = self._validate_max_los(max_los,id_rateplan,total_lenght.days)

        if avail_room == True:
            avail_room = self._validate_min_los(min_los,id_rateplan,total_lenght.days)

        return avail_room

    #Valida la compatibilidad con las promociones
    def validate_room_promotion(self,room,room_rates_avail):
        apply_room = False

        for item in room_rates_avail:
            if room["rateplan"] == item["rateplan"]:
                if room["room"] in item["rooms"]:
                    apply_room = True
                    break

        return apply_room

    #Valida si las promociones se aplican para la reserva
    def validate_apply_menors_promotion(self,pax_property,pax_room,pivot=None):
        apply=False
        try:
            # if isinstance(pax_property,list)==False:
            #     raise Exception("Lista de pax necesaria")
            if isinstance(pivot,int) == False:
                raise Exception("Id pax necesario")

            if pivot != 0:
                if len(pax_property) >= 1:
                    if pax_room is not None:
                        for paxes in pax_room.keys():
                            if paxes in pax_property:
                                if pax_room[paxes] >= 1:
                                    apply = True
                                    break
            elif pivot == 0:
                apply = True

        except Exception as error:
            pass
        
        return apply
    
    #valida si la fecha aplica para el rango
    def validate_apply_dates_ranges_tax(self,start,end,\
    apply_dates,dates):
        band_apply = False
        try:
            if apply_dates is True:
                if isinstance(start,datetime.date):
                    start = start.strftime("%Y-%m-%d")
                if isinstance(end,datetime.date):
                    end = end.strftime("%Y-%m-%d")
                band_apply = any(start >= y["start_date"] and end <= y["end_date"] for y in dates)
            else:
                band_apply = True

        except Exception as error:
            pass
        
        return band_apply
    
    #valida si aplica el maximo de tax
    def validate_apply_maximun_tax(self,apply_max,\
    amount,max_tax):
        band_max = False
        try:
            if apply_max is True:
                band_max = True if amount <= max_tax else False
            else:
                band_max = True

        except Exception as error:
            pass
        
        return band_max

class Search():

    def get_promocode_detail(self,promocode,hotel_code,date_start, date_end,list_rateplan,\
        list_room,idmarket,country_code,lang_code,amount=0):
        
        data = vhFunctions.getValidatePromoCode(promocode,property_code=hotel_code,\
        travel_window_start=date_start,travel_window_end=date_end,rateplans=list_rateplan,\
        rooms=list_room,market=idmarket,country=country_code,\
        min_booking_amount=amount,max_booking_amount=amount)

        return data

    #Obtiene informacion de las politicas
    def get_polici_tax(self,date_start,date_end,rateplan):
        data = {
            "rateplan":rateplan,
            "tax":None
        }
        if isinstance(date_start,datetime.date):
            date_start = date_start.strftime("%Y-%m-%d")
        if isinstance(date_end,datetime.date):
            date_end = date_end.strftime("%Y-%m-%d")
        tax = pfuntions.getPolicyTaxes(rateplan,date_start,\
        date_end, isFormat=True)
        if len(tax) > 0:
            data["tax"]=tax
        
        return data

    def get_crossout_in_date(self,rateplan,crossout_list,date):
        value = 0
        for cross_item in crossout_list:
            if cross_item["rateplan"] == rateplan:
                for item in cross_item["crossout_data"]:
                    if date in item.dates_apply:
                    #if date >= item.date_start and date <= item.date_end:
                    #if item.date_start <= date and item.date_end >= date:
                        value = item.percent
                        return value
        return value

    #Obtiene la informacion de las promociones
    def get_promotions(self,date_start,date_end,country_code,hotel_code,lang_code,\
        room_info=None,rateplan_info=None,rateplan=None,room=None):
        data = []
        
        if rateplan is not None and room is not None:
            data = promotionsFuntions.get_promotions_by_booking(self,date_start=date_start,\
            date_end=date_end,market=country_code,hotel=hotel_code,\
            include_free_room=True,list_room=room,list_rateplan=rateplan)
            # data = rtfuntions.get_promotions_by_booking(date_start=date_start,\
            # date_end=date_end,market=country_code,hotel=hotel_code,\
            # lang_code=lang_code,include_free_room=True,id_room=room,id_rateplan=rateplan)
        elif room_info is not None and rateplan_info is not None:
            data = promotionsFuntions.get_promotions_by_booking(self,date_start=date_start,\
            date_end=date_end,market=country_code,hotel=hotel_code,\
            include_free_room=True,list_room=room_info, list_rateplan=rateplan_info)
            # data = rtfuntions.get_promotions_by_booking(date_start=date_start,\
            # date_end=date_end,market=country_code,hotel=hotel_code,\
            # lang_code=lang_code,include_free_room=True,total_rooms=room_info)

        return data

    #Obtiene los crossouts
    def get_crossout_info(self,idrateplan,date_start,date_end,idmarket,country):
        
        data = crsFuntions.get_crossout_by_rateplan(self,idrateplan,date_start,\
        date_end,idmarket,country,only_crossout=False)

        item_rate = {
            "rateplan":idrateplan,
            "crossout_data":data
        }

        return item_rate

    #Obtiene las tarifas por dia para la reserva
    def get_price_per_day(self,propertyid,roomid,rateplanid,checkin_date,checkout_date,\
        adult=0, child=0, currency=None, market=None, country=None,paxes=None,apply_crossout=False,\
        show_cero=False):

        if paxes is not None:
            #Obtenemos los paxes
            adults, childs = self.get_paxes(propertyid,paxes)
        else:
            adults = adult
            childs = child

        adt_aux = adults
        chd_aux = childs
        #Single Parent Policy v1
        # rtcData = rtcModel.query.get(roomid)
        # if childs >=1:
        #     if rtcData.acept_chd == 1:
        #         while adults < rtcData.single_parent_policy and childs > 0:
        #             adults += 1
        #             childs -= 1

        #Obtenemos la informacion base del rateplan
        data_rateplan =  rpModel.query.get(rateplanid)
        currency_rateplan = data_rateplan.currency_code
        currency_rateplan = currency_rateplan.upper()
        
        #Obtenemos los datos de tipo de cambio
        exange_apply, to_usd_amount, exange_amount, exange_amount_tag = self.get_currency_rate(currency,currency_rateplan)

        idadults = self.get_idpax_type(adults)
        idchilds = 1

        checkin_date = utilFuntions.get_valid_dates(self,checkin_date)
        checkout_date = utilFuntions.get_valid_dates(self,checkout_date)
        
        price_per_day = []
        nigths = checkout_date - checkin_date
        adults_prices = []
        childs_prices = []

        adults_prices = self.get_price(propertyid,rateplanid,roomid,\
        idadults,checkin_date,checkout_date,overrides=False)

        if childs > 0:
            childs_prices = self.get_price(propertyid,rateplanid,roomid,\
            idchilds,checkin_date,checkout_date,overrides=False)

        price_per_day = self._set_price_adults(adults_prices,nigths.days,checkin_date,\
        checkout_date,exange_apply,to_usd_amount=to_usd_amount,exange_amount=exange_amount)

        if childs > 0:
            price_per_day = self._set_price_childs(adults,childs,price_per_day,childs_prices,\
            exange_apply,propertyid,roomid,rateplanid,to_usd_amount=to_usd_amount,\
            exange_amount=exange_amount)
        
        data = {
            "apply_room_free":False,
            "property":propertyid,
            "room":roomid,
            "rateplan":rateplanid,
            "paxes":paxes,
            "adults":adt_aux,
            "minors":chd_aux,
            "nights":nigths.days,
            "timer_on":False,
            "vaucher_applied":False,
            "date_end_promotion": datetime.datetime(1990,1,1,00,00,00),
            "total": 0.00,
            "total_crossout": 0,
            "exange_amount":exange_amount_tag,
            "price_per_day":price_per_day,
            "total_percent_discount":0
        }

        totales = Quotes.get_total_one(self,data)
        data["total"] = totales["total"]

        return data

    def apply_single_parent_policy(self,adults,childs,child_amount,\
        propertyid,roomid,rateplanid,date):
        amount = child_amount

        date = utilFuntions.get_valid_dates(self,date)

        # Igualamos los pax a la base de adultos
        # Single Parent Policy v2
        rtcData = rtcModel.query.get(roomid)
        if childs >=1:
            if rtcData.acept_chd == 1:
                while adults < rtcData.single_parent_policy and childs > 0:
                    adults += 1
                    childs -= 1

        idadults = self.get_idpax_type(adults)

        #Obtenemos las tarifas para adultos
        adults_prices = self.get_price(propertyid,rateplanid,roomid,\
        idadults,date,date,overrides=False)

        for rate in adults_prices:
            if date >= rate.date_start and date <= rate.date_end:
                amount = rate.amount
                break

        return amount + (child_amount * childs)
        
    
    #Setea los precios por dia de adultos
    def _set_price_adults(self,adults_prices,lenght_days,checkin_date,checkout_date,\
        exange_apply,to_usd_amount=1,exange_amount=1):
        
        price_per_day = []
        count = 0
        efective_date = checkin_date

        while count < lenght_days:
            for rate in adults_prices:
                if efective_date >= rate.date_start and efective_date <= rate.date_end:
                    amount = rate.amount

                    if exange_apply == True:
                        #Primero convertimos a dolares
                        amount = round(amount / to_usd_amount,2)

                        #De dolares convertimos al tipo de cambio solicitado
                        amount = round(amount * exange_amount,2)
                    
                    price_detail = {
                        "night":(count+1),
                        "amount": round(amount,0),
                        "amount_crossout": 0.0,
                        "percent_discount": 0,
                        "efective_date": efective_date,
                        "promotions":None,
                        "amount_to_pms":round(amount,0),
                        "promotion_amount": 0.0,
                        "tax_amount": 0.0,
                        "vaucher_discount":0.0
                    }

                    price_per_day.append(price_detail)
                    break

            count += 1
            efective_date = efective_date + datetime.timedelta(days=1)

        if len(price_per_day) < lenght_days:
            raise Exception("No all dates get rates")

        return price_per_day
    
    #Setea los precion por dia de los menores
    def _set_price_childs(self,pax_adults,pax_child,price_per_day,childs_prices,exange_apply,\
    propertyid,roomid,rateplanid,to_usd_amount=1,exange_amount=1):
        
        for day in price_per_day:
            for chd_pr in childs_prices:
                if chd_pr.date_start <= day["efective_date"] \
                and chd_pr.date_end >= day["efective_date"]:
                    apply_spp = False

                    amount = chd_pr.amount

                    if amount > 0:
                        apply_spp = True
                        amount = self.apply_single_parent_policy(pax_adults,pax_child,amount,\
                        propertyid,roomid,rateplanid,day["efective_date"])

                    #Si se necesita hacer alguna conversion
                    if exange_apply == True:
                        #Primero convertimos a dolares
                        amount = round(amount / to_usd_amount,2)

                        #De dolares convertimos al tipo de cambio solicitado
                        amount = round(amount * exange_amount,2)
                    
                    if apply_spp:
                        day["amount"] = amount
                    else:
                        day["amount"] += amount * pax_child
                    day["amount"] = round(day["amount"],0)
                    day["amount_to_pms"] += amount
                    day["amount_to_pms"] = round(day["amount_to_pms"],0)

                    break

        return price_per_day
    
    #Obtiene las tarifas segun el rango de fechas
    def get_price(self,property_id,rate_plan_id,room_type_id,pax_type_id,date_start,\
    date_end,overrides=True):

        if overrides is True:
            data = rtpModel.query.filter(and_(rtpModel.idproperty==property_id, \
            rtpModel.idrateplan==rate_plan_id, \
            rtpModel.idroom_type==room_type_id, \
            rtpModel.is_override == 1,\
            rtpModel.idpax_type==pax_type_id, rtpModel.estado==1, \
            or_(and_(rtpModel.date_start<=date_start, rtpModel.date_end>=date_end),\
            or_(rtpModel.date_start.between(date_start, date_end), \
            rtpModel.date_end.between(date_start, date_end))))).all()
        else:
            data = rtpModel.query.filter(and_(rtpModel.idproperty==property_id, \
            rtpModel.idrateplan==rate_plan_id, \
            rtpModel.idroom_type==room_type_id, \
            rtpModel.idpax_type==pax_type_id, rtpModel.estado==1, \
            or_(and_(rtpModel.date_start<=date_start, rtpModel.date_end>=date_end),\
            or_(rtpModel.date_start.between(date_start, date_end), \
            rtpModel.date_end.between(date_start, date_end))))).all()

        data = sorted(data, key = lambda x: (x.date_start, x.date_end))
        
        if data is None:
            raise Exception ("No se encontraron tarifas para las fechas selecionadas")

        return data

    #Se obtiene el id segun los pax
    def get_idpax_type(self,count):
        idType = 0
        
        ctpData = ctpModel.query.filter(ctpModel.estado==1,\
        ctpModel.pax_number==count, ctpModel.group_pax=="ADULT").first()
        
        if ctpData is not None:
            idType = ctpData.iddef_category_type_pax
        
        return idType
    
    #Obtiene las variables para la conversion
    def get_currency_rate(self,currency,currency_rateplan):
        exange_apply = False
        to_usd_amount = 1
        exange_amount = 1
        exange_amount_tag = 1

        date_today =  datetime.datetime.today()

        if currency is None:
            #utilizamos el currency por defecto
            currency = currency_rateplan

        currency = currency.upper()

        if currency != currency_rateplan:
            exange_apply = True
            #Si el tipo de cambio del rate plan esta en pesos y se solicita en un tipo de cambio
            #diferente a dolares, es necesario convertir de pesos a dolares primero
            #Y despues de dolares al tipo de cambio solicitado
            if currency_rateplan != "USD":
                #Siempre vamos a converir a dolares primero
                exangeDataMx = funtionsExchange.get_exchange_rate_date(date_today,currency_rateplan)
                to_usd_amount = round(exangeDataMx.amount,2)

            if currency != "USD":
                exangeData = funtionsExchange.get_exchange_rate_date(date_today,currency)
                exange_amount = round(exangeData.amount,2)
        
        if currency == "MXN":
            exangeaux = funtionsExchange.get_exchange_rate_date(date_today,"MXN")
            exange_amount_tag = round(exangeaux.amount,2)
        else:
            exange_amount_tag = exange_amount

        return exange_apply, to_usd_amount, exange_amount, exange_amount_tag

    #Obtiene la cantidad de pax segun los datos de una reserva
    def get_paxes(self,propertyId,pax_room):
        adults = 0
        childs = 0

        if pax_room is not None:
            age_code = agcFuntions.get_age_code_avail_by_property(self,propertyId)

            for paxes in pax_room.keys():
                if paxes in age_code:
                    if paxes.lower() == "adults":
                        adults += pax_room[paxes]
                    elif paxes.lower() != "infants":
                        childs += pax_room[paxes]

        return adults, childs
    
    def get_policy_rateplan(self,rateplan,data_list):
        
        data_policy = list(filter(lambda elem_r: elem_r["rateplan"] == rateplan, data_list))
        policy = data_policy[0]["tax"]
        
        return policy

class Functions():

    def get_response(self,item,only_one):
        response = item
        
        if only_one == True:
            if len(item)>=1:
                response = item[0]

        return response