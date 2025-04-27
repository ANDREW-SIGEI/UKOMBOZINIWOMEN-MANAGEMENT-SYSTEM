from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Booster

def index(request):
    """Main boosters dashboard view"""
    return render(request, 'base.html', {
        'title': 'Boosters Dashboard',
    }) 