from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import timedelta, datetime, timezone, time, timedelta
from .models import *
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db.models import Q


@csrf_exempt  # Or use CSRF token properly
def set_timezone(request):
    if request.method == "POST":
        data = json.loads(request.body)
        tz = data.get("timezone")
        if tz:
            request.session['user_timezone'] = tz
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "bad request"}, status=400)

#######################################################################
### Summaries

def summary(request):
    return render(request, 'summary.html')

def summary_myday(request):
    selected_date = None
    day_stats = None
    day_activities = []
    enhanced_day_activities = []

    if request.method == 'POST':
        form = MydayForm(request.POST)
        if form.is_valid():
            # Get date
            selected_date = form.cleaned_data.get('date')

            # Get day totals
            try:
                day_stats = ActivityDayCalculated.objects.get(date=selected_date)
            except ActivityDayCalculated.DoesNotExist:
                pass

            
            # Get day activities
            try:
                # Parse the date from the request

                # Define start and end of the day in UTC
                start_dt = datetime.combine(selected_date, time.min).replace(tzinfo=timezone.utc)
                end_dt = datetime.combine(selected_date + timedelta(days=1), time.min).replace(tzinfo=timezone.utc)

                # Query objects where start_datetime_utc is on that date in UTC
                
                day_activities = Activity.objects.filter(start_datetime_utc__gte=start_dt, start_datetime_utc__lt=end_dt)

            except (ValueError, TypeError):
                pass


            # Identify large breaks in day_activities and calculate time gaps
            enhanced_day_activities = []
            prev_end_time = None
            for activity in day_activities:
                start = activity.start_datetime_utc
                try:
                    end = start + activity.time_elapsed
                except TypeError:
                    end = start  # Default to 1 hour if time_elapsed is not set

                gap_hours = None
                if prev_end_time:
                    diff = start - prev_end_time
                    if diff > timedelta(hours=1):
                        # Round to nearest full hour
                        rounded_hours = round(diff.total_seconds() / 3600)
                        gap_hours = rounded_hours

                enhanced_day_activities.append({
                    'activity': activity,
                    'gap_hours': gap_hours,  # None if no separator needed
                })

                prev_end_time = end

    else:
        form = MydayForm()  # TODO : include date

    return render(request, 'summary_myday.html', {'form':form, 'selected_date': selected_date, 'day_stats': day_stats, 'enhanced_day_activities': enhanced_day_activities})


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
    # Cleanup adding activity
    request.session.pop('activityAuto_id', None)
    ActivityAuto.objects.filter(activity__isnull=True).delete()

    #
    activities = Activity.objects.all().select_related('activityauto')
    return render(request, 'activity_list.html', {'activities': activities})

def activity_add(request):
   
    auto = None
    vm = None
    
    if request.method == 'POST':
        if 'upload_button' in request.POST:
            uploaded_file = request.FILES.get('activity_file')
            if uploaded_file:                
                parsed_data = parse_file(uploaded_file)
                auto = ActivityAuto(**parsed_data)
                auto.save()
                request.session['activityAuto_id'] = auto.id
                return redirect('activity_add')
            else:
                messages.error(request, "No file uploaded.")
                return redirect('activity_add')


            #     form = ActivityForm(activity_auto=request.session['activity_activity_auto'])
            #     return render(request, 'activity_add.html', {
            #         'form': form,
            #         'activity_auto': request.session['activity_activity_auto']
            #     })
            # else:
            #     messages.error(request, "No file uploaded.")
            
            #     form = ActivityForm()
            #     return render(request, 'activity_add.html', {
            #         'form': form,
            #         'activity_auto': {}
            #     })
                

            

        elif 'submit_button' in request.POST:
            auto_id = request.session.get('activityAuto_id')
            auto = ActivityAuto.objects.filter(id=auto_id).first() if auto_id else None

            # Always pass a new Activity instance
            activity = Activity()
            vm = ActivityViewModel(activity, activity_auto=auto)

            form = ActivityViewModelForm(request.POST, vm=vm)
            if form.is_valid():
                request.session.pop('activityAuto_id', None)
                form.save()

                if auto:
                    auto.activity = vm._activity
                    auto.save()

                return redirect('activity_list')
            #else:
                # Form has errors, return it with POST data and auto
                #return render(request, 'activity_add.html', {'form': form})

    # GET request
    else:
        auto_id = request.session.get('activityAuto_id')
        auto = ActivityAuto.objects.filter(id=auto_id).first() if auto_id else None

        if auto:
        #activity = Activity()
            vm = ActivityViewModel(None, activity_auto=auto)
            form = ActivityViewModelForm(vm=vm)
        else:
            form = ActivityViewModelForm()

    return render(request, 'activity_add.html', {'form': form, 'vm': vm})

    # # GET request (including after redirect)
    # auto_id = request.session.get('activityAuto_id', None)
    # auto = ActivityAuto.objects.filter(id=auto_id).first()
    # form = ActivityViewModelForm(request.POST, activity_auto=auto)
    # return render(request, 'activity_add.html', {'form': form})



def activity_edit(request, pk):
    # TODO: gear saving/viewing
    # time at hr
    # time at pace
    # test required fields


    activity = get_object_or_404(Activity.objects.select_related('activityauto'), pk=pk)

    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            return redirect('activity_list')
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
    # Return a dictionary of extracted values

    ## Data collector class
    auto = ActivityAuto()

    ## Data collector variables
    # Time
    time_start = None
    time_end = None
    time_moving = timedelta(0)
    min_moving_pace = 0.3

    # Pace


    # speed zones
    bin_width = 0.5     # km/h
    speed_binned = []


    ## Get file type
    
    # If gpx
    #   TODO
    # If fit
    #   Open file
    # Else
    #   message error
    #   return None
    

    data = {
        'sport': 'boxing',  # Set this to an actual Activity instance before saving
        'file': None,  # FileField expects a file object or file path when saving
        'start_latitude': 51.5074,
        'start_longitude': -0.1278,
        'start_datetime_utc': datetime(year=2025, month=7, day=10, hour=7, minute=30, second=0, tzinfo=timezone.utc),  # ISO 8601 string or a datetime object
        'start_timezone': 'UTC',
        'time_elapsed': timedelta(hours=1,minutes=30),  # timedelta or string 'HH:MM:SS'
        'time_tracked': timedelta(hours=1,minutes=20),
        'time_moving': timedelta(hours=1,minutes=15),
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
    data["sport"] = Sport.objects.get(name=data["sport"])
    return data


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
