# -------------------------------------------------------------------
#                    MODELS.PY
# -------------------------------------------------------------------
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth.models import User 

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from star_ratings.models import AbstractBaseRating, Rating
from django.utils.text import slugify
from django.utils import timezone









