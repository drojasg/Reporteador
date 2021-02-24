from config import api
from .reports_setting import ReportSettingFilter, ReportsSettingStatus, ReportsSettingListSearch, ReportSetting

#urls apis basicas
api.add_resource(ReportSetting, '/api/reports-setting/create',endpoint="api-reports-setting-post", methods=["POST"])
api.add_resource(ReportSetting, '/api/reports-setting/search/<int:id>',endpoint="api-reports-setting-get-by-id", methods=["GET"])
api.add_resource(ReportSetting, '/api/reports-setting/update/<int:id>',endpoint="api-reports-setting-put", methods=["PUT"])
api.add_resource(ReportsSettingStatus, '/api/reports-setting/delete/<int:id>/<int:status>',endpoint="api-reports-setting-delete", methods=["PUT"])
api.add_resource(ReportSettingFilter, '/api/reports-setting/filter/get',endpoint="api-reports-setting-filter-get-all", methods=["GET"])
api.add_resource(ReportsSettingListSearch, '/api/reports-setting/get',endpoint="api-reports-setting-get-all", methods=["GET"])