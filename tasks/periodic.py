from config import app,celery

celery.conf.beat_schedule = {
    "pms-testing": {
        "task": "tasks.pms.schedule_pms",
        "schedule": 15.0
    }
}

"""
#beat schedule
#celery -A tasks.periodic.celery beat --loglevel=info

#worker background
#celery worker -A tasks.pms.celery --pool=solo --loglevel=info

"""