from flask import Flask, jsonify
from flask_migrate import Migrate
from config import Config
from extensions import db

from models import (
    ProductCategory, Product, SBU, LegalStatusMaster, VendorCategoryMaster,
    DesignationMaster, BankMaster
)

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    # Register the 6 extracted modules
    from routes.product_categories import bp as product_categories_bp
    from routes.products import bp as products_bp
    from routes.sbus import bp as sbus_bp
    from routes.vendor_masters import bp as vendor_masters_bp
    from routes.vendors import bp as vendors_bp
    from routes.po import bp as po_bp
    from routes.grn import bp as grn_bp

    app.register_blueprint(product_categories_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(sbus_bp)
    app.register_blueprint(vendor_masters_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(po_bp)
    app.register_blueprint(grn_bp)

    @app.route('/api/health')
    def health():
        return jsonify(status='LIVE', db='postgres', modules=[
            'product_categories', 'products', 'sbus', 'vendors', 'po', 'grn'
        ])

    with app.app_context():
        db.create_all()
        _seed_masters()

    return app


def _seed_masters():
    """Same default seed data as the original app, ported to Postgres."""
    try:
        default_categories = ["Packeging Materials", "Finished Products", "Raw Materials"]
        existing_cats = [c.category_name for c in ProductCategory.query.all()]
        if len(existing_cats) < 3:
            for cat_name in default_categories:
                if cat_name not in existing_cats:
                    db.session.add(ProductCategory(category_name=cat_name))
            db.session.commit()

        if Product.query.count() == 0:
            default_products = [
                {"product_code": "FINI-0018", "name": "Hydrate Lime 75%", "category": "Finished Products", "hsn_code": "25222000", "description": "hydrate from waste"},
                {"product_code": "FINI-0017", "name": "Silica", "category": "Finished Products", "hsn_code": "25222000", "description": "waste of Hydrate plant"},
                {"product_code": "FINI-0016", "name": "Hydrate Lime 80%", "category": "Finished Products", "hsn_code": "25222000", "description": "Pulviser material from calsined lime"},
                {"product_code": "FINI-0015", "name": "Hydrate Lime 90%", "category": "Finished Products", "hsn_code": "25222000", "description": "Classifier from quick Lime"},
                {"product_code": "FINI-0014", "name": "Quick Lime Powder 200 mesh", "category": "Finished Products", "hsn_code": "25222000", "description": "200 mesh quick lime powder"},
                {"product_code": "FINI-0013", "name": "Quick Lime Fines 0-3 mm", "category": "Finished Products", "hsn_code": "25222000", "description": "sinter fines"},
                {"product_code": "FINI-0012", "name": "Quick Lime Lumps 10-60 mm", "category": "Finished Products", "hsn_code": "25222000", "description": "quick lime lumps 10-60mm"},
                {"product_code": "FINI-0011", "name": "Quick Lime Lumps 40-60 mm", "category": "Finished Products", "hsn_code": "25222000", "description": "quick lime lumps 40-60mm"},
                {"product_code": "FINI-0010", "name": "Quick Lime Lumps 10-40 mm", "category": "Finished Products", "hsn_code": "25221000", "description": "sizing plant processed"},
                {"product_code": "FINI-0009", "name": "Gulli", "category": "Finished Products", "hsn_code": "25221000", "description": "Unburnt and over burnt"},
                {"product_code": "FINI-0008", "name": "Chunna", "category": "Finished Products", "hsn_code": "25221000", "description": "Waste Kiln Powder"},
                {"product_code": "FINI-0007", "name": "Quick Lime", "category": "Finished Products", "hsn_code": "25221000", "description": "From Kilns"},
                {"product_code": "PACK-0006", "name": "Jumbo Bags 48\"", "category": "Packeging Materials", "hsn_code": "1000000", "description": "Jumbo bags 48 inch"},
                {"product_code": "PACK-0005", "name": "Hydrate Lime Valve Bags", "category": "Packeging Materials", "hsn_code": "1000000", "description": "Valve bags"},
                {"product_code": "PACK-0004", "name": "Repol 1st", "category": "Packeging Materials", "hsn_code": "1000000", "description": "Repol 1st quality"},
                {"product_code": "PACK-0003", "name": "Jumbo Bags 52\"", "category": "Packeging Materials", "hsn_code": "1000000", "description": "Jumbo bags 52 inch"},
                {"product_code": "RAWM-0002", "name": "Pet Coke", "category": "Raw Materials", "hsn_code": "18000000", "description": "Kiln fuel"},
                {"product_code": "RAWM-0001", "name": "Lime Stone", "category": "Raw Materials", "hsn_code": "25221000", "description": "Main raw material"},
            ]
            for prod in default_products:
                if not Product.query.filter_by(product_code=prod["product_code"]).first():
                    db.session.add(Product(
                        name=prod["name"], category=prod["category"], product_code=prod["product_code"],
                        hsn_code=prod["hsn_code"], description=prod["description"],
                        loose_stock_mt=0, jumbo_mt=0, hdpe_40kg_mt=0, total_stock_mt=0,
                        min_stock=0, reorder_level=0, sale_price=0, purchase_price=0, location=""
                    ))
            db.session.commit()
    except Exception as e:
        print(f"Product/Category seeding failed: {e}")
        db.session.rollback()

    # Hidden vendor masters
    try:
        if LegalStatusMaster.query.count() == 0:
            for name in ["Proprietor", "Partnership", "LLP", "Private Limited", "Public Limited", "HUF", "Trust",
                         "Society", "Government", "OPC", "One Person Company", "Co-operative Society", "Others"]:
                db.session.add(LegalStatusMaster(name=name))
        if VendorCategoryMaster.query.count() == 0:
            for name in ["MSE", "MSME", "SSI", "Small", "Medium", "Large", "Non-MSE", "Government", "Trader",
                         "Importer", "Service Provider", "Manufacturer", "Distributor", "Others"]:
                db.session.add(VendorCategoryMaster(name=name))
        if DesignationMaster.query.count() == 0:
            for name in ["Proprietor", "Partner", "Director", "Managing Director", "Manager", "Purchase Manager",
                         "Accounts Manager", "Owner", "CEO", "AGM", "DGM", "Executive", "Accountant",
                         "Sales Manager", "General Manager", "Chairman", "Secretary", "Others"]:
                db.session.add(DesignationMaster(name=name))
        if BankMaster.query.count() == 0:
            banks = [
                ("State Bank of India", "SBI"), ("Punjab National Bank", "PNB"), ("Bank of Baroda", "BOB"),
                ("Canara Bank", "CAN"), ("Union Bank of India", "UBI"), ("Bank of India", "BOI"),
                ("Indian Bank", "INDIAN"), ("Central Bank of India", "CBI"), ("Indian Overseas Bank", "IOB"),
                ("UCO Bank", "UCO"), ("Bank of Maharashtra", "BOM"), ("Punjab & Sind Bank", "PSB"),
                ("HDFC Bank", "HDFC"), ("ICICI Bank", "ICICI"), ("Axis Bank", "AXIS"),
                ("Kotak Mahindra Bank", "KOTAK"), ("IndusInd Bank", "INDUS"), ("Yes Bank", "YES"),
                ("IDBI Bank", "IDBI"), ("IDFC First Bank", "IDFC"), ("Federal Bank", "FED"),
                ("South Indian Bank", "SIB"), ("Karnataka Bank", "KTK"), ("Karur Vysya Bank", "KVB"),
                ("City Union Bank", "CUB"), ("RBL Bank", "RBL"), ("Bandhan Bank", "BANDHAN"),
                ("Jammu & Kashmir Bank", "JKB"), ("Dhanlaxmi Bank", "DLB"), ("Nainital Bank", "NTB"),
                ("Ujjivan Small Finance Bank", "UJJIVAN"), ("AU Small Finance Bank", "AU"),
                ("Equitas Small Finance Bank", "EQUITAS"), ("Other Bank", "OTHER")
            ]
            for bname, bcode in banks:
                db.session.add(BankMaster(bank_name=bname, bank_code=bcode))
        db.session.commit()
    except Exception as e:
        print(f"Master seeding failed: {e}")
        db.session.rollback()


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
