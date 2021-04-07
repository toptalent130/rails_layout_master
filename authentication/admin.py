# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# from django.contrib import admin

# Register your models here.

from django.contrib import admin
from . import models

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        'username',
        'email',
        'date_joined',
    )

    list_display_links = (
        'username',
        'email',
    )