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