from datetime import datetime
import logging
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.sqltypes import CHAR
engine = create_engine('sqlite:///db.db?check_same_thread=False')
Base = declarative_base()


class persons(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    uid = Column(String, unique=True)
    username = Column(String, unique=True)
    gender = Column(Integer)


class pairs(Base):
    __tablename__ = 'pairs'
    id = Column(Integer, primary_key=True)
    first_person = Column(String)
    second_person = Column(String)
    create_date = Column(Integer)
    first_person_uid = Column(String)
    second_person_uid = Column(String)


class marriages(Base):
    __tablename__ = 'marriages'
    id = Column(Integer, primary_key=True)
    first_person = Column(String)
    second_person = Column(String)
    create_date = Column(DateTime)
    first_person_uid = Column(String, unique=True)
    second_person_uid = Column(String, unique=True)
    status = Column(Boolean)


def create_table():
    metadata = MetaData(bind=engine)
    main_table = Table('persons', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('uid', String, unique=True),
                       Column('username', String, unique=True),
                       Column('gender', Integer)
                       )
    metadata.create_all()


def create_pairs():
    metadata = MetaData(bind=engine)
    main_table = Table('pairs', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('first_person', String),
                       Column('second_person', String),
                       Column('second_person_uid', String),
                       Column('first_person_uid', String),
                       Column('create_date', Integer)
                       )
    metadata.create_all()


def create_marriages():
    metadata = MetaData(bind=engine)
    main_table = Table('marriages', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('first_person', String),
                       Column('second_person', String),
                       Column('second_person_uid', String, unique=True),
                       Column('first_person_uid', String, unique=True),
                       Column('create_date', Integer),
                       Column('status', Boolean)
                       )
    metadata.create_all()


class Pairs:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def delete_pair(self):
        try:
            self.session.query(pairs).delete()
            self.session.commit()
        except:
            return False

    def add_pair(self, first_person, first_person_uid, second_person, second_person_uid):
        try:
            now = datetime.now()
            pair = pairs(
                first_person=first_person,
                first_person_uid=first_person_uid,
                second_person=second_person,
                second_person_uid=second_person_uid,
                create_date=str(now.strftime("%d"))
            )
            self.session.add(pair)
            self.session.new
            self.session.commit()
            return True
        except IntegrityError:
            return False

    def get_pair(self):
        result = self.session.query(pairs).first()
        res = []
        res.append({"first_person": result.first_person,
                    "second_person": result.second_person,
                    "second_person_uid": result.second_person_uid,
                    "first_person_uid": result.first_person_uid,
                    "date": result.create_date})

        return res


class Marriages:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def update_marriage(self, uid, status):
        try:
            i = self.session.query(marriages).filter(
                marriages.second_person_uid == uid).first()
            i.status = status
            self.session.add(i)
            self.session.commit()
        except:
            return False

    def delete_marriage(self, uid):
        try:
            i = self.session.query(marriages).filter(
                marriages.first_person_uid == uid).first()
            self.session.delete(i)
            self.session.commit()
        except:
            pass
        try:
            i = self.session.query(marriages).filter(
                marriages.second_person_uid == uid).first()
            self.session.delete(i)
            self.session.commit()
        except:
            pass

    def add_mariage(self, first_person, first_person_uid, second_person, second_person_uid):
        try:
            print('1')
            now = datetime.now()
            pair = marriages(
                first_person=first_person,
                first_person_uid=first_person_uid,
                second_person=second_person,
                second_person_uid=second_person_uid,
                status=False,
                create_date=now
            )
            print(pair)
            self.session.add(pair)
            self.session.new
            self.session.commit()
            return True
        except IntegrityError:
            return False

    def check_mariage(self, uid):
        try:
            result = self.session.query(marriages).filter(
                marriages.first_person_uid == uid).first()
            return result
        except:
            pass
        try:
            result = self.session.query(marriages).filter(
                marriages.second_person_uid == uid).first()
            return result
        except:
            pass

    def get_mariages(self):
        result = self.session.query(marriages).all()
        res = []
        for r in result:
            res.append({"first_person": r.first_person,
                        "second_person": r.second_person,
                        "second_person_uid": r.second_person_uid,
                        "first_person_uid": r.first_person_uid,
                        "status": r.status,
                        "date": r.create_date})
        return res

    def all_mariages(self):
        print('0')
        result = self.session.query(marriages).all()
        print('1')
        res = []
        for r in result:
            res.append({"first_person": r.first_person,
                        "second_person": r.second_person,
                        "second_person_uid": r.second_person_uid,
                        "first_person_uid": r.first_person_uid,
                        "status": r.status,
                        "date": r.create_date})
        print('2')
        return res


class Database:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def add_person(self, username, uid):
        try:
            person = persons(
                uid=uid,
                gender=0,
                username=username
            )
            self.session.add(person)
            self.session.new
            self.session.commit()
            return True
        except IntegrityError:
            return False

    def update_person(self, uid, gender):
        try:
            i = self.session.query(persons).filter(persons.uid == uid).first()
            i.gender = gender
            self.session.add(i)
            self.session.commit()
        except:
            return False

    def delete_person(self, Slug):
        try:
            i = self.session.query(persons).filter(
                persons.Slug == Slug).first()
            self.session.delete(i)
            self.session.commit()
        except:
            return False

    def delete_persons(self):
        try:
            self.session.query(persons).delete()
            self.session.commit()
        except:
            return False

    def search_gender(self, gender):
        try:
            result = self.session.query(persons).filter(
                persons.gender != gender).all()
            persons1 = []
            for res in result:
                persons1.append({
                    "uid": res.uid,
                    "gender": res.gender,
                    "username": res.username
                })
            return persons1
        except:
            pass

    def get_persons(self):
        result = self.session.query(persons).all()
        persons1 = []
        for res in result:
            persons1.append({
                "uid": res.uid,
                "gender": res.gender,
                "username": res.username
            })
        return persons1
