from django.conf import settings
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # If your <field_name> is declared on your serializer with the parameter required=False
    # then this validation step will not take place if the field is not included.

    last_login = serializers.DateTimeField(format=settings.DATETIME_FORMAT, required=False)
    date_joined = serializers.DateTimeField(format=settings.DATE_FORMAT, required=False)

    class Meta:
        model = User
        fields = '__all__'
        # fields = ('id', 'username', 'email', 'password', 'last_login')
