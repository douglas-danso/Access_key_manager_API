from rest_framework.test import APITestCase
from tryapp.models import CustomUser
from django.urls import reverse

class CustomUserTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email = 'www@example.com',
        school_name = "haha intl",
        first_name = "Noone",
        last_name = "Noone",
        is_active = True,
        is_admin =True,
        is_verified = True
        )

    def test_user(self):
        user = CustomUser.objects.get(email = 'www@example.com' )
        self.assertEqual(user,self.user)

class TestViews(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email = 'www@example.com',
        
        first_name = "Noone",
        last_name = "Noone",
        school_name = "haha intl",
        password ='password')

    def test_signup(self):
        data = {
            'email': 'test@example.com',
            'password': 'mypassword',
            'first_name': 'John',
            'last_name': 'Doe',
            'school_name': 'Example School'
        }
        response = self.client.post(reverse('signup'), data=data)
        self.assertEqual(response.status_code, 201)