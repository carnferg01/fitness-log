from django.shortcuts import render, redirect, get_object_or_404

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

def gear_edit(request, pk):
    gear_item = get_object_or_404(Gear, pk=pk)
    if request.method == 'POST':
        form = GearForm(request.POST, instance=gear_item)
        if form.is_valid():
            form.save()
            return redirect('gear_list')  # change as needed
    else:
        form = GearForm(instance=gear_item)
    return render(request, 'gear_edit.html', {'form': form, 'gear_item': gear_item})

def gear_delete(request, pk):
    gear_item = get_object_or_404(Gear, pk=pk)
    if request.method == 'POST':
        gear_item.delete()
        return redirect('gear_list')  # change as needed
    return render(request, 'confirm_delete.html', {'gear_item': gear_item})
