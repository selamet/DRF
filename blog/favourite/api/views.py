from rest_framework.generics import ListCreateAPIView

from favourite.api.serializers import FavouriteListCreateAPISerializer
from favourite.models import Favourite


class FavouriteListCreateAPIView(ListCreateAPIView):
    queryset = Favourite.objects.all()
    serializer_class = FavouriteListCreateAPISerializer

    def get_queryset(self):
        return Favourite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) # kendi adına kayıt
