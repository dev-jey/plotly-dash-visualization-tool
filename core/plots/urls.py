"""
URL Configuration.

URL configurations for the plots application.
"""
from django.urls import path
from .views import HomeView

# Specify a namespace
app_name = "plots"

urlpatterns = [
    path('', HomeView.as_view()),
]
