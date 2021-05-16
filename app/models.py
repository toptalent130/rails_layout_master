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
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
      db_table = "TradeAccount"
class UserTradeAccount(models.Model):
    user_id = models.IntegerField(
        null=False
    )
    trade_account_id = models.IntegerField(
        null=False
    )
    role = models.CharField(
        max_length=255,
    )
    class Meta:
      db_table = "UserTradeAccount"