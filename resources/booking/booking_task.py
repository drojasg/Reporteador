from flask import current_app

class BookingTask():
    @staticmethod
    def interface_pms():
        try:
            res = current_app.celery.send_task('tasks.pms.interface_pms',args=["opera test", "description test"])
        except Exception as e:
            current_app.logger.error("Celery Task SQS Error: "+ str(e))


    @staticmethod
    def interface_booking(idbook_hotel):
        try:
            current_app.celery.send_task('tasks.pms.interface_booking',args=[idbook_hotel])
        except Exception as e:
            current_app.logger.error("Celery Task SQS Error: "+ str(e))

    @staticmethod
    def send_notification(idbook_hotel, usuario):
        try:
            current_app.celery.send_task('tasks.pms.send_notification_async', args=[idbook_hotel, usuario])
        except Exception as e:
            current_app.logger.error("Celery Task SQS Error: "+ str(e))
