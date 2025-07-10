from django.shortcuts import render, redirect

from .models import Gear
from .forms import GearForm

def home(request):
    return render(request, 'home.html')

def gear_list(request):
    gear = Gear.objects.all()
    return render(request, 'gear_list.html', {'gear': gear})

def gear_add(request):
    if request.method == 'POST':
        form = GearForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gear_list')
    else:
        form = GearForm()
    return render(request, 'gear_add.html', {'form': form})

