from django.db import models
from django.contrib.auth.models import User
from datetime import time, timedelta


class AttendanceRecord(models.Model):
    """勤怠記録モデル"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='ユーザー')
    date = models.DateField(verbose_name='記録日', auto_now_add=False)

    # 打刻時刻
    clock_in_time = models.TimeField(null=True, blank=True, verbose_name='出勤時刻')
    clock_out_time = models.TimeField(null=True, blank=True, verbose_name='退勤時刻')
    break_start_time = models.TimeField(null=True, blank=True, verbose_name='休憩開始時刻')
    break_end_time = models.TimeField(null=True, blank=True, verbose_name='休憩終了時刻')

    # 計算値（自動計算）
    total_work_time = models.DurationField(null=True, blank=True, verbose_name='実働時間')
    total_break_time = models.DurationField(null=True, blank=True, verbose_name='休憩時間')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        unique_together = ('user', 'date')
        verbose_name = '勤怠記録'
        verbose_name_plural = '勤怠記録'
        ordering = ['-date', 'user']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} - {self.date}'

    def calculate_work_time(self):
        """実働時間を計算"""
        if not self.clock_in_time or not self.clock_out_time:
            return None

        # 同じ日付内での計算を想定
        clock_in = self._time_to_datetime(self.clock_in_time)
        clock_out = self._time_to_datetime(self.clock_out_time)

        # 実働時間 = (退勤時刻 - 出勤時刻) - 休憩時間
        work_duration = clock_out - clock_in

        if self.total_break_time:
            work_duration -= self.total_break_time

        return work_duration if work_duration.total_seconds() > 0 else timedelta(0)

    def calculate_break_time(self):
        """休憩時間を計算"""
        if not self.break_start_time or not self.break_end_time:
            return timedelta(0)

        break_start = self._time_to_datetime(self.break_start_time)
        break_end = self._time_to_datetime(self.break_end_time)

        break_duration = break_end - break_start
        return break_duration if break_duration.total_seconds() > 0 else timedelta(0)

    def _time_to_datetime(self, t):
        """TimeフィールドをDatetimeに変換（日付は当日を使用）"""
        from datetime import datetime as dt
        return dt.combine(self.date, t)

    def save(self, *args, **kwargs):
        """保存時に実働時間と休憩時間を自動計算"""
        self.total_break_time = self.calculate_break_time()
        self.total_work_time = self.calculate_work_time()
        super().save(*args, **kwargs)

    @property
    def is_clocked_in(self):
        """出勤中か判定"""
        return self.clock_in_time is not None and self.clock_out_time is None

    @property
    def is_on_break(self):
        """休憩中か判定"""
        return self.break_start_time is not None and self.break_end_time is None

    def get_status_display(self):
        """ステータスを表示用に取得"""
        if not self.clock_in_time:
            return '未出勤'
        elif self.is_on_break:
            return '休憩中'
        elif self.is_clocked_in:
            return '出勤中'
        else:
            return '退勤済'
