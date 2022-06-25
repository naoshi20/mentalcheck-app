from django.http import HttpResponseRedirect
from django.shortcuts import redirect

def RootView(request):
    return redirect('check/')