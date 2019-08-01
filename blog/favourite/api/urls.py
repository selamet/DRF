from django.urls import path, include

from favourite.api.views import FavouriteListCreateAPIView

app_name = 'favourite'

urlpatterns = [
    path('list-create', FavouriteListCreateAPIView.as_view(), name='list'),

]
