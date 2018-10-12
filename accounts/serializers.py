from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        fields = ('username', 'date_joined', 'first_name', 'last_name', 'email')
        # fields = ('email', 'username', 'password')

