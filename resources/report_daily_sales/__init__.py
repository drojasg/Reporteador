from config import api
from .report_daily_sales import reportDailySales

api.add_resource(reportDailySales, '/api/reports/get-daily-sales-report',endpoint="api-reports-get-daily-sales-report", methods=["POST"])
