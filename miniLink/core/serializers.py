"""This module includes all the serializers
    that is needed to make the Views tasks easier and cleaner.

"""

import hashlib
import random
import string

import validators
from django.db import connection
from rest_framework import serializers

from miniLink.core.models import *

from miniLink.redisDriver.utils import *


class SignUpSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(default=datetime.datetime.now())

    def save(self, **kwargs):
        user = User(
            username=self.validated_data['username']
        )

        password = self.validated_data['password']
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'created_at')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class AnalyticsSerializer:
    """This class doesn't override any methods
        and it has been defined to make some task cleaner.
    """

    def get_start_end_time(self, time_filter):
        """Calculate the start and the end date-time
            based on the time_filter and return it
            to get analytics and filter data based on it.
        """
        # Set default value for start and end (time_filter=today)
        end = datetime.datetime.now()
        start = end.replace(year=end.year, month=end.month, day=end.day,
                            hour=0, minute=0, second=0)

        if time_filter == "yesterday":
            start = end.replace(year=end.year, month=end.month, day=end.day - 1,
                                hour=0, minute=0, second=0)
            end = end.replace(year=end.year, month=end.month, day=end.day - 1,
                              hour=23, minute=59, second=59)

        if time_filter == "last_week":
            start = end.replace(year=end.year, month=end.month, day=end.day - 7,
                                hour=0, minute=0, second=0)
            end = end.replace(year=end.year, month=end.month, day=end.day - 1,
                              hour=23, minute=59, second=59)

        if time_filter == "last_month":
            start = end.replace(year=end.year, month=end.month, day=end.day - 30,
                                hour=0, minute=0, second=0)
            end = end.replace(year=end.year, month=end.month, day=end.day - 1,
                              hour=23, minute=59, second=59)

        return start, end

    def get_analytics(self, params, url_id):
        result = 0

        start, end = self.get_start_end_time(params['time_filter'])

        if params['analytics_type'] == 'general':
            if params['visitor_type'] == "total":  # It's the "total" string
                result = GuestUrl.objects.filter(ur_id=url_id, created_at__range=[start, end]).count()
                return result

            if params['visitor_type'].startswith("d_"):  # It's based on the device

                device = params['visitor_type'][2:]
                guest_urls = GuestUrl.objects.filter(url_id=url_id, created_at__range=[start, end]).select_related()

                # Count the guests with specified device name
                for gu in guest_urls:
                    if device in gu.guest.device:
                        result += 1
                return result

            if params['visitor_type'].startswith("b_"):  # It's based on the browser
                browser = params['visitor_type'][2:]
                guest_urls = GuestUrl.objects.filter(url_id=url_id, created_at__range=[start, end]).select_related()

                # Counting guests with specified device name
                for gu in guest_urls:
                    if browser in gu.guest.browser:
                        result += 1

                return result

        if params['analytics_type'] == 'individual':
            if params['visitor_type'] == "total":  # It's the "total" string

                result = GuestUrl.objects.filter(ur_id=url_id, created_at__range=[start, end]).distinct().count()
                return result

            if params['visitor_type'].startswith("d_"):  # It's based on the device
                device = params['visitor_type'][2:]

                cursor = connection.cursor()
                cursor.execute(
                    'select COUNT(DISTINCT guest_id) '
                    'from guest_url join guest on guest_url.guest_id=guest.id '
                    'where url_id=%(url_id)s and guest.device=%(device)s'
                    'and guest_url.created_at between %(start)s and %(end)s',
                    params={'url_id': url_id,
                            'device': device,
                            'start': start,
                            'end': end})
                result = cursor.fetchone()
                return result[0]

            if params['visitor_type'].startswith("b_"):  # It's based on the browser
                browser = params['visitor_type'][2:]

                cursor = connection.cursor()
                cursor.execute(
                    'select COUNT(DISTINCT guest_id) '
                    'from guest_url join guest on guest_url.guest_id=guest.id '
                    'where url_id=%(url_id)s and guest.browser=%(browser)s'
                    'and guest_url.created_at between %(start)s and %(end)s',
                    params={'url_id': url_id,
                            'browser': browser,
                            'start': start,
                            'end': end})
                result = cursor.fetchone()
                return result[0]

        return result


class UrlSerializer(serializers.ModelSerializer):

    def hash_url(self, user_id, original_url):
        """This function hashes the original URL Using md5.
            To raise security and getting different short links from same URLs
             the hashed string consists:
                a random 5 character string +
                original URL +
                the user's id
        """
        mini_link_url = "ml/"
        random_string = ''.join(random.choices(string.ascii_uppercase +
                                               string.digits, k=5))
        # Mix them up
        mixed_string = random_string + original_url + str(user_id)

        result = hashlib.md5(mixed_string.encode())

        # Convert to hex
        hashed_url = mini_link_url + result.hexdigest()

        return hashed_url

    def validate_original_url(self, data):
        """Validate the original Link to be in a proper URL format.
        """

        if validators.url(data["original"]):
            return True
        else:
            return False

    def save(self, username):
        user = User.objects.get(username=username)
        hashed_url = self.hash_url(user.id, self.validated_data['original'])
        url = Url(
            original=self.validated_data['original'],
            hashed=hashed_url,
            user=user
        )

        url.save()

        # save "hashes : original" key-value to Redis
        save_url(hashed=hashed_url,
                 original=self.validated_data['original'])

        return url

    class Meta:
        model = Url
        fields = ('original',)


class RedirectUrlSerializer:

    def get_guest_info(self, request):
        guest_info = dict()

        # Get User IP using the request's META data
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        guest_info["ip"] = str(ip)

        guest_info["browser"] = str(request.user_agent.browser.family) + "_" + str(
            request.user_agent.browser.version_string)

        guest_info["os"] = str(request.user_agent.os.family) + "_" + str(
            request.user_agent.os.version_string)

        guest_info["device"] = str(request.user_agent.device.family) + "_" + str(
            request.user_agent.device.brand)
        return guest_info

