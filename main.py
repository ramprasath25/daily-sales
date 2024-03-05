from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Replace the connection string below with your PostgreSQL connection string
SQLALCHEMY_DATABASE_URL = "postgresql://kong:kong@localhost:5432/bruvvers"

# SQLAlchemy setup
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Product model
class Product(Base):
    __tablename__   = "products"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String, index=True, unique=True)

class DailyOnlineSales(Base):
    __tablename__   = "daily_online_sales"
    id              = Column(Integer, primary_key=True, index=True)
    online_sale     = Column(Integer, default=0)
    sale_date       = Column(DateTime, index=True, default=datetime.now)

# Define DailySales model
class DailySales(Base):
    __tablename__   = "daily_sales"
    id              = Column(Integer, primary_key=True, index=True)
    product_id      = Column(Integer, ForeignKey("products.id"))
    product         = relationship("Product", back_populates="sales")
    quantity_sold   = Column(Integer)
    sale_date       = Column(DateTime, index=True, default=datetime.now)

    # Function to serialize object to dictionary
    def to_dict(self):
        return {
            "product_name"  : self.product.name,
            "quantity_sold" : self.quantity_sold,
            "sale_date"     : self.sale_date.strftime("%Y-%m-%d")
        }

# Establish one-to-many relationship between Product and DailySales
Product.sales = relationship("DailySales", back_populates="product")

# Create tables
Base.metadata.create_all(bind=engine)

def get_products_from_database(date):
    db = SessionLocal()
    products_with_sales = db.query(Product.id, Product.name, func.coalesce(func.sum(DailySales.quantity_sold), 0).label('total_quantity_sold')) \
                            .outerjoin(DailySales, (Product.id == DailySales.product_id) & (DailySales.sale_date == date)) \
                            .group_by(Product.id, Product.name) \
                            .all()
    db.close()
    return products_with_sales

def get_online_sales_from_db(date):
    db = SessionLocal()
    online_sales = db.query(func.coalesce(DailyOnlineSales.online_sale, 0)).filter(DailyOnlineSales.sale_date==date).first()
    db.close()
    return online_sales
   
# Function to record daily sales
def record_daily_sales(product_id, quantity_sold, sale_date):
    db = SessionLocal()
    existing_sale = db.query(DailySales).filter_by(product_id=product_id, sale_date=sale_date).first()
    if existing_sale:
        existing_sale.quantity_sold = int(quantity_sold)
    else:
        sale = DailySales(product_id=product_id, quantity_sold=quantity_sold, sale_date=sale_date)
        db.add(sale)
    db.commit()
    db.close()

def record_online_sales(sale_date, online_sales):
    db = SessionLocal()
    existing_sale = db.query(DailyOnlineSales).filter_by(sale_date=sale_date).first()
    if existing_sale:
        existing_sale.online_sale = int(online_sales)
    else:
        sale = DailyOnlineSales(online_sale=int(online_sales), sale_date=sale_date)
        db.add(sale)
    db.commit()
    db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def get_products():
    date = request.args.get('date', datetime.now().date())  # Get date parameter from request, default to today's date
    try:
        date = datetime.strptime(str(date), '%Y-%m-%d').date()  # Convert date string to datetime object
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    products_with_sales = get_products_from_database(date)
    online_sales_result = get_online_sales_from_db(date)
    online_sales = online_sales_result[0] if online_sales_result is not None else 0
    products_data = [{"name": product_name, "total_quantity_sold": total_quantity_sold, "id": id} for id, product_name, total_quantity_sold in products_with_sales]
    result = {"date": date, "online_sales": online_sales, "product_data": products_data}
    return jsonify(result)


@app.route('/record-sale', methods=['POST'])
def record_sale():
    data = request.json
    product_id = data.get('product_id')
    quantity_sold = data.get('quantity_sold')
    sale_date_str = data.get('sale_date')
    # if product_id is None or quantity_sold is None or sale_date_str is None:
    #     return jsonify({"error": "Missing data"}), 400
    try:
        sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
    for prod in data.get("products"):
        record_daily_sales(prod["product_id"], prod["quantity_sold"], sale_date)
    record_online_sales(sale_date, data.get("online_sales", 0))
    return jsonify({"message": "Sale recorded successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
