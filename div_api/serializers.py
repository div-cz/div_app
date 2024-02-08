from rest_framework import serializers
from div_content.models import Movie
from div_content.models import Userprofile
from django.contrib.auth.models import User

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        #model = Userprofile
        #fields = '__all__'
        fields = ['username','email','password']
        extra_kwargs = {
            'password': { 'write_only': True }
        }

    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
