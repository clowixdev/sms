from datetime import datetime
from zoneinfo import ZoneInfo

from flask_login import UserMixin

from sqlalchemy.orm import backref

from src import db


def timestamp_msk():
    utctime = datetime.now(tz=ZoneInfo('Europe/Moscow'))
    return utctime

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) 
    psw = db.Column(db.String(250)) 

class Driver(db.Model):
    __tablename__ = 'driver'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(130), nullable=False)
    email = db.Column(db.String(130), nullable=False)
    gender = db.Column(db.String(1))
    birthday = db.Column(db.Date)
    hometown = db.Column(db.String(45))
    passport_id = db.Column(db.String(10))
    passport_given = db.Column(db.String(150))
    passport_date = db.Column(db.Date)
    inn = db.Column(db.String(12))
    snils = db.Column(db.String(14))
    oms = db.Column(db.String(16))
    d_license = db.Column(db.String(10))
    dl_date = db.Column(db.Date)
    dl_expire_date = db.Column(db.Date)
    c_cat = db.Column(db.Boolean)
    c1_cat = db.Column(db.Boolean)
    d_cat = db.Column(db.Boolean)
    d1_cat = db.Column(db.Boolean)
    e_cat = db.Column(db.Boolean)
    med_expire_date = db.Column(db.Date)
    phone = db.Column(db.String(11))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id')) 
    shipment_id = db.relationship('Shipment', backref='driver', uselist=False)


    def __repr__(self):
        return f'<Driver id{self.id}>'

class Car(db.Model):
    __tablename__ = 'car'
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    reg_num = db.Column(db.String(12), nullable=False)
    pts = db.Column(db.String(10))
    expire_date = db.Column(db.Date)
    osago = db.Column(db.String(13))
    osago_expire_date = db.Column(db.Date)
    kasko = db.Column(db.String(11))
    kasko_expire_date = db.Column(db.Date)
    has_trailer = db.Column(db.Boolean)
    shipment_id = db.relationship('Shipment', backref='car', uselist=False)

    def __repr__(self):
        return f'<Driver id{self.id}>'

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    manager = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    driver_id = db.relationship('Driver', backref="company", uselist=False)


class Shipment(db.Model):
    __tablename__ = 'shipment'
    id = db.Column(db.Integer, primary_key=True)
    docs_url = db.Column(db.String(100), nullable=True)
    create_date = db.Column(db.Date, default=timestamp_msk())
    arrival_date =  db.Column(db.Date)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id')) 
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    auth_token = db.Column(db.String(45), nullable=False)
    accepted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Shipment id{self.id}>'


    # type_id = db.Column(db.Integer, db.ForeignKey('shipment_types.id'))
    # class ShipmentType(db.Model):
    # __tablename__ = 'shipment_type'
    # id = db.Column(db.Integer, primary_key=True)
    # type = db.Column(db.String(100))
    # shipment_id = db.relationship('Shipment', backref="type", uselist=False)
    
    # def __repr__(self):
    #     return f'<Shipment_types id{self.id}>'