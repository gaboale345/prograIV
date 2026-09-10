from django.shortcuts import render
from django.http import HttpResponse
import getpass
usuario = getpass.getuser()
holamundo="hola "+usuario+" Desde django"
def hola(request):
    return HttpResponse(holamundo)