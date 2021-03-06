from django.views.decorators.cache import cache_page
from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render


cache_page(60*15)
def home_page(request):
    return render(request, 'index.html')

def logout_page(request, next_page):
    """
    Log users out and re-direct them to the main page.
    """
    logout(request)
    return HttpResponseRedirect(next_page)

