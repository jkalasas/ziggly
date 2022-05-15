from datetime import datetime, timedelta

from flask import abort, g, redirect, render_template, request, session, url_for
from sqlalchemy import func, text

from server.models import db, Item, ItemPurchase, Purchase, User, Stock
from server.plugins.login_manager import login_required, login_user, logout_user
from . import bp

@bp.before_app_request
def before_app_request():
    if session.get('signed_in'):
        g.user = User.query.get(session.get('user_id'))
        if g.user:
            g.user.last_access = datetime.utcnow()
            db.session.commit()

def referer_or(alternative):
    return request.headers.get('Referer', alternative)

@bp.get('/')
@login_required
def index():
    print(Item.most_sales())
    most_sales, total_sales = Item.most_sales()
    most_sold, total_sold = Item.most_sold()
    context = {
        'title': 'Home',
        'most_sold': most_sold,
        'total_sold': total_sold,
        'most_sales': most_sales,
        'total_sales': total_sales,
    }
    return render_template('main/index.html', **context)

@bp.get('/login')
def login_page():
    if getattr(g, 'user', None):
        return redirect(url_for('main.index'))

    context = {
        'title': 'Login'
    }
    return render_template('main/login.html', **context)

@bp.post('/login')
def login():
    user = User.verify(
        request.form.get('username', ''),
        request.form.get('password', ''),
    )
    if user:
        login_user(user)
        return redirect(url_for('main.index'))
    return redirect(url_for('main.login'))

@bp.get('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.get('/inventory')
@login_required
def inventory():
    try:
        page = int(request.args.get('p', 1))
    except ValueError:
        page = 1
    stocks = Stock.query.order_by(Stock.added_on.desc()).paginate(page, 20)
    context = {
        'title': 'Inventory',
        'stocks': stocks,
    }
    return render_template('main/inventory.html', **context)

@bp.get('/purchase')
@login_required
def purchases():
    try:
        page = int(request.args.get('p', 1))
    except ValueError:
        page = 1
    purchases = Purchase.query.order_by(Purchase.added_on.desc()).paginate(page, 20)
    context = {
        'title': 'Purchases',
        'purchases': purchases,
    }
    return render_template('main/purchases.html', **context)

@bp.get('/purchase/<int:id>')
@login_required
def receipt(id: int):
    purchase = Purchase.query.filter(Purchase.id==id).first_or_404()
    context = {
        'title': f'Purchase {purchase.id}',
        'purchase': purchase
    }
    return render_template('main/purchase.html', **context)

@bp.get('/cashier')
@login_required
def cashier():
    context = {
        'title': 'Cashier'
    }
    return render_template('main/cashier.html', **context)

@bp.get('/item')
@login_required
def items():
    return redirect(url_for('main.items_all'))

@bp.post('/item')
@login_required
def new_item():
    name = request.form.get('name')
    price = request.form.get('price')
    item = Item(name=name, price=price)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('main.items_all'))

@bp.get('/item/all')
@login_required
def items_all():
    try:
        page = int(request.args.get('p', 1))
    except ValueError:
        page = 1
    items = Item.query.order_by(Item.name.desc()).paginate(page, 20)
    context = {
        'title': 'Items',
        'items': items
    }
    return render_template('main/items.html', **context)

@bp.get('/item/<int:id>')
@login_required
def item_info(id: int):
    item = Item.query.filter(Item.id==id).first_or_404()
    stocks = item.stocks.order_by(Stock.added_on.desc()).limit(10)
    purchases = db.session.query(
        Purchase.id.label('id'), ItemPurchase.quantity.label('quantity'),
        ItemPurchase.discounted_total.label('total'), Purchase.added_on.label('added_on')
    ).select_from(Purchase).join(ItemPurchase).where(ItemPurchase.item_id==item.id).order_by(text('added_on DESC'))

    context = {
        'title': item.name,
        'item': item,
        'stocks': stocks,
        'purchases': purchases,
    }
    return render_template('main/item.html', **context)

@bp.post('/item/<int:id>')
@login_required
def manage_item(id: int):
    method = request.form.get('_method')
    if method == 'PUT':
        return update_item(id)
    elif method == 'DELETE':
        return delete_item(id)
    abort(404)

def update_item(id: int):
    item = Item.query.filter(Item.id==id).first_or_404()
    item.name = request.form.get('name')
    item.price = request.form.get('price')
    db.session.commit()
    return redirect(referer_or(url_for('main.item_info', id=id)))

def delete_item(id: int):
    item = Item.query.filter(Item.id==id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.items_all'))

@bp.get('/item/<int:id>/stock')
@login_required
def item_stock(id: int):
    try:
        page = int(request.args.get('p', 1))
    except ValueError:
        page = 1
    item: Item = Item.query.filter(Item.id==id).first_or_404()
    stocks = item.stocks.order_by(Stock.added_on.desc()).paginate(page, 20)
    context = {
        'title': f'{item.name} Stocks',
        'item': item,
        'stocks': stocks
    }
    return render_template('main/item_stock.html', **context)

@bp.post('/stock')
@login_required
def add_stock():
    item_id = request.form.get('item')
    quantity = request.form.get('quantity')
    cost = request.form.get('total-cost')
    per_item_cost = request.form.get('per-item-cost')
    if not (item_id and quantity and cost and per_item_cost):
        abort(401)
    stock = Stock(item_id=item_id, quantity=quantity, cost=cost, per_item_cost=per_item_cost)
    db.session.add(stock)
    db.session.commit()
    return redirect(referer_or(url_for('main.inventory')))

@bp.post('/stock/<int:id>')
@login_required
def manage_stock(id: int):
    method = request.form.get('_method')
    if method == 'DELETE':
        return delete_stock(id)
    abort(404)

def delete_stock(id: int):
    stock = Stock.query.filter(Stock.id==id).first_or_404()
    db.session.delete(stock)
    db.session.commit()
    return redirect(referer_or(url_for('main.inventory')))