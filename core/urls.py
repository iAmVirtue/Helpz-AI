from django.contrib import admin
from django.urls import path
from app.home.views import (
    home, analyze, about, explore, generate_explore_graph,
    interview_coach, chat_start, chat_message, chat_evaluate
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('analyze', analyze, name='analyze'),
    path('explore/', explore, name='explore'),
    path('api/explore_graph/', generate_explore_graph, name='explore_graph'),
    path('interview/', interview_coach, name='interview'),
    path('api/chat/start', chat_start, name='chat_start'),
    path('api/chat/message', chat_message, name='chat_message'),
    path('api/chat/evaluate', chat_evaluate, name='chat_evaluate'),
]
