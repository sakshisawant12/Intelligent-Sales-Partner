from django.shortcuts import render, redirect
from .models import Lead

def add_lead(request):
    if request.method == 'POST':
        Lead.objects.create(
            name=request.POST['name'],
            email=request.POST['email']
        )
        return redirect('/dashboard/')
    return render(request, 'leads/add_lead.html')
