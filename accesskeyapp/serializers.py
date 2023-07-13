from rest_framework import serializers
from tryapp.models import CustomUser
from .models import AccessKey
import random,string
import datetime
from django.http import JsonResponse
from tryapp.helpers.send_emails import access_key_email

class AccessKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessKey
        fields = ['expiry_date']

    def validate_date(self,data):
        expiry_date = data['expiry_date']
        if expiry_date and expiry_date< datetime.date.today():
            pass
            # raise serializers.ValidationError("expiry date cannot be in the past")
        return expiry_date

    def generate_key(self):
        # Generate a random 32-character string for the key
        return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))
        
    def create(self,validated_data,*args, **kwargs):
        user = self.context['request'].user
        school = CustomUser.objects.get(id=user.id)
        
        
        validated_data={
        'school' : school,
        'key' : self.generate_key(),
        'expiry_date': self.validate_date(validated_data)
        }
        access_key = AccessKey.objects.create(**validated_data)
        access_key_email(user,access_key)
        return access_key
    
    # def check_access_key(self,*args, **kwargs):
    #     user = self.context['request'].user
    #     access_key =AccessKey.objects.filter(school_id = user.id)
    #     for access_keys in access_key:
    #         if access_keys.status == 'active':
    #             pri
       
class AccessKeyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessKey
        fields = '__all__'   
    
    