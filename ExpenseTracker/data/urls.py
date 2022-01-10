from django.urls import path
from .views import DataListView, DataDetailView, DataDeleteView, DataUpdateView, TagDetailView

from . import views


urlpatterns = [
    path('', DataListView.as_view(), name='data-home'),

    path('entry/<int:pk>/', DataDetailView.as_view(), name='data-entry'),
    path('entry/<int:pk>/delete', DataDeleteView.as_view(), name='data-delete'),
    path('entry/<int:pk>/update', DataUpdateView.as_view(), name='data-update'),

    path('tag/<int:pk>/', TagDetailView.as_view(), name='data-tag')

]
