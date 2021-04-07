# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from app import views

urlpatterns = [
    path('', views.index, name='home'),
    path('add_trade_account', views.add_trade_account),  
    path('edit/<int:id>', views.edit),  
    path('update/<int:id>', views.update),  
    path('delete/<int:id>', views.destroy), 
    re_path(r'^.*\.*', views.pages, name='pages'),
]