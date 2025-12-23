
# 勤怠管理システム

Django を使用した勤怠管理アプリケーション。出勤・退勤・休憩機能を備え、ユーザーごとの勤務状況をリアルタイムで管理できます。

## 概要

このプロジェクトは、従業員の勤怠情報を一元管理するためのシステムです。管理者がユーザーを登録し、各ユーザーがパスワード認証を通じて出勤時間や休憩時間を記録できます。

### 主な特徴

- ✅ **ユーザー認証機能**：パスワード入力によるセキュアなユーザー認証
- ✅ **出勤・退勤管理**：日々の出勤・退勤時間を自動記録
- ✅ **休憩管理**：休憩開始・終了時間を記録し、実働時間を自動計算
- ✅ **ダッシュボード**：全体の勤務状況を可視化
- ✅ **レスポンシブ UI**：Bootstrap5 × Tailwind CSS による現代的なデザイン
- ✅ **Font Awesome アイコン**：直感的で分かりやすいUIコンポーネント

---

## 技術スタック

| 項目 | 版 |
|------|-----|
| **Backend** | Django (Python 3.12) |
| **Database** | SQLite3 |
| **Frontend** | Bootstrap5, Tailwind CSS, Font Awesome |

---

## セットアップ手順

### 1. 環境構築

```bash
# 仮想環境の作成と有効化
python3.12 -m venv venv
source venv/bin/activate

# Django のインストール
pip install django

# プロジェクトの初期化
django-admin startproject attendance .
python manage.py startapp attendance
```

### 2. マイグレーション

```bash
# データベーススキーマの作成
python manage.py migrate
```

### 3. 管理ユーザーの作成（オプション）

```bash
python manage.py createsuperuser
```

### 4. サーバーの起動

```bash
python manage.py runserver
```

ブラウザで `http://localhost:8000` にアクセスしてください。

---

## ディレクトリ構成

```
attendance_django/
├── attendance/                 # Django アプリケーション
│   ├── migrations/            # データベースマイグレーション
│   ├── templates/             # HTML テンプレート
│   │   └── attendance/
│   │       ├── base.html      # ベーステンプレート
│   │       ├── index.html     # ログインページ
│   │       ├── action_selection.html  # 勤務操作画面
│   │       └── dashboard.html # ダッシュボード
│   ├── static/                # CSS / JavaScript / 画像
│   ├── models.py              # データベースモデル
│   ├── views.py               # ビュー関数
│   ├── urls.py                # URL ルーティング
│   └── forms.py               # フォーム定義
├── attendance/                # Django プロジェクト設定
│   ├── settings.py            # 設定ファイル
│   ├── urls.py                # メインのURLルーティング
│   └── wsgi.py                # WSGI アプリケーション
├── manage.py                  # Django 管理コマンド
└── requirements.txt           # 依存パッケージ（必要に応じて作成）
```

---

## データベース設計

### User テーブル（ユーザー管理）

| カラム | 型 | 説明 |
|--------|-----|------|
| `id` | Integer | プライマリキー |
| `username` | String | ユーザー名 |
| `password` | String | パスワード |
| `email` | String | メールアドレス |
| `is_active` | Boolean | アクティブ状態 |
| `is_staff` | Boolean | スタッフ権限 |
| `created_at` | DateTime | 作成日時 |
| `updated_at` | DateTime | 更新日時 |

### AttendanceRecord テーブル（勤怠記録）

| カラム | 型 | 説明 |
|--------|-----|------|
| `id` | Integer | プライマリキー |
| `user_id` | Integer | ユーザーID（外部キー） |
| `date` | Date | 勤務日 |
| `clock_in_time` | Time | 出勤時間 |
| `clock_out_time` | Time | 退勤時間 |
| `break_start_time` | Time | 休憩開始時間 |
| `break_end_time` | Time | 休憩終了時間 |
| `total_work_time` | Duration | 実働時間（自動計算） |
| `total_break_time` | Duration | 休憩時間（自動計算） |
| `created_at` | DateTime | 作成日時 |
| `updated_at` | DateTime | 更新日時 |

---

## 機能説明

### 1. ログイン画面

- ユーザーを選択
- パスワードを入力してログイン
- 管理者のみ新規ユーザーを追加可能

### 2. 勤務操作画面

ログイン後、以下の操作が可能です：

- **出勤（Clock In）**：出勤時間を記録
- **退勤（Clock Out）**：退勤時間を記録
- **休憩入り（Break Start）**：休憩時間の開始を記録
- **休憩戻り（Break End）**：休憩時間の終了を記録
- **本日の状況表示**：現在の勤務状況をリアルタイム表示

### 3. ダッシュボード

全ユーザーの勤務状況を一覧表示：

- 本日の出勤状況
- ユーザーごとの実働時間
- 本月の勤務日数
- チーム全体の勤務パフォーマンス

---

## 使用上の注意

### UIコメント規約

HTMLテンプレート及びスタイル定義のコメントは**全て日本語**で記載しています。

```html
<!-- ログインフォーム -->
<form method="POST" action="{% url 'attendance:login' %}">
  <!-- ユーザー選択 -->
  <select name="user_id">
    ...
  </select>
</form>
```

### 命名規則

- **Python 変数・関数**：`snake_case`（例：`clock_in_time`）
- **Django モデル**：PascalCase（例：`AttendanceRecord`）
- **HTML クラス・ID**：kebab-case（例：`action-button`）
- **CSS クラス**：kebab-case（例：`user-selector`）

---

## トラブルシューティング

### データベースエラーが発生した場合

```bash
# マイグレーションをリセット
python manage.py migrate attendance zero
python manage.py migrate
```

### ポート 8000 が既に使用されている場合

```bash
python manage.py runserver 8001
```

### 静的ファイル（CSS/JS）が読み込まれない場合

```bash
python manage.py collectstatic
```

---

## 開発に参加される方へ

### Git コミット形式

本プロジェクトは [Conventional Commits](https://www.conventionalcommits.org/) に統一しています。

```
feat: 新機能の追加
fix: バグ修正
chore: 保守・整備関連
docs: ドキュメント更新
```

例：
```bash
git commit -m "feat: 勤務記録の一括エクスポート機能を追加"
git commit -m "fix: 休憩時間計算のバグを修正"
```

---

## ライセンス

このプロジェクトはプライベートプロジェクトです。

---

## サポート

問題が発生した場合や質問がある場合は、プロジェクト管理者に連絡してください。
