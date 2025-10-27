# InfraUAZ/administrador/views.py
from django.shortcuts import render

def panel_administrador(request):
    return render(request, 'administrador/panel.html')
