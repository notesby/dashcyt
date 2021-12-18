import os.path

from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import pyodbc

db = SQLAlchemy()
connection = None


def init_app(app):
    db.init_app(app)
    app.app_context().push()
    db.create_all()
    init_connection()
    return db


def init_connection():
    global connection
    server = 'DESKTOP-VLGTJDQ\MSSQLSERVER2019'
    database = 'Sedesa'
    username = 'dash'
    password = 'dash92'
    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    except pyodbc.OperationalError as e:
        print("couldn't connect to db")
    return connection


def get_connection():
    return connection


def load_data():
    data = None
    root = os.path.realpath(os.path.dirname(__file__))
    json_path = os.path.join(root, "static", "data.json")
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    if data is not None:
        for row in data["Users"]:
            _ = insert_or_update(User, row)
        for row in data["Reports"]:
            _ = insert_or_update(Report, row)
        delete_relationship = default_graph_default_fields.delete()
        db.session.execute(delete_relationship)
        for row in data["DefaultGraphs"]:
            _ = insert_or_update(DefaultGraph, row)
        for row in data["DefaultFields"]:
            _ = insert_or_update(DefaultField, row)
        for row in data["DefaultGraphFields"]:
            new_entry = default_graph_default_fields.insert().values(default_graph_id=row["default_graph_id"],
                                                                     default_field_id=row["default_field_id"])
            db.session.execute(new_entry)
        for row in data["SavedField"]:
            _ = insert_or_update(SavedField, row)
        for row in data["SavedGraph"]:
            _ = insert_or_update(SavedGraph, row)
    db.session.commit()
    print("data loaded successfully")


def insert_or_update(model_class, values):
    print(model_class)
    entry = None
    added = False
    if "id" in values:
        entry = model_class.query.filter_by(id=values["id"]).first()
    if not entry:
        entry = model_class()
        added = True
    for key in values:
        value = values[key]
        if type(value) == dict:
            if "hash" in value:
                if value["hash"]:
                    hashed = generate_password_hash(value["value"])
                    setattr(entry, key, hashed)
                else:
                    setattr(entry, key, value["value"])
            else:
                setattr(entry, key, value)
        else:
            setattr(entry, key, value)

    if added:
        db.session.add(entry)
    return entry


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.TEXT, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref=db.backref('reports', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())

    def __repr__(self):
        return '<Report %r>' % self.name


class SavedGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    graph_options = db.Column(db.JSON, nullable=True)
    geojson = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_by = db.relationship('User', backref=db.backref('graphs', lazy=True))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow())
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    report = db.relationship('Report', backref=db.backref('graphs', lazy=True))
    fields = db.relationship('SavedField', back_populates='graphs')
    cache = db.Column(db.JSON, nullable=True)
    image = None

    def __repr__(self):
        return '<SavedGraph %r>' % self.name


class SavedField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(200), nullable=False)
    graph_id = db.Column(db.Integer, db.ForeignKey('saved_graph.id'))
    graphs = db.relationship('SavedGraph', back_populates='fields')
    default_field_id = db.Column(db.Integer, db.ForeignKey('default_field.id'))
    default_field = db.relationship('DefaultField', back_populates='saved_fields')


    def __repr__(self):
        return '<SavedField %r>' % self.name


default_graph_default_fields = db.Table('default_graph_default_fields', db.metadata,
                                        db.Column('default_graph_id', db.ForeignKey('default_graph.id'), primary_key=True),
                                        db.Column('default_field_id', db.ForeignKey('default_field.id'), primary_key=True))


class DefaultGraph(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query_text = db.Column(db.Text, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    graph_options = db.Column(db.JSON, nullable=True)
    geojson = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, nullable=False, default=0)
    type = db.Column(db.String(150), nullable=False)
    fields = db.relationship('DefaultField', default_graph_default_fields, back_populates='graphs')

    @property
    def serialize(self):
        res = dict()
        res["id"] = self.id
        res["name"] = self.name
        res["query_text"] = self.query_text
        res["type"] = self.type
        res["graph_options"] = json.dumps(self.graph_options)
        res["geojson"] = self.geojson
        res["order"] = self.order
        return res

    def __repr__(self):
        return '<DefaultGraph %r>' % self.name


class DefaultField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    graphs = db.relationship('DefaultGraph', default_graph_default_fields, back_populates='fields')
    saved_fields = db.relationship('SavedField', back_populates='default_field')
    graph_ids = set()

    @property
    def serialize(self):
        res = dict()
        res["id"] = self.id
        res["name"] = self.name
        res["type"] = self.type
        res["description"] = self.description
        res["graph_ids"] = list(self.graph_ids)
        return res

    def __repr__(self):
        return '<DefaultField %r>' % self.name

