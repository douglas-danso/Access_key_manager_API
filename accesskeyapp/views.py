from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from tryapp.helpers.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import AccessKey
from tryapp.models import CustomUser
from .serializers import AccessKeySerializer,AccessKeyListSerializer
from tryapp.serializers import DeleteAccountSerializer 
import datetime
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from tryapp.helpers.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse,Http404
from rest_framework.pagination import PageNumberPagination
from tryapp.serializers import PasswordResetSerializer
from tryapp.helpers.send_emails import access_key_email,access_key_revoke_email
from .tasks import access_key_revoke_email

class AccessKeyPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class AccessKeyGenerate(generics.GenericAPIView):
    serializer_class = AccessKeySerializer
    permission_classes=(IsAuthenticated,)
    authentication_classes=(JWTAuthentication,)
    def post(self,request,*args, **kwargs):
        user =self.request.user
        access_key =AccessKey.objects.filter(status = 'active', school_id = user.id)
        if access_key:
            return JsonResponse({'detail':'cannot generate access key, you have an active access key'})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # access_key_email(request,user,access_key)
        serializer.save()

        return Response({'detail':'access key generated'})

class GetAllAccessKeys(generics.ListAPIView):
    
    queryset = AccessKey.objects.all()
    permission_classes=(IsAuthenticated,)
    authentication_classes=(JWTAuthentication,)
    serializer_class = AccessKeyListSerializer

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     print(queryset) # Add this line to print the queryset
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

class AccessKeyDeleteAll(generics.GenericAPIView):
    permission_classes=(IsAuthenticated,)
    authentication_classes=(JWTAuthentication,) 
    serializer_class = DeleteAccountSerializer 
    def delete(self,request, *args, **kwargs):
        serializer = self.get_serializer(data =request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = CustomUser.objects.get(email=serializer.validated_data['email'])  
        except(CustomUser.DoesNotExist):
            return JsonResponse('detail: No user with such email exist')
        user_dict ={
            
            'id': user.id,
            'first name': user.first_name,
        }
       
        access_key = AccessKey.objects.filter(school_id =user.id)
        if not access_key.exists():
            return JsonResponse({'detail': 'This user has no access keys'})
        
        access_key.delete()
        return JsonResponse({'detail': 'access keys for', 'user': user_dict, 'message': 'deleted'})
    
class AccessKeyDelete(generics.GenericAPIView):
    permission_classes=(IsAuthenticated,)
    authentication_classes=(JWTAuthentication,) 
    serializer_class = DeleteAccountSerializer
    lookup_field ='pk'

    def delete(self,request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = CustomUser.objects.get(email=serializer.validated_data['email']) 
        except CustomUser.DoesNotExist:
            return JsonResponse({'detail': 'No user with such email exist'})
        
        try:
            access_key_id = kwargs['pk']
            access_key = AccessKey.objects.get(pk=access_key_id)
        except AccessKey.DoesNotExist:
            return JsonResponse({'detail': 'Access key does not exist'})
        
        access_key_dict = {
            'id': access_key.id,
            'key': access_key.key,
            'created_at': access_key.date_of_procurement,
            'expires_at': access_key.expiry_date,
        }
        access_key.delete()
        
        return JsonResponse({'detail': 'access key', 'access_key': access_key_dict, 'message': 'deleted'})
    

class RevokeKey(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes =(JWTAuthentication,)
    lookup_field ='pk'
    def patch(self,request,*args, **kwargs):
        user = self.request.user
        try:
            access_key_id = kwargs['pk']
            access_key = AccessKey.objects.get(pk=access_key_id)
        except AccessKey.DoesNotExist:
            return JsonResponse({'detail': 'Access key does not exist'})
        if access_key.status == 'active'or access_key.status == 'expired':
            
            access_key.status ='revoked'
            access_key.save()
            access_key_revoke_email.apply_async(args=[user.id, access_key.id])
            # access_key_revoke_email(user.id,access_key.id)
            
           
        else:
            
            return JsonResponse({'detail' : 'access key is already revoked'})
        
        return JsonResponse({'detail' : 'access key  revoked'})
  
            

class GetSchoolAccesKey(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = AccessKeyListSerializer
    pagination_class = AccessKeyPagination
    
    def get_queryset(self):
        user = self.request.user
        return AccessKey.objects.filter(school_id=user.id).order_by('-date_of_procurement')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class GetActiveAccessKey(generics.GenericAPIView):
    permission_classes = (IsAdminUser,)
    authentication_classes=(JWTAuthentication,)
    serializer_class = AccessKeyListSerializer
    def get(self,request,*args, **kwargs):
        email = self.request.data.get('email')
        try:
            user = CustomUser.objects.get(email = email)
            access_key = AccessKey.objects.get(status ='active', school_id = user.id)
            serializer =self.get_serializer(access_key)
            return Response(serializer.data)
        except (CustomUser.DoesNotExist, AccessKey.DoesNotExist):
                raise Http404
       