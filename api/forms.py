from urllib.parse import urljoin, urlparse

from flask import redirect, request, url_for
from flask.ext.wtf import Form
from wtforms import validators, HiddenField, PasswordField, StringField, ValidationError, SelectField

from api.models import Member, Laptop, Admin


def validate_member(form, field):
    if form.crud_operation == 'create':
        member = Member.objects(id_no=field.data).first()
        if member:
            raise ValidationError('Member already exists')
    elif form.crud_operation == 'delete':
        member = Member.objects(id_no=field.data).first()
        if not member:
            raise ValidationError('Member does not exist.')
    elif form.crud_operation == 'update':
        member = Member.objects(id_no=field.data).first()
        if member and member.id_no != form.update_key:
            raise ValidationError('Member already exists.')

        member = Member.objects(id_no=field.update_key).first()
        if not member:
            raise ValidationError('Member does not exist.')


def validate_laptop_serial(form, field):
    if form.crud_operation == 'create':
        laptop = Laptop.objects(serial_no__iexact=field.data).first()
        if laptop:
            raise ValidationError('Laptop already registered.')
    elif form.crud_operation == 'delete':
        laptop = Laptop.objects(serial_no__iexact=field.data).first()
        if not laptop:
            raise ValidationError('Laptop not registered.')
    elif form.crud_operation == 'update':
        laptop = Laptop.objects(serial_no__iexact=field.data).first()
        if laptop and laptop.serial_no != form.update_key:
            raise ValidationError('Laptop already registered.')

        if not laptop:
            raise ValidationError('Laptop not registered.')


def validate_laptop_owner(form, field):
    member = Member.objects(id_no=field.data).first()
    if not member:
        raise ValidationError('Member does not exist.')


def validate_admin(form, field):
    admin = Admin.objects(username__iexact=field.data).first()

    if not admin:
        raise ValidationError("Admin does not exist")


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class RedirectForm(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class LoginForm(RedirectForm):
    username = StringField('Username', [validators.DataRequired(), validate_admin])
    password = PasswordField('Password', [validators.DataRequired()])
    errors_list = None


class MemberForm(RedirectForm):
    id_no = StringField('Student Id', [validators.DataRequired(), validate_member])
    name = StringField('Student Name', [validators.DataRequired()])
    major = SelectField('Major', choices=['ACS', 'MIS'])
    errors_list = None
    crud_operation = None
    update_key = None


class LaptopForm(RedirectForm):
    serial_no = StringField('Laptop serial', [validators.DataRequired(), validate_laptop_serial])
    make = StringField('Laptop make', [validators.DataRequired()])
    id_no = StringField('Owner id', [validators.DataRequired(), validate_laptop_owner])
    errors_list = None
    crud_operation = None
    update_key = None
