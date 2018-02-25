from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    path('page/<str:name>', views.PageView.as_view(), name = 'page'),
]
