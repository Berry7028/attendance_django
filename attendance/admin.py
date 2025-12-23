from django.contrib import admin
from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'clock_in_time', 'clock_out_time', 'break_start_time', 'break_end_time', 'total_work_time', 'get_status_display')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('total_work_time', 'total_break_time', 'created_at', 'updated_at')
    fieldsets = (
        ('ユーザー情報', {
            'fields': ('user', 'date'),
        }),
        ('打刻情報', {
            'fields': ('clock_in_time', 'clock_out_time', 'break_start_time', 'break_end_time'),
        }),
        ('計算値', {
            'fields': ('total_work_time', 'total_break_time'),
            'classes': ('collapse',),
        }),
        ('システム情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    ordering = ('-date', 'user')
