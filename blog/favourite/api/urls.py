from django.urls import path, include

from favourite.api.views import FavouriteListCreateAPIView, FavouriteAPIView

app_name = 'favourite'

urlpatterns = [
    path('list-create', FavouriteListCreateAPIView.as_view(), name='list'),
    path('update-delete/<pk>', FavouriteAPIView.as_view(), name='update-delete'),

]
