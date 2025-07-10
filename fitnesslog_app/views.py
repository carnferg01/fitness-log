from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta, datetime, timezone
from .models import Gear, GearCalculated, Sport, HRzones, Activity, Injury, Illness, ActivityAuto
from .forms import GearForm, SportForm, HRzonesForm, ActivityForm, InjuryForm, IllnessForm

def summary(request):
    return render(request, 'summary.html')


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
    activity_list = Activity.objects.select_related('sport', 'auto')
    for activity in activity_list:
        activity.sport = activity.get_value('sport', '')
        activity.activity_type = activity.get_value('activity_type', timedelta(0))
        activity.start_datetime = activity.get_value('start_datetime', '0001-01-01T00:00')
        activity.start_timezone = activity.get_value('start_timezone', 'UTC')
        activity.moving_time = activity.get_value('moving_time', timedelta(0))
        activity.distance = activity.get_value('distance', 0)
        activity.elevation_gain = activity.get_value('elevation_gain', 0)
        activity.calories = activity.get_value('calories', 0)
    return render(request, 'activity_list.html', {'activity_list': activity_list})

def activity_add(request):
    placeholder_data = request.session.get('extracted_activity_data', None)

    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save()

            # Create ActivityAuto using the extracted data from session (if available)
            if placeholder_data:
                ActivityAuto.objects.create(**placeholder_data, activity=activity)
                request.session.pop('extracted_activity_data', None)
            return redirect('activity_list')
    else:
        form = ActivityForm()

    return render(request, 'activity_add.html', {
        'form': form,
        'placeholders': placeholder_data or {},
    })


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

def parse_file(file):
    # Placeholder for actual file analysis logic
    # Return a dictionary of extracted values

    sport, sport_created_bool = Sport.objects.get_or_create(
        name='boxing',
        defaults={
            'colour': '#000000',  # default grey
            'impact': True,
        }
    )

    return {
        'sport': sport.id,  # Set this to an actual Activity instance before saving
        'file': None,  # FileField expects a file object or file path when saving
        'start_latitude': 51.5074,
        'start_longitude': -0.1278,
        'start_datetime': '2025-07-10T07:30:00',  # ISO 8601 string or a datetime object
        'start_timezone': 'UTC',
        'elapsed_time': '01:30:00',  # timedelta or string 'HH:MM:SS'
        'tracked_time': '01:20:00',
        'moving_time': '01:15:00',
        'distance': 15.2,
        'elevation_gain': 250.5,
        'elevation_loss': 240.3,
        'elevation_max': 180.0,
        'elevation_min': 50.0,
        'time_at_HR': '{"zone1": "00:10:00", "zone2": "00:30:00"}',  # JSON string
        'time_at_pace': '{"pace1": "00:15:00", "pace2": "01:15:00"}',
        'best_sustained_pace': 4.35,
        'device': 'Garmin Forerunner 945',
        'weather': 'Sunny, 20°C',
        'calories': 1200,
    } 

    # {
    #     'activity': None,  # Set this to an actual Activity instance before saving
    #     'file': None,  # FileField expects a file object or file path when saving
    #     'start_latitude': 51.5074,
    #     'start_longitude': -0.1278,
    #     'start_datetime': datetime(year=2025, month=7, day=10, hour=7, minute=30, second=0, tzinfo=timezone.utc),  # ISO 8601 string or a datetime object
    #     'start_timezone': 'UTC',
    #     'elapsed_time': timedelta(hours=1,minutes=30),  # timedelta or string 'HH:MM:SS'
    #     'tracked_time': timedelta(hours=1,minutes=20),
    #     'moving_time': timedelta(hours=1,minutes=15),
    #     'distance': 15.2,
    #     'elevation_gain': 250.5,
    #     'elevation_loss': 240.3,
    #     'elevation_max': 180.0,
    #     'elevation_min': 50.0,
    #     'time_at_HR': '{"zone1": "00:10:00", "zone2": "00:30:00"}',  # JSON string
    #     'time_at_pace': '{"pace1": "00:15:00", "pace2": "01:15:00"}',
    #     'best_sustained_pace': 4.35,
    #     'device': 'Garmin Forerunner 945',
    #     'weather': 'Sunny, 20°C',
    #     'calories': 1200,
    # }

def activity_add_from_file(request):
    if request.method == 'POST' and 'activity_file' in request.FILES:
        file = request.FILES['activity_file']
        extracted = parse_file(file)
        request.session['extracted_activity_data'] = extracted
        #auto = ActivityAuto.objects.create(**extracted)
    return redirect('activity_add')


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


########################################################################
### Illness


def illness_list(request):
    illnesss = Illness.objects.all()
    return render(request, 'illness_list.html', {'illnesss': illnesss})

def illness_add(request):
    if request.method == 'POST':
        form = IllnessForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('illness_list')
    else:
        form = IllnessForm()
    return render(request, 'illness_add.html', {'form': form})

def illness_edit(request, pk):
    illness = get_object_or_404(Illness, pk=pk)
    if request.method == 'POST':
        form = IllnessForm(request.POST, instance=illness)
        if form.is_valid():
            form.save()
            return redirect('illness_list')  # change as needed
    else:
        form = IllnessForm(instance=illness)
    return render(request, 'illness_edit.html', {'form': form, 'illness': illness})

def illness_delete(request, pk):
    illness = get_object_or_404(Illness, pk=pk)
    if request.method == 'POST':
        illness.delete()
        return redirect('illness_list')  # change as needed
    return render(request, 'confirm_delete.html', {'illness': illness})
