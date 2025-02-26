import json
import os
from models import Category, Product, User, Comment, Cart, CartItem, Order, OrderItem, db
from sqlalchemy import func
from flask_login import current_user

# Lấy đường dẫn tuyệt đối của thư mục hiện tại
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_categories():
    return Category.query.all()

def load_products(q=None, cate_id=None):
    query = Product.query
    
    if q:
        query = query.filter(Product.name.contains(q))
    if cate_id:
        query = query.filter(Product.category_id == cate_id)
        
    return query.all()

def get_product_by_id(id):
    return Product.query.get(id)

def add_user(username, password, email):
    user = User(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()

def get_user_by_username(username):
    return User.query.filter(User.username == username).first()

def add_to_cart(product_id, quantity=1):
    cart = Cart.query.filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    cart_item = CartItem.query.filter(CartItem.cart_id == cart.id,
                                    CartItem.product_id == product_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)
        
    db.session.commit()

def get_cart_items():
    cart = Cart.query.filter(Cart.user_id == current_user.id).first()
    if cart:
        return CartItem.query.filter(CartItem.cart_id == cart.id).all()
    return []

def add_comment(product_id, content, rating):
    comment = Comment(content=content, rating=rating,
                     product_id=product_id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()

def create_order():
    cart = Cart.query.filter(Cart.user_id == current_user.id).first()
    if cart:
        order = Order(user_id=current_user.id)
        db.session.add(order)
        
        for item in cart.items:
            order_item = OrderItem(order_id=order.id,
                                 product_id=item.product_id,
                                 quantity=item.quantity,
                                 price=item.product.price)
            db.session.add(order_item)
            
        db.session.delete(cart)
        db.session.commit()
        return order
    return None

if __name__=="__main__":
    print(load_products())