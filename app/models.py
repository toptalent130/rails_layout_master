# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class TradeAccount(models.Model):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    class Meta:
      db_table = "TradeAccount"