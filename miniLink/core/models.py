""" This module includes the Mini Link's models
    based on the database design

The names of class's attributes may differ
    from column names in the related table in database
"""

import datetime

from django.contrib.auth.models import User, AbstractUser, AbstractBaseUser

from django.db import models


# class MyUser(AbstractUser):
#     created_at = models.DateTimeField(default=datetime.datetime.now())
#
#     DATE_JOINED_FIELD = 'created_at'


class Url(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="url_owner", on_delete=models.DO_NOTHING, null=False)
    original = models.CharField(max_length=500, null=False)
    hashed = models.CharField(max_length=30, null=False)
    expires_at = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "url"


class Guest(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=45, null=False)
    device = models.CharField(max_length=30, null=False)
    browser = models.CharField(max_length=30, null=False)
    os = models.CharField(max_length=30, null=False)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "guest"


class GuestUrl(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.ForeignKey(Url, related_name="the_url", on_delete=models.DO_NOTHING, null=False)
    guest = models.ForeignKey(Guest, related_name="url_visitor", on_delete=models.DO_NOTHING, null=False)
    created_at = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        db_table = "guest_url"
