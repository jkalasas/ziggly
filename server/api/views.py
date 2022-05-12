from flask import g, request

from server.models import db, Item
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
    name = data.get('name')
    price = data.get('price')
    item = Item(name=name, price=price)
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