from django.contrib import admin
from .models import FieldOfficer, Member, Group, GroupMembership, FieldOfficerReport

@admin.register(FieldOfficer)
class FieldOfficerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'id_number', 'assigned_area', 'is_active')
    list_filter = ('is_active', 'assigned_area')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'id_number', 'phone_number')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'id_number', 'phone_number', 'gender', 'registration_date', 'is_active')
    list_filter = ('gender', 'is_active', 'registration_date')
    search_fields = ('first_name', 'last_name', 'id_number', 'phone_number')
    date_hierarchy = 'registration_date'

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'formation_date', 'meeting_location', 'is_active')
    list_filter = ('is_active', 'formation_date')
    search_fields = ('name', 'registration_number', 'meeting_location')
    date_hierarchy = 'formation_date'

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('member', 'group', 'position', 'join_date', 'is_active')
    list_filter = ('position', 'is_active', 'join_date')
    search_fields = ('member__first_name', 'member__last_name', 'group__name')
    date_hierarchy = 'join_date'

@admin.register(FieldOfficerReport)
class FieldOfficerReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'po_name', 'total_groups', 'total_attendees', 'total_money')
    list_filter = ('date', 'po_name')
    search_fields = ('po_name', 'group_names')
    readonly_fields = ('created_at', 'updated_at')
