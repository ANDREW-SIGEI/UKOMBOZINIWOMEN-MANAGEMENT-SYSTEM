from django import forms
from django.utils import timezone
from .models import Meeting, MeetingAttendance, MeetingAttachment
from user_management.models import Member, Group, FieldOfficer

class MeetingForm(forms.ModelForm):
    """Form for creating and editing meetings."""
    
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
    )
    
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        required=False
    )
    
    # For group selection
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control select2'}),
        required=False
    )
    
    # For selecting multiple members
    members = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False
    )
    
    # For selecting multiple field officers
    field_officers = forms.ModelMultipleChoiceField(
        queryset=FieldOfficer.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False
    )
    
    class Meta:
        model = Meeting
        fields = [
            'title', 'meeting_type', 'scheduled_date', 'start_time', 'end_time',
            'location', 'description', 'status', 'group', 'members', 'field_officers'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'meeting_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Validate that the meeting is not scheduled in the past
        if scheduled_date and start_time:
            meeting_datetime = timezone.make_aware(
                timezone.datetime.combine(scheduled_date, start_time)
            )
            if meeting_datetime < timezone.now():
                self.add_error('scheduled_date', 'Meeting cannot be scheduled in the past.')
        
        # Validate that end time is after start time
        if start_time and end_time and end_time <= start_time:
            self.add_error('end_time', 'End time must be after start time.')
        
        return cleaned_data


class MeetingAttendanceForm(forms.ModelForm):
    """Form for recording meeting attendance."""
    
    class Meta:
        model = MeetingAttendance
        fields = ['member', 'status', 'notes']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control select2'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class BulkAttendanceForm(forms.Form):
    """Form for bulk attendance marking."""
    
    ATTENDANCE_CHOICES = MeetingAttendance.ATTENDANCE_STATUS_CHOICES
    
    def __init__(self, meeting, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If the meeting has a specific group, get members from that group
        if meeting.group:
            members = meeting.group.members.all()
        else:
            # Otherwise, get members that were specifically invited
            members = meeting.members.all()
        
        # Create a field for each member
        for member in members:
            field_name = f"member_{member.id}"
            self.fields[field_name] = forms.ChoiceField(
                choices=self.ATTENDANCE_CHOICES,
                label=f"{member.full_name}",
                widget=forms.Select(attrs={'class': 'form-control attendance-select'}),
                initial='PRESENT'  # Default to present
            )
            
            # Add a notes field for each member
            notes_field_name = f"notes_{member.id}"
            self.fields[notes_field_name] = forms.CharField(
                required=False,
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 1, 'placeholder': 'Optional notes'}),
            )


class MeetingAttachmentForm(forms.ModelForm):
    """Form for uploading meeting attachments."""
    
    class Meta:
        model = MeetingAttachment
        fields = ['file', 'title', 'description']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        } 