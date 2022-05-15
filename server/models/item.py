from datetime import datetime, timedelta

from sqlalchemy import func, text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

from . import db


class Item(db.Model, SerializerMixin):
    __tablename__ = 'item'
    serialize_only = ('id', 'bar_code', 'name', 'price', 'added_on',)
    id = db.Column(db.Integer, primary_key=True)
    bar_code = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)
    stocks = db.relationship('Stock', lazy="dynamic", cascade="all, delete-orphan",
                             backref=db.backref('item', uselist=False))
    purchases = db.relationship('ItemPurchase', lazy='dynamic', cascade="all, delete-orphan",
                                backref=db.backref('item', uselist=False))

    def __repr__(self) -> str:
        return f'<Item {self.id}>'

    def __str__(self) -> str:
        return f'{self.name} {self.price} PHP'

    @property
    def in_stock(self) -> int:
        return self.total_stock - self.total_purchases

    @property
    def revenue(self) -> int:
        return self.stock_costs - self.total_sold

    @property
    def total_stock(self) -> int:
        result = db.session.query(func.sum(Stock.quantity).label('total_quantity')) \
            .select_from(Stock).where(Stock.item_id == self.id)[0][0]
        return result or 0

    @property
    def total_purchases(self) -> int:
        result = db.session.query(func.sum(ItemPurchase.quantity).label('total_quantity')) \
            .select_from(ItemPurchase).where(ItemPurchase.item_id == self.id)[0][0]
        return result or 0

    @property
    def stock_costs(self) -> float:
        result = db.session.query(func.sum(Stock.cost).label('total_cost')) \
            .select_from(Stock).where(Stock.item_id == self.id)[0][0]
        return result or 0.0

    @property
    def total_sold(self) -> float:
        result = db.session.query(func.sum(ItemPurchase.total).label('total_sold')) \
            .select_from(ItemPurchase).where(ItemPurchase.item_id == self.id)[0][0]
        return result or 0.0

    def get_sold(self, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple:
        result = db.session.query(func.sum(ItemPurchase.quantity).label('total_sold')) \
            .select_from(ItemPurchase).join(Purchase, Purchase.id == ItemPurchase.purchase_id) \
            .filter(ItemPurchase.item_id == self.id).first()
        return result[0] if result else 0

    @classmethod
    def most_sales(cls, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple:
        result = db.session.query(cls, func.sum(ItemPurchase.total).label('total_sales')) \
            .join(ItemPurchase).join(Purchase, Purchase.id == ItemPurchase.purchase_id) \
            .filter(Purchase.added_on.between(start_date, end_date)).group_by(Item) \
            .order_by(text('total_sales DESC')).first()
        return result if result else (None, 0,)

    @classmethod
    def most_sold(cls, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple:
        result = db.session.query(cls, func.sum(ItemPurchase.quantity).label('total_sold')) \
            .join(ItemPurchase).join(Purchase, Purchase.id == ItemPurchase.purchase_id) \
            .filter(Purchase.added_on.between(start_date, end_date)).group_by(Item) \
            .order_by(text('total_sold DESC')).first()
        return result if result else (None, 0,)


class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    cost = db.Column(db.Float)
    per_item_cost = db.Column(db.Float)
    quantity = db.Column(db.Integer, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f'<Stock {self.id}>'


class ItemPurchase(db.Model):
    __tablename__ = 'item_purchase'
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey(
        'purchase.id'), primary_key=True)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

    @hybrid_property
    def discounted_total(self):
        return self.total - (self.total * self.discount)

    def __repr__(self) -> str:
        return f'<ItemPurchase {self.id}'


class Purchase(db.Model):
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    items = db.relationship('ItemPurchase', lazy='dynamic', cascade="all, delete-orphan",
                            backref=db.backref('purchase', uselist=False))
    discount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    @hybrid_property
    def discounted_total(self) -> float:
        return self.total - (self.total * self.discount)

    def __repr__(self) -> str:
        return f'<Purchase {self.id}>'
