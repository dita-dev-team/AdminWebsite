from flask import jsonify, redirect, request, render_template, url_for
from flask.ext.login import current_user, login_required, login_user, logout_user, LoginManager

from api import app, bcrypt
from api.forms import LoginForm, MemberForm, LaptopForm
from api.models import Admin, Member, Laptop

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        admin = Admin.objects(username__iexact=form.username.data).first()
        if admin:
            if bcrypt.check_password_hash(admin.password, form.password.data):
                admin.authenticated = True
                login_user(admin, remember=True)

                return form.redirect(url_for('index'))

    if form.errors:
        form.errors_list = list(form.errors.values())

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    admin = current_user
    admin.authenticated = False
    logout_user()
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')


@app.route('/members', methods=['GET', 'POST'])
@login_required
def members():
    notification = ""
    if 'notification' in request.args:
        notification = request.args['notification']

    form = MemberForm(request.form)
    form.crud_operation = request.form['submit'] if 'submit' in request.form else None
    form.update_key = request.form['update-key'] if 'update-key' in request.form else None
    if form.validate_on_submit():
        if request.form['submit'] == 'create':
            member = Member(id_no=request.form['id_no'], name=request.form['name'], major=request.form['major'])
            member.save()
            notification = "Member created successfully."
        elif request.form['submit'] == 'delete':
            member = Member.objects(id_no=request.form['id_no']).first()
            member.delete()
            notification = "Member deleted successfully."
        elif request.form['submit'] == 'update':
            member = Member.objects(id_no=form.update_key).first()
            member.id_no = request.form['id_no']
            member.major = request.form['major']
            member.update()
            notification = "Member updated successfully."

        return redirect(url_for('members', notification=notification))

    if form.errors:
        form.errors_list = list(form.errors.values())

    members = Member.objects()
    return render_template('members.html', form=form, members=members, notification=notification)


@app.route('/member/<id_no>')
def member(id_no):
    member = Member.objects(id_no=id_no).first()
    response = jsonify({})

    if member:
        response = jsonify({
            'id_no': member.id_no,
            'name': member.name,
            'major': member.major
        })

    return response


@app.route('/laptops', methods=['GET', 'POST'])
@login_required
def laptops():
    notification = ""
    if 'notification' in request.args:
        notification = request.args['notification']

    form = LaptopForm(request.form)
    form.crud_operation = request.form['submit'] if 'submit' in request.form else None
    form.update_key = request.form['update-key'] if 'update-key' in request.form else None
    if form.validate_on_submit():
        if request.form['submit'] == 'create':
            member = Member.objects(id_no=request.form['id_no']).first()
            laptop = Laptop(serial_no=request.form['serial'], make=request.form['make'], owner=member)
            laptop.save()
            notification = "Laptop created successfully."
        elif request.form['submit'] == 'delete':
            laptop = Laptop.objects(serial_no=request.form['serial'])
            laptop.delete()
            notification = "Laptop deleted successfully."
        elif request.form['submit'] == 'update':
            laptop = Laptop.objects(serial_no__iexact=form.update_key).first()
            laptop.serial_no = request.form['serial']
            laptop.make = request.form['make']
            laptop.owner = Member.objects(id_no=request.form['id_no']).first()
            laptop.save()
            notification = "Laptop updated successfully."

        return redirect(url_for('laptops', notification=notification))
    if form.errors:
        form.errors_list = list(form.errors.values())

    laptops = Laptop.objects()
    return render_template('laptops.html', form=form, laptops=laptops, notification=notification)


@app.route('/laptop/<serial>')
def laptop(serial):
    laptop = Laptop.objects(serial_no__iexact=serial).first()
    response = jsonify({})

    if member:
        response = jsonify({
            'serial': laptop.serial,
            'make': laptop.make,
            'owner': laptop.owner.id_no
        })

    return response


@login_manager.user_loader
def load_user(user_id):
    return Admin.objects(username_iexact=user_id).first()
