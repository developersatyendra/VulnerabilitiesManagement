from rest_framework import serializers
from django.contrib.auth.models import User

PERMS_VIEWONLY = 0
PERMS_SUBMITTER = 1
PERMS_MANAGER = 2


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        fields = ('username', 'date_joined', 'first_name', 'last_name', 'email', 'is_active')
        # fields = ('email', 'username', 'password')


class AccountSerializer(serializers.ModelSerializer):

    permissionLevel = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'date_joined', 'first_name', 'last_name', 'email', 'is_active', 'is_superuser', 'permissionLevel')

    def get_permissionLevel(self, obj):
        # groupName = obj.groups.first().name
        groupName = User.objects.get(id=obj.id).groups.values_list('name', flat=True)
        print("Debug: {}".format(groupName))
        if 'submitter' in groupName.__str__().lower():
            return PERMS_SUBMITTER
        elif 'manager' in groupName.__str__().lower():
            return PERMS_MANAGER
        else:
            return PERMS_VIEWONLY
