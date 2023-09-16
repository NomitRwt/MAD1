#Import the object that would help in database creation
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Creating the database models
#User class
class User(db.Model):
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=True)

#Admin class
class Admin(db.Model):
    __tablename__ = "admin"
    aid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

#Category class
class Category(db.Model):
    __tablename__ = "category"
    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String, unique=True, nullable=False)
    
    #Using the relationship method
    products = db.relationship("Product", backref="category")


#Product class
class Product(db.Model):
    __tablename__ = "product"
    pid = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String, nullable=False)
    #The product category is the foreign key here
    pcid = db.Column(db.Integer, db.ForeignKey('category.cid'), nullable=False)
    pcount = db.Column(db.Integer, nullable=False)
    pprice = db.Column(db.Integer, nullable=False)