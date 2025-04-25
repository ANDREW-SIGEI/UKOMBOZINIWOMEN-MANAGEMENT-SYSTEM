from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from user_management.models import Member, Group, FieldOfficer

class Meeting(models.Model):
    """Model for scheduling group and member meetings."""
    MEETING_STATUS_CHOICES = (
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
        ('POSTPONED', 'Postponed'),
    )
    
    MEETING_TYPE_CHOICES = (
        ('GROUP', 'Group Meeting'),
        ('FIELD_VISIT', 'Field Visit'),
        ('TRAINING', 'Training Session'),
        ('COMMITTEE', 'Committee Meeting'),
        ('GENERAL', 'General Meeting'),
        ('OTHER', 'Other'),
    )
    
    RECURRENCE_CHOICES = (
        ('NONE', 'None'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Bi-weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
    )
    
    # Basic meeting information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='GROUP')
    location = models.CharField(max_length=200)
    
    # Date and time
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Status and recurrence
    status = models.CharField(max_length=20, choices=MEETING_STATUS_CHOICES, default='SCHEDULED')
    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='NONE')
    next_meeting_date = models.DateField(blank=True, null=True)
    
    # Relations to participants
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, 
                            related_name='group_meetings')
    members = models.ManyToManyField(Member, related_name='meetings', blank=True)
    field_officers = models.ManyToManyField(FieldOfficer, related_name='meetings', blank=True)
    
    # Tracking
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    previous_meeting = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='next_meetings')
    
    # Agenda and minutes
    agenda = models.TextField(blank=True, null=True)
    minutes = models.TextField(blank=True, null=True)
    
    # Notifications
    reminder_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-scheduled_date', 'start_time']
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"
    
    def reschedule(self, new_date, new_start_time=None, new_end_time=None, reason=None):
        """Reschedule this meeting and create a new one."""
        # Keep a reference to the original meeting
        original_meeting = self
        
        # Update the status of the original meeting
        self.status = 'RESCHEDULED'
        if reason:
            self.description += f"\n\nRescheduled reason: {reason}"
        self.save()
        
        # Create a new meeting with the same attributes but different date/time
        new_meeting = Meeting.objects.create(
            title=self.title,
            description=self.description,
            meeting_type=self.meeting_type,
            location=self.location,
            scheduled_date=new_date,
            start_time=new_start_time or self.start_time,
            end_time=new_end_time or self.end_time,
            status='SCHEDULED',
            recurrence=self.recurrence,
            organizer=self.organizer,
            group=self.group,
            previous_meeting=self,
            agenda=self.agenda,
        )
        
        # Copy the M2M relationships
        for member in self.members.all():
            new_meeting.members.add(member)
        
        for officer in self.field_officers.all():
            new_meeting.field_officers.add(officer)
        
        return new_meeting
    
    def get_attendees_count(self):
        """Get the total count of attendees (members + field officers)."""
        return self.members.count() + self.field_officers.count()
    
    def is_upcoming(self):
        """Check if the meeting is upcoming."""
        return self.scheduled_date >= timezone.now().date() and self.status == 'SCHEDULED'
    
    def is_past_due(self):
        """Check if the meeting is past due."""
        return self.scheduled_date < timezone.now().date() and self.status == 'SCHEDULED'

class MeetingAttendance(models.Model):
    """Records attendance for meetings."""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True)
    field_officer = models.ForeignKey(FieldOfficer, on_delete=models.CASCADE, null=True, blank=True)
    is_present = models.BooleanField(default=False)
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        unique_together = [['meeting', 'member'], ['meeting', 'field_officer']]
        
    def __str__(self):
        attendee = self.member.get_full_name() if self.member else self.field_officer.user.get_full_name()
        status = "Present" if self.is_present else "Absent"
        return f"{attendee} - {self.meeting.title} - {status}"

class AgendaItem(models.Model):
    """Individual agenda items for meetings."""
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='agenda_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    time_allocation = models.IntegerField(help_text="Time in minutes", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_date']
        
    def __str__(self):
        return f"{self.title} - {self.meeting.title}"
