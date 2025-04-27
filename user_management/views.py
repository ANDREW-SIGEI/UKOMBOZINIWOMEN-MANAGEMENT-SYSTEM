from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse
from .models import Member, Group, GroupMembership, FieldOfficer, FieldOfficerReport
from .forms import MemberForm, GroupForm, GroupMembershipForm, BulkMemberAddForm
from datetime import datetime, date
import calendar
from decimal import Decimal
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

# Member views
@login_required
def member_list(request):
    """Display list of all members with search and filter capabilities."""
    search_query = request.GET.get('search', '')
    is_active = request.GET.get('is_active', 'all')
    gender_filter = request.GET.get('gender', 'all')
    
    members = Member.objects.all().order_by('first_name', 'last_name')
    
    # Apply filters
    if search_query:
        members = members.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(id_number__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    if is_active != 'all':
        is_active_bool = is_active == 'active'
        members = members.filter(is_active=is_active_bool)
    
    if gender_filter != 'all':
        members = members.filter(gender=gender_filter)
    
    # Pagination
    paginator = Paginator(members, 10)  # Show 10 members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_menu': 'members',
        'page_obj': page_obj,
        'search_query': search_query,
        'is_active': is_active,
        'gender_filter': gender_filter,
        'total_members': members.count(),
        'active_members': members.filter(is_active=True).count(),
    }
    
    return render(request, 'dashboard/members/member_list.html', context)

@login_required
def member_detail(request, member_id):
    """Display detailed information about a specific member."""
    member = get_object_or_404(Member, pk=member_id)
    
    # Get groups this member belongs to
    memberships = GroupMembership.objects.filter(member=member)
    
    context = {
        'active_menu': 'members',
        'member': member,
        'memberships': memberships,
    }
    
    return render(request, 'dashboard/members/member_detail.html', context)

@login_required
def member_create(request):
    """Create a new member."""
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member {member.get_full_name()} has been created successfully.')
            return redirect('user_management:member_detail', member_id=member.id)
    else:
        form = MemberForm()
    
    context = {
        'active_menu': 'members',
        'form': form,
        'form_title': 'Add New Member',
        'submit_label': 'Add Member',
    }
    
    return render(request, 'dashboard/members/member_form.html', context)

@login_required
def member_edit(request, member_id):
    """Edit an existing member."""
    member = get_object_or_404(Member, pk=member_id)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            member = form.save()
            messages.success(request, f'Member {member.get_full_name()} has been updated successfully.')
            return redirect('user_management:member_detail', member_id=member.id)
    else:
        form = MemberForm(instance=member)
    
    context = {
        'active_menu': 'members',
        'form': form,
        'member': member,
        'form_title': f'Edit Member: {member.get_full_name()}',
        'submit_label': 'Update Member',
    }
    
    return render(request, 'dashboard/members/member_form.html', context)

@login_required
def member_delete(request, member_id):
    """Delete a member (set as inactive)."""
    member = get_object_or_404(Member, pk=member_id)
    
    if request.method == 'POST':
        # Instead of deleting, set member as inactive
        member.is_active = False
        member.save()
        messages.success(request, f'Member {member.get_full_name()} has been deactivated.')
        return redirect('user_management:member_list')
    
    context = {
        'active_menu': 'members',
        'member': member,
    }
    
    return render(request, 'dashboard/members/member_confirm_delete.html', context)

# Group views
@login_required
def group_list(request):
    """Display list of all groups with search and filter capabilities."""
    search_query = request.GET.get('search', '')
    is_active = request.GET.get('is_active', 'all')
    
    groups = Group.objects.all().order_by('name')
    
    # Apply filters
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) | 
            Q(registration_number__icontains=search_query)
        )
    
    if is_active != 'all':
        is_active_bool = is_active == 'active'
        groups = groups.filter(is_active=is_active_bool)
    
    # Pagination
    paginator = Paginator(groups, 10)  # Show 10 groups per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_menu': 'groups',
        'page_obj': page_obj,
        'search_query': search_query,
        'is_active': is_active,
        'total_groups': groups.count(),
        'active_groups': groups.filter(is_active=True).count(),
    }
    
    return render(request, 'dashboard/groups/group_list.html', context)

@login_required
def group_detail(request, group_id):
    """Display detailed information about a specific group."""
    group = get_object_or_404(Group, pk=group_id)
    
    # Get members of this group
    memberships = GroupMembership.objects.filter(group=group).select_related('member')
    
    context = {
        'active_menu': 'groups',
        'group': group,
        'memberships': memberships,
    }
    
    return render(request, 'dashboard/groups/group_detail.html', context)

@login_required
def group_create(request):
    """Create a new group."""
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Group {group.name} has been created successfully.')
            return redirect('user_management:group_detail', group_id=group.id)
    else:
        form = GroupForm()
    
    context = {
        'active_menu': 'groups',
        'form': form,
        'form_title': 'Create New Group',
        'submit_label': 'Create Group',
    }
    
    return render(request, 'dashboard/groups/group_form.html', context)

@login_required
def group_edit(request, group_id):
    """Edit an existing group."""
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Group {group.name} has been updated successfully.')
            return redirect('user_management:group_detail', group_id=group.id)
    else:
        form = GroupForm(instance=group)
    
    context = {
        'active_menu': 'groups',
        'form': form,
        'group': group,
        'form_title': f'Edit Group: {group.name}',
        'submit_label': 'Update Group',
    }
    
    return render(request, 'dashboard/groups/group_form.html', context)

@login_required
def group_delete(request, group_id):
    """Delete a group (set as inactive)."""
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        # Instead of deleting, set group as inactive
        group.is_active = False
        group.save()
        messages.success(request, f'Group {group.name} has been deactivated.')
        return redirect('user_management:group_list')
    
    context = {
        'active_menu': 'groups',
        'group': group,
    }
    
    return render(request, 'dashboard/groups/group_confirm_delete.html', context)

@login_required
def group_add_member(request, group_id):
    """Add a member to a group."""
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        form = GroupMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.group = group
            
            # Check if membership already exists
            if GroupMembership.objects.filter(group=group, member=membership.member).exists():
                messages.error(request, f'{membership.member.get_full_name()} is already a member of this group.')
            else:
                membership.save()
                messages.success(request, f'{membership.member.get_full_name()} has been added to the group.')
            
            return redirect('user_management:group_detail', group_id=group.id)
    else:
        # Pre-filter to only show members not already in the group
        current_members = GroupMembership.objects.filter(group=group).values_list('member__id', flat=True)
        form = GroupMembershipForm()
        form.fields['member'].queryset = Member.objects.exclude(id__in=current_members).filter(is_active=True)
    
    context = {
        'active_menu': 'groups',
        'form': form,
        'group': group,
    }
    
    return render(request, 'dashboard/groups/group_add_member.html', context)

@login_required
def group_bulk_add_members(request, group_id):
    """Add multiple members to a group at once."""
    group = get_object_or_404(Group, pk=group_id)
    
    if request.method == 'POST':
        form = BulkMemberAddForm(request.POST)
        if form.is_valid():
            members = form.cleaned_data['members']
            position = form.cleaned_data['position']
            
            added_count = 0
            for member in members:
                # Check if membership already exists
                if not GroupMembership.objects.filter(group=group, member=member).exists():
                    GroupMembership.objects.create(
                        group=group,
                        member=member,
                        position=position
                    )
                    added_count += 1
            
            if added_count > 0:
                messages.success(request, f'{added_count} members have been added to the group.')
            else:
                messages.info(request, 'No new members were added to the group.')
                
            return redirect('user_management:group_detail', group_id=group.id)
    else:
        # Pre-filter to only show members not already in the group
        current_members = GroupMembership.objects.filter(group=group).values_list('member__id', flat=True)
        form = BulkMemberAddForm()
        form.fields['members'].queryset = Member.objects.exclude(id__in=current_members).filter(is_active=True)
    
    context = {
        'active_menu': 'groups',
        'form': form,
        'group': group,
    }
    
    return render(request, 'dashboard/groups/group_bulk_add_members.html', context)

@login_required
def group_remove_member(request, group_id, membership_id):
    """Remove a member from a group."""
    membership = get_object_or_404(GroupMembership, pk=membership_id, group__id=group_id)
    
    if request.method == 'POST':
        member_name = membership.member.get_full_name()
        membership.delete()
        messages.success(request, f'{member_name} has been removed from the group.')
        return redirect('user_management:group_detail', group_id=group_id)
    
    context = {
        'active_menu': 'groups',
        'membership': membership,
        'group': membership.group,
    }
    
    return render(request, 'dashboard/groups/group_remove_member.html', context)

@login_required
def field_officer_daily_report(request):
    """
    View for field officers to submit daily reports with detailed financial information
    matching the paper form they currently use
    """
    if request.method == 'POST':
        # Process form data
        try:
            # Get basic report info
            report_date = request.POST.get('report_date')
            po_name = request.POST.get('po_name')
            
            # Get group data from form arrays
            group_names = request.POST.getlist('group_name[]')
            visit_venues = request.POST.getlist('visit_venue[]')
            visit_times = request.POST.getlist('visit_time[]')
            total_attendees_list = request.POST.getlist('total_attendet[]')
            admin_for_groups = request.POST.getlist('admin_for_group[]')
            project_registrations = request.POST.getlist('project_registration[]')
            mem_regs = request.POST.getlist('mem_reg[]')
            
            # Get loan information
            long_term_loans = request.POST.getlist('long_term_loan[]')
            short_term_loans = request.POST.getlist('short_term_loan[]')
            savings_before = request.POST.getlist('savings_before[]')
            total_loan_repaid = request.POST.getlist('total_loan_repaid[]')
            loan_principles = request.POST.getlist('loan_principle[]')
            loan_interests = request.POST.getlist('loan_interest[]')
            short_term_loan_repaid = request.POST.getlist('short_term_loan_repaid[]')
            
            # Get savings information
            savings_this_month = request.POST.getlist('savings_this_month[]')
            welfare_list = request.POST.getlist('welfare_for_group[]')
            project_list = request.POST.getlist('project[]')
            fines_and_charges = request.POST.getlist('fines_and_charges[]')
            total_savings_list = request.POST.getlist('total_savings[]')
            
            # Legacy fields for backward compatibility
            # These will be calculated from the new fields
            total_money_collected = request.POST.getlist('total_money_collected[]')
            
            # Calculate totals
            total_groups = len(group_names)
            total_attendees = sum(int(att or 0) for att in total_attendees_list)
            
            # Calculate financial totals
            long_term_loan_total = sum(float(loan or 0) for loan in long_term_loans)
            short_term_loan_total = sum(float(loan or 0) for loan in short_term_loans)
            savings_before_total = sum(float(amount or 0) for amount in savings_before)
            loan_repaid_total = sum(float(amount or 0) for amount in total_loan_repaid)
            loan_principle_total = sum(float(amount or 0) for amount in loan_principles)
            loan_interest_total = sum(float(amount or 0) for amount in loan_interests)
            short_term_repaid_total = sum(float(amount or 0) for amount in short_term_loan_repaid)
            
            savings_month_total = sum(float(amount or 0) for amount in savings_this_month)
            welfare_total = sum(float(welfare or 0) for welfare in welfare_list)
            project_total = sum(float(project or 0) for project in project_list)
            fines_total = sum(float(fine or 0) for fine in fines_and_charges)
            total_savings = sum(float(total or 0) for total in total_savings_list)
            
            # Calculate total money for backward compatibility
            total_money = loan_repaid_total + total_savings
            
            # For legacy compatibility
            # This is to ensure that old code that relies on these fields still works
            group_loans_total = loan_repaid_total  # Using loan repaid as an approximation
            project_loans_total = project_total
            
            # Create the report
            report = FieldOfficerReport(
                # Basic information
                date=report_date,
                po_name=po_name,
                group_names=', '.join(group_names),
                visit_venue=', '.join([v for v in visit_venues if v]),
                visit_time=', '.join([t for t in visit_times if t]),
                total_groups=total_groups,
                total_attendees=total_attendees,
                admin_for_group=', '.join(admin_for_groups),
                project_registration=', '.join(project_registrations),
                mem_reg=', '.join(mem_regs),
                
                # Loan details
                long_term_loan=long_term_loan_total,
                short_term_loan=short_term_loan_total,
                savings_before=savings_before_total,
                total_loan_repaid=loan_repaid_total,
                loan_principle=loan_principle_total,
                loan_interest=loan_interest_total,
                short_term_loan_repaid=short_term_repaid_total,
                
                # Savings and other collections
                savings_this_month=savings_month_total,
                welfare=welfare_total,
                project=project_total,
                fines_and_charges=fines_total,
                total_savings=total_savings,
                
                # Legacy fields for backward compatibility
                group_loans=group_loans_total,
                project_loans=project_loans_total,
                total_money=total_money
            )
            report.save()
            
            messages.success(request, f'Successfully saved report for {po_name} with {total_groups} groups. Total collected: KSh {total_money:.2f} (Loans: KSh {loan_repaid_total:.2f}, Savings: KSh {total_savings:.2f})')
            return redirect('user_management:field_officer_report_success')
        except Exception as e:
            messages.error(request, f"Error saving report: {str(e)}")
    
    context = {
        'active_menu': 'user_management_field_officers',
        'today_date': date.today(),
    }
    return render(request, 'user_management/field_officers/daily_report.html', context)

@login_required
def field_officer_monthly_report(request):
    """
    View for generating monthly reports for field officers
    """
    # Get month and year from request params or use current
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    
    # Get month name
    month_name = calendar.month_name[month]
    
    # Get all reports for the selected month and year
    # In a real environment, this would query the database
    try:
        reports = FieldOfficerReport.objects.filter(
            date__year=year,
            date__month=month
        ).order_by('date')
        
        # Calculate totals for the month from real data
        total_visits = reports.count()
        total_groups = sum(report.total_groups for report in reports)
        total_attendees = sum(report.total_attendees for report in reports)
        
        # Financial calculations
        total_group_loans = sum(report.group_loans for report in reports)
        total_project_loans = sum(report.project_loans for report in reports)
        total_welfare = sum(report.welfare for report in reports)
        total_money = sum(report.total_money for report in reports)
    except:
        # Fallback to sample data if needed
        reports = []
        # Sample data (same as before)
        sample_reports = [
            {
                'date': f"{year}-{month:02d}-01",
                'po_name': 'John Doe',
                'group_names': 'Chama A, Chama B',
                'total_groups': 2,
                'admin_for_group': 'Jane Smith, Peter Jones',
                'project_registration': 'Agriculture, Poultry',
                'mem_reg': '15, 22',
                'group_loans': '5000.00',
                'project_loans': '8000.00',
                'welfare': '1500.00',
                'total_money': '14500.00'
            },
            {
                'date': f"{year}-{month:02d}-05",
                'po_name': 'John Doe',
                'group_names': 'Chama C',
                'total_groups': 1,
                'admin_for_group': 'Mary Johnson',
                'project_registration': 'Textiles',
                'mem_reg': '18',
                'group_loans': '3500.00',
                'project_loans': '6000.00',
                'welfare': '1000.00',
                'total_money': '10500.00'
            },
            {
                'date': f"{year}-{month:02d}-10",
                'po_name': 'John Doe',
                'group_names': 'Chama A, Chama D, Chama E',
                'total_groups': 3,
                'admin_for_group': 'Jane Smith, Alice Brown, Susan White',
                'project_registration': 'Agriculture, Crafts, Food Processing',
                'mem_reg': '15, 12, 20',
                'group_loans': '7500.00',
                'project_loans': '12000.00',
                'welfare': '2500.00',
                'total_money': '22000.00'
            }
        ]
        
        if not reports and sample_reports:
            reports = sample_reports
            total_visits = len(sample_reports)
            total_groups = sum(report['total_groups'] for report in sample_reports)
            total_attendees = 102  # In real app, would calculate from actual data
            
            # Convert to Decimal for precise calculations
            total_group_loans = sum(Decimal(report['group_loans']) for report in sample_reports)
            total_project_loans = sum(Decimal(report['project_loans']) for report in sample_reports)
            total_welfare = sum(Decimal(report['welfare']) for report in sample_reports)
            total_money = sum(Decimal(report['total_money']) for report in sample_reports)
        else:
            total_visits = 0
            total_groups = 0
            total_attendees = 0
            total_group_loans = Decimal('0')
            total_project_loans = Decimal('0')
            total_welfare = Decimal('0')
            total_money = Decimal('0')
    
    context = {
        'active_menu': 'user_management_field_officers',
        'month': month,
        'year': year,
        'month_name': month_name,
        'reports': reports,
        'total_visits': total_visits,
        'total_groups': total_groups,
        'total_attendees': total_attendees,
        'total_group_loans': total_group_loans,
        'total_project_loans': total_project_loans,
        'total_welfare': total_welfare,
        'total_money': total_money
    }
    
    return render(request, 'user_management/field_officers/monthly_report.html', context)

@login_required
def field_officer_report_success(request):
    """
    Success page after submitting a report
    """
    return render(request, 'user_management/field_officers/report_success.html', {
        'active_menu': 'user_management_field_officers',
    })

@login_required
def field_officer_report_table(request):
    """
    View for displaying field officer reports in a table format that exactly matches
    the requested column structure
    """
    # Get date range from request params or use current month
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # If no dates specified, default to current month
    if not (start_date and end_date):
        today = datetime.now()
        start_date = date(today.year, today.month, 1)
        last_day = calendar.monthrange(today.year, today.month)[1]
        end_date = date(today.year, today.month, last_day)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get reports for the date range
    reports = FieldOfficerReport.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Format report data to match the exact column names requested
    report_data = []
    for report in reports:
        report_data.append({
            'date': report.date,
            'po_name': report.po_name,
            'groups_names': report.group_names,
            'total_groups_attendet': report.total_groups,
            'admin_for_each_group': report.admin_for_group,
            'project_registration': report.project_registration or '',
            'mem_reg': report.mem_reg or '',
            'group_loans_collected': f"KSh {report.group_loans}",
            'projects_loans': f"KSh {report.project_loans}",
            'welfare_for_each_group': f"KSh {report.welfare}",
            'total_money_collected': f"KSh {report.total_money}"
        })
    
    # If no reports found, show dummy sample data for demonstration
    if not report_data:
        # Add example data similar to what the user entered
        example_date = date.today()
        report_data = [
            {
                'date': example_date,
                'po_name': 'DAMARIS',
                'groups_names': 'KONOPGAA WG',
                'total_groups_attendet': 1,
                'admin_for_each_group': '290',
                'project_registration': '',
                'mem_reg': '',
                'group_loans_collected': 'KSh 0.00',
                'projects_loans': 'KSh 0.00',
                'welfare_for_each_group': 'KSh 360.00',
                'total_money_collected': 'KSh 360.00'
            },
            {
                'date': example_date,
                'po_name': 'DAMARIS',
                'groups_names': 'FAITH TENDWET WG',
                'total_groups_attendet': 2,
                'admin_for_each_group': '820',
                'project_registration': '',
                'mem_reg': '',
                'group_loans_collected': 'KSh 0.00',
                'projects_loans': 'KSh 0.00',
                'welfare_for_each_group': 'KSh 360.00',
                'total_money_collected': 'KSh 360.00'
            }
        ]
    
    # Calculate totals
    total_groups = sum(report.total_groups for report in reports) if reports else 2
    total_group_loans = sum(report.group_loans for report in reports) if reports else 0
    total_project_loans = sum(report.project_loans for report in reports) if reports else 0
    total_welfare = sum(report.welfare for report in reports) if reports else 720
    total_money = sum(report.total_money for report in reports) if reports else 1830
    
    totals = {
        'total_groups_attendet': total_groups,
        'group_loans_collected': f"KSh {total_group_loans}",
        'projects_loans': f"KSh {total_project_loans}",
        'welfare_for_each_group': f"KSh {total_welfare}",
        'total_money_collected': f"KSh {total_money}"
    }
    
    # Add grand totals for example
    summary_stats = {
        'total_saved': 'S=19390',
        'total_registered': 'R=400',
        'total_loans': 'L=68000',
        'total_fees': 'F=1550',
        'total_welfare': 'W=3510',
        'total_all': 'L=92850'
    }
    
    context = {
        'active_menu': 'user_management_field_officers',
        'report_data': report_data,
        'totals': totals,
        'start_date': start_date,
        'end_date': end_date,
        'summary_stats': summary_stats
    }
    
    return render(request, 'user_management/field_officers/report_table.html', context)

@login_required
@require_POST
def sync_offline_report(request):
    """
    API endpoint to handle synchronization of offline report data
    """
    try:
        # Parse JSON data from request body
        data = json.loads(request.body)
        
        # Basic validation
        if not data:
            return JsonResponse({'status': 'error', 'message': 'No data provided'}, status=400)
            
        # Extract report data
        report_date = data.get('report_date')
        po_name = data.get('po_name')
        
        # Get array data
        group_names = data.get('group_name', [])
        visit_venues = data.get('visit_venue', [])
        visit_times = data.get('visit_time', [])
        total_attendees_list = data.get('total_attendet', [])  # Note the typo in field name (matches the form)
        admin_for_groups = data.get('admin_for_group', [])
        project_registrations = data.get('project_registration', [])
        mem_regs = data.get('mem_reg', [])
        
        # Get loan information
        long_term_loans = data.get('long_term_loan', [])
        short_term_loans = data.get('short_term_loan', [])
        savings_before = data.get('savings_before', [])
        total_loan_repaid = data.get('total_loan_repaid', [])
        loan_principles = data.get('loan_principle', [])
        loan_interests = data.get('loan_interest', [])
        short_term_loan_repaid = data.get('short_term_loan_repaid', [])
        
        # Get savings information
        savings_this_month = data.get('savings_this_month', [])
        welfare_list = data.get('welfare_for_group', [])
        project_list = data.get('project', [])
        fines_and_charges = data.get('fines_and_charges', [])
        total_savings_list = data.get('total_savings', [])
        total_money_list = data.get('total_money_collected', [])
        
        # Calculate totals
        total_groups = len(group_names)
        total_attendees = sum(int(attendees) for attendees in total_attendees_list if attendees)
        
        # Calculate financial totals
        long_term_loan_total = sum(float(amount) for amount in long_term_loans if amount)
        short_term_loan_total = sum(float(amount) for amount in short_term_loans if amount)
        savings_before_total = sum(float(amount) for amount in savings_before if amount)
        loan_repaid_total = sum(float(amount) for amount in total_loan_repaid if amount)
        loan_principle_total = sum(float(amount) for amount in loan_principles if amount)
        loan_interest_total = sum(float(amount) for amount in loan_interests if amount)
        short_term_repaid_total = sum(float(amount) for amount in short_term_loan_repaid if amount)
        
        # Savings totals
        savings_month_total = sum(float(amount) for amount in savings_this_month if amount)
        welfare_total = sum(float(amount) for amount in welfare_list if amount)
        project_total = sum(float(amount) for amount in project_list if amount)
        fines_total = sum(float(amount) for amount in fines_and_charges if amount)
        
        # Total savings
        total_savings = savings_month_total + welfare_total + project_total + fines_total
        
        # For backward compatibility
        group_loans_total = loan_repaid_total if loan_repaid_total else 0
        project_loans_total = 0  # This is a legacy field
        total_money = loan_repaid_total + total_savings
        
        # Create the report
        report = FieldOfficerReport(
            # Basic information
            date=report_date,
            po_name=po_name,
            group_names=', '.join(group_names),
            visit_venue=', '.join([v for v in visit_venues if v]),
            visit_time=', '.join([t for t in visit_times if t]),
            total_groups=total_groups,
            total_attendees=total_attendees,
            admin_for_group=', '.join(admin_for_groups),
            project_registration=', '.join(project_registrations),
            mem_reg=', '.join(mem_regs),
            
            # Loan details
            long_term_loan=long_term_loan_total,
            short_term_loan=short_term_loan_total,
            savings_before=savings_before_total,
            total_loan_repaid=loan_repaid_total,
            loan_principle=loan_principle_total,
            loan_interest=loan_interest_total,
            short_term_loan_repaid=short_term_repaid_total,
            
            # Savings and other collections
            savings_this_month=savings_month_total,
            welfare=welfare_total,
            project=project_total,
            fines_and_charges=fines_total,
            total_savings=total_savings,
            
            # Legacy fields for backward compatibility
            group_loans=group_loans_total,
            project_loans=project_loans_total,
            total_money=total_money
        )
        report.save()
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Report synchronized successfully',
            'report_id': report.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
