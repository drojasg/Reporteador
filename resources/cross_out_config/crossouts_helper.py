from .cross_out_config import Model as cocModel, CRPModel, RPModel, crModel
from resources.restriction.restricctionHelper import RestricctionFunction as resFuntions
from resources.restriction.restriction_helper_v2 import Restrictions as resFuntions2
from common.utilities import Utilities
import datetime

class Crossout_Functions():
    def get_crossout_by_rateplan(self,idrateplan,date_start,date_end,market_id,country_code,\
        id_sistema=1,use_booking_window=True,only_crossout=True):
        data = None

        data_response_cross = []
        try:
            #Obtenemos los crosouts configurados
            data = cocModel.query.join(CRPModel,\
            CRPModel.iddef_crossout==cocModel.idop_cross_out_config).join(RPModel,\
            RPModel.idop_rateplan==CRPModel.iddef_rate_plan)\
            .filter(RPModel.id_sistema==id_sistema,\
            RPModel.idop_rateplan==idrateplan,CRPModel.estado==1).all()

            if only_crossout == False:

                for crossouts_data in data:
                    apply = False
                    cross_res = crModel.query.filter(crModel.idop_crossout==crossouts_data.idop_cross_out_config,\
                    crModel.estado==1).all()

                    apply_dates = []
                    for res_item in cross_res:
                        # restriction_details_apply = resFuntions.getRestrictionDetails(useBooking=use_booking_window,\
                        # travel_window_start=date_start.strftime("%Y-%m-%d"), \
                        # travel_window_end=date_end.strftime("%Y-%m-%d"),restriction_by=6,\
                        # restriction_type=4,market_targeting=market_id,\
                        # geo_targeting_country=country_code,\
                        # id_restriction=res_item.iddef_restriction)
                        obj = resFuntions2(useBooking=use_booking_window,\
                        travel_window_start=date_start.strftime("%Y-%m-%d"), \
                        travel_window_end=date_end.strftime("%Y-%m-%d"),restriction_by=6,\
                        restriction_type=4,market_targeting=market_id,\
                        geo_targeting_country=country_code,\
                        id_restriction=res_item.iddef_restriction)
                        restriction_details_apply = obj.get_restriction_details()

                        if len(restriction_details_apply) > 0:
                            apply = True
                            for item_rest in restriction_details_apply:
                                if item_rest["travel_window_option"] == '0':
                                    
                                    dates_aply = Utilities.format_dates_apply(self,date_start,date_end)
                                    for item_date in dates_aply:
                                        apply_dates.append(item_date)
                                    
                                elif item_rest["travel_window_option"] == '1':

                                    for item_res_date in item_rest["travel_window"]:
                                        aux_res_date_start = datetime.datetime.strftime(item_res_date["date_start"],"%Y-%m-%d")
                                        aux_res_date_end = datetime.datetime.strftime(item_res_date["date_end"],"%Y-%m-%d")
                                        if date_start >= aux_res_date_start and date_end <= aux_res_date_end:                                            
                                            dates_aply = Utilities.format_dates_apply(self,\
                                            aux_res_date_start,aux_res_date_end)
                                            for item_date in dates_aply:
                                                apply_dates.append(item_date)

                                elif item_rest["travel_window_option"]== '2':

                                    for item_res_date in item_rest["travel_window"]:
                                        dates_apply_aux = Utilities.format_dates_apply(self,\
                                        date_start,date_end)

                                        aux_res_date_start = datetime.datetime.strftime(item_res_date["date_start"],"%Y-%m-%d")
                                        aux_res_date_end = datetime.datetime.strftime(item_res_date["date_end"],"%Y-%m-%d")
                                        if date_start >= aux_res_date_start and date_end <= aux_res_date_end:                                            
                                            dates_aply = Utilities.format_dates_apply(self,\
                                            aux_res_date_start,aux_res_date_end)
                                            for item_date in dates_aply:
                                                if item_date not in dates_apply_aux:
                                                    apply_dates.append(item_date)

                        else:
                            pass

                    if apply == True:
                        crossouts_data.dates_apply = apply_dates
                        data_response_cross.append(crossouts_data)

            if len(data_response_cross) is None:
                raise Exception ("No se encontraron porcentajes para las fechas selecionadas")
        
        except Exception as coc_error:
            pass

        return data_response_cross