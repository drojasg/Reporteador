from config import api
from .report_cancelations import reportCancelations

api.add_resource(reportCancelations, '/api/reports/get-cancelation-report',endpoint="api-reports-get-cancelation-report", methods=["POST"])
