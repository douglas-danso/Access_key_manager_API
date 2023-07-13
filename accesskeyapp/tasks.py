from time import sleep
from django.core.mail import send_mail
from tryapp.models import CustomUser
from .models import AccessKey
from celery import shared_task

@shared_task()
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
