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
            activities = gear.activities.select_related('auto')

            total_distance = 0.0
            total_climb = 0.0
            first_used = None
            last_used = None
            count = 0

            for activity in activities:
                # Use field from Activity if not None, otherwise fall back to Activity.auto
                auto = getattr(activity, 'auto', None)

                # Choose distance
                distance = (
                    activity.distance if activity.distance is not None
                    else (auto.distance if auto and auto.distance is not None else 0.0)
                )
                climb = (
                    activity.elevation_gain if activity.elevation_gain is not None
                    else (auto.elevation_gain if auto and auto.elevation_gain is not None else 0.0)
                )

                # Use start_datetime from Activity or fallback to Auto
                start_dt = (
                    activity.start_datetime if activity.start_datetime
                    else (auto.start_datetime if auto else None)
                )

                # Update total fields
                total_distance += distance
                total_climb += climb
                count += 1

                # Update first/last used
                if start_dt:
                    if not first_used or start_dt < first_used:
                        first_used = start_dt
                    if not last_used or start_dt > last_used:
                        last_used = start_dt

            # Update or create GearCalculated
            gc, _ = GearCalculated.objects.get_or_create(gear=gear)

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

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=100)
    locations = models.TextField(blank=True)  # JSON string of locations
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
    ])
    feeling = models.PositiveSmallIntegerField(choices=[
        (1, 'Awful (really should not have done this)'),
        (2, 'Bad'),
        (3, 'Grim (having 2nd thoughts)'),
        (4, 'Not great'),
        (5, 'A little hard'),
        (6, 'Neutral'),
        (7, 'Reasonable'),
        (8, 'Great'),
        (9, 'Energised'),
        (10, 'Incredible'),
    ])
    terrain = models.CharField(max_length=100, blank=True)
    gear = models.ManyToManyField(Gear, blank=True, related_name='activities')
    note = models.TextField(blank=True)

    start_datetime = models.DateTimeField(blank=True, null=True) # UTC
    start_timezone = models.CharField(max_length=100, default='UTC')
    elapsed_time = models.DurationField(blank=True, null=True)  # Total time spent
    tracked_time = models.DurationField(blank=True, null=True)  # Time actively tracked
    moving_time = models.DurationField(blank=True, null=True)  # Time spent moving

    distance = models.FloatField(blank=True, null=True)  # km
    elevation_gain = models.FloatField(blank=True, null=True)     # m
    elevation_loss = models.FloatField(blank=True, null=True)     # m
    elevation_max = models.FloatField(blank=True, null=True)     # m
    elevation_min = models.FloatField(blank=True, null=True)     # m

    time_at_HR = models.TextField(blank=True)  # JSON string of time at HR zones
    time_at_pace = models.TextField(blank=True)  # JSON string of time at HR/pace zones

    calories = models.IntegerField(blank=True, null=True)  # Estimated calories burned


class ActivityAuto(models.Model):
    id = models.AutoField(primary_key=True)
    activity = models.OneToOneField(Activity, on_delete=models.CASCADE, related_name='auto')
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
    zone_multipliers = models.JSONField(default=dict)  # JSON object with zone multipliers 
    # need a function to convert a formula to multipliers