from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('offline/', views.offline_view, name='offline'),
    
    # Meeting URLs
    path('meetings/', views.meeting_list, name='meeting_list'),
    path('meetings/calendar/', views.calendar_view, name='meeting_calendar'),
    path('meetings/create/', views.meeting_create, name='meeting_create'),
    path('meetings/<int:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('meetings/<int:meeting_id>/edit/', views.meeting_edit, name='meeting_edit'),
    path('meetings/<int:meeting_id>/delete/', views.meeting_delete, name='meeting_delete'),
    path('meetings/<int:meeting_id>/reschedule/', views.meeting_reschedule, name='meeting_reschedule'),
    path('meetings/<int:meeting_id>/attendance/', views.meeting_attendance, name='meeting_attendance'),
    path('meetings/<int:meeting_id>/remove-attachment/<int:attachment_id>/', views.meeting_remove_attachment, name='meeting_remove_attachment'),
    path('meetings/<int:meeting_id>/details/', views.meeting_details_ajax, name='meeting_details_ajax'),
    
    # Settings and system URLs
    path('settings/', views.system_settings, name='system_settings'),
    path('profile/', views.user_profile, name='user_profile'),
    path('backup-restore/', views.backup_restore, name='backup_restore'),
    path('activity-logs/', views.activity_logs, name='activity_logs'),
] 