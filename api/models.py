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
    password = db.Column(db.String(250), nullable=False)
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
