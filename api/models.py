import datetime

from mongoengine import PULL, CASCADE

from api import db


class Member(db.Model):
    __tablename__ = 'Members'

    id_no = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=True)

    def __init__(self, id_no, name):
        self.id_no = id_no
        self.name = name

    def __repr__(self):
        return "%s [%s]" % (self.id_no, self.name)


class Laptop(db.Model):
    __tablename__ = 'Laptops'

    serial = db.Column(db.String(50), primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    id_no = db.Column(db.ForeignKey('Members.id_no', onupdate=True, ondelete=True), nullable=False)

    def __init__(self, serial, make, id_no):
        self.serial = serial
        self.make = make
        self.id_no = id_no

    def __repr__(self):
        return "%s [%s-%s]" % (self.serial, self.make, self.id_no)


class Admin(db.Model):
    __tablename__ = "Admins"

    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(250), required=True)
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "%s - %s" % (self.username, self.password)

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


class CustomDocument(db.Document):
    meta = {
        'abstract': True,
    }

    created_at = db.DateTimeField()
    updated_at = db.DateTimeField(default=datetime.datetime.now().replace(microsecond=0))

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.datetime.now().replace(microsecond=0)

        self.updated_at = datetime.datetime.now().replace(microsecond=0)
        return super(CustomDocument, self).save(*args, **kwargs)


class Member(CustomDocument):
    id_no = db.StringField(max_length=7, regex='\d{2}-\d{4}', required=True, primary_key=True)
    name = db.StringField(max_length=50, required=True)
    major = db.StringField(max_length=4, default=None)
    image = db.FileField(default=None)
    laptops = db.ListField(db.ReferenceField('Laptop'), default=None)

    @staticmethod
    def member_exists(member):
        return member is not None and Member.objects(id_no=member.id_no).first() is not None

    def __eq__(self, other):
        return self.id_no == other.id_no

    def __repr__(self):
        return "%s - %s" % (self.id_no, self.name)

    def __str__(self):
        return "[%s] %s - %s" % (self.major, self.id_no, self.name)


class Laptop(CustomDocument):
    serial_no = db.StringField(max_length=50, required=True, primary_key=True)
    make = db.StringField(max_length=10, required=True)
    owner = db.ReferenceField('Member')

    @staticmethod
    def laptop_exists(laptop):
        print(laptop)
        return laptop is not None and Laptop.objects(serial_no__iexact=laptop.serial_no).first() is not None

    def __repr__(self):
        return "%s - %s" % (self.serial_no, self.make)


class Log(CustomDocument):
    index = db.SequenceField(primary_key=True)
    member = db.ReferenceField('Member')
    date = db.DateTimeField(default=datetime.datetime.now().date())
    time_in = db.DateTimeField(default=datetime.datetime.now().replace(microsecond=0))
    time_out = db.DateTimeField(null=True)

    @staticmethod
    def get_members_in():
        members = []
        logs = Log.objects(time_out=None, date=datetime.datetime.now().date())
        for log in logs:
            members.append(log.member)

        return members


class Admin(CustomDocument):
    username = db.StringField(primary_key=True)
    password = db.StringField(required=True)
    active = db.BooleanField(default=True)
    authenticated = db.BooleanField(default=False)

    def __repr__(self):
        return "%s - %s" % (self.username, self.password)

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False


Laptop.register_delete_rule(Member, 'laptops', PULL)
Member.register_delete_rule(Laptop, 'owner', CASCADE)
