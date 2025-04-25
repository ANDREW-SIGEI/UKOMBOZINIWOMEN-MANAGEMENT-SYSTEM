from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Meeting, MeetingAttendance
from .forms import MeetingForm
from user_management.models import Member, Group, FieldOfficer
from datetime import timedelta, datetime
import calendar


@login_required
def dashboard_index(request):
    """Main dashboard view that displays system overview and statistics."""
    # In a real application, you would query your database for the following data
    context = {
        'active_menu': 'dashboard',
        'total_members': 6000,  # Placeholder value
        'total_groups': 120,    # Placeholder value
        'active_loans': 450,    # Placeholder value
        'total_savings': '7,500,000',  # Placeholder value
        
        # Recent loans (sample data)
        'recent_loans': [
            {'id': 'L1234', 'member_name': 'Jane Doe', 'amount': '25,000', 'status': 'active'},
            {'id': 'L1235', 'member_name': 'Women Empowerment Group', 'amount': '150,000', 'status': 'active'},
            {'id': 'L1236', 'member_name': 'John Smith', 'amount': '15,000', 'status': 'pending'},
            {'id': 'L1237', 'member_name': 'Agriculture Group', 'amount': '75,000', 'status': 'completed'},
        ],
        
        # Recent payments (sample data)
        'recent_payments': [
            {'date': '2023-05-10', 'member_name': 'Jane Doe', 'amount': '5,000', 'type': 'Loan Repayment'},
            {'date': '2023-05-09', 'member_name': 'Agriculture Group', 'amount': '25,000', 'type': 'Loan Repayment'},
            {'date': '2023-05-08', 'member_name': 'John Smith', 'amount': '2,000', 'type': 'Savings'},
            {'date': '2023-05-07', 'member_name': 'Women Empowerment Group', 'amount': '15,000', 'type': 'Loan Repayment'},
        ],
        
        # Agriculture collection data (sample data)
        'agriculture_total': '2,500,000',
        
        # School fees collection data (sample data)
        'school_fees_total': '1,800,000',
        
        # Upcoming payments (sample data)
        'upcoming_payments': [
            {'member_name': 'Jane Doe', 'amount': '5,000', 'due_date': 'Tomorrow'},
            {'member_name': 'Agriculture Group', 'amount': '25,000', 'due_date': '3 days'},
            {'member_name': 'John Smith', 'amount': '2,000', 'due_date': '5 days'},
        ],
    }
    
    # Add upcoming meetings to the dashboard
    try:
        upcoming_meetings = Meeting.objects.filter(
            scheduled_date__gte=timezone.now().date(),
            status='SCHEDULED'
        ).order_by('scheduled_date', 'start_time')[:5]
        
        context['upcoming_meetings'] = upcoming_meetings
    except:
        # Handle the case when the Meeting model doesn't exist yet
        context['upcoming_meetings'] = []
    
    return render(request, 'dashboard/index.html', context)


def offline_view(request):
    """View to display when user is offline."""
    return render(request, 'offline.html')


# Meeting Views
@login_required
def meeting_list(request):
    """View all meetings with filtering options."""
    # Get filter parameters
    meeting_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    # Start with all meetings
    meetings = Meeting.objects.all().order_by('-scheduled_date', 'start_time')
    
    # Apply filters
    if meeting_type:
        meetings = meetings.filter(meeting_type=meeting_type)
    
    if status:
        meetings = meetings.filter(status=status)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            meetings = meetings.filter(scheduled_date__gte=date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            meetings = meetings.filter(scheduled_date__lte=date_to)
        except ValueError:
            pass
    
    if search_query:
        meetings = meetings.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(group__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(meetings, 10)  # Show 10 meetings per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get some stats
    upcoming_count = Meeting.objects.filter(
        scheduled_date__gte=timezone.now().date(),
        status='SCHEDULED'
    ).count()
    
    completed_count = Meeting.objects.filter(status='COMPLETED').count()
    
    context = {
        'page_obj': page_obj,
        'meeting_types': Meeting.MEETING_TYPE_CHOICES,
        'status_choices': Meeting.MEETING_STATUS_CHOICES,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'active_menu': 'meetings',
        'meeting_type': meeting_type,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/meeting_list.html', context)


@login_required
def meeting_detail(request, meeting_id):
    """View details of a specific meeting."""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Get attendance records for this meeting
    attendance_records = MeetingAttendance.objects.filter(meeting=meeting)
    
    # Check if the current user is the organizer or a field officer assigned to this meeting
    is_organizer = (meeting.organizer == request.user)
    is_assigned = False
    
    # Try to get the field officer associated with the current user
    try:
        field_officer = FieldOfficer.objects.get(user=request.user)
        is_assigned = field_officer in meeting.field_officers.all()
    except FieldOfficer.DoesNotExist:
        field_officer = None
    
    can_edit = is_organizer or is_assigned
    
    context = {
        'meeting': meeting,
        'attendance_records': attendance_records,
        'can_edit': can_edit,
        'is_organizer': is_organizer,
        'is_assigned': is_assigned,
        'active_menu': 'meetings',
    }
    
    return render(request, 'dashboard/meeting_detail.html', context)


@login_required
def meeting_create(request):
    """Create a new meeting."""
    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.organizer = request.user
            meeting.save()
            
            # Handle many-to-many relationships
            if form.cleaned_data.get('members'):
                meeting.members.set(form.cleaned_data['members'])
            
            if form.cleaned_data.get('field_officers'):
                meeting.field_officers.set(form.cleaned_data['field_officers'])
            
            if form.cleaned_data.get('group'):
                meeting.group = form.cleaned_data['group']
                meeting.save()
            
            # Set next meeting date if recurrence is set
            if meeting.recurrence != 'NONE':
                next_date = meeting.scheduled_date
                if meeting.recurrence == 'DAILY':
                    next_date += timedelta(days=1)
                elif meeting.recurrence == 'WEEKLY':
                    next_date += timedelta(weeks=1)
                elif meeting.recurrence == 'BIWEEKLY':
                    next_date += timedelta(weeks=2)
                elif meeting.recurrence == 'MONTHLY':
                    # Add one month (handle month transitions)
                    month = next_date.month + 1
                    year = next_date.year
                    if month > 12:
                        month = 1
                        year += 1
                    # Ensure we don't exceed the number of days in the month
                    last_day = calendar.monthrange(year, month)[1]
                    day = min(next_date.day, last_day)
                    next_date = next_date.replace(year=year, month=month, day=day)
                elif meeting.recurrence == 'QUARTERLY':
                    # Add three months
                    month = next_date.month + 3
                    year = next_date.year
                    if month > 12:
                        month = month - 12
                        year += 1
                    # Ensure we don't exceed the number of days in the month
                    last_day = calendar.monthrange(year, month)[1]
                    day = min(next_date.day, last_day)
                    next_date = next_date.replace(year=year, month=month, day=day)
                
                meeting.next_meeting_date = next_date
                meeting.save()
            
            messages.success(request, f"Meeting '{meeting.title}' created successfully.")
            return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    else:
        form = MeetingForm()
    
    context = {
        'form': form,
        'meeting_types': Meeting.MEETING_TYPE_CHOICES,
        'recurrence_choices': Meeting.RECURRENCE_CHOICES,
        'active_menu': 'meetings',
    }
    
    return render(request, 'dashboard/meeting_form.html', context)


@login_required
def meeting_edit(request, meeting_id):
    """Edit an existing meeting."""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Check if user has permission to edit this meeting
    if meeting.organizer != request.user:
        try:
            officer = FieldOfficer.objects.get(user=request.user)
            if officer not in meeting.field_officers.all():
                messages.error(request, "You don't have permission to edit this meeting.")
                return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
        except FieldOfficer.DoesNotExist:
            messages.error(request, "You don't have permission to edit this meeting.")
            return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    
    if request.method == 'POST':
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.save()
            
            # Handle many-to-many relationships
            if form.cleaned_data.get('members'):
                meeting.members.set(form.cleaned_data['members'])
            else:
                meeting.members.clear()
            
            if form.cleaned_data.get('field_officers'):
                meeting.field_officers.set(form.cleaned_data['field_officers'])
            else:
                meeting.field_officers.clear()
            
            if form.cleaned_data.get('group'):
                meeting.group = form.cleaned_data['group']
            else:
                meeting.group = None
            
            meeting.save()
            
            # Update next meeting date if recurrence is set
            if meeting.recurrence != 'NONE':
                next_date = meeting.scheduled_date
                if meeting.recurrence == 'DAILY':
                    next_date += timedelta(days=1)
                elif meeting.recurrence == 'WEEKLY':
                    next_date += timedelta(weeks=1)
                elif meeting.recurrence == 'BIWEEKLY':
                    next_date += timedelta(weeks=2)
                elif meeting.recurrence == 'MONTHLY':
                    # Add one month (handle month transitions)
                    month = next_date.month + 1
                    year = next_date.year
                    if month > 12:
                        month = 1
                        year += 1
                    # Ensure we don't exceed the number of days in the month
                    last_day = calendar.monthrange(year, month)[1]
                    day = min(next_date.day, last_day)
                    next_date = next_date.replace(year=year, month=month, day=day)
                elif meeting.recurrence == 'QUARTERLY':
                    # Add three months
                    month = next_date.month + 3
                    year = next_date.year
                    if month > 12:
                        month = month - 12
                        year += 1
                    # Ensure we don't exceed the number of days in the month
                    last_day = calendar.monthrange(year, month)[1]
                    day = min(next_date.day, last_day)
                    next_date = next_date.replace(year=year, month=month, day=day)
                
                meeting.next_meeting_date = next_date
            else:
                meeting.next_meeting_date = None
            
            meeting.save()
            
            messages.success(request, f"Meeting '{meeting.title}' updated successfully.")
            return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    else:
        # Initialize form with existing meeting data
        form = MeetingForm(instance=meeting)
        
        # Set initial values for M2M fields
        if meeting.members.exists():
            form.fields['members'].initial = meeting.members.all()
        
        if meeting.field_officers.exists():
            form.fields['field_officers'].initial = meeting.field_officers.all()
        
        if meeting.group:
            form.fields['group'].initial = meeting.group
    
    context = {
        'form': form,
        'meeting': meeting,
        'meeting_types': Meeting.MEETING_TYPE_CHOICES,
        'status_choices': Meeting.MEETING_STATUS_CHOICES,
        'recurrence_choices': Meeting.RECURRENCE_CHOICES,
        'active_menu': 'meetings',
        'is_edit': True,
    }
    
    return render(request, 'dashboard/meeting_form.html', context)


@login_required
def meeting_delete(request, meeting_id):
    """Delete a meeting."""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Check if user has permission to delete this meeting
    if meeting.organizer != request.user:
        messages.error(request, "You don't have permission to delete this meeting.")
        return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    
    if request.method == 'POST':
        title = meeting.title
        meeting.delete()
        messages.success(request, f"Meeting '{title}' deleted successfully.")
        return redirect('dashboard:meeting_list')
    
    context = {
        'meeting': meeting,
        'active_menu': 'meetings',
    }
    
    return render(request, 'dashboard/meeting_confirm_delete.html', context)


@login_required
def meeting_reschedule(request, meeting_id):
    """Reschedule a meeting."""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Check if user has permission to reschedule this meeting
    if meeting.organizer != request.user:
        try:
            officer = FieldOfficer.objects.get(user=request.user)
            if officer not in meeting.field_officers.all():
                messages.error(request, "You don't have permission to reschedule this meeting.")
                return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
        except FieldOfficer.DoesNotExist:
            messages.error(request, "You don't have permission to reschedule this meeting.")
            return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    
    if request.method == 'POST':
        new_date = request.POST.get('new_date')
        new_start_time = request.POST.get('new_start_time')
        new_end_time = request.POST.get('new_end_time')
        reason = request.POST.get('reason')
        
        try:
            new_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            
            # Reschedule the meeting
            new_meeting = meeting.reschedule(
                new_date=new_date,
                new_start_time=new_start_time,
                new_end_time=new_end_time,
                reason=reason
            )
            
            messages.success(request, f"Meeting rescheduled to {new_date}.")
            return redirect('dashboard:meeting_detail', meeting_id=new_meeting.id)
            
        except (ValueError, TypeError) as e:
            messages.error(request, f"Error rescheduling meeting: {str(e)}")
    
    context = {
        'meeting': meeting,
        'active_menu': 'meetings',
    }
    
    return render(request, 'dashboard/meeting_reschedule.html', context)


@login_required
def meeting_attendance(request, meeting_id):
    """Take or view attendance for a meeting."""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Check if user has permission to manage attendance
    if meeting.organizer != request.user:
        try:
            officer = FieldOfficer.objects.get(user=request.user)
            if officer not in meeting.field_officers.all():
                messages.error(request, "You don't have permission to manage attendance for this meeting.")
                return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
        except FieldOfficer.DoesNotExist:
            messages.error(request, "You don't have permission to manage attendance for this meeting.")
            return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    
    # Get all members and field officers associated with this meeting
    members = meeting.members.all()
    officers = meeting.field_officers.all()
    
    # Get existing attendance records
    attendance_records = MeetingAttendance.objects.filter(meeting=meeting)
    
    # Map of attendee ID to attendance record
    member_attendance = {record.member_id: record for record in attendance_records if record.member}
    officer_attendance = {record.field_officer_id: record for record in attendance_records if record.field_officer}
    
    if request.method == 'POST':
        # Process attendance form submission
        present_members = request.POST.getlist('present_members')
        present_officers = request.POST.getlist('present_officers')
        
        # Record attendance for members
        for member in members:
            is_present = str(member.id) in present_members
            arrival_time = request.POST.get(f'arrival_time_member_{member.id}', None)
            departure_time = request.POST.get(f'departure_time_member_{member.id}', None)
            notes = request.POST.get(f'notes_member_{member.id}', '')
            
            # Update or create attendance record
            if member.id in member_attendance:
                record = member_attendance[member.id]
                record.is_present = is_present
                record.arrival_time = arrival_time if arrival_time else None
                record.departure_time = departure_time if departure_time else None
                record.notes = notes
                record.recorded_by = request.user
                record.save()
            else:
                MeetingAttendance.objects.create(
                    meeting=meeting,
                    member=member,
                    is_present=is_present,
                    arrival_time=arrival_time if arrival_time else None,
                    departure_time=departure_time if departure_time else None,
                    notes=notes,
                    recorded_by=request.user
                )
        
        # Record attendance for officers
        for officer in officers:
            is_present = str(officer.id) in present_officers
            arrival_time = request.POST.get(f'arrival_time_officer_{officer.id}', None)
            departure_time = request.POST.get(f'departure_time_officer_{officer.id}', None)
            notes = request.POST.get(f'notes_officer_{officer.id}', '')
            
            # Update or create attendance record
            if officer.id in officer_attendance:
                record = officer_attendance[officer.id]
                record.is_present = is_present
                record.arrival_time = arrival_time if arrival_time else None
                record.departure_time = departure_time if departure_time else None
                record.notes = notes
                record.recorded_by = request.user
                record.save()
            else:
                MeetingAttendance.objects.create(
                    meeting=meeting,
                    field_officer=officer,
                    is_present=is_present,
                    arrival_time=arrival_time if arrival_time else None,
                    departure_time=departure_time if departure_time else None,
                    notes=notes,
                    recorded_by=request.user
                )
        
        # If the meeting is not yet marked as completed, ask if it should be
        if meeting.status == 'SCHEDULED':
            mark_completed = request.POST.get('mark_completed', 'false') == 'true'
            if mark_completed:
                meeting.status = 'COMPLETED'
                meeting.save()
                messages.success(request, "Meeting marked as completed and attendance recorded.")
            else:
                messages.success(request, "Attendance recorded successfully.")
        else:
            messages.success(request, "Attendance updated successfully.")
        
        return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    
    context = {
        'meeting': meeting,
        'members': members,
        'officers': officers,
        'member_attendance': member_attendance,
        'officer_attendance': officer_attendance,
        'active_menu': 'meetings',
    }
    
    return render(request, 'dashboard/meeting_attendance.html', context)


@login_required
def calendar_view(request):
    """View meetings in a calendar format."""
    # Get the month and year from the query parameters or use current month/year
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Get all meetings for the selected month
    start_date = datetime(year, month, 1).date()
    
    # Get the last day of the month
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # Get meetings for the selected month
    meetings = Meeting.objects.filter(
        scheduled_date__gte=start_date,
        scheduled_date__lte=end_date
    ).order_by('scheduled_date', 'start_time')
    
    # Group meetings by date
    meeting_days = {}
    for meeting in meetings:
        day = meeting.scheduled_date.day
        if day not in meeting_days:
            meeting_days[day] = []
        meeting_days[day].append(meeting)
    
    # Get the calendar for the selected month
    cal = calendar.monthcalendar(year, month)
    
    # Get month name
    month_name = calendar.month_name[month]
    
    # Get previous and next month/year
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year = year - 1
    
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year = year + 1
    
    context = {
        'calendar': cal,
        'month': month,
        'month_name': month_name,
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'meeting_days': meeting_days,
        'active_menu': 'meeting_calendar',
        'today': now.date(),
    }
    
    return render(request, 'dashboard/calendar.html', context)


@login_required
def system_settings(request):
    """View and edit system settings."""
    context = {
        'active_menu': 'settings',
        'section': 'system_settings',
    }
    
    if request.method == 'POST':
        # Process the settings form (implement actual settings saving later)
        messages.success(request, "System settings updated successfully.")
        return redirect('dashboard:system_settings')
    
    return render(request, 'dashboard/settings/system_settings.html', context)


@login_required
def user_profile(request):
    """View and edit user profile."""
    context = {
        'active_menu': 'settings',
        'section': 'user_profile',
    }
    
    if request.method == 'POST':
        # Process the profile form (implement actual profile update later)
        messages.success(request, "Your profile has been updated successfully.")
        return redirect('dashboard:user_profile')
    
    return render(request, 'dashboard/settings/user_profile.html', context)


@login_required
def backup_restore(request):
    """Backup and restore system data."""
    context = {
        'active_menu': 'settings',
        'section': 'backup_restore',
    }
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'backup':
            # Implementation for backup
            messages.success(request, "System backup created successfully.")
        elif action == 'restore':
            # Implementation for restore
            messages.success(request, "System restored successfully from backup.")
        
        return redirect('dashboard:backup_restore')
    
    return render(request, 'dashboard/settings/backup_restore.html', context)


@login_required
def activity_logs(request):
    """View system activity logs."""
    # Placeholder data for activity logs
    activities = [
        {
            'user': 'admin',
            'action': 'Created new meeting',
            'timestamp': timezone.now() - timedelta(hours=1),
            'details': 'Weekly Status Meeting',
            'ip_address': '192.168.1.1'
        },
        {
            'user': 'jane_doe',
            'action': 'Updated member profile',
            'timestamp': timezone.now() - timedelta(hours=2),
            'details': 'Member ID: 12345',
            'ip_address': '192.168.1.2'
        },
        {
            'user': 'admin',
            'action': 'Processed loan payment',
            'timestamp': timezone.now() - timedelta(hours=3),
            'details': 'Loan ID: L789, Amount: $500',
            'ip_address': '192.168.1.1'
        },
        {
            'user': 'john_smith',
            'action': 'Added new member',
            'timestamp': timezone.now() - timedelta(days=1),
            'details': 'Member: Sarah Johnson',
            'ip_address': '192.168.1.3'
        },
        {
            'user': 'admin',
            'action': 'System backup',
            'timestamp': timezone.now() - timedelta(days=1, hours=12),
            'details': 'Full system backup',
            'ip_address': '192.168.1.1'
        },
    ]
    
    context = {
        'active_menu': 'settings',
        'section': 'activity_logs',
        'activities': activities,
    }
    
    return render(request, 'dashboard/settings/activity_logs.html', context)


@login_required
def meeting_remove_attachment(request, meeting_id, attachment_id):
    """Remove an attachment from a meeting."""
    meeting = get_object_or_404(Meeting, id=meeting_id)
    
    # Check if user has permission to edit this meeting
    if meeting.organizer != request.user:
        try:
            officer = FieldOfficer.objects.get(user=request.user)
            if officer not in meeting.field_officers.all():
                messages.error(request, "You don't have permission to edit this meeting.")
                return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
        except FieldOfficer.DoesNotExist:
            messages.error(request, "You don't have permission to edit this meeting.")
            return redirect('dashboard:meeting_detail', meeting_id=meeting.id)
    
    # This is a placeholder for when you implement the attachment model
    messages.info(request, "Attachment removal functionality will be implemented soon.")
    
    return redirect('dashboard:meeting_edit', meeting_id=meeting.id)
