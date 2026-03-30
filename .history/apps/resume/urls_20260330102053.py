from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('analyze', views.analyze, name='analyze'),
    path('explore', views.explore, name='explore'),
    path('api/explore_graph/', views.generate_explore_graph, name='explore_graph'),
    path('api/analyze/', views.analyze, name='analyze_api'),
]
