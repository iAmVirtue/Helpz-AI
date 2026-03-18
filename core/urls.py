from django.contrib import admin
from django.urls import path
from app.home.views import home, analyze, about, explore, generate_explore_graph

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('analyze', analyze, name='analyze'),
    path('explore/', explore, name='explore'),
    path('api/explore_graph/', generate_explore_graph, name='explore_graph'),
]
