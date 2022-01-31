from django.urls import path
from .views import DataListView, DataDetailView, DataDeleteView, DataUpdateView, TagDetailView, ChartData

from . import views


urlpatterns = [
    path('', DataListView.as_view(), name='data-home'),

    path('entry/<str:title>/<int:pk>/',
         DataDetailView.as_view(), name='data-entry'),
    path('entry/<str:title>/<int:pk>/delete',
         DataDeleteView.as_view(), name='data-delete'),
    path('entry/<str:title>/<int:pk>/update',
         DataUpdateView.as_view(), name='data-update'),

    path('tag/<str:title>/<int:pk>/', TagDetailView.as_view(), name='data-tag'),
    
    path('charts/<str:timeperiod>/', views.charts),
    path('charts/data/<int:pk>/',views.tagdetaildata)

]
