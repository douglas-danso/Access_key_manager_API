from django.urls import path

from accesskeyapp.views import AccessKeyGenerate,GetAllAccessKeys,AccessKeyDeleteAll,AccessKeyDelete,RevokeKey,GetSchoolAccesKey,GetActiveAccessKey
urlpatterns = [
    path('generate/', AccessKeyGenerate.as_view(), name='generate'),
    path('lists/', GetAllAccessKeys.as_view(), name='lists'),
    path('delete/', AccessKeyDeleteAll.as_view(), name='delete_all_keys'),
    path('delete/<int:pk>', AccessKeyDelete.as_view(), name='delete_key'),
    path('revoke/<int:pk>', RevokeKey.as_view(), name='revoke_key'),
    path('schoollists/', GetSchoolAccesKey.as_view(), name='schoollists'),
    path('active-access-key/', GetActiveAccessKey.as_view(), name = 'active-access-key')
    

]