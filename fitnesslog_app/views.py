from django.shortcuts import render, redirect, get_object_or_404

from .models import Gear, GearCalculated, Sport, HRzones, Activity, Injury
from .forms import GearForm, SportForm, HRzonesForm, ActivityForm, InjuryForm

def home(request):
    return render(request, 'home.html')


#######################################################################
### Gear

def gear_list(request):
    gear = Gear.objects.all().select_related('calculated')
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

def gear_refresh(request):
    GearCalculated.recalculate_all_gear()
    # After action, redirect back to gear list
    return redirect('gear_list')

########################################################################
### Sport


def sport_list(request):
    sports = Sport.objects.all()
    return render(request, 'sport_list.html', {'sports': sports})

def sport_add(request):
    if request.method == 'POST':
        form = SportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sport_list')
    else:
        form = SportForm()
    return render(request, 'sport_add.html', {'form': form})

def sport_edit(request, pk):
    sport = get_object_or_404(Sport, pk=pk)
    if request.method == 'POST':
        form = SportForm(request.POST, instance=sport)
        if form.is_valid():
            form.save()
            return redirect('sport_list')  # change as needed
    else:
        form = SportForm(instance=sport)
    return render(request, 'sport_edit.html', {'form': form, 'sport': sport})

def sport_delete(request, pk):
    sport = get_object_or_404(Sport, pk=pk)
    if request.method == 'POST':
        sport.delete()
        return redirect('sport_list')  # change as needed
    return render(request, 'confirm_delete.html', {'sport': sport})


########################################################################
### hrzones


def hrzones_list(request):
    hrzones = HRzones.objects.all()
    return render(request, 'hrzones_list.html', {'hrzones_list': hrzones})

def hrzones_add(request):
    if request.method == 'POST':
        form = HRzonesForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hrzones_list')
    else:
        form = HRzonesForm()
    return render(request, 'hrzones_add.html', {'form': form})

def hrzones_edit(request, pk):
    hrzones = get_object_or_404(HRzones, pk=pk)
    if request.method == 'POST':
        form = HRzonesForm(request.POST, instance=hrzones)
        if form.is_valid():
            form.save()
            return redirect('hrzones_list')  # change as needed
    else:
        form = HRzonesForm(instance=hrzones)
    return render(request, 'hrzones_edit.html', {'form': form, 'hrzones': hrzones})

def hrzones_delete(request, pk):
    hrzones = get_object_or_404(HRzones, pk=pk)
    if request.method == 'POST':
        hrzones.delete()
        return redirect('hrzones_list')  # change as needed
    return render(request, 'confirm_delete.html', {'hrzones': hrzones})


########################################################################
### activity


def activity_list(request):
    activity_list = Activity.objects.all()
    return render(request, 'activity_list.html', {'activity_list': activity_list})

def activity_add(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('activity_list')
    else:
        form = ActivityForm()
    return render(request, 'activity_add.html', {'form': form})

def activity_edit(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('activity_list')  # change as needed
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'activity_edit.html', {'form': form, 'activity': activity})

def activity_delete(request, pk):
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == 'POST':
        activity.delete()
        return redirect('activity_list')  # change as needed
    return render(request, 'confirm_delete.html', {'activity': activity})


########################################################################
### Injury


def injury_list(request):
    injurys = Injury.objects.all()
    return render(request, 'injury_list.html', {'injurys': injurys})

def injury_add(request):
    if request.method == 'POST':
        form = InjuryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('injury_list')
    else:
        form = InjuryForm()
    return render(request, 'injury_add.html', {'form': form})

def injury_edit(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    if request.method == 'POST':
        form = InjuryForm(request.POST, instance=injury)
        if form.is_valid():
            form.save()
            return redirect('injury_list')  # change as needed
    else:
        form = InjuryForm(instance=injury)
    return render(request, 'injury_edit.html', {'form': form, 'injury': injury})

def injury_delete(request, pk):
    injury = get_object_or_404(Injury, pk=pk)
    if request.method == 'POST':
        injury.delete()
        return redirect('injury_list')  # change as needed
    return render(request, 'confirm_delete.html', {'injury': injury})
