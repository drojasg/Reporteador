from config import api
from .repors import ReportsListSearch
from .report_daily_sales_by_market import ReportDailySalesByMarketExcell, ReportDailySalesByMarketPDF, ReportDailySalesByMarketApi
from .report_daily_sales_detailed import ReportDailySalesDetailedExcell, ReportDailySalesDetailedPDF,ReportDailySalesDetailedApi
from .report_daily_cancelations_consolidated import ReportDailyCancelationConsolidatedExcell, ReportDailyCancelationConsolidatedPDF, ReportDailyCancelationConsolidatedApi
from .report_daily_reservations_list import ReportDailyReservationListExcell, ReportDailyReservationListPDF, ReportDailyReservationListApi
from .report_consolidated_sales_by_room_category import ReportSalesByRoomCategoryExcell, ReportSalesByRoomCategoryPDF, ReportSalesByRoomCategoryApi 
from .report_daily_cancelations_list import ReportDailyCancelationListExcell, ReportDailyCancelationListApi, ReportDailyCancelationListPDF
from .report_booking_on_hold_consolidated import ReportOnHoldConsolidatedExcell, ReportOnHoldConsolidatedPDF, ReportOnHoldConsolidatedApi
from .report_promotion_consolidated import ReportPromotionConsolidatedExcell, ReportPromotionConsolidatedPDF, ReportPromotionConsolidatedApi
from .report_consolidated_daily_sales import ReportConsolidatedDailySalesExcell, ReportConsolidatedDailySalesPDF, ReportConsolidatedDailySalesApi

#urls apis basicas
api.add_resource(ReportsListSearch, '/api/reports/get',endpoint="api-reports-get-all", methods=["GET"])

#Consolidado Venta Diaria por Mercado ó rango de fechas especificada
api.add_resource(ReportDailySalesByMarketExcell, '/api/reports/get-daily-sales-by-market-date-report-excell',endpoint="api-reports-get-daily-sales-by-market-date-report-excell", methods=["POST"])
api.add_resource(ReportDailySalesByMarketPDF, '/api/reports/get-daily-sales-by-market-date-report-pdf',endpoint="api-reports-get-daily-sales-by-market-report-date-pdf", methods=["POST"])
api.add_resource(ReportDailySalesByMarketApi, '/api/reports/get-daily-sales-by-market-date-report-api',endpoint="api-reports-get-daily-sales-by-market-report-date-api", methods=["POST"])

#Cada mercado subcontiene las propiedades que conformaron la venta, asi mismo el canal(detallado)
api.add_resource(ReportDailySalesDetailedExcell, '/api/reports/get-daily-sales-detailed-report-excell',endpoint="api-reports-get-daily-sales-detailed-report-excell", methods=["POST"])
api.add_resource(ReportDailySalesDetailedPDF, '/api/reports/get-daily-sales-detailed-report-pdf',endpoint="api-reports-get-daily-sales-detailed-report-pdf", methods=["POST"])
api.add_resource(ReportDailySalesDetailedApi, '/api/reports/get-daily-sales-detailed-report-api',endpoint="api-reports-get-daily-sales-detailed-report-api", methods=["POST"])

#CONSOLIDADO CANCELACIONES DIARIAS Ó EN RANGO DE FECHAS ESPECIFICADAS#
api.add_resource(ReportDailyCancelationConsolidatedExcell, '/api/reports/get-daily-cancelations-consolidated-excell',endpoint="api-reports-get-daily-cancelations-consolidated-excell", methods=["POST"])
api.add_resource(ReportDailyCancelationConsolidatedPDF, '/api/reports/get-daily-cancelations-consolidated-pdf',endpoint="api-reports-get-daily-cancelations-consolidated-pdf", methods=["POST"])
api.add_resource(ReportDailyCancelationConsolidatedApi, '/api/reports/get-daily-cancelations-consolidated-api',endpoint="api-reports-get-daily-cancelations-consolidated-api", methods=["POST"])

#CONSOLIDADO DE VENTA POR CATEGORIA DE HABITACION
api.add_resource(ReportSalesByRoomCategoryExcell, '/api/reports/get-sales-by-room-category-excell',endpoint="api-reports-get-sales-by-room-category-excell", methods=["POST"])
api.add_resource(ReportSalesByRoomCategoryPDF, '/api/reports/get-sales-by-room-category-pdf',endpoint="api-reports-get-sales-by-room-category-pdf", methods=["POST"])
api.add_resource(ReportSalesByRoomCategoryApi, '/api/reports/get-sales-by-room-category-api',endpoint="api-reports-get-sales-by-room-category-api", methods=["POST"])

#LISTADO DE RESERVACIONES DIARIAS Ó RANGOS DE FECHAS DETERMINADOS     
api.add_resource(ReportDailyReservationListExcell, '/api/reports/daily_reservations_list-excell',endpoint="api-reports-daily_reservations_list-excell", methods=["POST"])
api.add_resource(ReportDailyReservationListPDF, '/api/reports/daily_reservations_list-pdf',endpoint="api-reports-daily_reservations_list-pdf", methods=["POST"])
api.add_resource(ReportDailyReservationListApi, '/api/reports/daily_reservations_list-api',endpoint="api-reports-daily_reservations_list-api", methods=["POST"])

#LISTADO DE CANCELACIONES DIARIAS Ó RANGOS DE FECHAS DETERMINADOS  
api.add_resource(ReportDailyCancelationListExcell, '/api/reports/daily_cancelations_list-excell',endpoint="api-reports-daily_cancelations_list-excell", methods=["POST"])
api.add_resource(ReportDailyCancelationListPDF, '/api/reports/daily_cancelations_list-pdf',endpoint="api-reports-daily_cancelations_list-pdf", methods=["POST"])
api.add_resource(ReportDailyCancelationListApi, '/api/reports/daily_cancelations_list-api',endpoint="api-reports-daily_cancelations_list-api", methods=["POST"])

#BOOKINGS ONHOLD, CONSOLIDADO   
api.add_resource(ReportOnHoldConsolidatedExcell, '/api/reports/booking_on_hold_consolidated-excell',endpoint="api-reports-booking_on_hold_consolidated-excell", methods=["POST"])
api.add_resource(ReportOnHoldConsolidatedPDF, '/api/reports/booking_on_hold_consolidated-pdf',endpoint="api-reports-booking_on_hold_consolidated-pdf", methods=["POST"])
api.add_resource(ReportOnHoldConsolidatedApi, '/api/reports/booking_on_hold_consolidated-api',endpoint="api-reports-booking_on_hold_consolidated-api", methods=["POST"])

#CONSOLIDADO DE PROMOCODES
api.add_resource(ReportPromotionConsolidatedExcell, '/api/reports/promotion_consolidated-excell',endpoint="api-reports-promotion_consolidated-excell", methods=["POST"])
api.add_resource(ReportPromotionConsolidatedPDF, '/api/reports/promotion_consolidated-pdf',endpoint="api-reports-promotion_consolidated-pdf", methods=["POST"])
api.add_resource(ReportPromotionConsolidatedApi, '/api/reports/promotion_consolidated-api',endpoint="api-reports-promotion_consolidated-api", methods=["POST"])

#Consolidado Venta Diaria por Hotel
api.add_resource(ReportConsolidatedDailySalesExcell, '/api/reports/consolidated-daily-sales-excell',endpoint="api-reports-consolidated-daily-sales-excell", methods=["POST"])
api.add_resource(ReportConsolidatedDailySalesPDF, '/api/reports/consolidated-daily-sales-pdf',endpoint="api-reports-consolidated-daily-sales-pdf", methods=["POST"])
api.add_resource(ReportConsolidatedDailySalesApi, '/api/reports/consolidated-daily-sales-api',endpoint="api-reports-consolidated-daily-sales-api", methods=["POST"])