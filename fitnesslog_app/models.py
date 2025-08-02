from datetime import timedelta, timezone
from time import localtime
from django.db import models
import pytz
TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.common_timezones]


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
            activities = gear.activities.filter(gear=gear).select_related('auto')

            total_elapsed_time = timedelta(0)
            total_distance = 0.0
            total_climb = 0.0
            first_used = None
            last_used = None
            count = 0

            for activity in activities:
                # Use field from Activity if not None, otherwise fall back to Activity.auto
                #auto = getattr(activity, 'auto', None)

                # Choose distance
                total_elapsed_time += activity.get_value('time_elapsed', timedelta(0))
                total_distance += activity.get_value('distance', 0)
                total_climb += activity.get_value('distance', 0)
                start_time = activity.get_value('start_datetime', None)
                if start_time:
                    if first_used is None or start_time < first_used:
                        first_used = start_time
                    if last_used is None or start_time > last_used:
                        last_used = start_time
                count += 1

            # Update or create GearCalculated
            gc, created = GearCalculated.objects.update_or_create(
                gear=gear,
                defaults={
                    'time_elapsed': total_elapsed_time,
                    'distance': total_distance,
                    'climb': total_climb,
                    'session_count': count,
                    'first_used': first_used,
                    'last_used': last_used,
                }
            )
            gc.save()

class Sport(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
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

    # user = users current timezone
    #  = activity timezone

    start_timezone = models.CharField(max_length=64, blank=True, null=True, choices=[(tz, tz) for tz in pytz.common_timezones])
    start_datetime_utc = models.DateTimeField(blank=True, null=True)
    
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
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, null=True, related_name='activityauto')
    file = models.FileField(upload_to="activity_files_uploads/")
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='activityautos', blank=True, null=True)
    start_latitude = models.FloatField(blank=True, null=True)
    start_longitude = models.FloatField(blank=True, null=True)

    start_timezone = models.CharField(max_length=64, blank=True, null=True, choices=[(tz, tz) for tz in pytz.common_timezones])
    start_datetime_utc = models.DateTimeField(blank=True, null=True)

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
    





class ActivityViewModel:
    def __init__(self, activity, activity_auto=None):
        self._activity = activity
        self._auto = activity_auto

    @property
    def pk(self):
        return self._activity.pk

    @property
    def _meta(self):
        return self._activity._meta

    def __getattr__(self, name):
        """Use Activity field if present, fallback to ActivityAuto."""
        #
        if hasattr(self.__class__, name):
            attr = getattr(self.__class__, name)
            if isinstance(attr, property):
                return attr.__get__(self)  # call property getter explicitly
            # If it's something else (method or class attr), raise error to let normal lookup handle it
            raise AttributeError
        
        #
        if hasattr(self._activity, name):
            value = getattr(self._activity, name)
            # If the value is a related field, return all related objects
            if hasattr(value, 'all') and callable(value.all):
                return value.all()
            if value is not None and value != '':
                return value
        
        #
        if self._auto and hasattr(self._auto, name):
            value = getattr(self._auto, name)
            if hasattr(value, 'all') and callable(value.all):
                return value.all()
            return value
        raise AttributeError(f"{name} not found in either Activity or ActivityAuto")

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        elif isinstance(getattr(self.__class__, name, None), property):
            object.__setattr__(self, name, value)  # this will trigger @property.setter
        elif hasattr(self._activity, name):
            setattr(self._activity, name, value)
        else:
            raise AttributeError(f"Can't set unknown field {name}")

    def save(self):
        self._activity.save()


    @property
    def start_datetime_utc(self):
        """Convert stored UTC start_datetime to the stored timezone."""
        return getattr(self._activity, "start_datetime_utc", None) or getattr(self._auto, "start_datetime_utc", None) or None
        

    ## start_datetime
    @property
    def start_datetime(self):
        """Convert stored UTC start_datetime to the stored timezone."""
        # Get stored datetime and timezone
        utc_dt = getattr(self._activity, "start_datetime_utc", None) or getattr(self._auto, "start_datetime_utc", None) or None
        if not utc_dt:
            return None  # or some default datetime if you want
        
        try:
            tz_name = (
                getattr(self._activity, "start_timezone", None)
                or getattr(self._auto, "start_timezone", None)
                or "UTC"
            )
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.UTC
            
        # Convert from UTC to local timezone-aware datetime
        local_dt = utc_dt.astimezone(tz)

        # Return naive local time (for GUI use)
        return local_dt.replace(tzinfo=None)
    
    @start_datetime.setter
    def start_datetime(self, naive_local_dt):
        """Takes a local datetime and stores it as UTC + sets timezone."""
        try:
            tz = pytz.timezone(self._activity.start_timezone)
        except Exception:
            tz = pytz.UTC

        # Ensure it's naive
        naive_local_dt = naive_local_dt.replace(tzinfo=None)

        # Localize based on timezone (adds tzinfo while preserving clock time)
        aware_local_dt = tz.localize(naive_local_dt, is_dst=None)

        # Convert to UTC and store
        self._activity.start_datetime_utc = aware_local_dt.astimezone(pytz.UTC)
        print()



        
    # def _get_field(self, field_name):
    #     value = getattr(self.activity, field_name, None)
    #     if value is None:
    #         return getattr(self._auto, field_name, None)
    #     else:
    #         return value
        
    # def _set_field(self, field_name, value):
    #     setattr(self.activity, field_name, value)

    # ## file
    # @property
    # def file(self):
    #     return self._get_field('file')

    # ## sport
    # @property
    # def sport(self):
    #     return self._get_field('sport')
    # @sport.setter
    # def sport(self, value):
    #     self._set_field('sport', value)

    # @property
    # def start_latitude(self):
    #     return self._get_field('start_latitude')
    
    # @property
    # def start_longitude(self):
    #     return self._get_field('start_longitude')
    
    # ## start_timezone
    # @property
    # def start_timezone(self):
    #     return self._get_field('start_timezone')
    # @start_timezone.setter
    # def start_timezone(self, value):
    #     self._set_field('start_timezone', value)

    # ## start_datetime_utc
    # @property
    # def start_datetime(self):
    #     """Return localized datetime (aware) based on stored time zone"""
    #     # Get database values: utc & timezone
    #     start_datetime_utc = self._get_field('start_datetime_utc')
    #     start_timezone = self._get_field('start_timezone')
    #     # Apply timezone to utc time
    #     if start_datetime_utc and start_timezone:
    #         tz = pytz.timezone(start_timezone)
    #         return start_datetime_utc.astimezone(tz)

    # @start_datetime.setter
    # def start_timezone(self, local_dt):
    #     """
    #     Set UTC datetime based on a timezone-aware or naive local datetime.
    #     Assumes local_dt is in the timezone given by start_timezone.
    #     """
    #     # if timezone info present in other variable
    #     if local_dt.tzinfo:
    #         #  Get timezone and calculate UTC
    #         tz = pytz.timezone(self.start_timezone)
    #         local_dt = tz.localize(local_dt)
        
    #     # Store as UTC assuming it is now utc
    #     self._set_field('start_datetime_utc', local_dt.astimezone(pytz.UTC))

    # ## elapsed_time
    # @property
    # def elapsed_time(self):
    #     return self._get_field('elapsed_time')
    # @elapsed_time.setter
    # def elapsed_time(self, value):
    #     self._set_field('elapsed_time', value)

    # ## tracked_time
    # @property
    # def tracked_time(self):
    #     return self._get_field('tracked_time')
    # @tracked_time.setter
    # def tracked_time(self, value):
    #     self._set_field('tracked_time', value)

    # ## moving_time
    # @property
    # def moving_time(self):
    #     return self._get_field('moving_time')
    # @moving_time.setter
    # def moving_time(self, value):
    #     self._set_field('moving_time', value)

    # ## distance
    # @property
    # def distance(self):
    #     return self._get_field('distance')
    # @distance.setter
    # def distance(self, value):
    #     self._set_field('distance', value)

    # # elevation_gain
    # @property
    # def elevation_gain(self):
    #     return self._get_field('elevation_gain')
    # @elevation_gain.setter
    # def elevation_gain(self, value):
    #     self._set_field('elevation_gain', value)

    # # elevation_loss
    # @property
    # def elevation_loss(self):
    #     return self._get_field('elevation_loss')
    # @elevation_loss.setter
    # def elevation_loss(self, value):
    #     self._set_field('elevation_loss', value)

    # # elevation_max
    # @property
    # def elevation_max(self):
    #     return self._get_field('elevation_max')
    # @elevation_max.setter
    # def elevation_max(self, value):
    #     self._set_field('elevation_max', value)

    # # elevation_min
    # @property
    # def elevation_min(self):
    #     return self._get_field('elevation_min')
    # @elevation_min.setter
    # def elevation_min(self, value):
    #     self._set_field('elevation_min', value)

    # # time_at_HR
    # @property
    # def time_at_HR(self):
    #     return self._get_field('time_at_HR')
    # @time_at_HR.setter
    # def time_at_HR(self, value):
    #     self._set_field('time_at_HR', value)

    # # time_at_pace
    # @property
    # def time_at_pace(self):
    #     return self._get_field('time_at_pace')
    # @time_at_pace.setter
    # def time_at_pace(self, value):
    #     self._set_field('time_at_pace', value)

    # # best_sustained_pace
    # @property
    # def best_sustained_pace(self):
    #     return self._get_field('best_sustained_pace')

    # # device
    # @property
    # def device(self):
    #     return self._get_field('device')
    
    # # weather
    # @property
    # def weather(self):
    #     return self._get_field('weather')
    # @weather.setter
    # def weather(self, value):
    #     self._set_field('weather', value)

    # # calories
    # @property
    # def calories(self):
    #     return self._get_field('calories')
    # @calories.setter
    # def calories(self, value):
    #     self._set_field('calories', value)

    


    
    
  