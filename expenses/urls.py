from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name="expenses"),
    path('add-expenses',views.add_expenses,name="add-expenses")
]
