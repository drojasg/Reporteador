from config import api
from .calendar import Calendar, CalendarV2, CalendarPrice, CalendarAvail, CalendarDisabled, CalendarMinLosMaxLos, CalendarUpdateMinMax

api.add_resource(Calendar, '/api/calendar/get-dates',endpoint="api-public-calendar-get", methods=["POST"])
api.add_resource(CalendarV2, '/api/v2/calendar/get-dates',endpoint="api-calendar-v2-get", methods=["POST"])

#Administrativas
api.add_resource(CalendarPrice, '/api/calendar/update',endpoint="api-calendar-update", methods=["POST"])
api.add_resource(CalendarAvail, '/api/calendar/get_avail_rooms',endpoint="api-calendar-get-avail", methods=["POST"])
api.add_resource(CalendarDisabled, '/api/calendar/disabled-room',endpoint="api-calendar-disabled-room", methods=["POST"])
api.add_resource(CalendarMinLosMaxLos, '/api/calendar/get-min-max',endpoint="api-calendar-min-max", methods=["POST"])
api.add_resource(CalendarUpdateMinMax, '/api/calendar/update-min-max',endpoint="api-calendar-update-min-max", methods=["POST"])