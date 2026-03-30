from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Home app routes
    path('', include('apps.home.urls')),
    # Resume analyzer routes
    path('', include('apps.resume.urls')),
    # Interview coach routes
    path('interview/', include('apps.interview.urls')),
]
