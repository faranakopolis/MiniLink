from miniLink.celery import app
from celery.utils.log import get_task_logger
from miniLink.core.models import *

logger = get_task_logger(__name__)


@app.task(name="store_guest_url_info_in_postgres")
def store_guest_url_info(guest_url_info):
    """Parsing the data and separating its different models
        to store in the tables below:
        - guest
        - guest_url
    """
    url = Url.objects.get(hashed=guest_url_info["hashed_url"])

    # Check if a visitor exists in the db or not
    guest = Guest.objects.filter(ip=guest_url_info["guest"]["ip"],
                                 os=guest_url_info["guest"]["os"],
                                 device=guest_url_info["guest"]["device"],
                                 browser=guest_url_info["guest"]["browser"])
    if guest.exists():
        # Just add data to the guest_url table
        gu = GuestUrl(url=url, guest=guest[0])
        gu.save()
    else:
        # This visitor(guest) is new, add it to its table too
        new_guest = Guest(ip=guest_url_info["guest"]["ip"],
                          os=guest_url_info["guest"]["os"],
                          device=guest_url_info["guest"]["device"],
                          browser=guest_url_info["guest"]["browser"])
        new_guest.save()
        gu = GuestUrl(url=url, guest=new_guest)
        gu.save()

    logger.info("guest_url_stored_in_db")
    return True
