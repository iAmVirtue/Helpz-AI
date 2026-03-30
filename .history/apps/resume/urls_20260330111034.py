from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('home', views.home, name='home'),
    path('explore', views.explore, name='explore'),
    path('api/explore_graph/', views.generate_explore_graph, name='explore_graph'),
]
