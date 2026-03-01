from django.urls import path
from . import views

app_name = 'evaluator'

urlpatterns = [
    path('evaluate/', views.evaluate, name='evaluate'),
    path('analyze/', views.analyze, name='analyze'),
]
