from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer,PasswordResetSerializer,PasswordResetConfirmSerializer,PasswordChangeSerializer,DeleteAccountSerializer,ResendSerializer
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser
from tryapp.helpers.permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.http import Http404,JsonResponse
from rest_framework.exceptions import NotFound
import jwt
from .helpers.send_emails import send_activation_email
from .models import BlacklistedToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.contrib.auth import authenticate, login,logout
from rest_framework_simplejwt.exceptions import TokenError
from .backend import GoogleAuthBackend

class UserSignupView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        if request.data.get('method') == 'google':
            id_token = request.data.get('id_token')
            backend = GoogleAuthBackend()

            user = backend.authenticate(request, id_token)
            if user:
                login(request, user)
                return Response({'message': 'Logged in with Google successfully.'})
            else:
                return Response({'message': 'Failed to log in with Google.'}, status=400)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ResendActivationLink(generics.GenericAPIView):
    permission_classes = ()
    serializer_class = ResendSerializer
    def post(self,request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = CustomUser.objects.get(email=serializer.validated_data['email'])
        except (CustomUser.DoesNotExist):
            return Response('detail: user does not exist')
        if user.is_active == True and user.is_verified== True:
            return Response('detail: user is already verified')
        else:
            send_activation_email(request, user)
            return Response('detail: activation email sent')

class Activate(APIView):
    permission_classes = ()
    def post(self, request, token):
        try:
            decoded_token = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            user_id = decoded_token['user_id']
            user = CustomUser.objects.get(id=user_id)
        except (jwt.exceptions.DecodeError, CustomUser.DoesNotExist):
            raise Http404('Invalid activation link')
        
        if not user.is_verified:
            user.is_verified = True
            user.is_active = True
            user.save()
            return JsonResponse({'detail': 'User has been activated'})
        else:
            return JsonResponse({'detail': 'User has already been activated'})

class UserLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request,user)
        # print(self.request.user)
        refresh = RefreshToken.for_user(user)
        # print(request.user.refresh)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class UserLists(generics.ListAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()



class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]
    def post(self, request, format=None,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data['email'])
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
                 reverse('passwordresetconfirm', kwargs={'uidb64': uidb64, 'token': token}))
            # Send the reset URL to the user by email
        subject = 'Password reset'
        message = f'Use this link to reset your password: {reset_url}'
        from_email = 'douglasdanso66@gmail.com'
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # Return a success message
        return Response({'success': 'Password reset email has been sent'}, status=status.HTTP_200_OK)
    
class PasswordResetConfirm(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                user = None
       
        if user is not None and default_token_generator.check_token(user, token):
            
            if  user.check_password(password):
                return Response({'detail':'password cannot be the same as previous password.'})
            user.set_password(password)
            user.save()
            return Response({'detail': 'Password has been reset.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordChange(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_password = serializer.validated_data['current_password']
        user = self.request.user
        
        if not user.check_password(current_password):
            raise NotFound("You have entered the wrong password, try again.")
        
        password = serializer.validated_data['password']
        user.set_password(password)
        user.save()
        return Response({'detail': 'Password has been changed.'}, status=status.HTTP_200_OK)

class DeleteAccount(generics.GenericAPIView):
    authentication_classes = (JWTAuthentication,)
    # lookup_field ='pk'
    permission_classes = [IsAdminUser]
    serializer_class = DeleteAccountSerializer 
    def delete(self,request,*args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(email=serializer.validated_data['email'])
        user.is_active = False
        user.delete()
        return Response({'detail: user deleted'})



# class LogoutView(generics.GenericAPIView):
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         # Get the user's refresh token from the request data
#         refresh_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
#         # print(refresh_token)
        

#         if not refresh_token:
#             return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             # Blacklist the refresh token
#             # token = RefreshToken(refresh_token)
#             # Set the access token's expiration time to a date in the past
#             # access_token = AccessToken(token)
            
#             # access_token.set_exp(lifetime=-1)
#             print(refresh_token)
#             refresh_token.blacklist()

#         except Exception as e:
#             print(Exception as e)
#             return Response({'error': 'Failed to logout user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({'message': 'User has been logged out successfully.'}, status=status.HTTP_200_OK)




class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        print(self.request.user.is_authenticated)
        # Get the user's refresh token from the request data
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            try:
                token.blacklist()
                print(token)
            except:
                # Token is already blacklisted
                pass

            # Set the access token's expiration time to a date in the past
            access_token = AccessToken(token)
            access_token.set_exp(lifetime=-1)
            try:
                access_token.blacklist()
            except :
                # Token is already blacklisted
                pass

        except TokenError:
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            return Response({'error': 'Failed to logout user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'User has been logged out successfully.'}, status=status.HTTP_200_OK)
