from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, date, time
from .models import AttendanceRecord
from .forms import ClockingForm, ActionSelectionForm
from django.contrib.auth.models import User
import json


@require_http_methods(["GET", "POST"])
def index(request):
    """トップページ - 打刻画面"""
    if request.method == 'POST':
        clocking_form = ClockingForm(request.POST)
        if clocking_form.is_valid():
            user = clocking_form.cleaned_data['user']
            # ユーザーをセッションに保存してアクション選択画面へ
            request.session['clock_user_id'] = user.id
            return redirect('attendance:action_selection')
        else:
            # エラーメッセージを表示
            for field, errors in clocking_form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        clocking_form = ClockingForm()

    context = {
        'clocking_form': clocking_form,
    }
    return render(request, 'attendance/index.html', context)


@require_http_methods(["GET", "POST"])
def action_selection(request):
    """アクション選択画面"""
    user_id = request.session.get('clock_user_id')
    if not user_id:
        messages.warning(request, 'ユーザーを再度選択してください。')
        return redirect('attendance:index')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        action_form = ActionSelectionForm(request.POST)
        if action_form.is_valid():
            action = action_form.cleaned_data['action']
            return redirect('attendance:clock_action', user_id=user_id, action=action)
    else:
        action_form = ActionSelectionForm()

    # 当日の勤怠記録を取得（なければNone）
    today = timezone.now().date()
    today_record = AttendanceRecord.objects.filter(user=user, date=today).first()

    context = {
        'action_form': action_form,
        'user': user,
        'today_record': today_record,
    }
    return render(request, 'attendance/action_selection.html', context)


@require_http_methods(["GET"])
def clock_action(request, user_id, action):
    """打刻処理"""
    user = get_object_or_404(User, id=user_id)
    today = timezone.now().date()
    now = timezone.now().time()

    # 当日のレコードを取得または作成
    record, created = AttendanceRecord.objects.get_or_create(
        user=user,
        date=today,
    )

    try:
        if action == 'clock_in':
            if record.clock_in_time:
                messages.warning(request, f'{user.get_full_name()}は既に出勤しています。')
            else:
                record.clock_in_time = now
                record.save()
                messages.success(request, f'{user.get_full_name()}が出勤しました。({now.strftime("%H:%M:%S")})')

        elif action == 'clock_out':
            if not record.clock_in_time:
                messages.warning(request, '出勤時刻が記録されていません。')
            elif record.clock_out_time:
                messages.warning(request, f'{user.get_full_name()}は既に退勤しています。')
            else:
                record.clock_out_time = now
                record.save()
                messages.success(request, f'{user.get_full_name()}が退勤しました。({now.strftime("%H:%M:%S")})')

        elif action == 'break_start':
            if not record.clock_in_time:
                messages.warning(request, '出勤時刻が記録されていません。')
            elif record.clock_out_time:
                messages.warning(request, '既に退勤しています。')
            elif record.break_start_time:
                messages.warning(request, '既に休憩中です。')
            else:
                record.break_start_time = now
                record.save()
                messages.success(request, f'{user.get_full_name()}が休憩を開始しました。({now.strftime("%H:%M:%S")})')

        elif action == 'break_end':
            if not record.break_start_time:
                messages.warning(request, '休憩中ではありません。')
            elif record.break_end_time:
                messages.warning(request, '既に休憩から戻っています。')
            else:
                record.break_end_time = now
                record.save()
                messages.success(request, f'{user.get_full_name()}が休憩から戻りました。({now.strftime("%H:%M:%S")})')

    except Exception as e:
        messages.error(request, f'エラーが発生しました: {str(e)}')

    # セッションをクリア
    request.session.pop('clock_user_id', None)

    return redirect('attendance:index')


@require_http_methods(["GET"])
def dashboard(request):
    """ダッシュボード - 当日の全ユーザーの勤怠状況"""
    today = timezone.now().date()

    # 全アクティブユーザーを取得
    all_users = User.objects.filter(is_active=True).order_by('last_name', 'first_name')

    # 当日の勤怠記録を取得
    today_records = AttendanceRecord.objects.filter(date=today).select_related('user')
    records_dict = {record.user_id: record for record in today_records}

    # 各ユーザーと対応する勤怠記録を結合
    user_attendance_list = []
    for user in all_users:
        record = records_dict.get(user.id)

        # 実働時間を計算
        total_work_hours = 0
        total_work_minutes = 0
        if record and record.total_work_time:
            total_seconds = int(record.total_work_time.total_seconds())
            total_work_hours = total_seconds // 3600
            total_work_minutes = (total_seconds % 3600) // 60

        user_attendance_list.append({
            'user': user,
            'record': record,
            'status': record.get_status_display() if record else '未出勤',
            'total_work_hours': total_work_hours,
            'total_work_minutes': total_work_minutes,
        })

    # 統計情報を計算
    total_clocked_in = sum(1 for item in user_attendance_list if item['record'] and item['record'].is_clocked_in)
    total_on_break = sum(1 for item in user_attendance_list if item['record'] and item['record'].is_on_break)
    total_clocked_out = sum(1 for item in user_attendance_list if item['record'] and not item['record'].is_clocked_in and item['record'].clock_in_time)
    total_not_clocked = sum(1 for item in user_attendance_list if not item['record'] or not item['record'].clock_in_time)

    context = {
        'date': today,
        'user_attendance_list': user_attendance_list,
        'total_clocked_in': total_clocked_in,
        'total_on_break': total_on_break,
        'total_clocked_out': total_clocked_out,
        'total_not_clocked': total_not_clocked,
    }
    return render(request, 'attendance/dashboard.html', context)


@require_http_methods(["GET"])
def clear_session(request):
    """セッションをクリア"""
    request.session.pop('clock_user_id', None)
    messages.info(request, '選択がリセットされました。')
    return redirect('attendance:index')


@require_http_methods(["GET"])
def reports(request):
    """レポート画面 - 日付範囲でフィルタリング"""
    from django.db.models import Q
    from .forms import DateRangeFilterForm

    form = DateRangeFilterForm(request.GET or None)
    records = AttendanceRecord.objects.select_related('user')

    # フィルタリング処理
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id = request.GET.get('user')

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            records = records.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            records = records.filter(date__lte=end_date)
        except ValueError:
            pass

    if user_id:
        records = records.filter(user_id=user_id)

    records = records.order_by('-date', 'user')

    context = {
        'form': form,
        'records': records,
    }
    return render(request, 'attendance/reports.html', context)


@require_http_methods(["GET"])
def report_export_csv(request):
    """CSV エクスポート"""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    # BOM を追加（Excel で正しく開くため）
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['ユーザー', 'ユーザー名', '日付', '出勤', '退勤', '休憩開始', '休憩終了', '実働時間', '休憩時間'])

    # フィルタリング
    records = AttendanceRecord.objects.select_related('user')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id = request.GET.get('user')

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            records = records.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            records = records.filter(date__lte=end_date)
        except ValueError:
            pass

    if user_id:
        records = records.filter(user_id=user_id)

    records = records.order_by('-date', 'user')

    for record in records:
        clock_in = record.clock_in_time.strftime('%H:%M:%S') if record.clock_in_time else '-'
        clock_out = record.clock_out_time.strftime('%H:%M:%S') if record.clock_out_time else '-'
        break_start = record.break_start_time.strftime('%H:%M:%S') if record.break_start_time else '-'
        break_end = record.break_end_time.strftime('%H:%M:%S') if record.break_end_time else '-'

        # 実働時間をフォーマット
        work_time = '-'
        if record.total_work_time:
            total_seconds = int(record.total_work_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            work_time = f'{hours:02d}:{minutes:02d}'

        # 休憩時間をフォーマット
        break_time = '-'
        if record.total_break_time:
            total_seconds = int(record.total_break_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            break_time = f'{hours:02d}:{minutes:02d}'

        writer.writerow([
            record.user.get_full_name(),
            record.user.username,
            record.date.strftime('%Y-%m-%d'),
            clock_in,
            clock_out,
            break_start,
            break_end,
            work_time,
            break_time,
        ])

    return response


@require_http_methods(["GET"])
def report_export_pdf(request):
    """PDF エクスポート"""
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from datetime import datetime as dt
    from io import BytesIO
    from django.http import HttpResponse

    # フィルタリング
    records = AttendanceRecord.objects.select_related('user')

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    user_id = request.GET.get('user')

    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            records = records.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            records = records.filter(date__lte=end_date)
        except ValueError:
            pass

    if user_id:
        records = records.filter(user_id=user_id)

    records = records.order_by('-date', 'user')

    # PDF を生成
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20, bottomMargin=20)
    elements = []

    # スタイル設定
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#007bff'),
        spaceAfter=12,
        alignment=1,  # Center
    )

    # タイトル
    title = Paragraph('勤怠レポート', title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.3*inch))

    # 生成日時
    now = dt.now().strftime('%Y年%m月%d日 %H:%M:%S')
    info = Paragraph(f'生成日時: {now}', styles['Normal'])
    elements.append(info)
    elements.append(Spacer(1, 0.2*inch))

    # テーブルデータ
    data = [['ユーザー', 'ユーザー名', '日付', '出勤', '退勤', '実働時間']]

    for record in records[:100]:  # 最初の100件のみ
        clock_in = record.clock_in_time.strftime('%H:%M') if record.clock_in_time else '-'
        clock_out = record.clock_out_time.strftime('%H:%M') if record.clock_out_time else '-'

        work_time = '-'
        if record.total_work_time:
            total_seconds = int(record.total_work_time.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            work_time = f'{hours}:{minutes:02d}'

        data.append([
            record.user.get_full_name(),
            record.user.username,
            record.date.strftime('%Y-%m-%d'),
            clock_in,
            clock_out,
            work_time,
        ])

    # テーブル作成
    table = Table(data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 0.9*inch, 0.9*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007bff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))
    elements.append(table)

    # PDF生成
    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
    return response
