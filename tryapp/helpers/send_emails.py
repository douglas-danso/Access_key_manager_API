from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from tryapp.models import CustomUser
from accesskeyapp.models import AccessKey
from django.urls import reverse
from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode
import jwt


def send_activation_email(request, user):
    token = jwt.encode({'user_id': user.id}, 'secret_key', algorithm='HS256')
    activation_link = reverse('activate', kwargs={'token': token})
    activation_url = f'http://{request.get_host()}{activation_link}'
    message = f'Hi {user.first_name}, please click on this link to activate your account: {activation_url}'
    send_mail(
        'Activate your account',
        message,
        'noreply@example.com',
        [user.email],
        fail_silently=False,
    )

def access_key_email(user, access_key):
    message = f'hello micro-focus admin, {user.first_name} from {user.school_name} has generated access key, {access_key.key} with expiry date, {access_key.expiry_date}' 
    send_mail(
        'Access key generation',
        message,
        user.email,
        ['douglasdanso66@gmail.com'],
        fail_silently=False,
    )

# def access_key_revoke_email(request,user, access_key):
#     message = f'hello, {user.first_name} from {user.school_name} your access key, {access_key.key} with expiry date, {access_key.expiry_date} has been revoked' 
#     send_mail(
#         'Revoked Access Key',
#         message,
        
#         'douglasdanso66@gmail.com',
#         [user.email],
#         fail_silently=False,
# #     )




def access_key_revoke_email(user_id, access_key_id):
    # sleep(5) 
    user = CustomUser.objects.get(id=user_id)
    access_key = AccessKey.objects.get(id=access_key_id)
    print(user)
    message = f'hello, {user.first_name} from {user.school_name} your access key, {access_key.key} with expiry date, {access_key.expiry_date} has been revoked' 
    send_mail(
        'Revoked Access Key',
        message,
        'douglasdanso66@gmail.com',
        [user.email],
        fail_silently=False,
    )
