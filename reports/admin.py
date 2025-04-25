from django.contrib import admin
from .models import Report, SavedQuery, ReportSchedule, DashboardWidget

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'generated_date', 'generated_by', 'is_public')
    list_filter = ('report_type', 'is_public', 'generated_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'generated_date'
    raw_id_fields = ('generated_by',)
    readonly_fields = ('generated_date',)

@admin.register(SavedQuery)
class SavedQueryAdmin(admin.ModelAdmin):
    list_display = ('name', 'query_type', 'created_by', 'created_date', 'is_public')
    list_filter = ('query_type', 'is_public', 'created_date')
    search_fields = ('name', 'description', 'sql_query')
    date_hierarchy = 'created_date'
    raw_id_fields = ('created_by',)
    readonly_fields = ('created_date',)

@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ('report_title', 'report_type', 'frequency', 'next_run_date', 'active', 'created_by')
    list_filter = ('report_type', 'frequency', 'active')
    search_fields = ('report_title', 'description')
    date_hierarchy = 'next_run_date'
    raw_id_fields = ('created_by', 'saved_query')

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'chart_type', 'data_source', 'created_by', 'is_public')
    list_filter = ('widget_type', 'chart_type', 'is_public')
    search_fields = ('title', 'description', 'data_source')
    raw_id_fields = ('created_by', 'saved_query')
    fieldsets = (
        ('Widget Information', {
            'fields': ('title', 'description', 'widget_type', 'chart_type', 'is_public')
        }),
        ('Data Source', {
            'fields': ('data_source', 'query', 'saved_query')
        }),
        ('Layout', {
            'fields': ('position_x', 'position_y', 'width', 'height')
        }),
        ('Configuration', {
            'fields': ('config', 'created_by')
        }),
    )
