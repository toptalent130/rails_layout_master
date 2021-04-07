# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from rest_framework.routers import DefaultRouter

from authentication.views import UserViewSet
# from app import views

router = DefaultRouter()
router.register(r'user', UserViewSet)

urlpatterns = [
    # path('admin', admin.site.urls),          # Django admin route
    path("", include("authentication.urls")), # Auth routes - login / register
    path("", include("app.urls")),            # UI Kits Html files
    path('api/', include(router.urls)),
     
]
