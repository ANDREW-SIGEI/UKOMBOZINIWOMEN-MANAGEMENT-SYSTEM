from django.db import models
from django.utils import timezone
from user_management.models import Member, Group, FieldOfficer


class Report(models.Model):
    """Base model for storing generated reports."""
    REPORT_TYPES = (
        ('TABLEBAKING', 'Tablebanking Report'),
        ('LOAN', 'Loan Report'),
        ('MEMBER', 'Member Report'),
        ('GROUP', 'Group Report'),
        ('AGRICULTURE', 'Agriculture Collection Report'),
        ('SCHOOL_FEES', 'School Fees Collection Report'),
        ('FINANCIAL', 'Financial Report'),
        ('CUSTOM', 'Custom Report'),
    )
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Report generation details
    generated_date = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    parameters = models.JSONField(blank=True, null=True, 
                                help_text="Parameters used to generate the report")
    
    # Report content references
    file_path = models.CharField(max_length=255, blank=True, null=True)
    report_format = models.CharField(max_length=20, 
                                   choices=(('PDF', 'PDF'), ('EXCEL', 'Excel'), ('CSV', 'CSV')))
    
    # Sharing and permissions
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(FieldOfficer, related_name='shared_reports', blank=True)
    
    # Date range covered by the report
    date_range_start = models.DateField(null=True, blank=True)
    date_range_end = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()}) - {self.generated_date.date()}"


class SavedQuery(models.Model):
    """Saved queries for generating reports."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    query_type = models.CharField(max_length=50)
    
    # Query definition
    sql_query = models.TextField(blank=True, null=True)
    parameters_definition = models.JSONField(blank=True, null=True)
    
    # Creator and permissions
    created_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.query_type})"


class ReportSchedule(models.Model):
    """Schedule for automatic report generation."""
    FREQUENCY_CHOICES = (
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    )
    
    report_title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Schedule details
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    next_run_date = models.DateTimeField()
    active = models.BooleanField(default=True)
    
    # Report parameters
    parameters = models.JSONField(blank=True, null=True)
    saved_query = models.ForeignKey(SavedQuery, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Distribution
    recipients = models.ManyToManyField(FieldOfficer, related_name='report_subscriptions')
    email_subject = models.CharField(max_length=200, blank=True, null=True)
    email_body = models.TextField(blank=True, null=True)
    
    # Creator
    created_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.report_title} - {self.get_frequency_display()} Schedule"


class DashboardWidget(models.Model):
    """Widgets for analytics dashboards."""
    WIDGET_TYPES = (
        ('CHART', 'Chart'),
        ('METRIC', 'Metric/KPI'),
        ('TABLE', 'Data Table'),
        ('MAP', 'Map'),
        ('CUSTOM', 'Custom Widget'),
    )
    
    CHART_TYPES = (
        ('BAR', 'Bar Chart'),
        ('LINE', 'Line Chart'),
        ('PIE', 'Pie Chart'),
        ('DONUT', 'Donut Chart'),
        ('AREA', 'Area Chart'),
        ('SCATTER', 'Scatter Plot'),
    )
    
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Data source
    data_source = models.CharField(max_length=100)
    query = models.TextField(blank=True, null=True)
    saved_query = models.ForeignKey(SavedQuery, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Display settings
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)
    height = models.IntegerField(default=1)
    
    # Widget configuration
    config = models.JSONField(blank=True, null=True)
    
    # Creator and permissions
    created_by = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"
