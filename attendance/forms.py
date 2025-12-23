from django import forms
from django.contrib.auth.models import User
from .models import AttendanceRecord


class ClockingForm(forms.Form):
    """打刻用フォーム"""

    # ユーザー選択
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'user_select',
        }),
        label='ユーザー',
        empty_label='ユーザーを選択してください'
    )

    # パスワード入力
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'パスワードを入力',
            'autocomplete': 'off',
        }),
        label='パスワード',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # アクティブなユーザーのみ表示
        self.fields['user'].queryset = User.objects.filter(is_active=True).order_by('last_name', 'first_name')

    def clean(self):
        """フォームの検証"""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        password = cleaned_data.get('password')

        if user and password:
            # ユーザーが存在するか、パスワードが正しいか確認
            if not user.check_password(password):
                raise forms.ValidationError('パスワードが正しくありません。', code='invalid_password')

        return cleaned_data


class ActionSelectionForm(forms.Form):
    """アクション選択フォーム"""

    ACTION_CHOICES = [
        ('clock_in', '出勤'),
        ('clock_out', '退勤'),
        ('break_start', '休憩開始'),
        ('break_end', '休憩終了'),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input',
        }),
        label='アクションを選択'
    )


class DateRangeFilterForm(forms.Form):
    """日付範囲フィルタフォーム"""

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        required=False,
        label='開始日'
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        }),
        required=False,
        label='終了日'
    )

    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True).order_by('last_name', 'first_name'),
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        required=False,
        label='ユーザー'
    )
