from django.urls import path, include

from comment.api.views import CommentCreateAPIView, CommentListAPIView

app_name = 'comment'

urlpatterns = [
    path('create', CommentCreateAPIView.as_view(), name='create'),
    path('list', CommentListAPIView.as_view(), name='list'),

]
