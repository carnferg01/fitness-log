from datetime import timedelta
from django.db import models

class Gear(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    datetime_added = models.DateTimeField(auto_now_add=True)
    model = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    retired = models.BooleanField(default=False)

    def __str__(self):
        return self.nickname
    
class GearCalculated(models.Model):
    id = models.AutoField(primary_key=True)
    gear = models.OneToOneField(Gear, on_delete=models.CASCADE, related_name='calculated')
    last_calculated = models.DateTimeField(auto_now=True)

    time_elapsed = models.DurationField(null=True, blank=True)
    first_used = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    distance = models.FloatField(default=0.0)  # km
    climb = models.FloatField(default=0.0)     # m
    session_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.gear.nickname}: #{self.session_count} {self.distance}km  +{self.climb}m {self.first_used} - {self.last_used}"

    def recalculate_all_gear():
        # TODO: This should be make efficent using Django ORM aggregations
        for gear in Gear.objects.all():
            activities = gear.activities.where(gear__contains=gear).select_related('auto')

            total_elapsed_time = timedelta(0)
            total_distance = 0.0
            total_climb = 0.0
            first_used = None
            last_used = None
            count = 0

            for activity in activities:
                # Use field from Activity if not None, otherwise fall back to Activity.auto
                auto = getattr(activity, 'auto', None)

                # Choose distance
                total_elapsed_time += activity.get_value('time_elapsed', timedelta(0))
                total_distance += activity.get_value('distance', 0)
                total_climb += activity.get_value('distance', 0)
                start_dt = activity.get_value(auto, 'start_datetime', 0)
                if start_dt > last_used:
                    last_used = start_dt
                if start_dt < first_used:
                    first_used = start_dt
                count += 1

            # Update or create GearCalculated
            gc, _ = GearCalculated.objects.get_or_create(gear=gear)
            gc.time_elapsed = total_elapsed_time
            gc.distance = total_distance
            gc.climb = total_climb
            gc.session_count = count
            gc.first_used = first_used
            gc.last_used = last_used
            gc.save()

class Sport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    colour = models.CharField(max_length=7, default='#000000')  # Hex color code
    description = models.TextField(blank=True)
    impact = models.BooleanField()

    def __str__(self):
        return self.name
    
class Activity(models.Model):
    id = models.AutoField(primary_key=True)
    datetime_added = models.DateTimeField(auto_now_add=True)

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='activities', blank=True, null=True)
    activity_type = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(blank=True, null=True)
    intensity = models.PositiveSmallIntegerField(choices=[
        (1, 'Leisure'),
        (2, 'Very easy'),
        (3, 'Easy'),
        (4, 'Steady'),
        (5, 'Moderate'),
        (6, 'Brisk'),
        (7, 'Quick'),
        (8, 'Hard'),
        (9, 'Very hard'),
        (10, 'Max'),
    ], blank=True, null=True)
    feeling = models.PositiveSmallIntegerField(choices=[
        (1, 'Terrible'),
        (2, 'Awful'),
        (3, 'Very bad'),
        (4, 'Not great'),
        (5, 'Meh'),
        (6, 'Okay'),
        (7, 'Good'),
        (8, 'Very good'),
        (9, 'Excellent'),
        (10, 'Euphoric'),
    ], blank=True, null=True)
    terrain = models.CharField(max_length=100, blank=True, null=True)
    gear = models.ManyToManyField(Gear, blank=True, related_name='activities')
    note = models.TextField(blank=True, null=True)

    start_datetime = models.DateTimeField(blank=True, null=True)  # UTC
    start_timezone = models.CharField(max_length=100, blank=True, null=True)
    elapsed_time = models.DurationField(blank=True, null=True)  # Total time spent
    tracked_time = models.DurationField(blank=True, null=True)  # Time actively tracked
    moving_time = models.DurationField(blank=True, null=True)  # Time spent moving

    distance = models.FloatField(blank=True, null=True)  # km
    elevation_gain = models.FloatField(blank=True, null=True)  # m
    elevation_loss = models.FloatField(blank=True, null=True)  # m
    elevation_max = models.FloatField(blank=True, null=True)  # m
    elevation_min = models.FloatField(blank=True, null=True)  # m

    time_at_HR = models.TextField(blank=True, null=True)  # JSON string of time at HR zones
    time_at_pace = models.TextField(blank=True, null=True)  # JSON string of time at HR/pace zones

    calories = models.IntegerField(blank=True, null=True)  # Estimated calories burned

    def get_value(self, field_name, default):
        value = getattr(self, field_name, None)
        if value is not None:
            return value
        if hasattr(self, 'auto'):
            auto_value = getattr(self.auto, field_name, None)
            if auto_value is not None:
                return auto_value
        return default


class ActivityAuto(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, null=True, related_name='auto')
    file = models.FileField(upload_to="activity_files_uploads/")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='activityautos', blank=True, null=True)
    start_latitude = models.FloatField(blank=True, null=True)
    start_longitude = models.FloatField(blank=True, null=True)

    start_datetime = models.DateTimeField() # UTC
    start_timezone = models.CharField(max_length=100, default='UTC')
    elapsed_time = models.DurationField()  # Total time spent
    tracked_time = models.DurationField()  # Time actively tracked
    moving_time = models.DurationField()  # Time spent moving

    distance = models.FloatField(blank=True, null=True)  # km
    elevation_gain = models.FloatField(blank=True, null=True)     # m
    elevation_loss = models.FloatField(blank=True, null=True)     # m
    elevation_max = models.FloatField(blank=True, null=True)     # m
    elevation_min = models.FloatField(blank=True, null=True)     # m

    time_at_HR = models.TextField(blank=True)  # JSON string of time at HR zones
    time_at_pace = models.TextField(blank=True)  # JSON string of time at HR/pace zones

    best_sustained_pace = models.FloatField(blank=True, null=True)  # min/km (for >=5 seconds)
    device = models.CharField(max_length=100, blank=True)  # Device used for tracking
    weather = models.CharField(max_length=100, blank=True)  # Weather conditions
    calories = models.IntegerField(blank=True, null=True)  # Estimated calories burned

    # ground_contact_time_avg
    # GC_time_balance_avg
    # vertical_oscillation_avg
    # vertical_ratio_avg
    # stride_length_avg
    # cadence_avg
    # cadence_max
    # HR_max
    # HR_avg



class ActivityCalculated(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='calculated', primary_key=True)
    last_calculated = models.DateTimeField(auto_now=True)

    load = models.FloatField()
    #pace_avg = models.FloatField(blank=True, null=True)  # min/km
    #moving_pace_avg = models.FloatField(blank=True, null=True)  # min/km
    time_in_HR_detailed = models.TextField(blank=True)  # JSON string of time in HR zones
    time_in_HR_zones = models.TextField(blank=True)  # JSON string of time in HR zones
    time_at_pace = models.TextField(blank=True)  # JSON string of time at HR/pace zones

class ActivityDayCalculated(models.Model):
    date = models.DateField(primary_key=True)
    last_calculated = models.DateTimeField(auto_now=True)

    load = models.FloatField()
    time_in_HR_detailed = models.TextField(blank=True)  # JSON string of time in HR zones
    time_in_HR_zones = models.TextField(blank=True)  # JSON string of time in HR zones
    time_at_pace = models.TextField(blank=True)  # JSON string of time at HR/pace zones

    total_distance = models.FloatField(default=0.0)  # km
    total_climb = models.FloatField(default=0.0)     # m
    total_session_count = models.IntegerField(default=0)

    def update_activity_day_calculated():
        from collections import defaultdict
        from datetime import timedelta

        data = defaultdict(lambda: {
            'distance': 0.0,
            'climb': 0.0,
            'sessions': 0,
            'elapsed_time': timedelta(0),
            'tracked_time': timedelta(0),
            'moving_time': timedelta(0),
            'load': 0.0,
        })

        activities = Activity.objects.select_related('auto').all()

        for activity in activities:
            day = activity.start_datetime.date() if activity.start_datetime else None
            if not day:
                continue  # skip if no start date

            dist = activity.get_value('distance', 0.0)
            climb = activity.get_value('elevation_gain', 0.0)
            elapsed = activity.get_value('elapsed_time', timedelta(0))
            tracked = activity.get_value('tracked_time', timedelta(0))
            moving = activity.get_value('moving_time', timedelta(0))

            load = getattr(activity.calculated, 'load', 0)

            data[day]['distance'] += dist
            data[day]['climb'] += climb
            data[day]['sessions'] += 1
            data[day]['elapsed_time'] += elapsed
            data[day]['tracked_time'] += tracked
            data[day]['moving_time'] += moving
            data[day]['load'] += load

        for day, values in data.items():
            obj, created = ActivityDayCalculated.objects.update_or_create(
                date=day,
                defaults={
                    'distance': values['distance'],
                    'climb': values['climb'],
                    'session_count': values['sessions'],
                    'elapsed_time': values['elapsed_time'],
                    'tracked_time': values['tracked_time'],
                    'moving_time': values['moving_time'],
                    'load': values['load'],
                }
            )

class OrienteeringProfile(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='orienteering_profile')

    controls_found = models.IntegerField(default=0)

class SimplifiedTraceCoordinates(models.Model):
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='simplified_trace')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField()

class HRzones(models.Model):
    id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    #sports = 
    notes = models.TextField(blank=True)

    zones = models.JSONField(default=dict)  # JSON object with zone definitions
    zone_multipliers = models.JSONField(default=list)  # JSON object with zone multipliers 
    # need a function to convert a formula to multipliers

class Injury(models.Model):
    id = models.AutoField(primary_key=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True)
    side = models.CharField(max_length=5, choices=[
        ('left', 'Left'),
        ('right', 'Right'),
        ('both', 'Both'),
        ('', ''),
    ], default='')
    notes = models.TextField(blank=True)
    severity = models.TextField()  # e.g. 1222233253300003

    def __str__(self):
        return f"{self.title} starting on {self.start_datetime}"
    
class Illness(models.Model):
    id = models.AutoField(primary_key=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100)
    start_datetime = models.DateTimeField()
    location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    severity = models.TextField()  # e.g. 1222233253300003

    def __str__(self):
        return f"{self.title} starting on {self.start_datetime}"