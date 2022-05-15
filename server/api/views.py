from flask import g, request

from sqlalchemy import or_
from server.models import db, Item, ItemPurchase, Purchase
from server.plugins.login_manager import login_required
from . import bp

@bp.before_request
@login_required
def before_request():
    pass

@bp.get('/item/<int:id>')
def get_item(id: int):
    item = Item.query.get(id)
    result = {
        'success': True,
        'result': item.to_dict() if item else {}
    }
    return result

@bp.post('/item')
def add_item():
    data = request.json
    bar_code = data.get('bar-code','')
    name = data.get('name')
    price = data.get('price')
    item = Item(name=name, price=price, bar_code=bar_code)
    db.session.add(item)
    db.session.commit()
    result = {
        'success': True,
        'item': item.to_dict(),
    }
    return result

@bp.put('/item/<int:id>')
def update_item(id: int):
    data = request.json
    item = Item.query.get(id)
    if not item:
        return {'success': True, 'result': {}}
    
    for key, value in data.items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    db.session.commit()
    return {'success': True, 'result': item.to_dict()}

@bp.get('/items')
def get_items():
    items = [x.to_dict() for x in Item.query.order_by(Item.name)]
    return {'success': True, 'items': items}

@bp.post('/purchase')
def purchase():
    data = request.json
    purchased_items = []
    grand_total = 0
    purchase = Purchase(total=0)
    for item in data.get('items', []):
        qitem = Item.query.filter(Item.id==item['id']).first_or_404()
        quantity = int(item['quantity'])
        total = quantity * qitem.price
        grand_total += total
        purchased_items.append(
            ItemPurchase(item=qitem, purchase=purchase, 
                quantity=quantity, price=qitem.price, total=total)
        )
    purchase.total = grand_total
    db.session.add(purchase)
    db.session.commit()
    return {
        'success': True,
        'result': {'id': purchase.id}
    }

@bp.get('/search/item')
def search_item():
    name = request.args.get('search', '')
    try:
        page = int(request.args.get('p', 1))
    except ValueError:
        page = 1
    query = Item.query.filter(or_(Item.name.ilike(f'%{name}%'), Item.bar_code.ilike(f'%{name}%'))) \
        .order_by(Item.name).paginate(page, 10)
    result = []
    for x in query.items:
        result.append({**x.to_dict(), 'stock': x.in_stock})
    context = {
        'success': True,
        'result': result,
        'has_next': query.has_next,
    }
    return context