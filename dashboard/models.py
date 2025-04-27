from django.db import models
from django.contrib.auth.models import User
from user_management.models import Member, Group, FieldOfficer

class Meeting(models.Model):
    """Model representing a meeting for Ukombozini Women groups."""
    
    MEETING_TYPE_CHOICES = [
        ('GENERAL', 'General Meeting'),
        ('EXECUTIVE', 'Executive Meeting'),
        ('TRAINING', 'Training Session'),
        ('FIELD_VISIT', 'Field Visit'),
        ('PROJECT', 'Project Meeting'),
        ('OTHER', 'Other')
    ]
    
    MEETING_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('POSTPONED', 'Postponed')
    ]
    
    RECURRENCE_CHOICES = [
        ('NONE', 'No Recurrence'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Biweekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly')
    ]
    
    title = models.CharField(max_length=255)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES, default='GENERAL')
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=MEETING_STATUS_CHOICES, default='SCHEDULED')
    recurrence = models.CharField(max_length=25, choices=RECURRENCE_CHOICES, default='NONE')
    next_meeting_date = models.DateField(null=True, blank=True)
    
    # Relations
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_meetings')
    members = models.ManyToManyField(Member, blank=True, related_name='meetings')
    field_officers = models.ManyToManyField(FieldOfficer, blank=True, related_name='assigned_meetings')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name='meetings')
    
    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Meeting notes and attachments
    minutes = models.TextField(blank=True)
    
    # Agenda items stored as JSON
    agenda_items = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-scheduled_date', 'start_time']


class MeetingAttendance(models.Model):
    """Model to track member attendance at meetings."""
    
    ATTENDANCE_STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('EXCUSED', 'Excused'),
        ('LATE', 'Late')
    ]
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attendance_records')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default='ABSENT')
    time_recorded = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_attendance')
    
    class Meta:
        unique_together = ['meeting', 'member']
        
    def __str__(self):
        return f"{self.member.full_name} - {self.meeting.title} - {self.status}"


class MeetingAttachment(models.Model):
    """Model for meeting attachments like documents, photos, etc."""
    
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='meeting_attachments/')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title 