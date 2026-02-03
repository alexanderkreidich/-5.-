import csv
from io import StringIO
from flask import Blueprint, render_template, request, make_response
from flask_login import login_required, current_user
from models import db, VisitLog, User
from decorators import check_rights

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

ITEMS_PER_PAGE = 10


@reports_bp.route('/logs')
@login_required
@check_rights('view_logs')
def visit_logs():
    """Журнал посещений с пагинацией."""
    page = request.args.get('page', 1, type=int)
    
    # Администратор видит все логи, пользователь — только свои
    if current_user.role and current_user.role.name == 'Администратор':
        query = VisitLog.query
    else:
        query = VisitLog.query.filter_by(user_id=current_user.id)
    
    pagination = query.order_by(VisitLog.created_at.desc()).paginate(
        page=page, per_page=ITEMS_PER_PAGE, error_out=False
    )
    
    logs = pagination.items
    
    return render_template('reports/logs.html', 
                          logs=logs, 
                          pagination=pagination)


@reports_bp.route('/pages')
@login_required
@check_rights('view_logs')
def pages_stats():
    """Статистика посещений по страницам."""
    # Для Администратора — все записи, для Пользователя — только свои
    if current_user.role and current_user.role.name == 'Администратор':
        stats = db.session.query(
            VisitLog.path,
            db.func.count(VisitLog.id).label('count')
        ).group_by(VisitLog.path).order_by(db.desc('count')).all()
    else:
        stats = db.session.query(
            VisitLog.path,
            db.func.count(VisitLog.id).label('count')
        ).filter(VisitLog.user_id == current_user.id
        ).group_by(VisitLog.path).order_by(db.desc('count')).all()
    
    return render_template('reports/pages_stats.html', stats=stats)


@reports_bp.route('/pages/export')
@login_required
@check_rights('view_logs')
def pages_stats_csv():
    """Экспорт статистики по страницам в CSV."""
    if current_user.role and current_user.role.name == 'Администратор':
        stats = db.session.query(
            VisitLog.path,
            db.func.count(VisitLog.id).label('count')
        ).group_by(VisitLog.path).order_by(db.desc('count')).all()
    else:
        stats = db.session.query(
            VisitLog.path,
            db.func.count(VisitLog.id).label('count')
        ).filter(VisitLog.user_id == current_user.id
        ).group_by(VisitLog.path).order_by(db.desc('count')).all()
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Страница', 'Количество посещений'])
    
    for i, (path, count) in enumerate(stats, 1):
        writer.writerow([i, path, count])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=pages_stats.csv'
    return response


@reports_bp.route('/users')
@login_required
@check_rights('view_logs')
def users_stats():
    """Статистика посещений по пользователям."""
    if current_user.role and current_user.role.name == 'Администратор':
        # Все пользователи + неаутентифицированные
        stats = db.session.query(
            VisitLog.user_id,
            db.func.count(VisitLog.id).label('count')
        ).group_by(VisitLog.user_id).order_by(db.desc('count')).all()
    else:
        # Только свои посещения
        stats = db.session.query(
            VisitLog.user_id,
            db.func.count(VisitLog.id).label('count')
        ).filter(VisitLog.user_id == current_user.id
        ).group_by(VisitLog.user_id).order_by(db.desc('count')).all()
    
    # Загружаем пользователей для отображения ФИО
    user_ids = [user_id for user_id, _ in stats if user_id is not None]
    users_map = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}
    
    stats_with_names = []
    for user_id, count in stats:
        if user_id is None:
            name = 'Неаутентифицированный пользователь'
        else:
            user = users_map.get(user_id)
            name = user.full_name if user else 'Удалённый пользователь'
        stats_with_names.append((name, count))
    
    return render_template('reports/users_stats.html', stats=stats_with_names)


@reports_bp.route('/users/export')
@login_required
@check_rights('view_logs')
def users_stats_csv():
    """Экспорт статистики по пользователям в CSV."""
    if current_user.role and current_user.role.name == 'Администратор':
        stats = db.session.query(
            VisitLog.user_id,
            db.func.count(VisitLog.id).label('count')
        ).group_by(VisitLog.user_id).order_by(db.desc('count')).all()
    else:
        stats = db.session.query(
            VisitLog.user_id,
            db.func.count(VisitLog.id).label('count')
        ).filter(VisitLog.user_id == current_user.id
        ).group_by(VisitLog.user_id).order_by(db.desc('count')).all()
    
    user_ids = [user_id for user_id, _ in stats if user_id is not None]
    users_map = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['№', 'Пользователь', 'Количество посещений'])
    
    for i, (user_id, count) in enumerate(stats, 1):
        if user_id is None:
            name = 'Неаутентифицированный пользователь'
        else:
            user = users_map.get(user_id)
            name = user.full_name if user else 'Удалённый пользователь'
        writer.writerow([i, name, count])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = 'attachment; filename=users_stats.csv'
    return response
