from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    """Base report model"""
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=(
        ('isg', 'İş Sağlığı ve Güvenliği'),
        ('verimlilik', 'Verimlilik Analizi'),
        ('uretim', 'Üretim Takibi'),
        ('genel', 'Genel Rapor'),
    ))
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    charts = models.JSONField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
    
    class Meta:
        ordering = ['-created_at']

class ReportTemplate(models.Model):
    """Templates for generating recurring reports"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=(
        ('isg', 'İş Sağlığı ve Güvenliği'),
        ('verimlilik', 'Verimlilik Analizi'),
        ('uretim', 'Üretim Takibi'),
        ('genel', 'Genel Rapor'),
    ))
    config = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class ScheduledReport(models.Model):
    """Schedule for automatically generating reports"""
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=100)
    frequency = models.CharField(max_length=20, choices=(
        ('daily', 'Günlük'),
        ('weekly', 'Haftalık'),
        ('monthly', 'Aylık'),
        ('quarterly', 'Üç Aylık'),
    ))
    day_of_week = models.PositiveSmallIntegerField(null=True, blank=True, help_text="0-6: Monday-Sunday")
    day_of_month = models.PositiveSmallIntegerField(null=True, blank=True)
    time_of_day = models.TimeField(default='08:00')
    recipients = models.ManyToManyField(User, related_name='report_subscriptions')
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_frequency_display()})"

class AIAnalysis(models.Model):
    """AI-generated insights and recommendations based on reports"""
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='ai_analyses')
    analysis_type = models.CharField(max_length=50, choices=(
        ('summary', 'Özet'),
        ('anomaly', 'Anomali Tespiti'),
        ('trend', 'Trend Analizi'),
        ('recommendation', 'Öneri'),
    ))
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=(
        ('high', 'Yüksek'),
        ('medium', 'Orta'),
        ('low', 'Düşük'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_analyses')
    review_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} - {self.report.title}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'AI Analyses'

class Dashboard(models.Model):
    """Custom dashboards for users"""
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboards')
    layout = models.JSONField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        unique_together = ('user', 'is_default')
