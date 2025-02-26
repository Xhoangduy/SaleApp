from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Product, Category, Comment, Cart, CartItem, Order
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import dao

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Thay đổi key này trong production
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Duy%402003@localhost/saleapp?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo database
db.init_app(app)

# Cấu hình Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes cho trang chủ và chi tiết sản phẩm
@app.route('/')
def index():
    q = request.args.get("q")
    cate_id = request.args.get("category_id")
    cates = dao.load_categories()
    products = dao.load_products(q=q, cate_id=cate_id)
    return render_template("index.html", cates=cates, products=products)

@app.route('/products/<int:id>')
def details(id):
    prod = dao.get_product_by_id(id)
    return render_template('product-details.html', prod=prod)

# Routes cho authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if dao.get_user_by_username(username):
            flash('Username đã tồn tại')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        dao.add_user(username, hashed_password, email)
        flash('Đăng ký thành công')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = dao.get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Username hoặc password không đúng')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Routes cho giỏ hàng
@app.route('/cart/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    dao.add_to_cart(product_id, quantity)
    flash('Đã thêm vào giỏ hàng')
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    cart_items = dao.get_cart_items()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', items=cart_items, total=total)

# Routes cho đơn hàng
@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    order = dao.create_order()
    if order:
        flash('Đặt hàng thành công')
        return redirect(url_for('orders'))
    flash('Giỏ hàng trống')
    return redirect(url_for('cart'))

@app.route('/orders')
@login_required
def orders():
    user_orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('orders.html', orders=user_orders)

# Routes cho comments
@app.route('/products/<int:product_id>/comment', methods=['POST'])
@login_required
def add_comment(product_id):
    content = request.form.get('content')
    rating = request.form.get('rating')
    dao.add_comment(product_id, content, rating)
    return redirect(url_for('details', id=product_id))

# Admin interface
admin = Admin(app, name='SaleApp Admin', template_mode='bootstrap3')

class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == 'ADMIN'

admin.add_view(AdminView(Category, db.session))
admin.add_view(AdminView(Product, db.session))
admin.add_view(AdminView(Order, db.session))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Tạo database tables
    app.run(debug=True)