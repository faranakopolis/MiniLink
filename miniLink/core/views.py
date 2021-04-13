""" This module includes the Mini Link's views.

Here are the functions and general logic of the project.

"""

import time

from django.shortcuts import redirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from miniLink.core.serializers import *
from miniLink.redisDriver.utils import *

from miniLink.core.celery_tasks import store_guest_url_info


class SignUpView(APIView):
    """Add a user to the system (Sign Up):
        Doesn't requires token authentication i.e. every guest user is able to access this view.

    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "user successfully signed up."
            data['username'] = user.username
        else:
            data['response'] = serializer.errors

        return Response(data)


class LogoutView(APIView):
    """Log out from account:
        Requires token authentication.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            # Get the refresh token from the request and add it to the black list table.
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(data={"response": "token added to black list"},
                            status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response(data={"response": "token has been black listed already"})
        except Exception as e:
            return Response(data={"response": "something went wrong !"},
                            status=status.HTTP_400_BAD_REQUEST)


class RedirectView(APIView):
    """A hashed string will be given as the url parameter
        and by searching in the Redis db the original url will be found
        and the visitor will be redirect to it.

        This API doesn't require Token Authentication.
    """

    permission_classes = [AllowAny]

    def get(self, request, hashed_string=None):
        start = time.time()

        # Get the original URL from Redis and redirect the guest (visitor) to it.

        original_url = get_original_url("ml/" + hashed_string)
        response = redirect(original_url)

        # Get guest (visitor) info from get_guest_info function using user_agent and META data.
        # Then pass them to the save function.

        serializer = RedirectUrlSerializer()
        guest_url_info = {"hashed_url": "ml/" + hashed_string,
                          "guest": serializer.get_guest_info(request=request)}

        # This function will be running in the background using Celery.
        # So visitor will be redirected to the original URL ASAP.
        store_guest_url_info.delay(guest_url_info)
        print(time.time() - start)

        return response


class AnalyticsView(APIView):
    """Two parameters will be passed to this view's get method:
        - url_id: The URL analytics will be based on this id.
        - analytics_type:
                + The number of visits for each URL.
                + The number of individual visits for each URL.
        - visitor_params:
            + total
            + device: numbers based on visitor's device.
            + browser: numbers based on visitor's browser.
            (user can choose either filtering based on device or browser, not both
                although filtering based on both of them can also be implemented)
        - time_filter: specifies the time filter to get the reports based on it:
            + today (until now)
            + yesterday
            + last week
            + last month
        """
    permission_classes = [IsAuthenticated]

    def post(self, request, url_id):
        serializer = AnalyticsSerializer()
        result = serializer.get_analytics(request.data, url_id)

        return Response({"result": result})


class UrlView(APIView):
    """Use-cases:
       - Create a (short) URL by its owner.
       - Get all URLs that belongs to an owner. (not implemented yet)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UrlSerializer(data=request.data)
        data = {}

        if serializer.is_valid():

            if not serializer.validate_original_url(data=request.data):
                data['response'] = "Please enter a valid URL"
                return Response(data)

            # Pass the username to save as owner of the URL.
            url = serializer.save(username=request.user)
            data['response'] = "URL shortened successfully"
            data['hashed_url'] = url.hashed
        else:
            data['response'] = serializer.errors

        return Response(data)

    def get(self, request):
        """Get all the links created by user
        """
        return ""
