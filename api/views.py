from flask import jsonify, redirect, request, render_template, url_for
from flask.ext.login import current_user, login_required, login_user, logout_user, LoginManager

from api import app, bcrypt, db
from api.forms import LoginForm, MemberForm, LaptopForm
from api.models import Admin, Member, Laptop


login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.init_app(app)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        admin = db.session.query(Admin).filter_by(username=form.username.data).first()
        if admin:
            if bcrypt.check_password_hash(admin.password, form.password.data):
                print("pass3")
                admin.authenticated = True
                db.session.add(admin)
                db.session.commit()
                login_user(admin, remember=True)

                return form.redirect(url_for('index'))

    if form.errors:
        form.errors_list = list(form.errors.values())

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    admin = current_user
    admin.authenticated = False
    db.session.add(admin)
    db.session.commit()
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
        member = Member(request.form['id_no'], request.form['name'])
        if request.form['submit'] == 'create':
            db.session.add(member)
            notification = "Member created successfully."
        elif request.form['submit'] == 'delete':
            db.session.query(Member).filter(Member.id_no == member.id_no).delete()
            notification = "Member deleted successfully."
        elif request.form['submit'] == 'update':
            db.session.query(Member).filter(Member.id_no == form.update_key).update({'id_no': member.id_no,
                                                                                     'name': member.name})
            notification = "Member updated successfully."

        db.session.commit()
        return redirect(url_for('members', notification=notification))

    if form.errors:
        form.errors_list = list(form.errors.values())

    members = db.session.query(Member).all()
    return render_template('members.html', form=form, members=members, notification=notification)


@app.route('/member/<id_no>')
def member(id_no):
    member = db.session.query(Member).filter_by(id_no=id_no).first()
    response = jsonify({})

    if member:
        response = jsonify({
            'id_no': member.id_no,
            'name': member.name
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
        laptop = Laptop(request.form['serial'], request.form['make'], request.form['id_no'])
        if request.form['submit'] == 'create':
            db.session.add(laptop)
            notification = "Laptop created successfully."
        elif request.form['submit'] == 'delete':
            db.session.query(Laptop).filter(db.func.lower(Laptop.serial) == db.func.lower(laptop.serial)).delete(
                synchronize_session=False)
            notification = "Laptop deleted successfully."
        elif request.form['submit'] == 'update':
            print(form.update_key)
            db.session.query(Laptop).filter(db.func.lower(Laptop.serial) == db.func.lower(form.update_key)).update({
                'serial': laptop.serial, 'make': laptop.make, 'id_no': laptop.id_no}, synchronize_session=False)
            notification = "Laptop updated successfully."

        db.session.commit()
        return redirect(url_for('laptops', notification=notification))
    if form.errors:
        form.errors_list = list(form.errors.values())

    laptops = db.session.query(Laptop).all()
    return render_template('laptops.html', form=form, laptops=laptops, notification=notification)


@app.route('/laptop/<serial>')
def laptop(serial):
    laptop = db.session.query(Laptop).filter_by(serial=serial).first()
    response = jsonify({})

    if member:
        response = jsonify({
            'serial': laptop.serial,
            'make': laptop.make,
            'id_no': laptop.id_no
        })

    return response


@login_manager.user_loader
def load_user(userid):
    return Admin.query.get(userid)