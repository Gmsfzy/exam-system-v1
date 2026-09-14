from flask import Flask, render_template, redirect, url_for, request, flash, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from openpyxl import Workbook, load_workbook
import pandas as pd
import io
import os

# 初始化应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'online_exam_system_2026_final_secure_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///exam.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
# 创建上传文件夹
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# 登录管理器配置
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# ===================== 数据库模型（新增班级表） =====================
# 班级表
class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # 班级名称
    students = db.relationship('User', backref='classroom', lazy=True)


# 用户表（管理员/老师/学生）- 关联班级
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin/teacher/student
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'), nullable=True)  # 学生关联班级


# 科目表
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    exam_duration = db.Column(db.Integer, default=30)  # 考试时长（分钟）
    questions = db.relationship('Question', backref='subject', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='subject', lazy=True, cascade="all, delete-orphan")


# 试题表（支持单选/多选/判断）
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    question_type = db.Column(db.String(10), default='single')  # single/ multiple/ judge
    title = db.Column(db.Text, nullable=False)  # 题干
    option_a = db.Column(db.String(200), nullable=True)
    option_b = db.Column(db.String(200), nullable=True)
    option_c = db.Column(db.String(200), nullable=True)
    option_d = db.Column(db.String(200), nullable=True)
    answer = db.Column(db.String(10), nullable=False)  # 单选A/B/C/D | 多选AB/BCD | 判断True/False
    score = db.Column(db.Integer, default=10)  # 每题分数


# 成绩表 - 关联班级
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    total_score = db.Column(db.Integer, nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())
    student = db.relationship('User', backref='scores')


# ===================== 登录加载用户 =====================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ===================== 全局工具函数 =====================
@app.template_global()
def get_username(uid):
    u = User.query.get(uid)
    return u.username if u else '未知用户'


@app.template_global()
def get_classname(cid):
    c = Class.query.get(cid)
    return c.name if c else '未分班'


# ===================== 公共路由 =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('用户名或密码错误，请重试！')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已成功退出登录！')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    subjects = Subject.query.all()
    classes = Class.query.all()
    return render_template('index.html', subjects=subjects, classes=classes)


# ===================== 学生路由 =====================
@app.route('/student/choose_class/<int:class_id>')
@login_required
def choose_class(class_id):
    """学生选择班级"""
    if current_user.role != 'student':
        flash('无权限操作！')
        return redirect(url_for('index'))
    current_user.class_id = class_id
    db.session.commit()
    flash(f'已选择班级：{get_classname(class_id)}')
    return redirect(url_for('index'))


@app.route('/student/exam/<int:subject_id>')
@login_required
def student_exam(subject_id):
    if current_user.role != 'student':
        flash('无权限访问学生考试页面！')
        return redirect(url_for('index'))
    # 检查是否选择班级
    if not current_user.class_id:
        flash('请先选择班级再进行考试！')
        return redirect(url_for('index'))
    subject = Subject.query.get_or_404(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).all()
    if not questions:
        flash('该科目暂无试题，请联系老师添加！')
        return redirect(url_for('index'))
    # 计算考试结束时间
    end_time = datetime.now() + timedelta(minutes=subject.exam_duration)
    return render_template('student_exam.html',
                           subject=subject,
                           questions=questions,
                           end_time=end_time.strftime('%Y-%m-%d %H:%M:%S'))


@app.route('/student/submit', methods=['POST'])
@login_required
def student_submit():
    if current_user.role != 'student':
        return redirect(url_for('index'))

    data = request.form.to_dict()
    subject_id = int(data.pop('subject_id'))
    subject = Subject.query.get(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).all()

    total_score = 0
    for q in questions:
        user_ans = data.get(f'q_{q.id}', '').strip()
        correct_ans = q.answer.strip()

        # 判分逻辑
        if q.question_type == 'multiple':
            user_ans_sorted = ''.join(sorted(user_ans.upper()))
            correct_ans_sorted = ''.join(sorted(correct_ans.upper()))
            if user_ans_sorted == correct_ans_sorted:
                total_score += q.score
        elif q.question_type == 'judge':
            if user_ans == correct_ans:
                total_score += q.score
        else:
            if user_ans.upper() == correct_ans.upper():
                total_score += q.score

    # 保存成绩
    score_record = Score(
        student_id=current_user.id,
        subject_id=subject_id,
        total_score=total_score
    )
    db.session.add(score_record)
    db.session.commit()

    return render_template('score_result.html', subject=subject, score=total_score, questions=questions)


# 限时自动提交接口
@app.route('/student/auto_submit', methods=['POST'])
@login_required
def auto_submit():
    if current_user.role != 'student':
        return jsonify({'status': 'error', 'msg': '无权限'})
    subject_id = request.json.get('subject_id')
    answers = request.json.get('answers', {})

    subject = Subject.query.get(subject_id)
    questions = Question.query.filter_by(subject_id=subject_id).all()
    total_score = 0

    for q in questions:
        user_ans = answers.get(f'q_{q.id}', '').strip()
        correct_ans = q.answer.strip()

        if q.question_type == 'multiple':
            user_ans_sorted = ''.join(sorted(user_ans.upper()))
            correct_ans_sorted = ''.join(sorted(correct_ans.upper()))
            if user_ans_sorted == correct_ans_sorted:
                total_score += q.score
        elif q.question_type == 'judge':
            if user_ans == correct_ans:
                total_score += q.score
        else:
            if user_ans.upper() == correct_ans.upper():
                total_score += q.score

    score_record = Score(
        student_id=current_user.id,
        subject_id=subject_id,
        total_score=total_score
    )
    db.session.add(score_record)
    db.session.commit()

    return jsonify({'status': 'success', 'score': total_score})


# ===================== 老师路由 =====================
@app.route('/teacher/score/<int:subject_id>')
@login_required
def teacher_score(subject_id):
    if current_user.role not in ['teacher', 'admin']:
        flash('无权限访问成绩页面！')
        return redirect(url_for('index'))
    subject = Subject.query.get_or_404(subject_id)
    # 支持按班级筛选
    class_id = request.args.get('class_id', type=int)
    if class_id:
        scores = Score.query.join(User).filter(
            Score.subject_id == subject_id,
            User.class_id == class_id
        ).order_by(Score.total_score.desc()).all()
    else:
        scores = Score.query.filter_by(subject_id=subject_id).order_by(Score.total_score.desc()).all()

    count = len(scores)
    avg_score = round(sum(s.total_score for s in scores) / count, 2) if count > 0 else 0
    max_score = scores[0].total_score if scores else 0
    classes = Class.query.all()
    return render_template('teacher_score.html',
                           subject=subject,
                           scores=scores,
                           count=count,
                           avg_score=avg_score,
                           max_score=max_score,
                           classes=classes,
                           selected_class=class_id)


@app.route('/teacher/export/<int:subject_id>')
@login_required
def export_score(subject_id):
    if current_user.role not in ['teacher', 'admin']:
        flash('无权限导出成绩！')
        return redirect(url_for('index'))

    subject = Subject.query.get_or_404(subject_id)
    class_id = request.args.get('class_id', type=int)
    if class_id:
        scores = Score.query.join(User).filter(
            Score.subject_id == subject_id,
            User.class_id == class_id
        ).order_by(Score.total_score.desc()).all()
    else:
        scores = Score.query.filter_by(subject_id=subject_id).order_by(Score.total_score.desc()).all()

    # 创建Excel
    wb = Workbook()
    ws = wb.active
    ws.title = f'{subject.name}成绩表'
    # 写入表头
    ws.append(['排名', '学生姓名', '班级', '得分', '考试时间'])
    # 写入数据
    for idx, s in enumerate(scores, 1):
        ws.append([
            idx,
            get_username(s.student_id),
            get_classname(User.query.get(s.student_id).class_id),
            s.total_score,
            s.create_time.strftime('%Y-%m-%d %H:%M:%S')
        ])

    # 保存到内存
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f'{subject.name}_成绩表_{datetime.now().strftime("%Y%m%d%H%M")}.xlsx'
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# ===================== 管理员路由 =====================
# 班级管理
@app.route('/admin/class', methods=['GET', 'POST'])
@login_required
def admin_class():
    if current_user.role != 'admin':
        flash('无权限访问管理员页面！')
        return redirect(url_for('index'))
    if request.method == 'POST':
        class_name = request.form['name'].strip()
        if not class_name:
            flash('班级名称不能为空！')
            return redirect(url_for('admin_class'))
        if Class.query.filter_by(name=class_name).first():
            flash('该班级已存在！')
            return redirect(url_for('admin_class'))
        new_class = Class(name=class_name)
        db.session.add(new_class)
        db.session.commit()
        flash('班级添加成功！')
    classes = Class.query.all()
    return render_template('admin_class.html', classes=classes)


# 删除班级
@app.route('/admin/class/delete/<int:class_id>', methods=['POST'])
@login_required
def delete_class(class_id):
    if current_user.role != 'admin':
        flash('无权限删除班级！')
        return redirect(url_for('index'))
    class_obj = Class.query.get_or_404(class_id)
    # 解除学生与班级的关联
    students = User.query.filter_by(class_id=class_id).all()
    for s in students:
        s.class_id = None
    db.session.delete(class_obj)
    db.session.commit()
    flash('班级已删除，关联学生已解除班级关系！')
    return redirect(url_for('admin_class'))


# 科目管理
@app.route('/admin/subject', methods=['GET', 'POST'])
@login_required
def admin_subject():
    if current_user.role != 'admin':
        flash('无权限访问管理员页面！')
        return redirect(url_for('index'))
    if request.method == 'POST':
        subject_name = request.form['name'].strip()
        exam_duration = int(request.form['exam_duration']) if request.form['exam_duration'].isdigit() else 30
        if not subject_name:
            flash('科目名称不能为空！')
            return redirect(url_for('admin_subject'))
        if Subject.query.filter_by(name=subject_name).first():
            flash('该科目已存在！')
            return redirect(url_for('admin_subject'))
        new_subject = Subject(name=subject_name, exam_duration=exam_duration)
        db.session.add(new_subject)
        db.session.commit()
        flash('科目添加成功！')
    subjects = Subject.query.all()
    return render_template('admin_subject.html', subjects=subjects)


# 删除科目
@app.route('/admin/subject/delete/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if current_user.role != 'admin':
        flash('无权限删除科目！')
        return redirect(url_for('index'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('科目及相关试题、成绩已删除！')
    return redirect(url_for('admin_subject'))


# 试题管理（含Excel导入）
@app.route('/admin/question', methods=['GET', 'POST'])
@login_required
def admin_question():
    if current_user.role != 'admin':
        flash('无权限访问管理员页面！')
        return redirect(url_for('index'))
    subjects = Subject.query.all()
    if not subjects:
        flash('请先添加科目，再添加试题！')
        return redirect(url_for('admin_subject'))

    current_subject_id = request.args.get('subject_id', type=int, default=subjects[0].id)
    current_subject = Subject.query.get(current_subject_id)
    questions = Question.query.filter_by(subject_id=current_subject_id).all()

    # 处理Excel批量导入
    if request.method == 'POST' and 'excel_file' in request.files:
        file = request.files['excel_file']
        if file.filename == '':
            flash('请选择Excel文件！')
            return redirect(request.url)
        if file and file.filename.endswith(('.xlsx', '.xls')):
            # 保存上传的文件
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            try:
                # 读取Excel
                df = pd.read_excel(file_path)
                required_cols = ['题型', '题干', '选项A', '选项B', '选项C', '选项D', '答案', '分数']
                if not all(col in df.columns for col in required_cols):
                    flash('Excel格式错误！请包含：题型、题干、选项A、选项B、选项C、选项D、答案、分数 列')
                    return redirect(request.url)

                success_count = 0
                for _, row in df.iterrows():
                    q_type = row['题型'].strip().lower()
                    if q_type not in ['single', 'multiple', 'judge']:
                        continue

                    question_data = {
                        'subject_id': current_subject_id,
                        'question_type': q_type,
                        'title': str(row['题干']).strip(),
                        'answer': str(row['答案']).strip(),
                        'score': int(row['分数']) if pd.notna(row['分数']) else 10
                    }

                    # 处理选项
                    if q_type in ['single', 'multiple']:
                        question_data['option_a'] = str(row['选项A']).strip() if pd.notna(row['选项A']) else ''
                        question_data['option_b'] = str(row['选项B']).strip() if pd.notna(row['选项B']) else ''
                        question_data['option_c'] = str(row['选项C']).strip() if pd.notna(row['选项C']) else ''
                        question_data['option_d'] = str(row['选项D']).strip() if pd.notna(row['选项D']) else ''
                    else:
                        question_data['option_a'] = None
                        question_data['option_b'] = None
                        question_data['option_c'] = None
                        question_data['option_d'] = None

                    new_question = Question(**question_data)
                    db.session.add(new_question)
                    success_count += 1

                db.session.commit()
                flash(f'成功导入 {success_count} 道试题！')
            except Exception as e:
                flash(f'导入失败：{str(e)}')
            finally:
                # 删除临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)
            return redirect(request.url)

    # 处理单题添加/编辑
    if request.method == 'POST' and 'question_id' in request.form:
        question_id = int(request.form['question_id'])
        question = Question.query.get_or_404(question_id)
        question.question_type = request.form['question_type']
        question.title = request.form['title'].strip()
        question.answer = request.form['answer'].strip()
        question.score = int(request.form['score']) if request.form['score'].isdigit() else 10

        if question.question_type in ['single', 'multiple']:
            question.option_a = request.form['option_a'].strip()
            question.option_b = request.form['option_b'].strip()
            question.option_c = request.form['option_c'].strip()
            question.option_d = request.form['option_d'].strip()
        else:
            question.option_a = None
            question.option_b = None
            question.option_c = None
            question.option_d = None

        db.session.commit()
        flash('试题编辑成功！')
        return redirect(request.url)

    return render_template('admin_question.html', subjects=subjects, current_subject=current_subject,
                           questions=questions)


# 单题添加接口
@app.route('/admin/question/add', methods=['POST'])
@login_required
def add_question():
    if current_user.role != 'admin':
        return jsonify({'status': 'error', 'msg': '无权限'})

    question_type = request.form['question_type']
    title = request.form['title'].strip()
    answer = request.form['answer'].strip()
    score = int(request.form['score']) if request.form['score'].isdigit() else 10
    subject_id = int(request.form['subject_id'])

    question_data = {
        'subject_id': subject_id,
        'question_type': question_type,
        'title': title,
        'answer': answer,
        'score': max(1, min(100, score))
    }

    if question_type in ['single', 'multiple']:
        question_data['option_a'] = request.form['option_a'].strip()
        question_data['option_b'] = request.form['option_b'].strip()
        question_data['option_c'] = request.form['option_c'].strip()
        question_data['option_d'] = request.form['option_d'].strip()
    else:
        question_data['option_a'] = None
        question_data['option_b'] = None
        question_data['option_c'] = None
        question_data['option_d'] = None

    new_question = Question(**question_data)
    db.session.add(new_question)
    db.session.commit()

    return jsonify({'status': 'success', 'msg': '试题添加成功！'})


# 删除试题
@app.route('/admin/question/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    if current_user.role != 'admin':
        flash('无权限删除试题！')
        return redirect(url_for('index'))
    question = Question.query.get_or_404(question_id)
    subject_id = question.subject_id
    db.session.delete(question)
    db.session.commit()
    flash('试题已删除！')
    return redirect(url_for('admin_question', subject_id=subject_id))


# 加载试题数据
@app.route('/admin/question/load/<int:question_id>')
@login_required
def load_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'status': 'error'})
    question = Question.query.get_or_404(question_id)
    return jsonify({
        'status': 'success',
        'id': question.id,
        'type': question.question_type,
        'title': question.title,
        'option_a': question.option_a or '',
        'option_b': question.option_b or '',
        'option_c': question.option_c or '',
        'option_d': question.option_d or '',
        'answer': question.answer,
        'score': question.score
    })


# ===================== 错误页面 =====================
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# ===================== 初始化数据 =====================
def init_data():
    with app.app_context():
        db.create_all()
        # 检查默认用户是否存在
        if not User.query.filter_by(username='admin').first():
            # 默认账号：admin/teacher/student 密码均为123456
            admin = User(username='admin', password=generate_password_hash('123456'), role='admin')
            teacher = User(username='teacher', password=generate_password_hash('123456'), role='teacher')
            student = User(username='student', password=generate_password_hash('123456'), role='student')
            db.session.add_all([admin, teacher, student])
            db.session.commit()
            print('默认用户创建成功！')
        print('数据库初始化完成！')


if __name__ == '__main__':
    init_data()
    app.run(debug=True, host='0.0.0.0', port=5000)