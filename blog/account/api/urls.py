from django.urls import path

from account.api.views import ProfileView, UpdatePassword

app_name = 'account'

urlpatterns = [
    path('me', ProfileView.as_view(), name='me'),
    path('change-password', UpdatePassword.as_view(), name='change-password'),

]
