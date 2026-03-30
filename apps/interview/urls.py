from django.urls import path
from . import views

app_name = 'interview'

urlpatterns = [
    path('', views.interview_coach, name='interview'),
    path('api/chat/start', views.chat_start, name='chat_start'),
    path('api/chat/message', views.chat_message, name='chat_message'),
    path('api/chat/evaluate', views.chat_evaluate, name='chat_evaluate'),
]
