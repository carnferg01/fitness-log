# forms.py
from django import forms
import pytz
from .models import Gear, Sport, HRzones, Activity, Injury, Illness
from django.utils.safestring import mark_safe
from django.forms import ChoiceField, ValidationError
from django.forms.models import fields_for_model

class GearForm(forms.ModelForm):
    class Meta:
        model = Gear
        fields = ['type', 'brand', 'model', 'nickname', 'retired']

class SportForm(forms.ModelForm):
    class Meta:
        model = Sport
        fields = ['name', 'colour', 'impact', 'description']
        widgets = {
            'colour': forms.TextInput(attrs={'type': 'color'}),
        }
        ### TODO: Allow text box to expand verticaly rather then overflow horizontaly

class HRzonesForm(forms.ModelForm):
    zones = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1}),  # or forms.TextInput if you prefer
        initial='[]',
        #help_text='e.g. [110, 132, 148, 159, 168]'
    )
    zone_multipliers = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1}),  # or forms.TextInput if you prefer
        initial='[]',
        #help_text='e.g. [0.6, 1, 1.5, 2, 4, 8]'
    )

    class Meta:
        model = HRzones
        fields = ['timestamp', 'zones', 'zone_multipliers']
        widgets = {
            'timestamp': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# class ActivityForm(forms.ModelForm):
#     required_fields = ['sport', 'start_timezone', 'elapsed_time', 'moving_time']

#     sport = forms.ModelChoiceField(
#         queryset=Sport.objects.all(),
#         widget=forms.Select(attrs={'class': 'form-control'}),
#     )
#     #start_datetime_local = forms.DateTimeField(label="Start datetime (in local time)")

#     def __init__(self, *args, **kwargs):
#         # Get auto
#         self.auto = kwargs.pop('activity_auto', None)
#         # convert json->object

#         super().__init__(*args, **kwargs)

#         # if self.instance and self.instance.start_datetime_utc and self.instance.start_timezone:
#         #     tz = pytz.timezone(self.instance.start_timezone)
#         #     # Convert UTC datetime to stored timezone for display in form field
#         #     local_dt = self.instance.start_datetime_utc.astimezone(tz).replace(tzinfo=None)
#         #     self.fields['start_datetime_local'].initial = local_dt
#         #     self.fields['start_timezone'].initial = self.instance.start_timezone

#         if self.auto:
#             # For each field
#             for field_name, field in self.fields.items():
#                 widget = field.widget

#                 # Set placeholder if widget supports it and value exists
#                 if isinstance(widget, (forms.TextInput, forms.Textarea, forms.NumberInput, forms.DateTimeInput)):
#                     value = getattr(self.auto, field_name, None)
#                     if value is not None:
#                         widget.attrs['placeholder'] = str(value)

#                 if isinstance(field, forms.ModelChoiceField):
#                     auto_value = getattr(self.auto, field_name, None)
#                     if auto_value:
#                         # Set placeholder
#                         field.empty_label = f"{auto_value} (From file)"
#                     #else:
#                         # Fallback
#                     #    field.empty_label = "Select an option"
#                 # # Custom empty label for sport
#                 if field_name == 'sport': #isinstance(field, ChoiceField):
#                     if getattr(self.auto, field_name, None):
#                         # has auto value
#                         field.required = False
#                     else:
#                         # don't have auto value
#                         field.required = True      


#         # Apply Bootstrap class to all appropriate widgets
#         for field_name, field in self.fields.items():
#             widget = field.widget
#             # Skip certain widgets that shouldn't have form-control
#             if not isinstance(widget, (forms.CheckboxInput, forms.ClearableFileInput)):
#                 existing_classes = widget.attrs.get('class', '')
#                 classes = existing_classes.split()
#                 if 'form-control' not in classes:
#                     classes.append('form-control')
#                 widget.attrs['class'] = ' '.join(classes)

#         for field_name in self.required_fields:
#             if field_name in self.fields:
#                 label = self.fields[field_name].label or field_name.replace('_', ' ').capitalize()
#                 self.fields[field_name].label = mark_safe(f"{label} <span class='text-danger'>*</span>")
        
#     def clean(self):
#         cleaned_data = super().clean()

#         # local_dt = cleaned_data.get('start_datetime_local')
#         # tz_name = cleaned_data.get('start_timezone')

#         # if local_dt and tz_name:
#         #     tz = pytz.timezone(tz_name)
#         #     # Localize naive local datetime
#         #     if local_dt.tzinfo is None:
#         #         aware_local_dt = tz.localize(local_dt)
#         #     else:
#         #         aware_local_dt = local_dt.astimezone(tz)

#         #     # Convert to UTC for storage
#         #     cleaned_data['start_datetime_utc'] = aware_local_dt.astimezone(pytz.UTC)


#         # Validate required fields presence
#         errors = {}
#         for field in self.required_fields:
#             value = cleaned_data.get(field)
#             auto_value = getattr(self.auto, field) if self.auto else None

#             if not value and not auto_value:
#                 errors[field] = "Specify by file or enter manually."

#         for field, message in errors.items():
#             self.add_error(field, message)

#         return cleaned_data



#     class Meta:
#         model = Activity
#         fields = [
#             'sport',
#             'activity_type',
#             'location',
#             'intensity',
#             'feeling',
#             'terrain',
#             #'start_datetime',
#             'start_timezone',
#             'elapsed_time',
#             'tracked_time',
#             'moving_time',
#             'distance',
#             'elevation_gain',
#             'elevation_loss',
#             'elevation_max',
#             'elevation_min',
#             'time_at_HR',
#             'time_at_pace',
#             'calories',
#             'gear'
#         ]

class ActivityForm(forms.ModelForm):
    required_fields = [
        'sport',
        'start_datetime_local',
        'start_timezone',
        'time_elapsed',
    ]

    class Meta:
        model = Activity
        fields = [
            'sport',
            'activity_type',
            'location',
            'intensity',
            'feeling',
            'terrain',
            'gear',
            'note',
            'start_timezone',
            # 'start_datetime_utc'
            'time_elapsed',
            'time_tracked',
            'time_moving',
            'distance',
            'elevation_gain',
            'elevation_loss',
            'elevation_max',
            'elevation_min',
            'time_at_HR',
            'time_at_pace',
            'calories',
        ]

    def __init__(self, *args, **kwargs): # activity=None,
        super().__init__(*args, **kwargs)

        # Add virtual form field(s) manually
        self.fields['start_datetime_local'] = forms.DateTimeField(
            label='Start datetime (local to run)',
            widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'type': 'datetime-local'}),
            input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S'],  # add formats your app might receive
        )
        if self.instance and hasattr(self.instance, 'start_datetime_local'):
            self.fields['start_datetime_local'].initial = (
                self.instance.start_datetime_local.strftime('%Y-%m-%dT%H:%M')
                if self.instance.start_datetime_local else None
            )
            
        # Adjust queryset for gear without replacing the field
        #self.fields['gear'].queryset = Gear.objects.filter(retired=False)

        

        # Make sure Django doesn't do its own required check yet
        for field_name in self.required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

    def clean(self):
        cleaned_data = super().clean()
        activity = self.instance
        auto = getattr(activity, 'activityauto', None)

        for field_name in self.required_fields:
            form_value = cleaned_data.get(field_name)
            auto_value = getattr(auto, field_name, None) if auto else None

            if form_value in (None, '', [], {}) and auto_value in (None, '', [], {}):
                # Add standard 'required' error
                self.add_error(
                    field_name,
                    forms.ValidationError(self.fields[field_name].error_messages['required'])
                )

        return cleaned_data
    
    def clean_start_datetime_local(self):
        dt = self.cleaned_data.get('start_datetime_local')
        if dt:
            # Zero out seconds and microseconds
            dt = dt.replace(second=0, microsecond=0)
        return dt
    
    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set start_timezone and start_datetime_view first
        if 'start_timezone' in self.cleaned_data:
            instance.start_timezone = self.cleaned_data['start_timezone']
        if 'start_datetime_local' in self.cleaned_data:
            instance.start_datetime_local = self.cleaned_data['start_datetime_local']


        # # Assign other fields
        # for field_name, value in self.cleaned_data.items():
        #     if field_name in ('start_timezone', 'start_datetime_local'):
        #         continue

        #     field = self._meta.model._meta.get_field(field_name)
        #     if field.many_to_many:
        #         # Store the m2m data for after saving
        #         m2m_data[field_name] = value
        #     else:
        #         view_name = f"{field_name}_view"
        #         if hasattr(type(instance), view_name):
        #             setattr(instance, view_name, value)
        #         else:
        #             setattr(instance, field_name, value)

        if commit:
            instance.save()
            self.save_m2m()

        return instance



# class ActivityViewModelForm(forms.Form):
#     """This ActivityViewModelForm is a custom Django Form that wraps around 
#     an ActivityViewModel instance, allowing you to edit it via a form 
#     interface"""
#     def __init__(self, *args, vm=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.vm = vm

#         # A hardcoded list of fields that the form should expose.
#         field_names = [
#             'sport',
#             'activity_type',
#             'location',
#             'intensity',
#             'feeling',
#             'terrain',
#             'start_datetime',
#             'start_timezone',
#             'time_elapsed',
#             'time_tracked',
#             'time_moving',
#             'distance',
#             'elevation_gain',
#             'elevation_loss',
#             'elevation_max',
#             'elevation_min',
#             'time_at_HR',
#             'time_at_pace',
#             'calories',
#             'gear',
#         ]

#         # This uses Django's fields_for_model() helper to generate form fields for the listed fields on the Activity model.
#         #activity = vm._activity if vm and vm._activity else Activity()
#         self.fields.update(fields_for_model(Activity, fields=field_names))

#         # Add virtual form field(s) manually
#         self.fields['start_datetime'] = forms.DateTimeField(
#             label='Start Time (local to run)',
#             required=True,
#             widget=forms.DateTimeInput(format='%Y-%m-%d %H:%M:%S'),
#             input_formats=['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S'],  # add formats your app might receive
#         )

#         # Explicitly define gear field
#         self.fields['gear'] = forms.ModelMultipleChoiceField(
#             queryset=Gear.objects.filter(retired=False),
#             required=False,
#             widget=forms.SelectMultiple
#         )

#         # Sets initial values for the form fields from the view model, only when the form is unbound (i.e., not processing a POST request).
#         if vm and not self.is_bound:
#             for name in self.fields:
#                 val = getattr(vm, name, None)

#                 #
#                 if hasattr(val, 'all') and callable(val.all):
#                     val = list(val.all())

#                 # Convert datetime to string format the widget expects
#                 if name == 'start_datetime' and val:
#                     val = val.strftime('%Y-%m-%d %H:%M:%S') if val else None
                
#                 #
#                 if val is None or val == '':
#                     fallback = getattr(vm._auto, name, None) if vm._auto else None
#                     if hasattr(fallback, 'all') and callable(fallback.all):
#                         fallback = list(fallback.all())
#                     val = fallback
                    
#                 self.initial[name] = val

#     # def clean_distance(self):
#     #     val = self.cleaned_data.get('distance')
#     #     auto_val = getattr(self.vm._auto, 'distance', None)
#     #     if auto_val and val and val < 0.5 * auto_val:
#     #         raise forms.ValidationError("Distance is unusually low compared to auto estimate.")
#     #     return val

#     def save(self):
#         ### TODO: Make the following more efficent
#         # Set start_timezone before start_datetime
#         if 'start_timezone' in self.cleaned_data:
#             setattr(self.vm, 'start_timezone', self.cleaned_data['start_timezone'])
#         if 'start_datetime' in self.cleaned_data:
#             setattr(self.vm, 'start_datetime', self.cleaned_data['start_datetime'])
    
#         for name in self.fields:
#             value = self.cleaned_data[name]
#             # Special handling for ManyToMany
#             if name == 'gear':
#                 if hasattr(self.vm._activity.gear, 'set'):
#                     self.vm._activity.gear.set(value)
#             else:
#                 setattr(self.vm, name, value)
#         self.vm.save()
#         return self.vm


class InjuryForm(forms.ModelForm):
    class Meta:
        model = Injury
        fields = ['title', 'start_datetime', 'location', 'side', 'severity', 'notes']

class IllnessForm(forms.ModelForm):
    class Meta:
        model = Illness
        fields = ['title', 'start_date', 'location', 'severity', 'notes']
        ### TODO: include a date picker widget for start_date

class MydayForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True,
        label='Pick a date'
    )