from datetime import date, datetime

from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

from . import db

class Item(db.Model, SerializerMixin):
    __tablename__ = 'item'
    serialize_only = ('id', 'name', 'price', 'added_on',)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    stocks = db.relationship('Stock', lazy="dynamic", cascade="all, delete-orphan",
        backref=db.backref('item', uselist=False))

    def __repr__(self) -> str:
        return f'<Item {self.id}>'

class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Stock {self.id}>'

class ItemPurchase(db.Model):
    __tablename__ = 'item_purchase'
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), primary_key=True)
    discount = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)

    @hybrid_property
    def discounted_total(self):
        return self.total - (self.total * self.discount)

    def __repr__(self) -> str:
        return f'<ItemPurchase {self.id}'

class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('ItemPurchase', lazy='dynamic', 
        backref=db.backref('purchase', uselist=False))
    discount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    @hybrid_property
    def discounted_total(self):
        return self.total - (self.total * self.discount)

    def __repr__(self) -> str:
        return f'<Purchase {self.id}>'