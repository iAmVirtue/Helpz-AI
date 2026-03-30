from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie


def home(request):
    """Render home/resume analyzer page"""
    return render(request, "home/index.html")


def about(request):
    """Render about page"""
    return render(request, "home/about_me.html")
