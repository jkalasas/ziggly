from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import func, text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property

from . import db

def random_uuid() -> str:
    """Generates a random uuid using uuid module
    Returns
    -------
    str
        a random uuid
    """
    return uuid4().hex

class Item(db.Model, SerializerMixin):
    """Item model storing the items information in the database

    ...
    Attributes
    ----------
    id: int
        the id of the item
    bar_code: str
        the barcode of the item
    name: str
        the name of the item
    price: float
        the price of the item
    added_on: datetime.datetime
        the time object was created (automatically setted when not specified using datetime.utcnow method)
    stocks: sqlalchemy.orm.dynamic.AppenderBaseQuery
        stock history of the item
    purchases: sqlalchemy.orm.dynamic.AppenderBaseQuery
        purchase history of the item
    in_stock: int
        available stock of the item
    total_stock: int
        sum of the stock history of the item
    total_purchases: int
        number of times the item was purchased
    stock_costs: float
        total costs the item was needed
    total_sold: float
        total money of the purchases made with this item
    
    Methods
    -------
    get_sold(self, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> int
        returns the number of items purchased in the specified timeframe
    most_sales(cls, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple
        returns the item with the most sales in the specified timeframe
    most_sold(cls,  start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple
        returns the item with the most items sold in the specified timeframe
    """
    __tablename__ = 'item'
    serialize_only = ('id', 'bar_code', 'name', 'price', 'added_on',)
    id = db.Column(db.Integer, primary_key=True)
    bar_code = db.Column(db.String(128), nullable=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
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
        """Available stock of the item
        Parameters
        ----------
        self: Item
            the item
        Returns
        -------
        int
            the available stock of the item
        """
        return self.total_stock - self.total_purchases

    @property
    def total_stock(self) -> int:
        """Sums of the stock history of the item
        Parameters
        ----------
        self: Item
            the item
        Returns
        -------
        int
            sum of the stock history of the item
        """
        result = db.session.query(func.sum(Stock.quantity).label('total_quantity')) \
            .select_from(Stock).where(Stock.item_id == self.id)[0][0]
        return result or 0

    @property
    def total_purchases(self) -> int:
        """Sums number of times the item was purchased
        Parameters
        ----------
        self: Item
            the item
        Returns
        -------
        int
            number of times the item was purchased
        """
        result = db.session.query(func.sum(ItemPurchase.quantity).label('total_quantity')) \
            .select_from(ItemPurchase).where(ItemPurchase.item_id == self.id)[0][0]
        return result or 0

    @property
    def stock_costs(self) -> float:
        """Sums the total costs of the item's stocks
        Parameters
        ----------
        self: Item
            the item
        Returns
        -------
        float
            total costs the item was needed
        """
        result = db.session.query(func.sum(Stock.cost).label('total_cost')) \
            .select_from(Stock).where(Stock.item_id == self.id)[0][0]
        return result or 0.0

    @property
    def total_sold(self) -> float:
        """Sums the money of the purchases made with this item
        Parameters
        ----------
        self: Item
            the item
        Returns
        -------
        float
            total money of the purchases made with this item
        """
        result = db.session.query(func.sum(ItemPurchase.total).label('total_sold')) \
            .select_from(ItemPurchase).where(ItemPurchase.item_id == self.id)[0][0]
        return result or 0.0

    def get_sold(self, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> int:
        """Gets the number of items purchased in the specified timeframe
        Parameters
        ----------
        self: Item
            the item
        start_date: datetime.datetime, optional
            start of the timeframe
        end_date: datetime.datetime, optional
        
        Returns
        -------
        int
            total number of items purchased
        """
        result = db.session.query(func.sum(ItemPurchase.quantity).label('total_sold')) \
            .select_from(ItemPurchase).join(Purchase, Purchase.id == ItemPurchase.purchase_id) \
            .filter(ItemPurchase.item_id == self.id).first()
        return result[0] if result else 0

    @classmethod
    def most_sales(cls, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple:
        """Gets the item with the most sales in the specified timeframe
        Parameters
        ----------
        cls: Item
            the Item object
        start_date: datetime.datetime, optional
            the start of the timeframe
        end_date: datetime.datetime, optional
            the end of the timeframe

        Returns
        -------
        tuple
            the item along with the total sales it made in the specified timeframe
        """
        result = db.session.query(cls, func.sum(ItemPurchase.total).label('total_sales')) \
            .join(ItemPurchase).join(Purchase, Purchase.id == ItemPurchase.purchase_id) \
            .filter(Purchase.added_on.between(start_date, end_date)).group_by(Item) \
            .order_by(text('total_sales DESC')).first()
        return result if result else (None, 0,)

    @classmethod
    def most_sold(cls, start_date=datetime.utcnow()-timedelta(days=30), end_date=datetime.utcnow()) -> tuple:
        """Gets the item with the most items sold in the specified timefraze
        Parameters
        ----------
        cls: Item
            the Item object
        start_date: datetime.datetime, optional
        end_date: datetime.datetime, optional

        Returns
        -------
        tuple
            the item along with the total items sold it made in the specified timeframe
        """
        result = db.session.query(cls, func.sum(ItemPurchase.quantity).label('total_sold')) \
            .join(ItemPurchase).join(Purchase, Purchase.id == ItemPurchase.purchase_id) \
            .filter(Purchase.added_on.between(start_date, end_date)).group_by(Item) \
            .order_by(text('total_sold DESC')).first()
        return result if result else (None, 0,)


class Stock(db.Model):
    """Stock model storing the stock history of the items

    ...
    Attributes
    ----------
    id: int
        the id of the stock
    item_id: int
        the id of the item that was stocked
    cost: float
        total cost it needed to make the stock
    per_item_cost: float
        per item cost of the stock
    quantity: int
        number of items that was stocked
    added_on: datetime.datetime
        the time object was created (automatically setted when not specified using datetime.utcnow method)
    item: Item
        the item that was stocked
    """
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
    """ItemPurchase model storing the item purchases with their respected purchases

    ...
    Attributes
    ----------
    item_id: int
        the id of the purchased item
    purchase_id: int
        the id of the purchase instance
    price: float
        the price of the item
    discount: float
        discount for the current item
    quantity: int
        total items bought
    total: float
        total of the purchase
    item: Item
        the item bought
    purchase: Purchase
        the linked purchase instance
    
    Methods
    -------
    discounted_total(self)
        returns the discounted total of the purchase
    """
    __tablename__ = 'item_purchase'
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey(
        'purchase.id'), primary_key=True)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

    @hybrid_property
    def discounted_total(self) -> float:
        """Returns the discounted total of the item purchased
        Returns
        -------
        float
            discounted total
        """
        return self.total - (self.total * self.discount)

    def __repr__(self) -> str:
        return f'<ItemPurchase {self.id}'


class Purchase(db.Model):
    """Purchase model storing the purchase information

    ...
    Attributes
    ----------
    id: int
        id of the purchase
    reference_id: str
        a uuid identifier of the purchase
    items: sqlalchemy.orm.dynamic.AppenderBaseQuery
        the record of items purchased
    discount: float
        discount of the purchase
    total: float
        total of the purchase
    
    Methods
    -------
    discounted_total(self) -> float
        returns the discounted total of the purchase
    """
    __tablename__ = 'purchase'
    id = db.Column(db.Integer, primary_key=True)
    reference_id = db.Column(db.String(32), default=random_uuid)
    items = db.relationship('ItemPurchase', lazy='dynamic', cascade="all, delete-orphan",
                            backref=db.backref('purchase', uselist=False))
    discount = db.Column(db.Float, default=0)
    total = db.Column(db.Float, nullable=False)
    added_on = db.Column(db.DateTime, default=datetime.utcnow)

    @hybrid_property
    def discounted_total(self) -> float:
        """Calculates the discounted total of the purchase
        Returns
        -------
        float
            discounted total
        """
        return self.total - (self.total * self.discount)

    def __repr__(self) -> str:
        return f'<Purchase {self.id}>'
