from django.contrib import admin

# Import models only if they exist
try:
    from .models import Notification, Activity, SystemLog, Meeting, MeetingAttendance, AgendaItem
    
    @admin.register(Notification)
    class NotificationAdmin(admin.ModelAdmin):
        list_display = ('user', 'title', 'created_date', 'notification_type', 'is_read')
        list_filter = ('notification_type', 'is_read', 'created_date')
        search_fields = ('title', 'message', 'user__username', 'user__email')
        date_hierarchy = 'created_date'
        raw_id_fields = ('user',)
        readonly_fields = ('created_date',)
    
    @admin.register(Activity)
    class ActivityAdmin(admin.ModelAdmin):
        list_display = ('user', 'activity_type', 'activity_date', 'ip_address')
        list_filter = ('activity_type', 'activity_date')
        search_fields = ('user__username', 'user__email', 'description')
        date_hierarchy = 'activity_date'
        raw_id_fields = ('user',)
        readonly_fields = ('activity_date', 'ip_address')
    
    @admin.register(SystemLog)
    class SystemLogAdmin(admin.ModelAdmin):
        list_display = ('log_level', 'component', 'timestamp', 'summary')
        list_filter = ('log_level', 'component', 'timestamp')
        search_fields = ('summary', 'details')
        date_hierarchy = 'timestamp'
        readonly_fields = ('timestamp',)
    
    @admin.register(Meeting)
    class MeetingAdmin(admin.ModelAdmin):
        list_display = ('title', 'scheduled_date', 'start_time', 'end_time', 'meeting_type', 
                       'location', 'status', 'recurrence', 'get_attendees_count')
        list_filter = ('meeting_type', 'status', 'recurrence', 'scheduled_date')
        search_fields = ('title', 'description', 'location', 'agenda')
        date_hierarchy = 'scheduled_date'
        raw_id_fields = ('organizer', 'group', 'previous_meeting')
        filter_horizontal = ('members', 'field_officers')
        readonly_fields = ('created_date', 'modified_date')
        
        fieldsets = (
            ('Meeting Information', {
                'fields': ('title', 'description', 'meeting_type', 'location')
            }),
            ('Schedule', {
                'fields': ('scheduled_date', 'start_time', 'end_time', 'status', 
                          'recurrence', 'next_meeting_date')
            }),
            ('Participants', {
                'fields': ('organizer', 'group', 'members', 'field_officers')
            }),
            ('Content', {
                'fields': ('agenda', 'minutes')
            }),
            ('Related', {
                'fields': ('previous_meeting',)
            }),
            ('System', {
                'fields': ('created_date', 'modified_date', 'reminder_sent'),
                'classes': ('collapse',)
            }),
        )
        
        def get_attendees_count(self, obj):
            return obj.get_attendees_count()
        get_attendees_count.short_description = 'Attendees'
    
    @admin.register(MeetingAttendance)
    class MeetingAttendanceAdmin(admin.ModelAdmin):
        list_display = ('meeting', 'get_attendee_name', 'is_present', 'arrival_time', 
                       'departure_time', 'recorded_by')
        list_filter = ('is_present', 'meeting__scheduled_date', 'meeting__meeting_type')
        search_fields = ('meeting__title', 'member__first_name', 'member__last_name', 
                        'field_officer__user__first_name', 'field_officer__user__last_name')
        raw_id_fields = ('meeting', 'member', 'field_officer', 'recorded_by')
        
        def get_attendee_name(self, obj):
            if obj.member:
                return f"{obj.member.get_full_name()} (Member)"
            elif obj.field_officer:
                return f"{obj.field_officer.user.get_full_name()} (Officer)"
            return "Unknown"
        get_attendee_name.short_description = 'Attendee'
    
    @admin.register(AgendaItem)
    class AgendaItemAdmin(admin.ModelAdmin):
        list_display = ('title', 'meeting', 'time_allocation', 'order', 'created_date')
        list_filter = ('meeting__scheduled_date', 'created_date')
        search_fields = ('title', 'description', 'meeting__title')
        raw_id_fields = ('meeting',)
        readonly_fields = ('created_date', 'modified_date')

except ImportError:
    # Models are not defined yet or have different names
    pass
