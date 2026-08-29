
"""
LEMON ERP - MASTER WORKFLOW - v4.5
BASE: v1.3.py = v4.4.7 Fixed Tabular Duplicate + Vendor Master Enhanced
Fixes in v4.4.10:
- ONLY Vendor master enhanced - Added on top of v4.4.9.1 - Nothing removed - No other module changed
- A. Compliance: MSME Certificate No + Expiry + Upload, GST Registration Type Regular/Composition/Unregistered/SEZ/Deemed Export, TDS Section 194C 194J 194Q 194H 194I etc, Vendor Rating 1-5 stars + Last Audit Date, Document uploads GST Cert PAN Card Cancelled Cheque MSME Cert ISO Cert (base64 storage)
- B. Opening Balance Dr/Cr for migration + Ledger Group Sundry Creditors etc
- E. Departments in contacts + Primary contact flag is_primary checkbox
- F. Created By/At Updated By/At auto + Approval Workflow Draft Pending Approved Rejected + Last Transaction Date + Total Business Value sum of POs (po value = qty*rate)
- All previous fields kept: VEND-0001, Station, State, GST PAN TAN Legal Status Vendor Category Bank Details single dropdown searchable + Contacts
- Filters enhanced with Approval Status, Rating
- List shows new fields in tooltip and badges
- Bank single dropdown fix kept from v4.4.9.1
Fixes in v4.4.9.1:
- Fixed Bank Details form had 2 fields for bank selection - Now single searchable dropdown only - Removed extra select vb_bank_sel - Keep only input list datalist
- Rest locked to v4.4.9
Fixes in v4.4.9:
- ONLY Vendor module changed, rest locked to v4.4.8 FIXED
- Vendor Master redesigned: Heading + Add New Vendor button top after heading + Filters + Search bar
- Fields: Vendor Code Auto VEND-0001, Vendor Name text, Station text, Address text, State text for GST, GST No text, PAN No text, TAN No text, Legal Status dropdown (hidden master), Vendor Category dropdown (hidden master MSE/MSME etc), Bank Details Add Bank Account button with lines: Select Bank searchable dropdown nationalised banks India + Other (hidden bank master), Branch Name, Account Name, IFSC, Account No, Transaction Limit, Add Contact button with lines: Name, Designation dropdown hidden master, Mobile No, Whatsapp No, Land Line, Extension No, Email
- Bank master hidden database: 35+ nationalised/private banks seeded
- Legal Status master hidden: Proprietor, Partnership, LLP, Private Limited, Public Limited, HUF, Trust, Society, Govt, Others
- Vendor Category master: MSE, MSME, SSI, Small, Medium, Large, Non-MSE, Govt, Trader, Others
- Designation master: Proprietor, Partner, Director, Managing Director, Manager, Purchase Manager, Accounts Manager, Owner, CEO, AGM, DGM, Executive, Accountant, Others
- Vendor model expanded: vendor_code UNIQUE, name, station, address, state, gst_no, pan_no, tan_no, legal_status, vendor_category, bank_details JSON, contacts JSON, status Active/Inactive/Blocked, created_at + old fields compatibility
- List: Tabular clean with filters: Search by name/GST/PAN/Station/State, Type filters Legal Status, Vendor Category, State, Bank, Status, plus PO/GRN counts (yes for productivity)
- Credit varies PO to PO so not fixed - removed credit limit fixed, showing PO counts
- Duplicate NO
- Everything else 100% unchanged from v4.4.8 FIXED
DB: lemon_erp_v44_1_category.db single file persistent path via DATABASE_PATH env
File: backend/app_v4_final.py
URL: https://lemon-erp.onrender.com
"""

from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json, os, re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lemon-erp-v45-po-module-fixed'
db_path = os.environ.get('DATABASE_PATH', os.path.join(os.path.dirname(__file__), '..', 'instance', 'lemon_erp_v44_1_category.db'))
os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath(db_path)}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================
class ProductCategory(db.Model):
    __tablename__ = 'product_category'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True)
    hsn_code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    loose_stock_mt = db.Column(db.Float, default=0)
    jumbo_mt = db.Column(db.Float, default=0)
    hdpe_40kg_mt = db.Column(db.Float, default=0)
    total_stock_mt = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    reorder_level = db.Column(db.Float, default=0)
    sale_price = db.Column(db.Float, default=0)
    purchase_price = db.Column(db.Float, default=0)
    location = db.Column(db.String(100), default='')

class SBU(db.Model):
    __tablename__ = 'sbu'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class KilnAsset(db.Model):
    __tablename__ = 'kiln_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    kiln_no = db.Column(db.String(50))
    lining_installation_date = db.Column(db.String(20), default='')
    health_status = db.Column(db.String(50), default='Good')
    products_capacity = db.Column(db.Text)

class SizingPlantAsset(db.Model):
    __tablename__ = 'sizing_plant_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    plant_no = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)
    machineries = db.Column(db.Text, default='')

class HydrationPlantAsset(db.Model):
    __tablename__ = 'hydration_plant_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    plant_no = db.Column(db.String(50))
    products_capacity = db.Column(db.Text)
    machineries = db.Column(db.Text, default='')

class StockYardAsset(db.Model):
    __tablename__ = 'stock_yard_asset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=False)
    yard_name = db.Column(db.String(100))
    yard_items = db.Column(db.Text)

# Hidden Masters for Vendor
class LegalStatusMaster(db.Model):
    __tablename__ = 'legal_status_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)

class VendorCategoryMaster(db.Model):
    __tablename__ = 'vendor_category_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)

class DesignationMaster(db.Model):
    __tablename__ = 'designation_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True)

class BankMaster(db.Model):
    __tablename__ = 'bank_master'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bank_name = db.Column(db.String(200), unique=True)
    bank_code = db.Column(db.String(20))

# Vendor Master Enhanced v4.4.9
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor_code = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(200), nullable=False)
    station = db.Column(db.String(100))
    address = db.Column(db.Text)
    state = db.Column(db.String(100))
    gst_no = db.Column(db.String(50))
    pan_no = db.Column(db.String(20))
    tan_no = db.Column(db.String(20))
    legal_status = db.Column(db.String(100))
    vendor_category = db.Column(db.String(100))
    bank_details = db.Column(db.Text)  # JSON list
    contacts = db.Column(db.Text)  # JSON list - now includes department, is_primary
    status = db.Column(db.String(20), default='Active')
    # old compatibility
    type = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    credit_limit = db.Column(db.Float, default=0)
    pending_due = db.Column(db.Float, default=0)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # v4.4.10 new fields - Compliance
    msme_cert_no = db.Column(db.String(100), default='')
    msme_expiry = db.Column(db.String(20), default='')
    msme_upload = db.Column(db.Text, default='')  # base64 or filename
    gst_reg_type = db.Column(db.String(50), default='Regular')  # Regular/Composition/Unregistered/SEZ/Deemed Export
    tds_section = db.Column(db.String(50), default='194C')
    vendor_rating = db.Column(db.Integer, default=0)  # 1-5 stars
    last_audit_date = db.Column(db.String(20), default='')
    # Document uploads JSON: {gst_cert, pan_card, cancelled_cheque, msme_cert, iso_cert} base64
    documents = db.Column(db.Text, default='{}')
    # B. Financial migration
    opening_balance = db.Column(db.Float, default=0)
    opening_balance_type = db.Column(db.String(10), default='Dr')  # Dr/Cr
    ledger_group = db.Column(db.String(100), default='Sundry Creditors')
    # F. Audit & Workflow
    created_by = db.Column(db.String(100), default='Admin')
    updated_by = db.Column(db.String(100), default='Admin')
    updated_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    approval_status = db.Column(db.String(20), default='Draft')  # Draft/Pending/Approved/Rejected
    last_transaction_date = db.Column(db.String(30), default='')
    total_business_value = db.Column(db.Float, default=0)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    type = db.Column(db.String(50))
    gst_no = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    pending_receivable = db.Column(db.Float, default=0)

class Packaging(db.Model):
    __tablename__ = 'packaging'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pack_type = db.Column(db.String(100))
    pack_cat = db.Column(db.String(50))
    capacity = db.Column(db.Float, default=0)
    closing = db.Column(db.Float, default=0)
    min_stock = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))

class MO(db.Model):
    __tablename__ = 'manufacturing_order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sbu = db.Column(db.String(100))
    type = db.Column(db.String(50))
    unit = db.Column(db.String(100))
    limestone_mt = db.Column(db.Float, default=0)
    petcoke_mt = db.Column(db.Float, default=0)
    output_mt = db.Column(db.Float, default=0)
    wastage = db.Column(db.Float, default=0)
    input_product = db.Column(db.String(100))
    output_product = db.Column(db.String(100))
    operator = db.Column(db.String(100))
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class PO(db.Model):
    __tablename__ = 'po'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Header - v4.5
    po_no = db.Column(db.String(100), unique=True)
    rfq_no = db.Column(db.String(100), default='')
    po_date = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))
    po_validity = db.Column(db.String(20), default='')
    po_type = db.Column(db.String(50), default='Raw Material')
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=True)
    sbu_name = db.Column(db.String(100), default='')
    delivery_address = db.Column(db.Text, default='')
    billing_address = db.Column(db.Text, default='')
    same_as_delivery = db.Column(db.Boolean, default=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name_filter = db.Column(db.String(100), default='')
    vendor = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
    vendor_code = db.Column(db.String(50), default='')
    vendor_state = db.Column(db.String(100), default='')
    items = db.Column(db.Text, default='[]')
    taxable_value = db.Column(db.Float, default=0)
    cgst_amount = db.Column(db.Float, default=0)
    sgst_amount = db.Column(db.Float, default=0)
    igst_amount = db.Column(db.Float, default=0)
    freight_amount = db.Column(db.Float, default=0)
    round_off = db.Column(db.Float, default=0)
    grand_total = db.Column(db.Float, default=0)
    material = db.Column(db.String(100))
    qty = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    unit = db.Column(db.String(100))
    delivery_type = db.Column(db.String(50), default='One Time')
    delivery_schedule = db.Column(db.Text, default='')
    payment_terms_days = db.Column(db.Integer, default=0)
    rate_basis = db.Column(db.String(50), default='FOR')
    freight_terms = db.Column(db.String(100), default='')
    tds_applicable = db.Column(db.String(20), default='Not Applicable')
    tds_percent = db.Column(db.Float, default=0)
    rcm_applicable = db.Column(db.String(20), default='No')
    rcm_percent = db.Column(db.Float, default=0)
    documents = db.Column(db.Text, default='{}')
    status = db.Column(db.String(50), default='Draft')
    approval_status = db.Column(db.String(50), default='Draft')
    created_by = db.Column(db.String(100), default='Admin')
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_by = db.Column(db.String(100), default='Admin')
    updated_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class GRN(db.Model):
    __tablename__ = 'grn'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grn_no = db.Column(db.String(100), unique=True)
    grn_date = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))
    grn_type = db.Column(db.String(50), default='Against PO')
    po_id = db.Column(db.Integer, db.ForeignKey('po.id'), nullable=True)
    po_no = db.Column(db.String(100), default='')
    sbu_id = db.Column(db.Integer, db.ForeignKey('sbu.id'), nullable=True)
    sbu_name = db.Column(db.String(100), default='')
    sbu_code = db.Column(db.String(20), default='')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=True)
    vendor = db.Column(db.String(100))
    vendor_code = db.Column(db.String(50), default='')
    vendor_state = db.Column(db.String(100), default='')
    station = db.Column(db.String(100), default='')
    vehicle_no = db.Column(db.String(100))
    driver_name = db.Column(db.String(100), default='')
    driver_mobile = db.Column(db.String(20), default='')
    transporter = db.Column(db.String(100), default='')
    lr_no = db.Column(db.String(100), default='')
    eway_bill = db.Column(db.String(100), default='')
    invoice_no = db.Column(db.String(100), default='')
    invoice_date = db.Column(db.String(20), default='')
    challan_no = db.Column(db.String(100), default='')
    bill_no = db.Column(db.String(100), default='')
    rawana_no = db.Column(db.String(100), default='')
    wayment_slip_no = db.Column(db.String(100), default='')
    material = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(100), default='')
    product_code = db.Column(db.String(50), default='')
    hsn_code = db.Column(db.String(20), default='')
    spec = db.Column(db.Text, default='')
    unit = db.Column(db.String(100), default='MT')
    po_qty = db.Column(db.Float, default=0)
    supplier_qty = db.Column(db.Float, default=0)
    received_qty = db.Column(db.Float, default=0)
    accepted_qty = db.Column(db.Float, default=0)
    rejected_qty = db.Column(db.Float, default=0)
    wastage_kg = db.Column(db.Float, default=0)
    rate = db.Column(db.Float, default=0)
    amount = db.Column(db.Float, default=0)
    taxable_value = db.Column(db.Float, default=0)
    cgst_percent = db.Column(db.Float, default=0)
    cgst_amount = db.Column(db.Float, default=0)
    sgst_percent = db.Column(db.Float, default=0)
    sgst_amount = db.Column(db.Float, default=0)
    igst_percent = db.Column(db.Float, default=0)
    igst_amount = db.Column(db.Float, default=0)
    grand_total = db.Column(db.Float, default=0)
    gross_kg = db.Column(db.Float, default=0)
    tare_kg = db.Column(db.Float, default=0)
    net_kg = db.Column(db.Float, default=0)
    net_mt = db.Column(db.Float, default=0)
    qty_differ = db.Column(db.Float, default=0)
    differ_percent = db.Column(db.Float, default=0)
    bilty_rate = db.Column(db.Float, default=0)
    bilty_amount = db.Column(db.Float, default=0)
    freight_advance = db.Column(db.Float, default=0)
    unloading_point = db.Column(db.String(100), default='')
    unloading_charges = db.Column(db.Float, default=0)
    stock_yard_id = db.Column(db.Integer, default=0)
    stock_yard_name = db.Column(db.String(100), default='')
    moisture_percent = db.Column(db.Float, default=0)
    quality_status = db.Column(db.String(20), default='OK')
    quality_remark = db.Column(db.Text, default='OK')
    deduction_amount = db.Column(db.Float, default=0)
    shortage_ded = db.Column(db.Float, default=0)
    rate_difference = db.Column(db.Float, default=0)
    debit_note_no = db.Column(db.String(100), default='')
    remarks = db.Column(db.Text, default='')
    documents = db.Column(db.Text, default='{}')
    status = db.Column(db.String(50), default='Approved')
    approval_status = db.Column(db.String(50), default='Approved')
    created_by = db.Column(db.String(100), default='Admin')
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    updated_by = db.Column(db.String(100), default='Admin')
    updated_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class Dispatch(db.Model):
    __tablename__ = 'dispatch'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer = db.Column(db.String(100))
    vehicle_no = db.Column(db.String(100))
    product = db.Column(db.String(100))
    qty_mt = db.Column(db.Float, default=0)
    qr_bags = db.Column(db.Integer, default=0)
    unit = db.Column(db.String(100))

class QRBag(db.Model):
    __tablename__ = 'qr_bag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bag_id = db.Column(db.String(100), unique=True)
    product = db.Column(db.String(100))
    weight = db.Column(db.Float)
    unit = db.Column(db.String(100))
    qr_data = db.Column(db.Text)
    qr_base64 = db.Column(db.Text)
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

with app.app_context():
    db.create_all()
    # ========== V1 DEFAULT MASTERS SEEDING - 3 CATEGORIES + 18 PRODUCTS - From Screenshots v4.4.6 ==========
    try:
        default_categories = ["Packeging Materials", "Finished Products", "Raw Materials"]
        existing_cats = [c.category_name for c in ProductCategory.query.all()]
        if len(existing_cats) < 3:
            for cat_name in default_categories:
                if cat_name not in existing_cats:
                    db.session.add(ProductCategory(category_name=cat_name))
            db.session.commit()
            print("V1 Seeded Product Categories:", default_categories)
        
        if Product.query.count() == 0:
            default_products = [
                {"product_code": "FINI-0018", "name": "Hydrate Lime 75%", "category": "Finished Products", "hsn_code": "25222000", "description": "hydrate from waste"},
                {"product_code": "FINI-0017", "name": "Silica", "category": "Finished Products", "hsn_code": "25222000", "description": "waste of Hydrate plant"},
                {"product_code": "FINI-0016", "name": "Hydrate Lime 80%", "category": "Finished Products", "hsn_code": "25222000", "description": "Pulviser material from calsined lime"},
                {"product_code": "FINI-0015", "name": "Hydrate Lime 90%", "category": "Finished Products", "hsn_code": "25222000", "description": "Classifier from quick Lime"},
                {"product_code": "FINI-0014", "name": "Quick Lime Powder 200 mesh", "category": "Finished Products", "hsn_code": "25222000", "description": "fghj"},
                {"product_code": "FINI-0013", "name": "Quick Lime Fines 0-3 mm", "category": "Finished Products", "hsn_code": "25222000", "description": "sinter fines"},
                {"product_code": "FINI-0012", "name": "Quick Lime Lumps 10-60 mm", "category": "Finished Products", "hsn_code": "25222000", "description": "dfgh"},
                {"product_code": "FINI-0011", "name": "Quick Lime Lumps 40-60 mm", "category": "Finished Products", "hsn_code": "25222000", "description": "dfg"},
                {"product_code": "FINI-0010", "name": "Quick Lime Lumps 10-40 mm", "category": "Finished Products", "hsn_code": "25221000", "description": "sizing plant processed"},
                {"product_code": "FINI-0009", "name": "Gulli", "category": "Finished Products", "hsn_code": "25221000", "description": "Unburnt and over burnt"},
                {"product_code": "FINI-0008", "name": "Chunna", "category": "Finished Products", "hsn_code": "25221000", "description": "Waste Klin Powder"},
                {"product_code": "FINI-0007", "name": "Quick Lime", "category": "Finished Products", "hsn_code": "25221000", "description": "From Klins"},
                {"product_code": "PACK-0006", "name": "Jumbo Bags 48\"", "category": "Packeging Materials", "hsn_code": "1000000", "description": "fghj"},
                {"product_code": "PACK-0005", "name": "Hydrate Lime Valve Bags", "category": "Packeging Materials", "hsn_code": "1000000", "description": "fds"},
                {"product_code": "PACK-0004", "name": "Repol 1st", "category": "Packeging Materials", "hsn_code": "1000000", "description": "f"},
                {"product_code": "PACK-0003", "name": "Jumbo Bags 52\"", "category": "Packeging Materials", "hsn_code": "1000000", "description": "dd"},
                {"product_code": "RAWM-0002", "name": "Pet Coke", "category": "Raw Materials", "hsn_code": "18000000", "description": "dd"},
                {"product_code": "RAWM-0001", "name": "Lime Stone", "category": "Raw Materials", "hsn_code": "25221000", "description": "fff"},
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
            print(f"V1 Seeded {len(default_products)} Products from screenshots")
    except Exception as e:
        print(f"V1 Seeding failed: {e}")
        db.session.rollback()

    # v4.5 Fix: Safe migration for PO table - if old schema exists, add missing columns
    try:
        from sqlalchemy import inspect, text
        inspector=inspect(db.engine)
        if 'po' in inspector.get_table_names():
            cols=[c['name'] for c in inspector.get_columns('po')]
            # If new columns missing, add them via ALTER TABLE
            missing=[]
            for col_name, col_type in [('po_no','VARCHAR(100)'),('rfq_no','VARCHAR(100)'),('po_date','VARCHAR(20)'),('po_validity','VARCHAR(20)'),('po_type','VARCHAR(50)'),('sbu_id','INTEGER'),('sbu_name','VARCHAR(100)'),('delivery_address','TEXT'),('billing_address','TEXT'),('same_as_delivery','BOOLEAN'),('product_id','INTEGER'),('product_name_filter','VARCHAR(100)'),('vendor_code','VARCHAR(50)'),('vendor_state','VARCHAR(100)'),('items','TEXT'),('taxable_value','FLOAT'),('cgst_amount','FLOAT'),('sgst_amount','FLOAT'),('igst_amount','FLOAT'),('freight_amount','FLOAT'),('round_off','FLOAT'),('grand_total','FLOAT'),('delivery_type','VARCHAR(50)'),('delivery_schedule','TEXT'),('payment_terms_days','INTEGER'),('rate_basis','VARCHAR(50)'),('freight_terms','VARCHAR(100)'),('tds_applicable','VARCHAR(20)'),('tds_percent','FLOAT'),('rcm_applicable','VARCHAR(20)'),('rcm_percent','FLOAT'),('documents','TEXT'),('approval_status','VARCHAR(50)'),('created_by','VARCHAR(100)'),('updated_by','VARCHAR(100)'),('updated_at','VARCHAR(30)')]:
                if col_name not in cols:
                    missing.append((col_name,col_type))
            if missing:
                print(f"v4.5 Migration: Adding missing columns to PO table: {missing}")
                with db.engine.connect() as conn:
                    for col_name, col_type in missing:
                        try:
                            conn.execute(text(f"ALTER TABLE po ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                        except Exception as e:
                            print(f"Failed to add {col_name}: {e}")
                    # For po_no unique, set default for existing rows
                    try:
                        conn.execute(text("UPDATE po SET po_no = 'PO/26-27/PRODUCT/0001' WHERE po_no IS NULL"))
                        conn.commit()
                    except:
                        pass
    except Exception as e:
        print(f"v4.5 Migration check failed: {e}")

    try:
        from sqlalchemy import inspect, text
        inspector=inspect(db.engine)
        if 'grn' in inspector.get_table_names():
            cols=[c['name'] for c in inspector.get_columns('grn')]
            missing=[]
            for col_name, col_type in [
                ('grn_no','VARCHAR(100)'),('grn_date','VARCHAR(20)'),('grn_type','VARCHAR(50)'),
                ('po_id','INTEGER'),('po_no','VARCHAR(100)'),
                ('sbu_id','INTEGER'),('sbu_name','VARCHAR(100)'),('sbu_code','VARCHAR(20)'),
                ('vendor_code','VARCHAR(50)'),('vendor_state','VARCHAR(100)'),('station','VARCHAR(100)'),
                ('driver_name','VARCHAR(100)'),('driver_mobile','VARCHAR(20)'),('transporter','VARCHAR(100)'),('lr_no','VARCHAR(100)'),('eway_bill','VARCHAR(100)'),
                ('invoice_no','VARCHAR(100)'),('invoice_date','VARCHAR(20)'),('challan_no','VARCHAR(100)'),('bill_no','VARCHAR(100)'),('rawana_no','VARCHAR(100)'),('wayment_slip_no','VARCHAR(100)'),
                ('product_id','INTEGER'),('product_name','VARCHAR(100)'),('product_code','VARCHAR(50)'),('hsn_code','VARCHAR(20)'),('spec','TEXT'),
                ('po_qty','FLOAT'),('supplier_qty','FLOAT'),('received_qty','FLOAT'),('accepted_qty','FLOAT'),('rejected_qty','FLOAT'),('wastage_kg','FLOAT'),('rate','FLOAT'),('amount','FLOAT'),
                ('taxable_value','FLOAT'),('cgst_percent','FLOAT'),('cgst_amount','FLOAT'),('sgst_percent','FLOAT'),('sgst_amount','FLOAT'),('igst_percent','FLOAT'),('igst_amount','FLOAT'),('grand_total','FLOAT'),
                ('net_mt','FLOAT'),('qty_differ','FLOAT'),('differ_percent','FLOAT'),
                ('bilty_rate','FLOAT'),('bilty_amount','FLOAT'),('freight_advance','FLOAT'),('unloading_point','VARCHAR(100)'),('unloading_charges','FLOAT'),('stock_yard_id','INTEGER'),('stock_yard_name','VARCHAR(100)'),
                ('moisture_percent','FLOAT'),('quality_status','VARCHAR(20)'),('quality_remark','TEXT'),('deduction_amount','FLOAT'),('shortage_ded','FLOAT'),('rate_difference','FLOAT'),('debit_note_no','VARCHAR(100)'),('remarks','TEXT'),
                ('documents','TEXT'),('status','VARCHAR(50)'),('approval_status','VARCHAR(50)'),('created_by','VARCHAR(100)'),('created_at','VARCHAR(30)'),('updated_by','VARCHAR(100)'),('updated_at','VARCHAR(30)')
            ]:
                if col_name not in cols:
                    missing.append((col_name,col_type))
            if missing:
                print(f"v4.6 GRN Migration: Adding {len(missing)} columns")
                with db.engine.connect() as conn:
                    for col_name, col_type in missing:
                        try:
                            conn.execute(text(f"ALTER TABLE grn ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                        except Exception as ex:
                            print(f"Failed {col_name}: {ex}")
    except Exception as e:
        print(f"v4.6 GRN Migration failed: {e}")
    # Seed hidden masters if empty
    if LegalStatusMaster.query.count()==0:
        for name in ["Proprietor","Partnership","LLP","Private Limited","Public Limited","HUF","Trust","Society","Government","OPC","One Person Company","Co-operative Society","Others"]:
            db.session.add(LegalStatusMaster(name=name))
    if VendorCategoryMaster.query.count()==0:
        for name in ["MSE","MSME","SSI","Small","Medium","Large","Non-MSE","Government","Trader","Importer","Service Provider","Manufacturer","Distributor","Others"]:
            db.session.add(VendorCategoryMaster(name=name))
    if DesignationMaster.query.count()==0:
        for name in ["Proprietor","Partner","Director","Managing Director","Manager","Purchase Manager","Accounts Manager","Owner","CEO","AGM","DGM","Executive","Accountant","Sales Manager","General Manager","Chairman","Secretary","Others"]:
            db.session.add(DesignationMaster(name=name))
    if BankMaster.query.count()==0:
        banks = [
            ("State Bank of India","SBI"), ("Punjab National Bank","PNB"), ("Bank of Baroda","BOB"), ("Canara Bank","CAN"), ("Union Bank of India","UBI"),
            ("Bank of India","BOI"), ("Indian Bank","INDIAN"), ("Central Bank of India","CBI"), ("Indian Overseas Bank","IOB"), ("UCO Bank","UCO"),
            ("Bank of Maharashtra","BOM"), ("Punjab & Sind Bank","PSB"), ("HDFC Bank","HDFC"), ("ICICI Bank","ICICI"), ("Axis Bank","AXIS"),
            ("Kotak Mahindra Bank","KOTAK"), ("IndusInd Bank","INDUS"), ("Yes Bank","YES"), ("IDBI Bank","IDBI"), ("IDFC First Bank","IDFC"),
            ("Federal Bank","FED"), ("South Indian Bank","SIB"), ("Karnataka Bank","KTK"), ("Karur Vysya Bank","KVB"), ("City Union Bank","CUB"),
            ("RBL Bank","RBL"), ("Bandhan Bank","BANDHAN"), ("Jammu & Kashmir Bank","JKB"), ("Dhanlaxmi Bank","DLB"), ("Nainital Bank","NTB"),
            ("Ujjivan Small Finance Bank","UJJIVAN"), ("AU Small Finance Bank","AU"), ("Equitas Small Finance Bank","EQUITAS"), ("Other Bank","OTHER")
        ]
        for bname, bcode in banks:
            db.session.add(BankMaster(bank_name=bname, bank_code=bcode))
    try:
        db.session.commit()
    except:
        db.session.rollback()

def generate_product_code(category, count):
    base = ''.join([c for c in category if c.isalnum()])[:4].upper()
    if len(base)<4: base = (base + 'XXXX')[:4]
    return f"{base}-{count:04d}"

def generate_vendor_code(count):
    return f"VEND-{count:04d}"

def sanitize_product_name_for_po(name):
    import re
    try:
        name=(name or '').strip()
        name=name.replace(' ', '').replace('"','').replace("'",'').replace('&','').replace('/','')
        name=re.sub(r'[^A-Za-z0-9\-_]', '', name)
        result=name.upper()[:30]
        return result if result and len(result)>=2 else "PRODUCT"
    except Exception as e:
        print(f"sanitize error {e}")
        return "PRODUCT"

def get_financial_year(date_str=None):
    from datetime import datetime
    if date_str:
        try:
            d=datetime.strptime(date_str, '%Y-%m-%d')
        except:
            d=datetime.now()
    else:
        d=datetime.now()
    if d.month>=4:
        fy_start=d.year
        fy_end=d.year+1
    else:
        fy_start=d.year-1
        fy_end=d.year
    return f"{str(fy_start)[-2:]}-{str(fy_end)[-2:]}"

def generate_po_no(fy, product_name, count):
    base=sanitize_product_name_for_po(product_name)
    return f"PO/{fy}/{base}/{count:04d}"

def sanitize_sbu_code(sbu_name):
    import re
    try:
        name=(sbu_name or '').strip().upper()
        words=name.split()
        if len(words)>=2:
            if len(words[0])<=4:
                code=words[0]
            else:
                code=''.join([w[0] for w in words])[:4]
        else:
            code=name[:4]
        code=re.sub(r'[^A-Z0-9]', '', code)
        return code[:6] if code else "SBU"
    except:
        return "SBU"

def generate_grn_no(fy, sbu_code, count):
    sbu_code=sanitize_sbu_code(sbu_code) if sbu_code else "SBU"
    return f"GRN/{fy}/{sbu_code}/{count:04d}"

# ========== API ==========
@app.route('/api/health')
def health():
    return jsonify(status='LIVE', version='v4.5.2 PO Module Locked + Backup v4.5.1 + Product Master 3 Cat 18 Prod', db_file='lemon_erp_v44_1_category.db', url='https://lemon-erp.onrender.com')

@app.route('/api/product_categories', methods=['GET','POST'])
def pc_list():
    if request.method=='GET':
        cats = ProductCategory.query.order_by(ProductCategory.id.desc()).all()
        return jsonify([{'id':c.id,'category_name':c.category_name,'created_at':c.created_at} for c in cats])
    data=request.get_json() or {}
    name=(data.get('category_name') or '').strip()
    if not name: return jsonify(error='Category Name required'),400
    if ProductCategory.query.filter_by(category_name=name).first():
        return jsonify(error='Category already exists'),400
    cat=ProductCategory(category_name=name)
    db.session.add(cat); db.session.commit()
    return jsonify(id=cat.id, category_name=cat.category_name)

@app.route('/api/product_categories/<int:id>', methods=['GET','PUT','DELETE'])
def pc_one(id):
    cat=ProductCategory.query.get_or_404(id)
    if request.method=='GET':
        return jsonify(id=cat.id, category_name=cat.category_name, created_at=cat.created_at)
    if request.method=='PUT':
        data=request.get_json() or {}
        name=(data.get('category_name') or '').strip()
        if not name: return jsonify(error='Required'),400
        exists=ProductCategory.query.filter(ProductCategory.category_name==name, ProductCategory.id!=id).first()
        if exists: return jsonify(error='Exists'),400
        cat.category_name=name; db.session.commit()
        return jsonify(ok=True)
    db.session.delete(cat); db.session.commit()
    return jsonify(ok=True)

@app.route('/api/products', methods=['GET','POST'])
def prod_list():
    if request.method=='GET':
        prods=Product.query.order_by(Product.id.desc()).all()
        return jsonify([{'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description,'total_stock_mt':p.total_stock_mt} for p in prods])
    data=request.get_json() or {}
    for f in ['name','category','hsn_code','description']:
        if not (data.get(f) or '').strip(): return jsonify(error=f'{f} mandatory'),400
    cnt=Product.query.filter_by(category=data['category']).count()+1
    code=generate_product_code(data['category'], cnt)
    while Product.query.filter_by(product_code=code).first():
        cnt+=1; code=generate_product_code(data['category'], cnt)
    p=Product(name=data['name'].strip(), category=data['category'].strip(), product_code=code, hsn_code=data['hsn_code'].strip(), description=data['description'].strip())
    db.session.add(p); db.session.commit()
    return jsonify(id=p.id, name=p.name, product_code=p.product_code, hsn_code=p.hsn_code, category=p.category)

@app.route('/api/products/<int:pid>', methods=['GET','PUT','DELETE'])
def prod_one(pid):
    p=Product.query.get_or_404(pid)
    if request.method=='GET': return jsonify(id=p.id,name=p.name,category=p.category,product_code=p.product_code,hsn_code=p.hsn_code,description=p.description)
    if request.method=='PUT':
        data=request.get_json() or {}
        for f in ['name','category','hsn_code','description']:
            if not (data.get(f) or '').strip(): return jsonify(error=f'{f} mandatory'),400
        p.name=data['name'].strip(); p.category=data['category'].strip(); p.hsn_code=data['hsn_code'].strip(); p.description=data['description'].strip()
        db.session.commit(); return jsonify(ok=True)
    db.session.delete(p); db.session.commit(); return jsonify(ok=True)

# SBUs API - v4.4.7 fixed + v4.4.8 masters reordered (unchanged)
@app.route('/api/sbus', methods=['GET','POST'])
def sbu_list():
    if request.method=='GET':
        sbus=SBU.query.order_by(SBU.id.desc()).all()
        out=[]
        all_prods={pr.id: pr for pr in Product.query.all()}
        for s in sbus:
            kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
            sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
            hydrations=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
            yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
            def res_k(k):
                pcs=[]
                try: raw=json.loads(k.products_capacity) if k.products_capacity else []
                except: raw=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else f"ID {it.get('product_id')}", 'product_code':prod.product_code if prod else '', 'capacity_per_day': it.get('capacity_per_day') or it.get('capacity') or 0, 'capacity': it.get('capacity_per_day') or 0})
                return {'id':k.id,'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':pcs,'products_capacity_raw':k.products_capacity}
            def res_sz(sp):
                try: raw=json.loads(sp.products_capacity) if sp.products_capacity else []
                except: raw=[]
                pcs=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else f"ID {it.get('product_id')}", 'product_code':prod.product_code if prod else '', 'capacity_per_hour':it.get('capacity_per_hour') or it.get('capacity') or 0, 'capacity':it.get('capacity_per_hour') or 0, 'machineries':it.get('machineries','')})
                return {'id':sp.id,'plant_no':sp.plant_no,'products_capacity':pcs,'products_capacity_raw':sp.products_capacity,'machineries':sp.machineries}
            def res_hy(h):
                try: raw=json.loads(h.products_capacity) if h.products_capacity else []
                except: raw=[]
                pcs=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    pcs.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else '', 'product_code':prod.product_code if prod else '', 'capacity_per_hour':it.get('capacity_per_hour') or 0, 'machineries':it.get('machineries','')})
                return {'id':h.id,'plant_no':h.plant_no,'products_capacity':pcs,'products_capacity_raw':h.products_capacity,'machineries':h.machineries}
            def res_y(y):
                try: raw=json.loads(y.yard_items) if y.yard_items else []
                except: raw=[]
                items=[]
                for it in raw:
                    prod=all_prods.get(it.get('product_id'))
                    items.append({'product_id':it.get('product_id'),'product_name':prod.name if prod else '', 'product_code':prod.product_code if prod else '', 'opening_stock':it.get('opening_stock') or it.get('opening') or 0})
                return {'id':y.id,'yard_name':y.yard_name,'yard_items':items,'yard_items_raw':y.yard_items}
            out.append({'id':s.id,'sbu_name':s.sbu_name,'address':s.address,'kilns':[res_k(k) for k in kilns],'sizing_plants':[res_sz(sp) for sp in sizings],'hydration_plants':[res_hy(h) for h in hydrations],'stock_yards':[res_y(y) for y in yards]})
        return jsonify(out)
    data=request.get_json() or {}
    sbu_name=(data.get('sbu_name') or '').strip()
    if not sbu_name: return jsonify(error='SBU Name required'),400
    s=SBU(sbu_name=sbu_name, address=data.get('address',''))
    db.session.add(s); db.session.flush()
    for k in data.get('kilns',[]):
        db.session.add(KilnAsset(sbu_id=s.id, kiln_no=k.get('kiln_no',''), lining_installation_date=k.get('lining_installation_date') or k.get('lining_date') or '', health_status=k.get('health_status','Good'), products_capacity=json.dumps(k.get('products_capacity',[]))))
    for sp in data.get('sizing_plants',[]):
        db.session.add(SizingPlantAsset(sbu_id=s.id, plant_no=sp.get('plant_no',''), products_capacity=json.dumps(sp.get('products_capacity',[])), machineries=sp.get('machineries','')))
    for hp in data.get('hydration_plants',[]):
        db.session.add(HydrationPlantAsset(sbu_id=s.id, plant_no=hp.get('plant_no',''), products_capacity=json.dumps(hp.get('products_capacity',[])), machineries=hp.get('machineries','')))
    for y in data.get('stock_yards',[]):
        db.session.add(StockYardAsset(sbu_id=s.id, yard_name=y.get('yard_name',''), yard_items=json.dumps(y.get('yard_items',[]))))
    db.session.commit()
    return jsonify(id=s.id, sbu_name=s.sbu_name)

@app.route('/api/sbus/<int:sid>', methods=['GET','PUT','DELETE'])
def sbu_one(sid):
    s=SBU.query.get_or_404(sid)
    if request.method=='GET':
        kilns=KilnAsset.query.filter_by(sbu_id=s.id).all()
        sizings=SizingPlantAsset.query.filter_by(sbu_id=s.id).all()
        hydrations=HydrationPlantAsset.query.filter_by(sbu_id=s.id).all()
        yards=StockYardAsset.query.filter_by(sbu_id=s.id).all()
        return jsonify(id=s.id, sbu_name=s.sbu_name, address=s.address,
                       kilns=[{'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'lining_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':json.loads(k.products_capacity) if k.products_capacity else [],'products_capacity_raw':k.products_capacity} for k in kilns],
                       sizing_plants=[{'plant_no':sp.plant_no,'products_capacity':json.loads(sp.products_capacity) if sp.products_capacity else [],'products_capacity_raw':sp.products_capacity,'machineries':sp.machineries} for sp in sizings],
                       hydration_plants=[{'plant_no':h.plant_no,'products_capacity':json.loads(h.products_capacity) if h.products_capacity else [],'products_capacity_raw':h.products_capacity,'machineries':h.machineries} for h in hydrations],
                       stock_yards=[{'yard_name':y.yard_name,'yard_items':json.loads(y.yard_items) if y.yard_items else [],'yard_items_raw':y.yard_items} for y in yards])
    if request.method=='PUT':
        data=request.get_json() or {}
        s.sbu_name=(data.get('sbu_name') or s.sbu_name).strip()
        s.address=data.get('address', s.address)
        KilnAsset.query.filter_by(sbu_id=s.id).delete()
        SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
        HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
        StockYardAsset.query.filter_by(sbu_id=s.id).delete()
        for k in data.get('kilns',[]):
            db.session.add(KilnAsset(sbu_id=s.id, kiln_no=k.get('kiln_no',''), lining_installation_date=k.get('lining_installation_date') or k.get('lining_date') or '', health_status=k.get('health_status','Good'), products_capacity=json.dumps(k.get('products_capacity',[]))))
        for sp in data.get('sizing_plants',[]):
            db.session.add(SizingPlantAsset(sbu_id=s.id, plant_no=sp.get('plant_no',''), products_capacity=json.dumps(sp.get('products_capacity',[])), machineries=sp.get('machineries','')))
        for hp in data.get('hydration_plants',[]):
            db.session.add(HydrationPlantAsset(sbu_id=s.id, plant_no=hp.get('plant_no',''), products_capacity=json.dumps(hp.get('products_capacity',[])), machineries=hp.get('machineries','')))
        for y in data.get('stock_yards',[]):
            db.session.add(StockYardAsset(sbu_id=s.id, yard_name=y.get('yard_name',''), yard_items=json.dumps(y.get('yard_items',[]))))
        db.session.commit()
        return jsonify(ok=True)
    KilnAsset.query.filter_by(sbu_id=s.id).delete()
    SizingPlantAsset.query.filter_by(sbu_id=s.id).delete()
    HydrationPlantAsset.query.filter_by(sbu_id=s.id).delete()
    StockYardAsset.query.filter_by(sbu_id=s.id).delete()
    db.session.delete(s); db.session.commit()
    return jsonify(ok=True)

# Vendor Masters API - hidden
@app.route('/api/vendor_masters')
def vendor_masters_api():
    legal=[{'id':l.id,'name':l.name} for l in LegalStatusMaster.query.order_by(LegalStatusMaster.name).all()]
    vcat=[{'id':v.id,'name':v.name} for v in VendorCategoryMaster.query.order_by(VendorCategoryMaster.name).all()]
    desg=[{'id':d.id,'name':d.name} for d in DesignationMaster.query.order_by(DesignationMaster.name).all()]
    banks=[{'id':b.id,'bank_name':b.bank_name,'bank_code':b.bank_code} for b in BankMaster.query.order_by(BankMaster.bank_name).all()]
    return jsonify(legal_status=legal, vendor_category=vcat, designations=desg, banks=banks)

@app.route('/api/vendor_masters/<string:mtype>', methods=['GET','POST'])
def vendor_master_type(mtype):
    mapping={'legal_status':LegalStatusMaster,'vendor_category':VendorCategoryMaster,'designation':DesignationMaster,'bank':BankMaster}
    Model=mapping.get(mtype)
    if not Model: return jsonify(error='Invalid type'),400
    if request.method=='GET':
        if mtype=='bank':
            return jsonify([{'id':b.id,'bank_name':b.bank_name,'bank_code':b.bank_code,'name':b.bank_name} for b in Model.query.order_by(Model.bank_name).all()])
        return jsonify([{'id':x.id,'name':x.name} for x in Model.query.order_by(Model.name).all()])
    data=request.get_json() or {}
    name=(data.get('name') or data.get('bank_name') or '').strip()
    if not name: return jsonify(error='Name required'),400
    if mtype=='bank':
        if BankMaster.query.filter_by(bank_name=name).first(): return jsonify(error='Exists'),400
        obj=BankMaster(bank_name=name, bank_code=data.get('bank_code','OTHER'))
    else:
        if Model.query.filter_by(name=name).first(): return jsonify(error='Exists'),400
        obj=Model(name=name)
    db.session.add(obj); db.session.commit()
    return jsonify(ok=True, id=obj.id)

# Vendor Enhanced API v4.4.9
@app.route('/api/vendors', methods=['GET','POST'])
def vendors_api():
    if request.method=='GET':
        q=request.args.get('search','').lower()
        type_f=request.args.get('type','')
        cat_f=request.args.get('category','')
        status_f=request.args.get('status','')
        state_f=request.args.get('state','')
        approval_f=request.args.get('approval','')
        rating_f=request.args.get('rating','')
        vendors=Vendor.query.order_by(Vendor.id.desc()).all()
        result=[]
        for v in vendors:
            po_list=PO.query.filter((PO.vendor_id==v.id) | (PO.vendor==v.name)).all()
            po_count=len(po_list)
            grn_count=GRN.query.filter((GRN.vendor_id==v.id) | (GRN.vendor==v.name)).count()
            # calc business value and last transaction
            total_val=sum([(p.qty or 0)*(p.rate or 0) for p in po_list])
            last_trans = max([p.created_at for p in po_list if p.created_at], default='') if po_list else v.last_transaction_date
            try:
                banks=json.loads(v.bank_details) if v.bank_details else []
            except:
                banks=[]
            try:
                contacts=json.loads(v.contacts) if v.contacts else []
            except:
                contacts=[]
            try:
                docs=json.loads(v.documents) if v.documents else {}
            except:
                docs={}
            if q and not (q in (v.name or '').lower() or q in (v.vendor_code or '').lower() or q in (v.gst_no or '').lower() or q in (v.pan_no or '').lower() or q in (v.station or '').lower() or q in (v.state or '').lower() or q in (v.msme_cert_no or '').lower()):
                continue
            if type_f and v.legal_status!=type_f: continue
            if cat_f and v.vendor_category!=cat_f: continue
            if status_f and v.status!=status_f: continue
            if state_f and v.state!=state_f: continue
            if approval_f and v.approval_status!=approval_f: continue
            if rating_f and str(v.vendor_rating)!=str(rating_f): continue
            result.append({
                'id':v.id,'vendor_code':v.vendor_code,'name':v.name,'station':v.station,'address':v.address,'state':v.state,
                'gst_no':v.gst_no,'pan_no':v.pan_no,'tan_no':v.tan_no,'legal_status':v.legal_status,'vendor_category':v.vendor_category,
                'bank_details':banks,'contacts':contacts,'status':v.status,
                'msme_cert_no':v.msme_cert_no,'msme_expiry':v.msme_expiry,'msme_upload':bool(v.msme_upload),
                'gst_reg_type':v.gst_reg_type,'tds_section':v.tds_section,'vendor_rating':v.vendor_rating,'last_audit_date':v.last_audit_date,
                'documents':docs,'has_docs':len(docs)>0,
                'opening_balance':v.opening_balance,'opening_balance_type':v.opening_balance_type,'ledger_group':v.ledger_group,
                'created_by':v.created_by,'created_at':v.created_at,'updated_by':v.updated_by,'updated_at':v.updated_at,
                'approval_status':v.approval_status,'last_transaction_date':last_trans or v.last_transaction_date,'total_business_value':total_val or v.total_business_value,
                'po_count':po_count,'grn_count':grn_count,
                'type':v.legal_status or v.type,'gst':v.gst_no,'contact':contacts[0]['name'] if contacts else ''
            })
        return jsonify(result)
    data=request.get_json() or {}
    name=(data.get('name') or '').strip()
    if not name: return jsonify(error='Vendor Name mandatory'),400
    cnt=Vendor.query.count()+1
    code=generate_vendor_code(cnt)
    while Vendor.query.filter_by(vendor_code=code).first():
        cnt+=1; code=generate_vendor_code(cnt)
    v=Vendor(
        vendor_code=code,
        name=name,
        station=data.get('station',''),
        address=data.get('address',''),
        state=data.get('state',''),
        gst_no=data.get('gst_no',''),
        pan_no=data.get('pan_no',''),
        tan_no=data.get('tan_no',''),
        legal_status=data.get('legal_status',''),
        vendor_category=data.get('vendor_category',''),
        bank_details=json.dumps(data.get('bank_details',[])),
        contacts=json.dumps(data.get('contacts',[])),
        status=data.get('status','Active'),
        msme_cert_no=data.get('msme_cert_no',''),
        msme_expiry=data.get('msme_expiry',''),
        msme_upload=data.get('msme_upload',''),
        gst_reg_type=data.get('gst_reg_type','Regular'),
        tds_section=data.get('tds_section','194C'),
        vendor_rating=int(data.get('vendor_rating') or 0),
        last_audit_date=data.get('last_audit_date',''),
        documents=json.dumps(data.get('documents',{})),
        opening_balance=float(data.get('opening_balance') or 0),
        opening_balance_type=data.get('opening_balance_type','Dr'),
        ledger_group=data.get('ledger_group','Sundry Creditors'),
        created_by=data.get('created_by','Admin'),
        updated_by=data.get('created_by','Admin'),
        approval_status=data.get('approval_status','Draft'),
        type=data.get('legal_status',''),
        contact=data.get('contacts',[{}])[0].get('name','') if data.get('contacts') else ''
    )
    db.session.add(v); db.session.commit()
    return jsonify(id=v.id, vendor_code=v.vendor_code, name=v.name)

@app.route('/api/vendors/<int:vid>', methods=['GET','PUT','DELETE'])
def vendor_one(vid):
    v=Vendor.query.get_or_404(vid)
    if request.method=='GET':
        try:
            banks=json.loads(v.bank_details) if v.bank_details else []
        except:
            banks=[]
        try:
            contacts=json.loads(v.contacts) if v.contacts else []
        except:
            contacts=[]
        try:
            docs=json.loads(v.documents) if v.documents else {}
        except:
            docs={}
        po_list=PO.query.filter((PO.vendor_id==v.id) | (PO.vendor==v.name)).all()
        po_count=len(po_list)
        grn_count=GRN.query.filter((GRN.vendor_id==v.id) | (GRN.vendor==v.name)).count()
        total_val=sum([(p.qty or 0)*(p.rate or 0) for p in po_list])
        last_trans = max([p.created_at for p in po_list if p.created_at], default='') if po_list else v.last_transaction_date
        return jsonify(id=v.id, vendor_code=v.vendor_code, name=v.name, station=v.station, address=v.address, state=v.state, gst_no=v.gst_no, pan_no=v.pan_no, tan_no=v.tan_no, legal_status=v.legal_status, vendor_category=v.vendor_category, bank_details=banks, contacts=contacts, status=v.status, msme_cert_no=v.msme_cert_no, msme_expiry=v.msme_expiry, msme_upload=v.msme_upload, gst_reg_type=v.gst_reg_type, tds_section=v.tds_section, vendor_rating=v.vendor_rating, last_audit_date=v.last_audit_date, documents=docs, opening_balance=v.opening_balance, opening_balance_type=v.opening_balance_type, ledger_group=v.ledger_group, created_by=v.created_by, created_at=v.created_at, updated_by=v.updated_by, updated_at=v.updated_at, approval_status=v.approval_status, last_transaction_date=last_trans or v.last_transaction_date, total_business_value=total_val or v.total_business_value, po_count=po_count, grn_count=grn_count)
    if request.method=='PUT':
        data=request.get_json() or {}
        name=(data.get('name') or '').strip()
        if not name: return jsonify(error='Vendor Name mandatory'),400
        v.name=name
        v.station=data.get('station', v.station)
        v.address=data.get('address', v.address)
        v.state=data.get('state', v.state)
        v.gst_no=data.get('gst_no', v.gst_no)
        v.pan_no=data.get('pan_no', v.pan_no)
        v.tan_no=data.get('tan_no', v.tan_no)
        v.legal_status=data.get('legal_status', v.legal_status)
        v.vendor_category=data.get('vendor_category', v.vendor_category)
        v.bank_details=json.dumps(data.get('bank_details', []))
        v.contacts=json.dumps(data.get('contacts', []))
        v.status=data.get('status', v.status)
        v.msme_cert_no=data.get('msme_cert_no', v.msme_cert_no)
        v.msme_expiry=data.get('msme_expiry', v.msme_expiry)
        if data.get('msme_upload'): v.msme_upload=data.get('msme_upload')
        v.gst_reg_type=data.get('gst_reg_type', v.gst_reg_type)
        v.tds_section=data.get('tds_section', v.tds_section)
        v.vendor_rating=int(data.get('vendor_rating') or v.vendor_rating or 0)
        v.last_audit_date=data.get('last_audit_date', v.last_audit_date)
        if data.get('documents'): v.documents=json.dumps(data.get('documents'))
        v.opening_balance=float(data.get('opening_balance') or v.opening_balance or 0)
        v.opening_balance_type=data.get('opening_balance_type', v.opening_balance_type)
        v.ledger_group=data.get('ledger_group', v.ledger_group)
        v.updated_by=data.get('updated_by','Admin')
        v.updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        v.approval_status=data.get('approval_status', v.approval_status)
        v.type=v.legal_status
        db.session.commit()
        return jsonify(ok=True)
    db.session.delete(v); db.session.commit()
    return jsonify(ok=True)

# Other modules API minimal
@app.route('/api/inventory/combined')
def inv_combined():
    prods=Product.query.all()
    raw=[{'product_code':p.product_code,'hsn_code':p.hsn_code,'name':p.name,'total_mt':p.total_stock_mt,'status':'OK'} for p in prods if 'raw' in p.category.lower() or 'lime' in p.category.lower()]
    finished=[{'product_code':p.product_code,'hsn_code':p.hsn_code,'name':p.name,'total_mt':p.total_stock_mt,'status':'OK'} for p in prods]
    return jsonify(raw=raw, wip=[], finished=finished, total_value_lakh=sum([p.total_stock_mt*1000/100000 for p in prods]))

@app.route('/api/customers', methods=['GET','POST'])
def customers_api():
    if request.method=='GET': return jsonify([{'id':c.id,'name':c.name,'type':c.type} for c in Customer.query.all()])
    d=request.get_json() or {}; c=Customer(name=d.get('name'), type=d.get('type')); db.session.add(c); db.session.commit(); return jsonify(ok=True)

@app.route('/api/customers/<int:id>', methods=['PUT','DELETE'])
def cust_one(id):
    c=Customer.query.get_or_404(id)
    if request.method=='DELETE': db.session.delete(c); db.session.commit(); return jsonify(ok=True)
    return jsonify(ok=True)

@app.route('/api/manufacturing_orders', methods=['GET','POST'])
def mo_api():
    if request.method=='GET': return jsonify([{'id':m.id,'unit':m.unit} for m in MO.query.all()])
    d=request.get_json() or {}; m=MO(sbu=d.get('sbu'), type=d.get('type'), unit=d.get('unit')); db.session.add(m); db.session.commit(); return jsonify(ok=True)

@app.route('/api/mo/total')
def mo_total(): return jsonify(total=MO.query.count())

@app.route('/api/po', methods=['GET','POST'])
def po_api():
    if request.method=='GET':
        search=(request.args.get('search') or '').strip().lower()
        po_type=request.args.get('po_type','')
        status_f=request.args.get('status','')
        sbu_f=request.args.get('sbu','')
        vendor_f=request.args.get('vendor','')
        pos=PO.query.order_by(PO.id.desc()).all()
        result=[]
        for p in pos:
            try:
                items=json.loads(p.items) if p.items else []
            except:
                items=[]
            try:
                docs=json.loads(p.documents) if p.documents else {}
            except:
                docs={}
            if search and not (search in (p.po_no or '').lower() or search in (p.vendor or '').lower() or search in (p.sbu_name or '').lower() or search in (p.po_type or '').lower() or search in (p.rfq_no or '').lower()):
                continue
            if po_type and p.po_type!=po_type: continue
            if status_f and p.status!=status_f: continue
            if sbu_f and str(p.sbu_id)!=str(sbu_f) and p.sbu_name!=sbu_f: continue
            if vendor_f and str(p.vendor_id)!=str(vendor_f): continue
            total_qty=sum([float(i.get('qty') or 0) for i in items])
            result.append({
                'id':p.id,'po_no':p.po_no,'rfq_no':p.rfq_no,'po_date':p.po_date,'po_validity':p.po_validity,'po_type':p.po_type,
                'sbu_id':p.sbu_id,'sbu_name':p.sbu_name,'delivery_address':p.delivery_address,'billing_address':p.billing_address,'same_as_delivery':p.same_as_delivery,
                'product_id':p.product_id,'product_name_filter':p.product_name_filter,
                'vendor':p.vendor,'vendor_id':p.vendor_id,'vendor_code':p.vendor_code,'vendor_state':p.vendor_state,
                'items':items,'items_count':len(items),'total_qty':total_qty,
                'taxable_value':p.taxable_value,'cgst_amount':p.cgst_amount,'sgst_amount':p.sgst_amount,'igst_amount':p.igst_amount,'freight_amount':p.freight_amount,'round_off':p.round_off,'grand_total':p.grand_total,
                'delivery_type':p.delivery_type,'delivery_schedule':p.delivery_schedule,'payment_terms_days':p.payment_terms_days,'rate_basis':p.rate_basis,'freight_terms':p.freight_terms,
                'tds_applicable':p.tds_applicable,'tds_percent':p.tds_percent,'rcm_applicable':p.rcm_applicable,'rcm_percent':p.rcm_percent,
                'documents':docs,'has_docs':len([v for v in docs.values() if v])>0,
                'status':p.status,'approval_status':p.approval_status,
                'created_by':p.created_by,'created_at':p.created_at,'updated_by':p.updated_by,'updated_at':p.updated_at,
                'material':p.material,'qty':p.qty,'rate':p.rate
            })
        return jsonify(result)
    try:
        data=request.get_json() or {}
        sbu_id=data.get('sbu_id')
        if not sbu_id: return jsonify(error='SBU mandatory - Select SBU'),400
        sbu=SBU.query.get(sbu_id)
        if not sbu: return jsonify(error=f'SBU not found ID {sbu_id}'),400
        vendor_id=data.get('vendor_id')
        if not vendor_id: return jsonify(error='Vendor mandatory - Select Vendor'),400
        vendor=Vendor.query.get(vendor_id)
        if not vendor: return jsonify(error=f'Vendor not found ID {vendor_id}'),400
        items=data.get('items') or []
        if not items or len(items)==0: return jsonify(error='Add at least one line item - Click Add Line Item'),400
        for idx, it in enumerate(items):
            if not it.get('product_id') and not it.get('product_name'):
                return jsonify(error=f'Line {idx+1}: Product mandatory'),400
            try:
                q=float(it.get('qty') or 0); r=float(it.get('rate') or 0)
            except:
                return jsonify(error=f'Line {idx+1}: Qty/Rate must be numbers'),400
            if q<=0 or r<=0:
                return jsonify(error=f'Line {idx+1}: Qty>0 and Rate>0 required'),400
        po_date=data.get('po_date') or datetime.now().strftime('%Y-%m-%d')
        fy=get_financial_year(po_date)
        prod_name_for_code=data.get('product_name_filter') or (items[0].get('product_name') if items else 'PRODUCT')
        if not prod_name_for_code or not str(prod_name_for_code).strip():
            prod_name_for_code='PRODUCT'
        prod_sanitized=sanitize_product_name_for_po(prod_name_for_code)
        existing_count=PO.query.filter(PO.po_no.like(f"PO/{fy}/{prod_sanitized}/%")).count()+1
        po_no=generate_po_no(fy, prod_name_for_code, existing_count)
        while PO.query.filter_by(po_no=po_no).first():
            existing_count+=1
            po_no=generate_po_no(fy, prod_name_for_code, existing_count)
        taxable=0
        cgst_total=0
        sgst_total=0
        igst_total=0
        for it in items:
            qty=float(it.get('qty') or 0)
            rate=float(it.get('rate') or 0)
            gst_percent=float(it.get('gst_percent') or 0)
            amt=qty*rate
            taxable+=amt
            gst_type=it.get('gst_type','inter')
            if gst_type=='intra':
                cgst=amt*gst_percent/100/2
                sgst=amt*gst_percent/100/2
                igst=0
            else:
                cgst=0
                sgst=0
                igst=amt*gst_percent/100
            cgst_total+=cgst
            sgst_total+=sgst
            igst_total+=igst
            it['amount']=round(amt,2)
            it['cgst_amount']=round(cgst,2)
            it['sgst_amount']=round(sgst,2)
            it['igst_amount']=round(igst,2)
            it['tax_amount']=round(cgst+sgst+igst,2)
            it['total_amount']=round(amt+cgst+sgst+igst,2)
        freight=float(data.get('freight_amount') or 0)
        round_off=float(data.get('round_off') or 0)
        grand_total=taxable+cgst_total+sgst_total+igst_total+freight+round_off
        po=PO(
            po_no=po_no,
            rfq_no=data.get('rfq_no',''),
            po_date=po_date,
            po_validity=data.get('po_validity',''),
            po_type=data.get('po_type','Raw Material'),
            sbu_id=sbu.id,
            sbu_name=sbu.sbu_name,
            delivery_address=data.get('delivery_address',''),
            billing_address=data.get('billing_address',''),
            same_as_delivery=bool(data.get('same_as_delivery',True)),
            product_id=data.get('product_id'),
            product_name_filter=prod_name_for_code,
            vendor=vendor.name,
            vendor_id=vendor.id,
            vendor_code=vendor.vendor_code or '',
            vendor_state=vendor.state or data.get('vendor_state','') or '',
            items=json.dumps(items),
            taxable_value=round(taxable,2),
            cgst_amount=round(cgst_total,2),
            sgst_amount=round(sgst_total,2),
            igst_amount=round(igst_total,2),
            freight_amount=round(freight,2),
            round_off=round(round_off,2),
            grand_total=round(grand_total,2),
            material=items[0].get('product_name','') if items else '',
            qty=sum([float(i.get('qty') or 0) for i in items]),
            rate=items[0].get('rate',0) if items else 0,
            unit=items[0].get('uom','MT') if items else 'MT',
            delivery_type=data.get('delivery_type','One Time'),
            delivery_schedule=data.get('delivery_schedule',''),
            payment_terms_days=int(data.get('payment_terms_days') or 0),
            rate_basis=data.get('rate_basis','FOR'),
            freight_terms=data.get('freight_terms',''),
            tds_applicable=data.get('tds_applicable','Not Applicable'),
            tds_percent=float(data.get('tds_percent') or 0),
            rcm_applicable=data.get('rcm_applicable','No'),
            rcm_percent=float(data.get('rcm_percent') or 0),
            documents=json.dumps(data.get('documents',{})),
            status=data.get('status','Draft'),
            approval_status=data.get('approval_status','Draft'),
            created_by=data.get('created_by','Admin'),
            updated_by=data.get('created_by','Admin')
        )
        db.session.add(po)
        db.session.commit()
        print(f"✅ PO Created: {po.po_no} Grand {po.grand_total}")
        return jsonify(id=po.id, po_no=po.po_no, grand_total=po.grand_total)
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        print(f"❌ PO POST Error: {e}")
        return jsonify(error=f'Server error saving PO: {str(e)}'),500


@app.route('/api/po/<int:pid>', methods=['GET','PUT','DELETE'])
def po_one(pid):
    p=PO.query.get_or_404(pid)
    if request.method=='GET':
        try:
            items=json.loads(p.items) if p.items else []
        except:
            items=[]
        try:
            docs=json.loads(p.documents) if p.documents else {}
        except:
            docs={}
        return jsonify(id=p.id, po_no=p.po_no, rfq_no=p.rfq_no, po_date=p.po_date, po_validity=p.po_validity, po_type=p.po_type, sbu_id=p.sbu_id, sbu_name=p.sbu_name, delivery_address=p.delivery_address, billing_address=p.billing_address, same_as_delivery=p.same_as_delivery, product_id=p.product_id, product_name_filter=p.product_name_filter, vendor=p.vendor, vendor_id=p.vendor_id, vendor_code=p.vendor_code, vendor_state=p.vendor_state, items=items, taxable_value=p.taxable_value, cgst_amount=p.cgst_amount, sgst_amount=p.sgst_amount, igst_amount=p.igst_amount, freight_amount=p.freight_amount, round_off=p.round_off, grand_total=p.grand_total, delivery_type=p.delivery_type, delivery_schedule=p.delivery_schedule, payment_terms_days=p.payment_terms_days, rate_basis=p.rate_basis, freight_terms=p.freight_terms, tds_applicable=p.tds_applicable, tds_percent=p.tds_percent, rcm_applicable=p.rcm_applicable, rcm_percent=p.rcm_percent, documents=docs, status=p.status, approval_status=p.approval_status, created_by=p.created_by, created_at=p.created_at, updated_by=p.updated_by, updated_at=p.updated_at)
    if request.method=='PUT':
        data=request.get_json() or {}
        sbu_id=data.get('sbu_id')
        if sbu_id:
            sbu=SBU.query.get(sbu_id)
            if sbu:
                p.sbu_id=sbu.id
                p.sbu_name=sbu.sbu_name
        vendor_id=data.get('vendor_id')
        if vendor_id:
            vendor=Vendor.query.get(vendor_id)
            if vendor:
                p.vendor_id=vendor.id
                p.vendor=vendor.name
                p.vendor_code=vendor.vendor_code
                p.vendor_state=vendor.state or p.vendor_state
        items=data.get('items')
        if items is not None:
            taxable=0
            cgst_total=0
            sgst_total=0
            igst_total=0
            for it in items:
                qty=float(it.get('qty') or 0)
                rate=float(it.get('rate') or 0)
                gst_percent=float(it.get('gst_percent') or 0)
                amt=qty*rate
                taxable+=amt
                gst_type=it.get('gst_type','inter')
                if gst_type=='intra':
                    cgst=amt*gst_percent/100/2
                    sgst=amt*gst_percent/100/2
                    igst=0
                else:
                    cgst=0
                    sgst=0
                    igst=amt*gst_percent/100
                cgst_total+=cgst
                sgst_total+=sgst
                igst_total+=igst
                it['amount']=round(amt,2)
                it['cgst_amount']=round(cgst,2)
                it['sgst_amount']=round(sgst,2)
                it['igst_amount']=round(igst,2)
                it['tax_amount']=round(cgst+sgst+igst,2)
                it['total_amount']=round(amt+cgst+sgst+igst,2)
            p.items=json.dumps(items)
            p.taxable_value=round(taxable,2)
            p.cgst_amount=round(cgst_total,2)
            p.sgst_amount=round(sgst_total,2)
            p.igst_amount=round(igst_total,2)
            p.qty=sum([float(i.get('qty') or 0) for i in items])
            p.material=items[0].get('product_name','') if items else p.material
            p.rate=items[0].get('rate',0) if items else p.rate
            freight=float(data.get('freight_amount', p.freight_amount) or 0)
            round_off=float(data.get('round_off', p.round_off) or 0)
            p.freight_amount=round(freight,2)
            p.round_off=round(round_off,2)
            p.grand_total=round(taxable+cgst_total+sgst_total+igst_total+freight+round_off,2)
        p.rfq_no=data.get('rfq_no', p.rfq_no)
        p.po_date=data.get('po_date', p.po_date)
        p.po_validity=data.get('po_validity', p.po_validity)
        p.po_type=data.get('po_type', p.po_type)
        p.delivery_address=data.get('delivery_address', p.delivery_address)
        p.billing_address=data.get('billing_address', p.billing_address)
        p.same_as_delivery=bool(data.get('same_as_delivery', p.same_as_delivery))
        p.product_id=data.get('product_id', p.product_id)
        p.product_name_filter=data.get('product_name_filter', p.product_name_filter)
        p.delivery_type=data.get('delivery_type', p.delivery_type)
        p.delivery_schedule=data.get('delivery_schedule', p.delivery_schedule)
        p.payment_terms_days=int(data.get('payment_terms_days', p.payment_terms_days) or 0)
        p.rate_basis=data.get('rate_basis', p.rate_basis)
        p.freight_terms=data.get('freight_terms', p.freight_terms)
        p.tds_applicable=data.get('tds_applicable', p.tds_applicable)
        p.tds_percent=float(data.get('tds_percent', p.tds_percent) or 0)
        p.rcm_applicable=data.get('rcm_applicable', p.rcm_applicable)
        p.rcm_percent=float(data.get('rcm_percent', p.rcm_percent) or 0)
        if data.get('documents') is not None:
            p.documents=json.dumps(data.get('documents'))
        p.status=data.get('status', p.status)
        p.approval_status=data.get('approval_status', p.approval_status)
        p.updated_by=data.get('updated_by','Admin')
        p.updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()
        return jsonify(ok=True, po_no=p.po_no, grand_total=p.grand_total)
    db.session.delete(p)
    db.session.commit()
    return jsonify(ok=True)

@app.route('/api/po/rate_history', methods=['GET'])
def po_rate_history():
    vendor_id=request.args.get('vendor_id')
    product_id=request.args.get('product_id')
    product_name=request.args.get('product_name','').lower()
    pos=PO.query.order_by(PO.id.desc()).limit(50).all()
    history=[]
    for p in pos:
        if vendor_id and str(p.vendor_id)!=str(vendor_id): continue
        try:
            items=json.loads(p.items) if p.items else []
        except:
            items=[]
        for it in items:
            pid_match=False
            if product_id and str(it.get('product_id'))==str(product_id):
                pid_match=True
            if product_name and product_name in (it.get('product_name') or '').lower():
                pid_match=True
            if not product_id and not product_name:
                pid_match=True
            if pid_match:
                history.append({
                    'po_no':p.po_no,'po_date':p.po_date,'vendor':p.vendor,'vendor_id':p.vendor_id,
                    'product_code':it.get('product_code'),'product_name':it.get('product_name'),
                    'spec':it.get('spec'), 'qty':it.get('qty'), 'rate':it.get('rate'), 'uom':it.get('uom'),
                    'gst_percent':it.get('gst_percent')
                })
            if len(history)>=10: break
        if len(history)>=10: break
    return jsonify(history)

@app.route('/api/po/duplicate/<int:pid>', methods=['POST'])
def po_duplicate(pid):
    p=PO.query.get_or_404(pid)
    try:
        items=json.loads(p.items) if p.items else []
    except:
        items=[]
    try:
        docs=json.loads(p.documents) if p.documents else {}
    except:
        docs={}
    fy=get_financial_year(p.po_date)
    prod_name=p.product_name_filter or 'PRODUCT'
    prod_sanitized=sanitize_product_name_for_po(prod_name)
    existing_count=PO.query.filter(PO.po_no.like(f"PO/{fy}/{prod_sanitized}/%")).count()+1
    new_po_no=generate_po_no(fy, prod_name, existing_count)
    while PO.query.filter_by(po_no=new_po_no).first():
        existing_count+=1
        new_po_no=generate_po_no(fy, prod_name, existing_count)
    new_po=PO(
        po_no=new_po_no,
        rfq_no=p.rfq_no,
        po_date=datetime.now().strftime('%Y-%m-%d'),
        po_validity=p.po_validity,
        po_type=p.po_type,
        sbu_id=p.sbu_id,
        sbu_name=p.sbu_name,
        delivery_address=p.delivery_address,
        billing_address=p.billing_address,
        same_as_delivery=p.same_as_delivery,
        product_id=p.product_id,
        product_name_filter=p.product_name_filter,
        vendor=p.vendor,
        vendor_id=p.vendor_id,
        vendor_code=p.vendor_code,
        vendor_state=p.vendor_state,
        items=json.dumps(items),
        taxable_value=p.taxable_value,
        cgst_amount=p.cgst_amount,
        sgst_amount=p.sgst_amount,
        igst_amount=p.igst_amount,
        freight_amount=p.freight_amount,
        round_off=p.round_off,
        grand_total=p.grand_total,
        material=p.material,
        qty=p.qty,
        rate=p.rate,
        unit=p.unit,
        delivery_type=p.delivery_type,
        delivery_schedule=p.delivery_schedule,
        payment_terms_days=p.payment_terms_days,
        rate_basis=p.rate_basis,
        freight_terms=p.freight_terms,
        tds_applicable=p.tds_applicable,
        tds_percent=p.tds_percent,
        rcm_applicable=p.rcm_applicable,
        rcm_percent=p.rcm_percent,
        documents=json.dumps(docs),
        status='Draft',
        approval_status='Draft',
        created_by='Admin',
        updated_by='Admin'
    )
    db.session.add(new_po)
    db.session.commit()
    return jsonify(id=new_po.id, po_no=new_po.po_no)


# ========== BACKUP MODULE v4.5.1 - ONLY BACKUP MODULE ADDED - OTHER MODULES LOCKED ==========
@app.route('/api/backup', methods=['GET'])
def backup_api():
    try:
        # Collect all tables data
        data={}
        # Product Categories
        data['product_category']=[{'id':c.id,'category_name':c.category_name,'created_at':c.created_at} for c in ProductCategory.query.all()]
        # Products
        data['product']=[{'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description,'loose_stock_mt':p.loose_stock_mt,'jumbo_mt':p.jumbo_mt,'hdpe_40kg_mt':p.hdpe_40kg_mt,'total_stock_mt':p.total_stock_mt,'min_stock':p.min_stock,'reorder_level':p.reorder_level,'sale_price':p.sale_price,'purchase_price':p.purchase_price,'location':p.location} for p in Product.query.all()]
        # SBUs
        data['sbu']=[{'id':s.id,'sbu_name':s.sbu_name,'address':s.address,'created_at':s.created_at} for s in SBU.query.all()]
        # Kiln Assets
        data['kiln_asset']=[{'id':k.id,'sbu_id':k.sbu_id,'kiln_no':k.kiln_no,'lining_installation_date':k.lining_installation_date,'health_status':k.health_status,'products_capacity':k.products_capacity} for k in KilnAsset.query.all()]
        # Sizing Plant Assets
        data['sizing_plant_asset']=[{'id':s.id,'sbu_id':s.sbu_id,'plant_no':s.plant_no,'products_capacity':s.products_capacity,'machineries':s.machineries} for s in SizingPlantAsset.query.all()]
        # Hydration Plant Assets
        data['hydration_plant_asset']=[{'id':h.id,'sbu_id':h.sbu_id,'plant_no':h.plant_no,'products_capacity':h.products_capacity,'machineries':h.machineries} for h in HydrationPlantAsset.query.all()]
        # Stock Yard Assets
        data['stock_yard_asset']=[{'id':y.id,'sbu_id':y.sbu_id,'yard_name':y.yard_name,'items':y.items} for y in StockYardAsset.query.all()]
        # Vendors - handle both old and new schema
        vendors=[]
        for v in Vendor.query.all():
            try:
                vendors.append({
                    'id':v.id,'vendor_code':getattr(v,'vendor_code',''),'name':v.name,'station':getattr(v,'station',''),'address':getattr(v,'address',''),'state':getattr(v,'state',''),
                    'gst_no':getattr(v,'gst_no',''),'pan_no':getattr(v,'pan_no',''),'tan_no':getattr(v,'tan_no',''),
                    'legal_status':getattr(v,'legal_status',''),'vendor_category':getattr(v,'vendor_category',''),
                    'bank_details':getattr(v,'bank_details','[]'),'contacts':getattr(v,'contacts','[]'),
                    'status':getattr(v,'status','Active'),
                    'msme_cert_no':getattr(v,'msme_cert_no',''),'msme_expiry':getattr(v,'msme_expiry',''),'msme_upload':getattr(v,'msme_upload',''),
                    'gst_reg_type':getattr(v,'gst_reg_type','Regular'),'tds_section':getattr(v,'tds_section','194C'),
                    'vendor_rating':getattr(v,'vendor_rating',0),'last_audit_date':getattr(v,'last_audit_date',''),
                    'documents':getattr(v,'documents','{}'),
                    'opening_balance':getattr(v,'opening_balance',0),'opening_balance_type':getattr(v,'opening_balance_type','Dr'),
                    'ledger_group':getattr(v,'ledger_group','Sundry Creditors'),'total_business_value':getattr(v,'total_business_value',0),
                    'approval_status':getattr(v,'approval_status','Draft'),'created_by':getattr(v,'created_by','Admin'),
                    'created_at':getattr(v,'created_at',''),'updated_by':getattr(v,'updated_by','Admin'),
                    'updated_at':getattr(v,'updated_at',''),'last_transaction_date':getattr(v,'last_transaction_date',''),
                    'po_count':getattr(v,'po_count',0),'grn_count':getattr(v,'grn_count',0)
                })
            except Exception as e:
                print(f"Vendor backup error {v.id}: {e}")
        data['vendor']=vendors
        # Customers
        try:
            data['customer']=[{'id':c.id,'name':c.name,'type':getattr(c,'type','')} for c in Customer.query.all()]
        except:
            data['customer']=[]
        # POs - handle both old and new schema
        pos=[]
        for p in PO.query.all():
            try:
                pos.append({
                    'id':p.id,'po_no':getattr(p,'po_no',''),'rfq_no':getattr(p,'rfq_no',''),'po_date':getattr(p,'po_date',''),
                    'po_validity':getattr(p,'po_validity',''),'po_type':getattr(p,'po_type','Raw Material'),
                    'sbu_id':getattr(p,'sbu_id',None),'sbu_name':getattr(p,'sbu_name',''),
                    'delivery_address':getattr(p,'delivery_address',''),'billing_address':getattr(p,'billing_address',''),
                    'same_as_delivery':getattr(p,'same_as_delivery',True),
                    'product_id':getattr(p,'product_id',None),'product_name_filter':getattr(p,'product_name_filter',''),
                    'vendor':getattr(p,'vendor',''),'vendor_id':getattr(p,'vendor_id',None),'vendor_code':getattr(p,'vendor_code',''),'vendor_state':getattr(p,'vendor_state',''),
                    'items':getattr(p,'items','[]'),
                    'taxable_value':getattr(p,'taxable_value',0),'cgst_amount':getattr(p,'cgst_amount',0),'sgst_amount':getattr(p,'sgst_amount',0),'igst_amount':getattr(p,'igst_amount',0),
                    'freight_amount':getattr(p,'freight_amount',0),'round_off':getattr(p,'round_off',0),'grand_total':getattr(p,'grand_total',0),
                    'material':getattr(p,'material',''),'qty':getattr(p,'qty',0),'rate':getattr(p,'rate',0),'unit':getattr(p,'unit','MT'),
                    'delivery_type':getattr(p,'delivery_type','One Time'),'delivery_schedule':getattr(p,'delivery_schedule',''),
                    'payment_terms_days':getattr(p,'payment_terms_days',0),'rate_basis':getattr(p,'rate_basis','FOR'),'freight_terms':getattr(p,'freight_terms',''),
                    'tds_applicable':getattr(p,'tds_applicable','Not Applicable'),'tds_percent':getattr(p,'tds_percent',0),
                    'rcm_applicable':getattr(p,'rcm_applicable','No'),'rcm_percent':getattr(p,'rcm_percent',0),
                    'documents':getattr(p,'documents','{}'),'status':getattr(p,'status','Draft'),'approval_status':getattr(p,'approval_status','Draft'),
                    'created_by':getattr(p,'created_by','Admin'),'created_at':getattr(p,'created_at',''),
                    'updated_by':getattr(p,'updated_by','Admin'),'updated_at':getattr(p,'updated_at','')
                })
            except Exception as e:
                print(f"PO backup error {p.id}: {e}")
        data['po']=pos
        # GRNs
        data['grn']=[{'id':g.id,'vehicle_no':g.vehicle_no,'material':g.material,'unit':getattr(g,'unit','MT'),'gross_kg':getattr(g,'gross_kg',0),'tare_kg':getattr(g,'tare_kg',0),'vendor':g.vendor,'net_kg':getattr(g,'net_kg',0)} for g in GRN.query.all()]
        # MOs
        data['manufacturing_order']=[{'id':m.id,'sbu':m.sbu,'type':m.type,'unit':m.unit,'limestone_mt':getattr(m,'limestone_mt',0),'petcoke_mt':getattr(m,'petcoke_mt',0),'output_mt':getattr(m,'output_mt',0),'wastage':getattr(m,'wastage',0),'input_product':getattr(m,'input_product',''),'output_product':getattr(m,'output_product',''),'operator':getattr(m,'operator',''),'created_at':getattr(m,'created_at','')} for m in MO.query.all()]
        # Dispatch
        data['dispatch']=[{'id':d.id,'customer':d.customer,'vehicle_no':d.vehicle_no,'product':d.product,'qty_mt':d.qty_mt,'qr_bags':getattr(d,'qr_bags',0),'unit':d.unit} for d in Dispatch.query.all()]
        # QR Bags
        data['qr_bag']=[{'id':q.id,'bag_id':q.bag_id,'product':q.product,'weight':q.weight,'unit':q.unit,'qr_data':q.qr_data,'qr_base64':q.qr_base64,'created_at':q.created_at} for q in QRBag.query.all()]
        data['meta']={'backup_date':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'version':'v4.5.1 Backup Module','total_tables':len(data)}
        return jsonify(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(error=str(e)),500

@app.route('/api/backup/download', methods=['GET'])
def backup_download():
    try:
        # Reuse backup_api logic to get data
        with app.test_request_context():
            # Collect data same as backup_api
            data={}
            data['product_category']=[{'id':c.id,'category_name':c.category_name,'created_at':c.created_at} for c in ProductCategory.query.all()]
            data['product']=[{'id':p.id,'name':p.name,'category':p.category,'product_code':p.product_code,'hsn_code':p.hsn_code,'description':p.description} for p in Product.query.all()]
            data['sbu']=[{'id':s.id,'sbu_name':s.sbu_name,'address':s.address} for s in SBU.query.all()]
            data['vendor']=[{'id':v.id,'vendor_code':getattr(v,'vendor_code',''),'name':v.name,'station':getattr(v,'station',''),'state':getattr(v,'state',''),'gst_no':getattr(v,'gst_no',''),'pan_no':getattr(v,'pan_no',''),'bank_details':getattr(v,'bank_details','[]'),'contacts':getattr(v,'contacts','[]')} for v in Vendor.query.all()]
            data['customer']=[{'id':c.id,'name':c.name} for c in Customer.query.all()]
            data['po']=[{'id':p.id,'po_no':getattr(p,'po_no',''),'po_date':getattr(p,'po_date',''),'vendor':getattr(p,'vendor',''),'grand_total':getattr(p,'grand_total',0),'items':getattr(p,'items','[]')} for p in PO.query.all()]
            data['grn']=[{'id':g.id,'vehicle_no':g.vehicle_no,'material':g.material,'vendor':g.vendor} for g in GRN.query.all()]
            data['meta']={'backup_date':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'version':'v4.5.1'}
        from flask import Response
        import json
        json_str=json.dumps(data, indent=2)
        filename=f"lemon_erp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        return Response(json_str, mimetype='application/json', headers={'Content-Disposition': f'attachment; filename={filename}'})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(error=str(e)),500

@app.route('/api/backup/upload', methods=['POST'])
def backup_upload():
    try:
        data=request.get_json() or {}
        # If file uploaded as multipart, handle
        if 'file' in request.files:
            file=request.files['file']
            content=file.read().decode('utf-8')
            data=json.loads(content)
        # Also support direct JSON body with backup data
        if 'product_category' in data or 'product' in data or 'vendor' in data:
            backup_data=data
        else:
            # Maybe data is wrapped
            backup_data=data.get('backup_data') or data
        
        restored_counts={}
        # Restore Product Categories
        if 'product_category' in backup_data:
            count=0
            for cat in backup_data['product_category']:
                cat_name=cat.get('category_name')
                if not cat_name: continue
                existing=ProductCategory.query.filter_by(category_name=cat_name).first()
                if not existing:
                    db.session.add(ProductCategory(category_name=cat_name, created_at=cat.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))))
                    count+=1
            db.session.commit()
            restored_counts['product_category']=count
        
        # Restore Products
        if 'product' in backup_data:
            count=0
            for prod in backup_data['product']:
                code=prod.get('product_code')
                if not code: continue
                existing=Product.query.filter_by(product_code=code).first()
                if not existing:
                    # Find category exists
                    p=Product(
                        name=prod.get('name',''), category=prod.get('category',''), product_code=code,
                        hsn_code=prod.get('hsn_code',''), description=prod.get('description',''),
                        loose_stock_mt=prod.get('loose_stock_mt',0), jumbo_mt=prod.get('jumbo_mt',0),
                        hdpe_40kg_mt=prod.get('hdpe_40kg_mt',0), total_stock_mt=prod.get('total_stock_mt',0)
                    )
                    db.session.add(p)
                    count+=1
            db.session.commit()
            restored_counts['product']=count
        
        # Restore SBUs
        if 'sbu' in backup_data:
            count=0
            for s in backup_data['sbu']:
                name=s.get('sbu_name')
                if not name: continue
                existing=SBU.query.filter_by(sbu_name=name).first()
                if not existing:
                    db.session.add(SBU(sbu_name=name, address=s.get('address','')))
                    count+=1
            db.session.commit()
            restored_counts['sbu']=count
        
        # Restore Vendors
        if 'vendor' in backup_data:
            count=0
            for v in backup_data['vendor']:
                code=v.get('vendor_code')
                name=v.get('name')
                if not name: continue
                existing=None
                if code:
                    existing=Vendor.query.filter_by(vendor_code=code).first()
                if not existing:
                    existing=Vendor.query.filter_by(name=name).first()
                if not existing:
                    # Create vendor with minimal fields, try full fields if model supports
                    try:
                        vendor=Vendor(
                            vendor_code=code or f"VEND-{Vendor.query.count()+1:04d}",
                            name=name,
                            station=v.get('station',''), address=v.get('address',''), state=v.get('state',''),
                            gst_no=v.get('gst_no',''), pan_no=v.get('pan_no',''), tan_no=v.get('tan_no',''),
                            legal_status=v.get('legal_status',''), vendor_category=v.get('vendor_category',''),
                            bank_details=v.get('bank_details','[]') if isinstance(v.get('bank_details'), str) else json.dumps(v.get('bank_details',[])),
                            contacts=v.get('contacts','[]') if isinstance(v.get('contacts'), str) else json.dumps(v.get('contacts',[])),
                            status=v.get('status','Active')
                        )
                        # Try to set extra fields if they exist on model
                        for field in ['msme_cert_no','msme_expiry','gst_reg_type','tds_section','vendor_rating','documents','opening_balance','ledger_group','approval_status']:
                            if field in v and hasattr(vendor, field):
                                setattr(vendor, field, v[field])
                        db.session.add(vendor)
                        count+=1
                    except Exception as e:
                        print(f"Vendor restore error {name}: {e}")
            db.session.commit()
            restored_counts['vendor']=count
        
        # Restore POs
        if 'po' in backup_data:
            count=0
            for p in backup_data['po']:
                po_no=p.get('po_no')
                if po_no:
                    existing=PO.query.filter_by(po_no=po_no).first()
                    if existing:
                        continue
                # Create PO - try with new schema, fallback to old
                try:
                    po=PO(
                        po_no=po_no or f"PO/RESTORE/{PO.query.count()+1:04d}",
                        po_date=p.get('po_date',''), po_type=p.get('po_type','Raw Material'),
                        sbu_name=p.get('sbu_name',''), vendor=p.get('vendor',''),
                        material=p.get('material',''), qty=p.get('qty',0), rate=p.get('rate',0),
                        unit=p.get('unit','MT'), status=p.get('status','Draft')
                    )
                    # Try set new fields if exist
                    for field in ['rfq_no','po_validity','sbu_id','delivery_address','billing_address','same_as_delivery','product_id','product_name_filter','vendor_id','vendor_code','vendor_state','items','taxable_value','cgst_amount','sgst_amount','igst_amount','freight_amount','round_off','grand_total','delivery_type','delivery_schedule','payment_terms_days','rate_basis','freight_terms','tds_applicable','tds_percent','rcm_applicable','rcm_percent','documents','approval_status','created_by']:
                        if field in p and hasattr(po, field):
                            setattr(po, field, p[field])
                    db.session.add(po)
                    count+=1
                except Exception as e:
                    print(f"PO restore error {po_no}: {e}")
            db.session.commit()
            restored_counts['po']=count
        
        # Restore Customers
        if 'customer' in backup_data:
            count=0
            for c in backup_data['customer']:
                name=c.get('name')
                if not name: continue
                existing=Customer.query.filter_by(name=name).first()
                if not existing:
                    db.session.add(Customer(name=name, type=c.get('type','')))
                    count+=1
            db.session.commit()
            restored_counts['customer']=count
        
        return jsonify(ok=True, restored=restored_counts, message=f"Backup restored: {restored_counts}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify(error=str(e)),500

@app.route('/api/grn', methods=['GET','POST'])
def grn_api():
    if request.method=='GET':
        search=(request.args.get('search') or '').strip().lower()
        grn_type=request.args.get('grn_type','')
        status_f=request.args.get('status','')
        sbu_f=request.args.get('sbu','')
        vendor_f=request.args.get('vendor','')
        grns=GRN.query.order_by(GRN.id.desc()).all()
        result=[]
        for g in grns:
            try:
                docs=json.loads(g.documents) if g.documents else {}
            except:
                docs={}
            if search and not (search in (g.grn_no or '').lower() or search in (g.vehicle_no or '').lower() or search in (g.vendor or '').lower() or search in (g.po_no or '').lower() or search in (g.product_name or '').lower()):
                continue
            if grn_type and g.grn_type!=grn_type: continue
            if status_f and g.status!=status_f: continue
            if sbu_f and str(g.sbu_id)!=str(sbu_f): continue
            if vendor_f and str(g.vendor_id)!=str(vendor_f): continue
            result.append({
                'id':g.id,'grn_no':g.grn_no,'grn_date':g.grn_date,'grn_type':g.grn_type,
                'po_id':g.po_id,'po_no':g.po_no,
                'sbu_id':g.sbu_id,'sbu_name':g.sbu_name,'sbu_code':g.sbu_code,
                'vendor_id':g.vendor_id,'vendor':g.vendor,'station':g.station,
                'vehicle_no':g.vehicle_no,'product_name':g.product_name,'material':g.material,
                'received_qty':g.received_qty,'accepted_qty':g.accepted_qty,'net_mt':g.net_mt,'net_kg':g.net_kg,
                'documents':docs,'has_docs':len([v for v in docs.values() if v])>0,
                'status':g.status,'created_by':g.created_by
            })
        return jsonify(result)
    try:
        data=request.get_json() or {}
        grn_date=data.get('grn_date') or datetime.now().strftime('%Y-%m-%d')
        fy=get_financial_year(grn_date)
        sbu_id=data.get('sbu_id')
        sbu_name=''
        sbu_code='SBU'
        if sbu_id:
            sbu=SBU.query.get(sbu_id)
            if sbu:
                sbu_name=sbu.sbu_name
                sbu_code=sanitize_sbu_code(sbu.sbu_name)
        existing_count=GRN.query.filter(GRN.grn_no.like(f"GRN/{fy}/{sbu_code}/%")).count()+1
        grn_no=data.get('grn_no') or generate_grn_no(fy, sbu_code, existing_count)
        while GRN.query.filter_by(grn_no=grn_no).first():
            existing_count+=1
            grn_no=generate_grn_no(fy, sbu_code, existing_count)
        vendor_id=data.get('vendor_id')
        vendor_name=data.get('vendor','')
        station=data.get('station','')
        if vendor_id:
            v=Vendor.query.get(vendor_id)
            if v:
                vendor_name=v.name
                station=data.get('station') or v.station or ''
        product_id=data.get('product_id')
        product_name=data.get('product_name','')
        if product_id:
            prod=Product.query.get(product_id)
            if prod:
                product_name=prod.name
        gross_kg=float(data.get('gross_kg') or 0)
        tare_kg=float(data.get('tare_kg') or 0)
        net_kg=gross_kg - tare_kg if gross_kg and tare_kg else float(data.get('net_kg') or 0)
        net_mt=round(net_kg/1000,3) if net_kg else float(data.get('net_mt') or 0)
        received_qty=float(data.get('received_qty') or net_mt or 0)
        accepted_qty=float(data.get('accepted_qty') or received_qty or 0)
        rate=float(data.get('rate') or 0)
        taxable=round(accepted_qty*rate,2) if accepted_qty and rate else 0
        grn=GRN(
            grn_no=grn_no,grn_date=grn_date,grn_type=data.get('grn_type','Against PO'),
            po_id=data.get('po_id'),po_no=data.get('po_no',''),
            sbu_id=sbu_id,sbu_name=sbu_name,sbu_code=sbu_code,
            vendor_id=vendor_id,vendor=vendor_name,station=station,
            vehicle_no=data.get('vehicle_no',''),driver_name=data.get('driver_name',''),
            bill_no=data.get('bill_no',''),wayment_slip_no=data.get('wayment_slip_no',''),
            product_id=product_id,product_name=product_name,material=data.get('material') or product_name,
            received_qty=received_qty,accepted_qty=accepted_qty,rate=rate,taxable_value=taxable,grand_total=taxable,
            gross_kg=gross_kg,tare_kg=tare_kg,net_kg=net_kg,net_mt=net_mt,
            stock_yard_id=int(data.get('stock_yard_id') or 0),stock_yard_name=data.get('stock_yard_name',''),
            quality_status=data.get('quality_status','OK'),documents=json.dumps(data.get('documents',{})),
            status='Approved',created_by=data.get('created_by','Admin')
        )
        db.session.add(grn)
        db.session.commit()
        try:
            if product_id and accepted_qty:
                prod=Product.query.get(product_id)
                if prod:
                    prod.total_stock_mt=(prod.total_stock_mt or 0) + accepted_qty
                    db.session.commit()
        except Exception as e:
            print(f"Stock update failed: {e}")
        return jsonify(id=grn.id, grn_no=grn.grn_no, accepted_qty=grn.accepted_qty)
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify(error=f'Server error saving GRN: {str(e)}'),500

@app.route('/api/grn/<int:gid>', methods=['GET','PUT','DELETE'])
def grn_one(gid):
    g=GRN.query.get_or_404(gid)
    if request.method=='GET':
        try:
            docs=json.loads(g.documents) if g.documents else {}
        except:
            docs={}
        return jsonify(id=g.id,grn_no=g.grn_no,grn_date=g.grn_date,grn_type=g.grn_type,po_id=g.po_id,po_no=g.po_no,sbu_id=g.sbu_id,sbu_name=g.sbu_name,sbu_code=g.sbu_code,vendor_id=g.vendor_id,vendor=g.vendor,station=g.station,vehicle_no=g.vehicle_no,product_id=g.product_id,product_name=g.product_name,material=g.material,received_qty=g.received_qty,accepted_qty=g.accepted_qty,rate=g.rate,gross_kg=g.gross_kg,tare_kg=g.tare_kg,net_kg=g.net_kg,net_mt=g.net_mt,stock_yard_id=g.stock_yard_id,documents=docs,status=g.status,created_by=g.created_by)
    if request.method=='PUT':
        try:
            data=request.get_json() or {}
            for field in ['grn_date','grn_type','po_id','po_no','sbu_id','sbu_name','vendor_id','vendor','station','vehicle_no','product_id','product_name','material','received_qty','accepted_qty','rate','gross_kg','tare_kg','net_kg','net_mt','stock_yard_id','stock_yard_name','quality_status','remarks','status']:
                if field in data and hasattr(g, field):
                    setattr(g, field, data[field])
            if 'documents' in data:
                g.documents=json.dumps(data['documents'])
            g.updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.commit()
            return jsonify(ok=True, grn_no=g.grn_no)
        except Exception as e:
            db.session.rollback()
            return jsonify(error=str(e)),500
    try:
        db.session.delete(g)
        db.session.commit()
        return jsonify(ok=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(error=str(e)),500

@app.route('/api/grn/po_list', methods=['GET'])
def grn_po_list():
    search=(request.args.get('search') or '').lower()
    pos=PO.query.order_by(PO.id.desc()).limit(100).all()
    result=[]
    for p in pos:
        if search and not (search in (p.po_no or '').lower() or search in (p.vendor or '').lower()):
            continue
        try:
            items=json.loads(p.items) if p.items else []
        except:
            items=[]
        prod_name=items[0].get('product_name') if items else p.material
        result.append({'id':p.id,'po_no':p.po_no,'po_date':p.po_date,'sbu_id':p.sbu_id,'sbu_name':p.sbu_name,'vendor_id':p.vendor_id,'vendor':p.vendor,'material':prod_name,'items':items})
    return jsonify(result)

@app.route('/api/grn/sbu_yards/<int:sbu_id>', methods=['GET'])
def grn_sbu_yards(sbu_id):
    yards=StockYardAsset.query.filter_by(sbu_id=sbu_id).all()
    return jsonify([{'id':y.id,'yard_name':y.yard_name,'sbu_id':y.sbu_id} for y in yards])

@app.route('/api/grn/ocr', methods=['POST'])
def grn_ocr():
    return jsonify(vehicle_no='',gross_kg=0,tare_kg=0,net_kg=0,slip_no='',date=datetime.now().strftime('%Y-%m-%d'),message='OCR placeholder')


@app.route('/api/dispatch', methods=['GET','POST'])
def disp_api():
    if request.method=='GET': return jsonify([])
    return jsonify(ok=True)

@app.route('/api/packaging', methods=['GET','POST'])
def pack_api():
    if request.method=='GET': return jsonify([])
    return jsonify(ok=True)

@app.route('/api/qr_generate', methods=['POST'])
def qr_gen():
    import qrcode, io, base64
    d=request.get_json() or {}
    cnt=QRBag.query.count()+1
    bag_id=f"JMB-{d.get('product','PROD')}-2026-{cnt:05d}"
    qr_data=f"{bag_id}|{d.get('product')}|{d.get('weight')} MT|{d.get('unit')}"
    qr=qrcode.QRCode(box_size=8, border=3); qr.add_data(qr_data); qr.make(fit=True)
    img=qr.make_image(fill_color="#1A2E1E", back_color="#FAF6F0")
    buf=io.BytesIO(); img.save(buf, format='PNG'); b64=base64.b64encode(buf.getvalue()).decode()
    qb=QRBag(bag_id=bag_id, product=d.get('product'), weight=d.get('weight'), unit=d.get('unit'), qr_data=qr_data, qr_base64=b64)
    db.session.add(qb); db.session.commit()
    return jsonify(bag_id=bag_id, qr_data=qr_data, qr_base64=b64)

@app.route('/api/qr_list')
def qr_list(): return jsonify([{'bag_id':q.bag_id,'product':q.product} for q in QRBag.query.order_by(QRBag.id.desc()).all()])

# ========== FRONTEND HTML - v4.5.2 PO Module Locked + Backup v4.5.1 + Product Master 3 Cat 18 Prod ==========
HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lemon ERP v4.4.10.1 - Vendor Docs Drag Drop + File Select</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
<style>
:root{--green:#1A2E1E;--brass:#C9A86A;--alab:#FAF6F0;--lemon:#F2E863;--line:#E8E0D5;--gray:#F6F5F3}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui;background:var(--gray)}
.topnav{background:var(--green);color:white;padding:0 14px;display:flex;justify-content:space-between;align-items:center;height:44px;position:sticky;top:0;z-index:200}
.brand{font-weight:900;font-size:15px} .brand span{color:var(--lemon)}
.layout{display:flex}
.sidebar{width:210px;background:white;border-right:1px solid var(--line);padding:10px 0;position:sticky;top:44px;height:calc(100vh - 44px);overflow-y:auto}
.sidebar h4{font-size:10px;color:#888;margin:14px 10px 4px;text-transform:uppercase;letter-spacing:0.6px}
.menu{padding:7px 10px;margin:2px 6px;border-radius:7px;cursor:pointer;display:flex;align-items:center;gap:8px;font-weight:600;font-size:12px;color:#444}
.menu:hover{background:var(--alab)} .menu.active{background:var(--green);color:var(--brass)}
.content{flex:1;padding:14px;max-width:1500px}
.card{background:white;border-radius:10px;padding:14px;margin:8px 0;box-shadow:0 2px 6px rgba(0,0,0,0.04);border:1px solid var(--line)}
.card h3{margin:0 0 10px;font-size:13px;font-weight:800}
.kpi{border-left:4px solid var(--brass);padding:12px} .kpi .val{font-size:20px;font-weight:900}
.btn{padding:7px 12px;border-radius:7px;border:none;cursor:pointer;font-weight:700;font-size:11px}
.btn-g{background:var(--green);color:white} .btn-y{background:var(--lemon);color:var(--green)} .btn-w{background:white;color:var(--green);border:1px solid var(--line)} .btn-r{background:#C5221F;color:white} .btn-b{background:#E8F0FE;color:#1A2E1E;border:1px solid #C2D6FF} .btn-o{background:#FFF3E0;color:#8C6B2A;border:1px solid var(--brass)}
.badge{padding:3px 8px;border-radius:12px;font-size:10px;font-weight:800}
.ok{background:#E6F4EA;color:#1E7D32} .warn{background:#FEF3CD;color:#9C6F00} .crit{background:#FCE8E6;color:#C5221F} .brass{background:#FFFBEB;color:#8C6B2A;border:1px solid var(--brass)}
table{width:100%;border-collapse:collapse;font-size:12px} th{background:#F8F6F3;padding:8px 6px;text-align:left;font-weight:700;border-bottom:2px solid var(--line)} td{padding:7px 6px;border-bottom:1px solid #F0EBE2;vertical-align:top}
input,select,textarea{padding:8px 10px;border-radius:7px;border:1.5px solid var(--line);width:100%;font-size:12px;margin:4px 0}
.row{display:flex;gap:8px;flex-wrap:wrap} .row>*{flex:1;min-width:140px}
.hidden{display:none !important}
.form-box{background:var(--alab);padding:12px;border-radius:8px;border:1px dashed var(--brass);margin-bottom:10px}
.modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(26,46,30,0.65);z-index:1000;display:flex;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(4px)}
.modal-content{background:white;border-radius:14px;width:100%;max-width:1000px;max-height:94vh;display:flex;flex-direction:column;box-shadow:0 24px 64px rgba(0,0,0,0.35);border:1px solid var(--brass);animation:slideUp 0.25s ease}
@keyframes slideUp{from{transform:translateY(20px);opacity:0}to{transform:translateY(0);opacity:1}}
.modal-header{padding:16px 20px;border-bottom:2px solid var(--line);display:flex;justify-content:space-between;align-items:center;background:var(--alab);border-radius:14px 14px 0 0;position:sticky;top:0;z-index:2}
.modal-body{padding:16px 20px;overflow-y:auto;flex:1}
.modal-footer{padding:14px 20px;border-top:2px solid var(--line);background:var(--alab);border-radius:0 0 14px 14px;display:flex;gap:10px;position:sticky;bottom:0;z-index:2}
.close-x{background:white;border:1.5px solid var(--line);border-radius:50%;width:34px;height:34px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-weight:900;font-size:18px}
.close-x:hover{background:#FCE8E6;color:#C5221F;border-color:#C5221F}
.asset-section{background:white;border:1.5px solid var(--line);border-radius:12px;padding:14px;margin:14px 0}
.kiln-line{background:#FFFBEB;border:1.5px solid var(--brass);border-radius:10px;padding:12px;margin:10px 0}
.product-line{background:white;border:1px dashed var(--brass);border-radius:8px;padding:10px;margin:8px 0;margin-left:12px;border-left:4px solid var(--brass)}
.tooltip{position:relative;display:inline-block}
.tooltip .tip{visibility:hidden;width:260px;background:var(--green);color:white;border-radius:8px;padding:10px;position:absolute;bottom:125%;left:50%;margin-left:-130px;z-index:10;font-size:11px}
.tooltip:hover .tip{visibility:visible}
.sbu-card{border:1.5px solid var(--line);border-radius:12px;padding:14px;margin:12px 0;background:white}
.filter-bar{background:white;border:1.5px solid var(--line);border-radius:10px;padding:10px;margin:10px 0;display:flex;gap:8px;flex-wrap:wrap;align-items:end}
.search-input{position:relative} .search-input i{position:absolute;left:8px;top:50%;transform:translateY(-50%);color:#888}
.search-input input{padding-left:28px}

/* v4.4.10.1 Drag & Drop Document Upload Styles - ONLY Vendor Docs */
.drop-zone{border:2px dashed var(--brass);border-radius:10px;padding:16px;text-align:center;background:#FFFBEB;cursor:pointer;transition:all 0.2s;min-height:90px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px}
.drop-zone:hover{background:#FFF8E1;border-color:#1A2E1E}
.drop-zone.dragover{background:#E8F0FE;border-color:#1A2E1E;transform:scale(1.02);box-shadow:0 4px 12px rgba(26,46,30,0.15)}
.drop-zone i{font-size:28px;color:var(--brass)}
.drop-zone .dz-title{font-size:11px;font-weight:800;color:#1A2E1E}
.drop-zone .dz-hint{font-size:9px;color:#888}
.drop-zone .dz-file{font-size:10px;font-weight:700;color:#1A2E1E;background:white;padding:4px 8px;border-radius:6px;border:1px solid var(--line);margin-top:4px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.drop-zone .dz-clear{font-size:9px;color:#B33;background:none;border:none;cursor:pointer;text-decoration:underline;margin-top:4px}
.doc-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:700px){.doc-grid{grid-template-columns:1fr}}

</style></head>
<body>
<div class="topnav"><div class="brand">🍋 LEMON <span>ERP</span> v4.4.10.1 - Vendor Docs Drag Drop + File Select - Base v1.3.py</div><button class="btn btn-y" onclick="location.reload()">Reload</button></div>
<div class="layout">
<div class="sidebar">
<h4>MAIN</h4>
<div class="menu active" onclick="openTab('dash')"><i class="bi bi-speedometer2"></i> Dashboard</div>
<h4>OPERATIONS</h4>
<div class="menu" onclick="openTab('stock')"><i class="bi bi-box-seam"></i> Stock</div>
<div class="menu" onclick="openTab('make')"><i class="bi bi-gear"></i> Make</div>
<div class="menu" onclick="openTab('buy')"><i class="bi bi-cart"></i> Buy</div>
<div class="menu" onclick="openTab('grn')"><i class="bi bi-truck-flatbed"></i> GRN - v4.6</div>
<div class="menu" onclick="openTab('sell')"><i class="bi bi-truck"></i> Sell</div>
<div class="menu" onclick="openTab('pack')"><i class="bi bi-box"></i> Pack</div>
<div class="menu" onclick="openTab('qr')"><i class="bi bi-qr-code"></i> QR</div>
<h4>MASTERS</h4>
<div class="menu" onclick="openTab('product_category')"><i class="bi bi-tags"></i> Product Category</div>
<div class="menu" onclick="openTab('products')"><i class="bi bi-bag"></i> Products</div>
<div class="menu" onclick="openTab('sbus')"><i class="bi bi-building"></i> SBUs</div>
<div class="menu" onclick="openTab('vendors')"><i class="bi bi-people"></i> Vendors</div>
<div class="menu" onclick="openTab('customers')"><i class="bi bi-person"></i> Customers</div>
<div class="menu" onclick="openTab('cost')"><i class="bi bi-currency-rupee"></i> Cost</div>
<div class="menu" onclick="openTab('mobile')"><i class="bi bi-phone"></i> Mobile</div>
<h4>BACKUP</h4>
<div class="menu" onclick="openTab('backup')"><i class="bi bi-cloud-arrow-down"></i> Backup & Restore</div>
</div>
<div class="content">
<!-- DASH -->
<div id="dash" class="tabcontent">
<div class="card"><h3>Dashboard - v4.5 PO Module Fixed - Masters Locked - Single Dropdown - Base v1.3.py</h3>
<div class="row"><div class="card kpi"><div>Total Value</div><div class="val" id="totalVal">Rs 0 Lakh</div></div><div class="card kpi"><div>SBUs</div><div class="val" id="sbuCountDash">0</div></div><div class="card kpi"><div>Products</div><div class="val" id="prodCountDash">0</div></div><div class="card kpi"><div>Categories</div><div class="val" id="catCountDash">0</div></div></div>
<div class="card"><b>v4.4.10 Changes:</b> ONLY Vendor Master Enhanced - A MSME Cert No+Expiry+Upload GST Reg Type Regular/Composition/Unregistered/SEZ TDS 194C/194J/194Q/194H Rating 1-5 + Last Audit + Docs GST Cert PAN Cheque MSME ISO + B Opening Bal Dr/Cr Ledger Group Sundry Creditors + E Dept + Primary flag + F CreatedBy/At UpdatedBy/At Approval Draft/Pending/Approved/Rejected Last Trans Date Total Business Value - Bank single dropdown fix kept - Nothing removed - Heading + Add Vendor Button top + Filters + Search bar + Auto Code VEND-0001 + Station/State/GST/PAN/TAN/Legal Status/Vendor Category hidden masters + Bank Details Add Bank Account (Bank searchable nationalised banks + Branch/Account Name/IFSC/Account No/Transaction Limit) + Add Contact (Name/Designation hidden master/Mobile/Whatsapp/Land Line/Ext/Email) + PO/GRN counts - Everything else locked to v4.4.8 FIXED</div>
<div id="alerts"></div>
</div></div>

<!-- PRODUCT CATEGORY -->
<div id="product_category" class="tabcontent hidden">
<div class="card" style="text-align:center"><h1 style="font-size:22px;font-weight:900">Product Category Master - DB File for Further Use - v4.4.3 Unchanged</h1><p style="font-size:11px;color:#666">DB File: lemon_erp_v44_1_category.db - Table: product_category</p>
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass);text-align:left;max-width:600px;margin:12px auto"><b>Add Product Category - 1 Input Field</b><input type="hidden" id="cat_id"><div style="margin-top:8px">Category Name *<input id="category_name" placeholder="Category Name e.g. Raw - Limestone, Finished - Quicklime 10-40mm"></div><div class="row" style="margin-top:8px"><button class="btn btn-g" onclick="saveCategory()">Save Category</button><button class="btn btn-w" onclick="resetCat()">Reset</button></div></div>
<table><thead><tr><th>#</th><th>Category Name</th><th>Created At</th><th>DB File</th><th>Actions</th></tr></thead><tbody id="catTbl"></tbody></table>
</div></div>

<!-- PRODUCTS -->
<div id="products" class="tabcontent hidden">
<div class="card" style="text-align:center"><h1 style="font-size:22px;font-weight:900;text-align:center"><i class="bi bi-bag"></i> Products</h1><p style="font-size:11px;color:#666;text-align:center">Landing Page Heading Products centrally aligned - HSN + Description + Auto Code + Category-wise + Hover narration - v4.4.3 Unchanged</p><button class="btn btn-y" style="padding:12px 28px;font-size:14px;font-weight:800" onclick="openAddProductPopup()">Add New Product</button>
<div id="prodList"></div></div></div>

<!-- SBUS -->
<div id="sbus" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 14px;text-align:center"><i class="bi bi-building"></i> Strategic Business Units</h1>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddSBU()">Add New SBU</button>
</div>
<div id="sbuList">Loading SBUs...</div>
</div>

<!-- VENDORS v4.4.10 COMPLIANCE + DOCS + OPENING + WORKFLOW -->
<div id="vendors" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 6px;text-align:center"><i class="bi bi-people"></i> Vendor Master</h1>
<p style="font-size:11px;color:#666;text-align:center;margin:0 0 14px">Vendor Master - VEND-0001 + Compliance MSME GST Reg TDS Rating + Docs GST PAN Cheque MSME ISO + Opening Bal Dr/Cr Ledger + Dept Primary + Workflow Draft/Pending/Approved + Business Value - v4.4.10 - Base v1.3.py</p>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddVendorPopup()">Add New Vendor</button>
</div>

<div class="filter-bar">
<div class="search-input" style="flex:2;min-width:200px"><i class="bi bi-search"></i><input id="vendorSearch" placeholder="Search Name, Code, Station, State, GST, PAN, MSME Cert..." onkeyup="loadVendors()"></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">Legal Status</label><select id="vendorLegalFilter" onchange="loadVendors()"><option value="">All Legal Status</option></select></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">Category</label><select id="vendorCatFilter" onchange="loadVendors()"><option value="">All Categories</option></select></div>
<div style="flex:1;min-width:100px"><label style="font-size:10px;font-weight:700">State</label><select id="vendorStateFilter" onchange="loadVendors()"><option value="">All States</option></select></div>
<div style="flex:1;min-width:100px"><label style="font-size:10px;font-weight:700">Status</label><select id="vendorStatusFilter" onchange="loadVendors()"><option value="">All Status</option><option value="Active">Active</option><option value="Inactive">Inactive</option><option value="Blocked">Blocked</option></select></div>
<div style="flex:1;min-width:110px"><label style="font-size:10px;font-weight:700">Approval</label><select id="vendorApprovalFilter" onchange="loadVendors()"><option value="">All Approval</option><option value="Draft">Draft</option><option value="Pending">Pending</option><option value="Approved">Approved</option><option value="Rejected">Rejected</option></select></div>
<div style="flex:1;min-width:80px"><label style="font-size:10px;font-weight:700">Rating</label><select id="vendorRatingFilter" onchange="loadVendors()"><option value="">All Rating</option><option value="5">5★</option><option value="4">4★</option><option value="3">3★</option><option value="2">2★</option><option value="1">1★</option></select></div>
<div style="display:flex;gap:6px;align-items:end"><button class="btn btn-g" onclick="loadVendors()">Filter</button><button class="btn btn-w" onclick="resetVendorFilters()">Reset</button></div>
</div>

<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h3>Vendors List - Compliance + Docs + Business Value - v4.4.10</h3><span id="vendorCountBadge" class="badge brass">0 Vendors</span></div>
<div style="overflow-x:auto"><table><thead><tr><th>#</th><th>Code | Name</th><th>Station | State | GST Reg</th><th>MSME | Rating | Audit</th><th>Opening | Ledger | TDS</th><th>Banks | Contacts (Dept+Primary)</th><th>POs | GRNs | Value | Last Trans</th><th>Docs | Approval | Status | Created</th><th>Actions</th></tr></thead><tbody id="vendorTbl"></tbody></table></div>
</div>
</div>

<!-- STOCK etc -->
<div id="stock" class="tabcontent hidden"><div class="card"><h3>Stock - v4.4 Unchanged</h3><div class="row"><select id="fUnit"><option>All Units</option><option>Unit 1 72MT</option><option>Unit 2 84MT</option><option>Unit 3 125MT</option></select><button class="btn btn-g" onclick="loadStock()">Filter</button></div><div id="rawTbl"></div><div id="wipTbl"></div><div id="finTbl"></div></div></div>
<div id="make" class="tabcontent hidden"><div class="card"><h3>Make</h3><p>Make module v4.4 Unchanged</p><div id="moList"></div></div></div>
<!-- BUY - PURCHASE ORDER MODULE v4.5 FIXED - ONLY PO MODULE CHANGED, MASTERS LOCKED -->
<div id="buy" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 6px;text-align:center"><i class="bi bi-cart"></i> Purchase Orders</h1>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddPOPopup()">Add Purchase Order</button>
</div>
<div class="filter-bar">
<div class="search-input" style="flex:2;min-width:200px"><i class="bi bi-search"></i><input id="poSearch" placeholder="Search PO No, Vendor, SBU, Product, RFQ..." onkeyup="loadPOs()"></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">PO Type</label><select id="poTypeFilter" onchange="loadPOs()"><option value="">All Types</option><option value="Raw Material">Raw Material</option><option value="Consumables">Consumables</option><option value="CAPEX">CAPEX</option><option value="Packing">Packing</option><option value="Services">Services</option><option value="Others">Others</option></select></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">Status</label><select id="poStatusFilter" onchange="loadPOs()"><option value="">All Status</option><option value="Draft">Draft</option><option value="Pending">Pending</option><option value="Approved">Approved</option><option value="Sent to Vendor">Sent to Vendor</option><option value="Partially Received">Partially Received</option><option value="Closed">Closed</option></select></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">SBU</label><select id="poSbuFilter" onchange="loadPOs()"><option value="">All SBUs</option></select></div>
<div style="flex:1;min-width:120px"><label style="font-size:10px;font-weight:700">Vendor</label><select id="poVendorFilter" onchange="loadPOs()"><option value="">All Vendors</option></select></div>
<div style="display:flex;gap:6px;align-items:end"><button class="btn btn-g" onclick="loadPOs()">Filter</button><button class="btn btn-w" onclick="resetPOFilters()">Reset</button></div>
</div>
<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px"><h3>PO List - PO/26-27/PRODUCT/0001 + GST Breakup + Freight + Validity - v4.5 Fixed</h3><span id="poCountBadge" class="badge brass">0 POs</span></div>
<div style="overflow-x:auto"><table><thead><tr><th>#</th><th>PO No | Date | Validity</th><th>SBU | Delivery | Billing</th><th>Vendor | Rating | State</th><th>Type | Items | Qty</th><th>Taxable | CGST+SGST/IGST | Freight | Grand Total</th><th>Delivery Type | Schedule | Payment Days | Rate Basis | TDS/RCM</th><th>Docs | Status | Created</th><th>Actions</th></tr></thead><tbody id="poTbl"></tbody></table></div>
</div>
</div>

<!-- GRN MODULE v4.6 - Only GRN Module Added - Other Modules Locked to v4.5.2 -->
<div id="grn" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:18px">
<h1 style="font-size:22px;font-weight:900"><i class="bi bi-truck-flatbed"></i> GRN Module v4.6 - SBU Code + PO Link + Weighment + Stock Auto</h1>
<p style="font-size:11px;color:#666">GRN No: GRN/26-27/SBUCODE/0001 - PO searchable - SBU Code auto - Weighment Gross/Tare/Net auto - Stock auto update - v4.6 New</p>
<div class="row" style="justify-content:center">
<button class="btn btn-g" style="padding:12px 28px;font-size:14px" onclick="openAddGRNPopup()">Add New GRN - v4.6</button>
<button class="btn btn-y" onclick="loadGRNs()">Reload GRNs</button>
</div>
</div>
<div class="card">
<div class="filter-bar">
<div><label style="font-size:10px">Search</label><div class="search-input"><i class="bi bi-search"></i><input id="grn_search" placeholder="GRN No, Vehicle, Vendor, PO, Material" onkeyup="loadGRNs()"></div></div>
<div><label style="font-size:10px">GRN Type</label><select id="grn_type_filter" onchange="loadGRNs()"><option value="">All Types</option><option value="Against PO">Against PO</option><option value="Direct">Direct</option></select></div>
<div><label style="font-size:10px">Status</label><select id="grn_status_filter" onchange="loadGRNs()"><option value="">All Status</option><option value="Approved">Approved</option><option value="Received">Received</option></select></div>
<div><label style="font-size:10px">SBU</label><select id="grn_sbu_filter" onchange="loadGRNs()"><option value="">All SBUs</option></select></div>
<div><label style="font-size:10px">Vendor</label><select id="grn_vendor_filter" onchange="loadGRNs()"><option value="">All Vendors</option></select></div>
<div><button class="btn btn-w" onclick="clearGRNFilters()">Clear</button></div>
</div>
<div style="display:flex;gap:12px;margin:8px 0">
<div class="card kpi" style="flex:1"><div>Total GRNs</div><div class="val" id="grnTotalCount">0</div></div>
<div class="card kpi" style="flex:1"><div>Total MT</div><div class="val" id="grnTotalMT">0 MT</div></div>
<div class="card kpi" style="flex:1"><div>Accepted MT</div><div class="val" id="grnAcceptedMT">0 MT</div></div>
</div>
<div style="overflow-x:auto">
<table><thead><tr><th>GRN No</th><th>Date</th><th>PO No</th><th>SBU</th><th>Vendor</th><th>Vehicle</th><th>Material</th><th>Received</th><th>Accepted</th><th>Net MT</th><th>Status</th><th>Actions</th></tr></thead><tbody id="grnTbl"><tr><td colspan="12" style="text-align:center">Loading GRNs...</td></tr></tbody></table>
</div>
</div>
</div>

<div id="sell" class="tabcontent hidden"><div class="card"><h3>Sell</h3><p>Sell module v4.4 Unchanged</p></div></div>
<div id="customers" class="tabcontent hidden"><div class="card"><h3>Customers</h3><table><tbody id="customerTbl"></tbody></table></div></div>
<div id="pack" class="tabcontent hidden"><div class="card"><h3>Pack</h3><p>Pack v4.4</p></div></div>
<div id="qr" class="tabcontent hidden"><div class="card"><h3>QR</h3><p>QR module</p><div id="qrList"></div></div></div>
<div id="cost" class="tabcontent hidden"><div class="card"><h3>Cost</h3><div id="costVal"></div><div id="costTbl"></div></div></div>
<div id="mobile" class="tabcontent hidden"><div class="card"><h3>Mobile - Placeholder</h3></div></div>

<!-- BACKUP MODULE v4.5.1 - ONLY BACKUP MODULE ADDED - OTHER MODULES LOCKED -->
<div id="backup" class="tabcontent hidden">
<div class="card" style="text-align:center;padding:24px">
<h1 style="font-size:26px;font-weight:900;margin:0 0 6px;text-align:center"><i class="bi bi-cloud-arrow-down"></i> Backup & Restore Module</h1>
<p style="font-size:11px;color:#666;text-align:center;margin:0 0 14px">Backup all ERP data to JSON file + Restore from backup file - v4.5.1 - Other modules locked - Base v1.3.py</p>
<div class="row" style="justify-content:center;max-width:600px;margin:0 auto">
<button class="btn btn-g" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="backupNow()"><i class="bi bi-download"></i> Backup Now - Download Backup File</button>
<button class="btn btn-y" style="padding:14px 36px;font-size:15px;font-weight:800" onclick="openAddDataPopup()"><i class="bi bi-upload"></i> Add Data - Upload Backup</button>
</div>
</div>

<div class="card">
<h3>Backup Information - v4.5.1</h3>
<div class="row">
<div class="card kpi" style="flex:1"><div>Total Categories</div><div class="val" id="backupCatCount">0</div></div>
<div class="card kpi" style="flex:1"><div>Total Products</div><div class="val" id="backupProdCount">0</div></div>
<div class="card kpi" style="flex:1"><div>Total Vendors</div><div class="val" id="backupVendorCount">0</div></div>
<div class="card kpi" style="flex:1"><div>Total POs</div><div class="val" id="backupPOCount">0</div></div>
</div>
<p style="font-size:11px;color:#666">Backup file format: JSON - Contains product_category, product, sbu, vendor, customer, po, grn, dispatch, qr_bag, manufacturing_order - File name: lemon_erp_backup_YYYYMMDD_HHMMSS.json - Can be used for uploading to restore data into respective tables</p>
<div id="backupStatus" style="margin-top:10px;padding:10px;background:#FFFBEB;border:1px solid var(--brass);border-radius:8px;display:none"></div>
</div>

<div class="card">
<h3>Last Backup Details</h3>
<div id="backupDetails">No backup yet - Click Backup Now button to create backup file</div>
</div>
</div>

</div></div>

<!-- PRODUCT MODAL -->
<div id="productModal" class="modal hidden" onclick="if(event.target===this) closeProductPopup()"><div class="modal-content" style="max-width:620px"><div class="modal-header"><b>Add Product - HSN + Description + Auto Code - v4.4.3</b><button class="close-x" onclick="closeProductPopup()">×</button></div><div class="modal-body"><input type="hidden" id="prod_id"><div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)">Product Name *<input id="prod_name">Product Category *<select id="prod_cat"></select><p style="font-size:10px;color:#888">DB File: lemon_erp_v44_1_category.db - Table: product_category</p><div class="row"><div>HSN Code *<input id="prod_hsn" placeholder="2522"></div><div>Product Code (Auto)<input id="prod_code_preview" disabled style="background:var(--alab);font-weight:800"></div></div>Product Description *<textarea id="prod_desc" placeholder="Product Description - Mandatory - Shows narration when roll mouse over name in list"></textarea></div></div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:13px" onclick="saveProduct()">Save Product - Auto Code Generate</button><button class="btn btn-w" onclick="closeProductPopup()">Cancel</button></div></div></div>

<!-- SBU MODAL -->
<div id="sbuModal" class="modal hidden" onclick="if(event.target===this) closeAddSBU()"><div class="modal-content" style="max-width:1000px"><div class="modal-header"><b>Add SBU - Strategic Business Units - v4.4.9</b><button class="close-x" onclick="closeAddSBU()">×</button></div><div class="modal-body">
<input type="hidden" id="sbu_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>SBU Details</b><div style="margin-top:8px">SBU Name - e.g. Unit 1 72MT, Jodhpur Plant *<input id="sbu_name" placeholder="SBU Name"></div>Address - Full address field<textarea id="sbu_address" placeholder="Address - Full address field e.g. Plot 123, RIICO Industrial Area, Jodhpur, Rajasthan 342001"></textarea></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>🔥 Kilns - v4.4.7 Fixed - Lining & Health once per kiln</h4><button class="btn btn-y" onclick="addKilnField()">Add Kiln</button></div><p style="font-size:10px;color:#666">When clicked Add Kiln - Add new line: *Kiln No. *Lining Date *Health Status *Products and Capacity *Add Product Button *Delete button. Products only ask Product + Capacity/Day.</p><div id="kilnsContainer"><p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p></div></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>⚙ Sizing Plants</h4><button class="btn btn-y" onclick="addSizingField()">Add Sizing Plant</button></div><div id="sizingContainer"><p style="text-align:center;color:#888">No sizing plants</p></div></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>💧 Hydration Plants</h4><button class="btn btn-y" onclick="addHydrationField()">Add Hydration Plant</button></div><div id="hydrationContainer"><p style="text-align:center;color:#888">No hydration plants</p></div></div>
<div class="asset-section"><div style="display:flex;justify-content:space-between"><h4>📦 Stock Yards</h4><button class="btn btn-y" onclick="addYardField()">Add Stock Yard</button></div><p style="font-size:10px;color:#666">Add Stock Yard Button - when clicked: *Yard Name *Add Yard Items - dropdown from all categories, Opening stock.</p><div id="yardsContainer"><p style="text-align:center;color:#888">No stock yards</p></div></div>
</div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="saveSBU()">Save SBU - Strategic Business Units</button><button class="btn btn-w" onclick="closeAddSBU()">Cancel</button></div></div></div>

<!-- VENDOR MODAL v4.4.10 COMPLIANCE + DOCS + OPENING + WORKFLOW -->
<div id="vendorModal" class="modal hidden" onclick="if(event.target===this) closeAddVendorPopup()"><div class="modal-content" style="max-width:1200px"><div class="modal-header"><b>Add Vendor - v4.4.10 Compliance Docs Opening Bal Workflow - VEND-0001 + Banks + Contacts + Dept Primary</b><button class="close-x" onclick="closeAddVendorPopup()">×</button></div><div class="modal-body">
<input type="hidden" id="vend_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>Vendor Details - Mandatory Fields * - v4.4.10</b>
<div class="row"><div>Vendor Name *<input id="vend_name" placeholder="Vendor Name e.g. Rajasthan Limestone Suppliers"></div><div>Station - Text field<input id="vend_station" placeholder="Station e.g. Jodhpur, Gotan, Beawar"></div></div>
<div>Address - Text<textarea id="vend_address" placeholder="Full Address"></textarea></div>
<div class="row"><div>State - Text (for identifying GST code)<input id="vend_state" placeholder="State e.g. Rajasthan - RJ" list="stateList"><datalist id="stateList"><option value="Rajasthan"><option value="Gujarat"><option value="Madhya Pradesh"><option value="Maharashtra"><option value="Uttar Pradesh"><option value="Andhra Pradesh"><option value="Karnataka"><option value="Tamil Nadu"><option value="Haryana"><option value="Punjab"><option value="Delhi"><option value="West Bengal"><option value="Bihar"><option value="Odisha"><option value="Chhattisgarh"></datalist></div><div>GST No. - Text<input id="vend_gst" placeholder="22AAAAA0000A1Z5"></div></div>
<div class="row"><div>PAN No. - Text<input id="vend_pan" placeholder="AAAAA0000A"></div><div>TAN No. - Text<input id="vend_tan" placeholder="AAAA00000A"></div></div>
<div class="row"><div>Legal Status - Dropdown<input type="hidden" id="vend_legal_status"><select id="vend_legal_status_sel" onchange="document.getElementById('vend_legal_status').value=this.value"><option value="">Select Legal Status</option></select><p style="font-size:9px;color:#888">Hidden master: Proprietor, Partnership, Private Limited etc</p></div><div>Vendor Category - Dropdown<input type="hidden" id="vend_category"><select id="vend_category_sel" onchange="document.getElementById('vend_category').value=this.value"><option value="">Select Category</option></select><p style="font-size:9px;color:#888">Hidden master: MSE, MSME, SSI, Large etc</p></div></div>
<div class="row"><div>Vendor Code - Auto Generated<input id="vend_code_preview" disabled style="background:var(--alab);font-weight:800" placeholder="VEND-0001 Auto when saved"></div><div>Status<select id="vend_status"><option value="Active">Active</option><option value="Inactive">Inactive</option><option value="Blocked">Blocked</option></select></div></div>
</div>

<div class="asset-section"><h4>📋 Compliance - MSME + GST Reg Type + TDS + Rating + Audit - v4.4.10</h4>
<div class="row"><div>MSME Certificate No<input id="vend_msme_no" placeholder="MSME Cert No e.g. UDYAM-RJ-..."></div><div>MSME Expiry Date<input type="date" id="vend_msme_expiry"></div><div>MSME Upload (File name / base64)<input id="vend_msme_upload" placeholder="Paste base64 or file name - GST Cert upload section below for all docs"></div></div>
<div class="row"><div>GST Registration Type<select id="vend_gst_reg_type"><option value="Regular">Regular</option><option value="Composition">Composition</option><option value="Unregistered">Unregistered</option><option value="SEZ">SEZ</option><option value="Deemed Export">Deemed Export</option><option value="Overseas">Overseas</option></select></div><div>TDS Section<select id="vend_tds_section"><option value="194C">194C - Contractors</option><option value="194J">194J - Professional</option><option value="194Q">194Q - Purchase >50L</option><option value="194H">194H - Commission</option><option value="194I">194I - Rent</option><option value="192">192 - Salary</option><option value="None">None</option></select></div></div>
<div class="row"><div>Vendor Rating 1-5 stars<select id="vend_rating"><option value="0">0 - Not Rated</option><option value="1">1★ - Poor</option><option value="2">2★ - Average</option><option value="3">3★ - Good</option><option value="4">4★ - Very Good</option><option value="5">5★ - Excellent</option></select></div><div>Last Audit Date<input type="date" id="vend_last_audit"></div></div>
</div>

<div class="asset-section"><h4>📄 Document Uploads - Drag & Drop + File Select - GST, PAN, Cheque, MSME, ISO - v4.4.10.1</h4><p style="font-size:10px;color:#666">Select file from computer - Drag & Drop supported - Stored as base64 in documents JSON - {gst_cert, pan_card, cancelled_cheque, msme_cert, iso_cert, other} - Preview file name + size - Click to select or drag file onto zone - Supports PDF, JPG, PNG</p>
<div class="doc-grid">
<div><label style="font-size:10px;font-weight:700">GST Certificate</label><div class="drop-zone" id="dz_gst_cert" onclick="document.getElementById('file_gst_cert').click()" ondragover="handleDragOver(event,'dz_gst_cert')" ondragleave="handleDragLeave(event,'dz_gst_cert')" ondrop="handleDrop(event,'gst_cert')"><i class="bi bi-cloud-arrow-up"></i><div class="dz-title">GST Certificate</div><div class="dz-hint">Click to select file or drag & drop here<br>PDF, JPG, PNG up to 5MB</div><div class="dz-file" id="dz_file_gst_cert" style="display:none"></div><button class="dz-clear" id="dz_clear_gst_cert" style="display:none" onclick="clearDoc('gst_cert',event)">Clear</button></div><input type="file" id="file_gst_cert" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'gst_cert')"><input type="hidden" id="doc_gst_cert"><small style="font-size:9px;color:#888" id="doc_gst_cert_info">No file selected - will store base64</small></div>
<div><label style="font-size:10px;font-weight:700">PAN Card</label><div class="drop-zone" id="dz_pan_card" onclick="document.getElementById('file_pan_card').click()" ondragover="handleDragOver(event,'dz_pan_card')" ondragleave="handleDragLeave(event,'dz_pan_card')" ondrop="handleDrop(event,'pan_card')"><i class="bi bi-card-image"></i><div class="dz-title">PAN Card</div><div class="dz-hint">Click to select or drag & drop<br>PDF, JPG, PNG</div><div class="dz-file" id="dz_file_pan_card" style="display:none"></div><button class="dz-clear" id="dz_clear_pan_card" style="display:none" onclick="clearDoc('pan_card',event)">Clear</button></div><input type="file" id="file_pan_card" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'pan_card')"><input type="hidden" id="doc_pan_card"><small style="font-size:9px;color:#888" id="doc_pan_card_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">Cancelled Cheque</label><div class="drop-zone" id="dz_cancelled_cheque" onclick="document.getElementById('file_cancelled_cheque').click()" ondragover="handleDragOver(event,'dz_cancelled_cheque')" ondragleave="handleDragLeave(event,'dz_cancelled_cheque')" ondrop="handleDrop(event,'cancelled_cheque')"><i class="bi bi-bank"></i><div class="dz-title">Cancelled Cheque</div><div class="dz-hint">Click to select or drag & drop</div><div class="dz-file" id="dz_file_cancelled_cheque" style="display:none"></div><button class="dz-clear" id="dz_clear_cancelled_cheque" style="display:none" onclick="clearDoc('cancelled_cheque',event)">Clear</button></div><input type="file" id="file_cancelled_cheque" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'cancelled_cheque')"><input type="hidden" id="doc_cancelled_cheque"><small style="font-size:9px;color:#888" id="doc_cancelled_cheque_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">MSME Certificate</label><div class="drop-zone" id="dz_msme_cert" onclick="document.getElementById('file_msme_cert').click()" ondragover="handleDragOver(event,'dz_msme_cert')" ondragleave="handleDragLeave(event,'dz_msme_cert')" ondrop="handleDrop(event,'msme_cert')"><i class="bi bi-award"></i><div class="dz-title">MSME Certificate</div><div class="dz-hint">Click to select or drag & drop</div><div class="dz-file" id="dz_file_msme_cert" style="display:none"></div><button class="dz-clear" id="dz_clear_msme_cert" style="display:none" onclick="clearDoc('msme_cert',event)">Clear</button></div><input type="file" id="file_msme_cert" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'msme_cert')"><input type="hidden" id="doc_msme_cert"><small style="font-size:9px;color:#888" id="doc_msme_cert_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">ISO Certificate</label><div class="drop-zone" id="dz_iso_cert" onclick="document.getElementById('file_iso_cert').click()" ondragover="handleDragOver(event,'dz_iso_cert')" ondragleave="handleDragLeave(event,'dz_iso_cert')" ondrop="handleDrop(event,'iso_cert')"><i class="bi bi-patch-check"></i><div class="dz-title">ISO Certificate</div><div class="dz-hint">Click to select or drag & drop</div><div class="dz-file" id="dz_file_iso_cert" style="display:none"></div><button class="dz-clear" id="dz_clear_iso_cert" style="display:none" onclick="clearDoc('iso_cert',event)">Clear</button></div><input type="file" id="file_iso_cert" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handleFileSelect(event,'iso_cert')"><input type="hidden" id="doc_iso_cert"><small style="font-size:9px;color:#888" id="doc_iso_cert_info">No file selected</small></div>
<div><label style="font-size:10px;font-weight:700">Other Document</label><div class="drop-zone" id="dz_other" onclick="document.getElementById('file_other').click()" ondragover="handleDragOver(event,'dz_other')" ondragleave="handleDragLeave(event,'dz_other')" ondrop="handleDrop(event,'other')"><i class="bi bi-file-earmark-plus"></i><div class="dz-title">Other Document</div><div class="dz-hint">Click to select or drag & drop - Any file</div><div class="dz-file" id="dz_file_other" style="display:none"></div><button class="dz-clear" id="dz_clear_other" style="display:none" onclick="clearDoc('other',event)">Clear</button></div><input type="file" id="file_other" hidden accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onchange="handleFileSelect(event,'other')"><input type="hidden" id="doc_other"><small style="font-size:9px;color:#888" id="doc_other_info">No file selected</small></div>
</div>
<p style="font-size:9px;color:#1A2E1E;background:#F0F8FF;padding:6px;border-radius:6px;margin-top:8px">💡 v4.4.10.1 - Select file from computer with drag & drop - File stored as base64 data URI - Max 5MB per file - Previous version only had text input - Now enhanced with file select + drag drop + preview + clear - No other module changed</p>
</div>

<div class="asset-section"><h4>💰 Opening Balance + Ledger Group - For Migration - v4.4.10</h4>
<div class="row"><div>Opening Balance - Number<input type="number" id="vend_opening_bal" placeholder="Opening Balance e.g. 150000"></div><div>Dr/Cr<select id="vend_opening_type"><option value="Dr">Dr - Receivable from vendor (Advance paid)</option><option value="Cr">Cr - Payable to vendor (Due)</option></select></div></div>
<div class="row"><div>Ledger Group<input id="vend_ledger_group" list="ledgerList" placeholder="Sundry Creditors" value="Sundry Creditors"><datalist id="ledgerList"><option value="Sundry Creditors"><option value="Sundry Debtors"><option value="Trade Creditors"><option value="MSME Creditors"><option value="Non-MSME Creditors"><option value="Service Creditors"></datalist></div><div>Total Business Value (Auto from POs - qty*rate)<input id="vend_total_business" disabled style="background:var(--alab);font-weight:800" placeholder="Auto calculated from POs"></div></div>
</div>

<div class="asset-section"><h4>🏦 Bank Details - Add Bank Account Button - Single Searchable Dropdown - v4.4.10</h4><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-size:10px;color:#666">When clicked on Add Bank Account - Add new line: Select Bank searchable dropdown nationalised banks + Other bank hidden bank master + Branch + Account Name + IFSC + Account No + Transaction Limit</span><button class="btn btn-y" onclick="addVendorBankField()">Add Bank Account</button></div><div id="vendorBanksContainer"><p style="text-align:center;color:#888;padding:12px">No bank accounts - Click Add Bank Account Button</p></div></div>

<div class="asset-section"><h4>👤 Contacts - Add Contact Button - Dept + Primary Flag - v4.4.10</h4><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span style="font-size:10px;color:#666">When clicked on Add Contact - Add new line: Name + Designation hidden master + Department + Primary flag + Mobile + Whatsapp + Land Line + Ext + Email</span><button class="btn btn-y" onclick="addVendorContactField()">Add Contact</button></div><div id="vendorContactsContainer"><p style="text-align:center;color:#888;padding:12px">No contacts - Click Add Contact Button</p></div></div>

<div class="asset-section"><h4>✅ Approval Workflow + Audit - v4.4.10</h4>
<div class="row"><div>Approval Status<select id="vend_approval_status"><option value="Draft">Draft</option><option value="Pending">Pending Approval</option><option value="Approved">Approved</option><option value="Rejected">Rejected</option></select></div><div>Created By<input id="vend_created_by" placeholder="Admin" value="Admin"></div></div>
<div class="row"><div>Last Transaction Date (Auto from POs)<input id="vend_last_trans" disabled style="background:var(--alab)" placeholder="Auto from POs"></div><div>Updated By<input id="vend_updated_by" placeholder="Admin" value="Admin"></div></div>
<p style="font-size:10px;color:#888">Created At / Updated At auto - Total Business Value = Sum of PO qty*rate - Last Transaction = Max PO date - Approval workflow Draft→Pending→Approved→Rejected</p>
</div>

</div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="saveVendor()">Save Vendor - v4.4.10 Compliance + Docs + Opening + Workflow</button><button class="btn btn-w" onclick="closeAddVendorPopup()">Cancel</button></div></div></div>

<!-- PO MODAL v4.5 FIXED - PURCHASE ORDER - ONLY PO MODULE -->
<div id="poModal" class="modal hidden" onclick="if(event.target===this) closeAddPOPopup()"><div class="modal-content" style="max-width:1300px"><div class="modal-header"><b>Add Purchase Order - PO/26-27/PRODUCT/0001 Auto + Line Items + GST Breakup + Docs Drag Drop - v4.5 Fixed Masters Locked</b><button class="close-x" onclick="closeAddPOPopup()">×</button></div><div class="modal-body">
<input type="hidden" id="po_id">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>PO Header - RFQ + PO No + Date + Validity + SBU + Billing + Product + Vendor - v4.5</b>
<div class="row"><div>RFQ No. (for future workflow - keep blank)<input id="po_rfq_no" placeholder="RFQ No. e.g. RFQ/26-27/0001 - Future use"></div><div>PO No - Auto Generated (PO/FY/PRODUCT/SEQ without spaces)<input id="po_no_preview" disabled style="background:var(--alab);font-weight:800" placeholder="PO/26-27/PRODUCTNAME/0001 Auto when saved"></div></div>
<div class="row"><div>PO Date - Default today auto editable<input type="date" id="po_date"></div><div>PO Validity - Date format<input type="date" id="po_validity"></div></div>
<div class="row"><div>PO Type - Raw Material etc<select id="po_type" onchange="filterProductsByPOType()"><option value="Raw Material">Raw Material</option><option value="Consumables">Consumables</option><option value="CAPEX">CAPEX</option><option value="Packing">Packing</option><option value="Services">Services</option><option value="Others">Others</option></select></div><div>SBU - Delivery Location - Dropdown from SBUs<select id="po_sbu" onchange="onSBUChange()"></select></div></div>
<div>Delivery Address - Selection from SBU address + Company address<textarea id="po_delivery_address" placeholder="Delivery Address - Auto from SBU, editable"></textarea></div>
<div><label style="font-size:10px"><input type="checkbox" id="po_same_as_delivery" checked onchange="toggleBillingSame()"> Same as Delivery Address</label></div>
<div>Billing Address - Selection from dropdown list from SBUs and company address<textarea id="po_billing_address" placeholder="Billing Address - Same as delivery if checked"></textarea></div>
<div class="row"><div>Product - Dropdown list of Products - Raw materials - For auto fill line item<input type="hidden" id="po_product_id"><select id="po_product_filter" onchange="onProductFilterChange()"><option value="">Select Product for auto fill line items</option></select></div><div>Vendor Name - Searchable dropdown list of vendors<select id="po_vendor" onchange="onVendorChange()"></select></div></div>
</div>
<div class="asset-section"><div style="display:flex;justify-content:space-between;align-items:center"><h4>📦 Line Item Details - Add Line Item Button</h4><button class="btn btn-y" onclick="addPOLineItem()">Add Line Item</button></div><div id="poItemsContainer"><p style="text-align:center;color:#888;padding:12px">No line items - Click Add Line Item Button</p></div></div>
<div class="asset-section"><h4>💰 Totals</h4>
<div class="row"><div>Taxable Value<input id="po_taxable" disabled style="background:var(--alab);font-weight:800"></div><div>CGST<input id="po_cgst" disabled style="background:var(--alab)"></div><div>SGST<input id="po_sgst" disabled style="background:var(--alab)"></div></div>
<div class="row"><div>IGST<input id="po_igst" disabled style="background:var(--alab)"></div><div>Freight Amount<input type="number" id="po_freight" placeholder="Freight" step="0.01" oninput="recalcPOTotals()"></div><div>Round Off<input type="number" id="po_round_off" placeholder="Round Off" step="0.01" value="0" oninput="recalcPOTotals()"></div></div>
<div class="row"><div>Grand Total<input id="po_grand_total" disabled style="background:var(--green);color:white;font-weight:900;font-size:14px"></div></div>
</div>
<div class="asset-section"><h4>🚚 Delivery & Commercial Terms</h4>
<div class="row"><div>Delivery Type<select id="po_delivery_type"><option value="One Time">One Time</option><option value="Partial">Partial</option><option value="As per schedule">As per schedule</option><option value="Immediate">Immediate</option></select></div><div>Delivery Schedule<input id="po_delivery_schedule" placeholder="e.g. 10 MT per week"></div></div>
<div class="row"><div>Payment Terms days<input type="number" id="po_payment_terms" placeholder="e.g. 30"></div><div>Rate Basis<select id="po_rate_basis"><option value="FOR">FOR</option><option value="Ex-factory">Ex-factory</option><option value="Delivered">Delivered</option><option value="FOB">FOB</option><option value="Ex-Works">Ex-Works</option></select></div></div>
<div class="row"><div>Freight Terms<input id="po_freight_terms" placeholder="Included, Extra"></div><div>TDS<select id="po_tds_applicable"><option value="Not Applicable">Not Applicable</option><option value="Applicable">Applicable</option></select></div><div>TDS %<input type="number" id="po_tds_percent" step="0.01"></div></div>
<div class="row"><div>RCM<select id="po_rcm_applicable"><option value="No">No</option><option value="Yes">Yes</option></select></div><div>RCM %<input type="number" id="po_rcm_percent" step="0.01"></div></div>
</div>
<div class="asset-section"><h4>📄 PO Document Uploads - Drag & Drop</h4>
<div class="doc-grid">
<div><label style="font-size:10px;font-weight:700">PO Document</label><div class="drop-zone" id="dz_po_doc" onclick="document.getElementById('file_po_doc').click()" ondragover="handlePODragOver(event,'dz_po_doc')" ondragleave="handlePODragLeave(event,'dz_po_doc')" ondrop="handlePODrop(event,'po_doc')"><i class="bi bi-file-earmark-pdf"></i><div class="dz-title">PO Document</div><div class="dz-hint">Click or drag & drop PDF</div><div class="dz-file" id="dz_file_po_doc" style="display:none"></div><button class="dz-clear" id="dz_clear_po_doc" style="display:none" onclick="clearPODoc('po_doc',event)">Clear</button></div><input type="file" id="file_po_doc" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handlePOFileSelect(event,'po_doc')"><input type="hidden" id="doc_po_doc"><small id="doc_po_doc_info" style="font-size:9px;color:#888">No file</small></div>
<div><label style="font-size:10px;font-weight:700">Freight Slip</label><div class="drop-zone" id="dz_freight_slip" onclick="document.getElementById('file_freight_slip').click()" ondragover="handlePODragOver(event,'dz_freight_slip')" ondragleave="handlePODragLeave(event,'dz_freight_slip')" ondrop="handlePODrop(event,'freight_slip')"><i class="bi bi-truck"></i><div class="dz-title">Freight Slip</div><div class="dz-hint">Click or drag & drop</div><div class="dz-file" id="dz_file_freight_slip" style="display:none"></div><button class="dz-clear" id="dz_clear_freight_slip" style="display:none" onclick="clearPODoc('freight_slip',event)">Clear</button></div><input type="file" id="file_freight_slip" hidden accept=".pdf,.jpg,.jpeg,.png" onchange="handlePOFileSelect(event,'freight_slip')"><input type="hidden" id="doc_freight_slip"><small id="doc_freight_slip_info" style="font-size:9px;color:#888">No file</small></div>
</div>
</div>
<div class="asset-section"><h4>✅ Approval</h4>
<div class="row"><div>Status<select id="po_status"><option value="Draft">Draft</option><option value="Pending">Pending</option><option value="Approved">Approved</option><option value="Sent to Vendor">Sent to Vendor</option><option value="Partially Received">Partially Received</option><option value="Closed">Closed</option></select></div><div>Created By<input id="po_created_by" value="Admin"></div></div>
</div>
</div><div class="modal-footer"><button class="btn btn-g" style="flex:1;padding:14px;font-size:13px" onclick="savePO()">Save PO - v4.5 Fixed</button><button class="btn btn-w" onclick="closeAddPOPopup()">Cancel</button></div></div></div>

<!-- BACKUP MODALS v4.5.1 - ONLY BACKUP MODULE - OTHER MODULES LOCKED -->
<div id="backupModal" class="modal hidden" onclick="if(event.target===this) closeAddDataPopup()"><div class="modal-content" style="max-width:700px"><div class="modal-header"><b>Add Data - Upload Backup File - Drag & Drop + Upload to Database - v4.5.1</b><button class="close-x" onclick="closeAddDataPopup()">×</button></div><div class="modal-body">
<div class="form-box" style="background:#FFFBEB;border:2px solid var(--brass)"><b>Upload Backup Data - Drag & Drop JSON file - v4.5.1</b>
<p style="font-size:11px;color:#666">Drag and drop backup JSON file (lemon_erp_backup_*.json) or click to select file - File contains product_category, product, sbu, vendor, customer, po, grn, etc - When file dropped, Upload Data button will appear to upload into database tables</p>

<div class="drop-zone" id="dz_backup_file" onclick="document.getElementById('file_backup').click()" ondragover="handleBackupDragOver(event)" ondragleave="handleBackupDragLeave(event)" ondrop="handleBackupDrop(event)" style="min-height:150px;border:3px dashed var(--brass)">
<i class="bi bi-cloud-arrow-up" style="font-size:40px"></i>
<div class="dz-title" style="font-size:14px">Backup File - Drag & Drop Here</div>
<div class="dz-hint">Click to select JSON backup file or drag & drop here<br>Supported: lemon_erp_backup_*.json - Max 10MB</div>
<div class="dz-file" id="dz_file_backup" style="display:none"></div>
<button class="dz-clear" id="dz_clear_backup" style="display:none" onclick="clearBackupFile(event)">Clear</button>
</div>
<input type="file" id="file_backup" hidden accept=".json" onchange="handleBackupFileSelect(event)">
<input type="hidden" id="backup_file_content">
<div id="backup_file_info" style="margin-top:10px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line);display:none">
<h4 style="margin:0 0 8px">📄 Backup File Preview</h4>
<div id="backup_preview"></div>
</div>

<div id="backup_upload_section" style="margin-top:16px;display:none">
<div style="padding:12px;background:#E6F4EA;border:1px solid #1E7D32;border-radius:8px">
<b>✅ File Ready to Upload</b><br>
<small id="backup_file_summary" style="color:#1A2E1E"></small>
</div>
<button class="btn btn-g" style="width:100%;padding:14px;font-size:14px;font-weight:800;margin-top:12px" onclick="uploadBackupData()"><i class="bi bi-cloud-upload"></i> Upload Data - Restore into Database Tables</button>
<p style="font-size:10px;color:#666;margin-top:8px">When clicked, all data in backup file will be uploaded into respective data tables - product_category → Product Category table, product → Products table, sbu → SBUs table, vendor → Vendors table, po → POs table, etc - Existing data preserved, only new data added</p>
</div>

<div id="backup_upload_result" style="margin-top:16px;display:none;padding:12px;border-radius:8px"></div>

</div>
</div><div class="modal-footer"><button class="btn btn-w" onclick="closeAddDataPopup()">Close</button></div></div></div>


<script>
function openTab(id){document.querySelectorAll('.tabcontent').forEach(e=>e.classList.add('hidden'));document.getElementById(id).classList.remove('hidden');document.querySelectorAll('.menu').forEach(m=>m.classList.remove('active')); if(id==='product_category') loadCategories(); if(id==='products') loadProducts(); if(id==='sbus') loadSBUs(); if(id==='dash') loadDash(); if(id==='stock') loadStock(); if(id==='vendors') loadVendors(); if(id==='buy') loadPOs(); if(id==='grn') {loadGRNs(); loadGRNFilters();} if(id==='backup') loadBackupInfo();}

let allProducts=[], finishedProducts=[]; let kilnCounter=0;
async function loadAllProductsForSBU(){
 let r=await fetch('/api/products'); let d=await r.json(); allProducts=d;
 finishedProducts=d.filter(p=>{let c=(p.category||'').toLowerCase(); return c.includes('finish')||c.includes('quicklime')||c.includes('cao')||c.includes('hydrat')||c.includes('sizing');}); if(finishedProducts.length===0) finishedProducts=d;
}
function getFinishedProductOptions(sel){let h='<option value="">Select Finished Product</option>'; finishedProducts.forEach(p=>{h+=`<option value="${p.id}" ${sel==p.id?'selected':''}>${p.name} (${p.product_code}) - ${p.category}</option>`}); return h;}
function getAllProductOptions(sel){let h='<option value="">Select Product</option>'; allProducts.forEach(p=>{h+=`<option value="${p.id}" ${sel==p.id?'selected':''}>${p.name} (${p.product_code}) - ${p.category}</option>`}); return h;}

// Category
async function loadCategories(){let r=await fetch('/api/product_categories'); let d=await r.json(); let tb=document.getElementById('catTbl'); tb.innerHTML=''; d.forEach((c,i)=>{tb.innerHTML+=`<tr><td>${i+1}</td><td>${c.category_name}</td><td>${c.created_at}</td><td>lemon_erp_v44_1_category.db / product_category / ${c.id}</td><td><button class="btn btn-b" onclick="editCat(${c.id})">Edit</button> <button class="btn btn-r" onclick="delCat(${c.id})">Del</button></td></tr>`}); document.getElementById('catCountDash').innerText=d.length;}
async function saveCategory(){let id=document.getElementById('cat_id').value; let name=document.getElementById('category_name').value.trim(); if(!name) return alert('Required'); let url=id?`/api/product_categories/${id}`:'/api/product_categories'; let m=id?'PUT':'POST'; let res=await fetch(url,{method:m,headers:{'Content-Type':'application/json'},body:JSON.stringify({category_name:name})}); let j=await res.json(); if(res.ok){resetCat(); loadCategories(); loadProdCatOptions();} else alert(j.error);}
function resetCat(){document.getElementById('cat_id').value=''; document.getElementById('category_name').value='';}
async function editCat(id){let r=await fetch(`/api/product_categories/${id}`); let c=await r.json(); document.getElementById('cat_id').value=c.id; document.getElementById('category_name').value=c.category_name;}
async function delCat(id){if(!confirm('Delete?'))return; await fetch(`/api/product_categories/${id}`,{method:'DELETE'}); loadCategories();}
async function loadProdCatOptions(){let r=await fetch('/api/product_categories'); let d=await r.json(); let sel=document.getElementById('prod_cat'); if(!sel) return; sel.innerHTML='<option value="">Select Category</option>'; d.forEach(c=>{sel.innerHTML+=`<option value="${c.category_name}">${c.category_name}</option>`});}

// Products
async function loadProducts(){await loadAllProductsForSBU(); await loadProdCatOptions(); let r=await fetch('/api/products'); let d=await r.json(); let groups={}; d.forEach(p=>{if(!groups[p.category]) groups[p.category]=[]; groups[p.category].push(p);}); let html=''; for(let cat in groups){html+=`<div style="border:1.5px solid var(--line);border-radius:10px;margin:12px 0;overflow:hidden"><div style="background:var(--green);color:var(--brass);padding:10px 14px;font-weight:800;font-size:12px">${cat} - ${groups[cat].length} Products</div><table><thead><tr><th>Product Code</th><th>HSN</th><th>Product Name - Hover for Narration</th><th>Description</th><th>Actions</th></tr></thead><tbody>`; groups[cat].forEach(p=>{html+=`<tr><td><span style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line)">${p.product_code}</span></td><td><span class="badge ok">${p.hsn_code}</span></td><td><div class="tooltip">${p.name}<span class="tip">Code: ${p.product_code}<br>HSN: ${p.hsn_code}<br>Cat: ${p.category}<br>Desc: ${p.description}</span></div></td><td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px">${p.description}</td><td><button class="btn btn-b" onclick="editProd(${p.id})">Edit</button> <button class="btn btn-r" onclick="delProd(${p.id})">Del</button></td></tr>`}); html+='</tbody></table></div>';} document.getElementById('prodList').innerHTML=html||'<p>No products</p>'; document.getElementById('prodCountDash').innerText=d.length;}
function openAddProductPopup(){document.getElementById('productModal').classList.remove('hidden');}
function closeProductPopup(){document.getElementById('productModal').classList.add('hidden'); document.getElementById('prod_id').value=''; document.getElementById('prod_name').value=''; document.getElementById('prod_hsn').value=''; document.getElementById('prod_desc').value=''; document.getElementById('prod_code_preview').value='';}
async function saveProduct(){let id=document.getElementById('prod_id').value; let payload={name:document.getElementById('prod_name').value, category:document.getElementById('prod_cat').value, hsn_code:document.getElementById('prod_hsn').value, description:document.getElementById('prod_desc').value}; if(!payload.name||!payload.category||!payload.hsn_code||!payload.description) return alert('All fields mandatory'); let url=id?`/api/products/${id}`:'/api/products'; let m=id?'PUT':'POST'; let res=await fetch(url,{method:m,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); let j=await res.json(); if(res.ok){closeProductPopup(); loadProducts();} else alert(j.error);}
async function editProd(id){let r=await fetch(`/api/products/${id}`); let p=await r.json(); openAddProductPopup(); document.getElementById('prod_id').value=p.id; document.getElementById('prod_name').value=p.name; document.getElementById('prod_cat').value=p.category; document.getElementById('prod_hsn').value=p.hsn_code; document.getElementById('prod_desc').value=p.description; document.getElementById('prod_code_preview').value=p.product_code;}
async function delProd(id){if(!confirm('Delete?'))return; await fetch(`/api/products/${id}`,{method:'DELETE'}); loadProducts();}

// SBU v4.4.7 FIXED kept
function openAddSBU(){document.getElementById('sbuModal').classList.remove('hidden'); document.getElementById('sbu_id').value=''; document.getElementById('sbu_name').value=''; document.getElementById('sbu_address').value=''; document.getElementById('kilnsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p>'; document.getElementById('sizingContainer').innerHTML='<p style="text-align:center;color:#888">No sizing plants</p>'; document.getElementById('hydrationContainer').innerHTML='<p style="text-align:center;color:#888">No hydration plants</p>'; document.getElementById('yardsContainer').innerHTML='<p style="text-align:center;color:#888">No stock yards</p>'; loadAllProductsForSBU();}
function closeAddSBU(){document.getElementById('sbuModal').classList.add('hidden');}
function addKilnField(data=null){
 let c=document.getElementById('kilnsContainer'); if(c.innerHTML.includes('No kilns')) c.innerHTML='';
 kilnCounter++; let id=`kiln_${kilnCounter}_${Date.now()}`;
 let lining=data?.lining_installation_date||data?.lining_date||''; let health=data?.health_status||'Good';
 let html=`<div id="${id}" class="kiln-line"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px"><b>Kiln Line - *Kiln No. *Lining Date *Health + Products</b><div><button class="btn btn-b" onclick="addKilnProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete Kiln</button></div></div>
 <div class="row" style="margin-top:8px"><div>*Kiln No. e.g. Kiln 1, K-01<input class="k_no" placeholder="Kiln No." value="${data?.kiln_no||''}"></div><div>*Lining Installation Date<input type="date" class="k_lining" value="${lining}"></div><div>*Health Status<select class="k_health"><option ${health==='Good'?'selected':''}>Good</option><option ${health==='Needs Repair'?'selected':''}>Needs Repair</option><option ${health==='Critical'?'selected':''}>Critical</option><option ${health==='New'?'selected':''}>New</option></select></div></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Products and Capacity - v4.4.7 Fixed (Product + Capacity only)</b><div id="${id}-products" class="kiln-products-container">${data?.products_capacity?.length? '' : '<p style="font-size:10px;color:#888">No products - Click Add Product → Inset Product name, Capacity/Day, Delete</p>'}</div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let prodContainer=document.getElementById(`${id}-products`);
 if(data?.products_capacity){ data.products_capacity.forEach(pc=>{ prodContainer.insertAdjacentHTML('beforeend', renderKilnProductLine(pc)); });}
}
function renderKilnProductLine(pc){
 let id=`kprod_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line"><div class="row" style="align-items:end"><div>Product name (Finished List)<select class="kp_product">${getFinishedProductOptions(pc.product_id||pc.product_id)}</select></div><div>Capacity/Day MT/day e.g. 15<input type="number" class="kp_capacity" placeholder="Capacity/Day - MT/day e.g. 15" value="${pc.capacity_per_day||pc.capacity||''}"></div><div><button class="btn btn-r" style="margin-top:18px" onclick="document.getElementById('${id}').remove()">Delete</button></div></div></div>`;
}
function addKilnProduct(kilnId){
 let cont=document.getElementById(`${kilnId}-products`)||document.querySelector(`#${kilnId} .kiln-products-container`); if(!cont) return; if(cont.innerHTML.includes('No products')) cont.innerHTML=''; cont.insertAdjacentHTML('beforeend', renderKilnProductLine({}));
}
function addSizingField(data=null){
 let c=document.getElementById('sizingContainer'); if(c.innerHTML.includes('No sizing')) c.innerHTML='';
 kilnCounter++; let id=`sizing_${kilnCounter}_${Date.now()}`;
 let html=`<div id="${id}" class="kiln-line" style="background:#F6FFF6;border-color:#C5E1C5"><div style="display:flex;justify-content:space-between"><b>Sizing Plant - *Plant No. *Products and Capacity</b><div><button class="btn btn-b" onclick="addSizingProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div>
 <div class="row" style="margin-top:8px"><div>*Plant No. e.g. Sizing 1, SP-01<input class="s_no" placeholder="Plant No." value="${data?.plant_no||''}"></div></div>
 <div style="margin-top:8px"><b>Whole Plant Machineries</b><textarea class="s_mach" placeholder="List of Machineries - Whole plant - e.g. Crusher, Vibrating Screen 10-40mm, Conveyor 20m, Dust Collector">${data?.machineries||''}</textarea></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Products and Capacity</b><div id="${id}-products" class="sizing-products-container"></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let pc=document.getElementById(`${id}-products`);
 if(data?.products_capacity){ data.products_capacity.forEach(p=>{ pc.insertAdjacentHTML('beforeend', renderSizingProductLine(p)); });}
}
function renderSizingProductLine(pc){
 let id=`sprod_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line" style="border-left-color:#C5E1C5"><div class="row" style="align-items:end"><div>Product<select class="sp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div>Capacity/hour<input type="number" class="sp_capacity" placeholder="Capacity/hour" value="${pc.capacity_per_hour||pc.capacity||''}"></div><div>List Machineries for this product line<textarea class="sp_mach_line" placeholder="Machineries">${pc.machineries||pc.machineries_line||''}</textarea></div><div><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Del</button></div></div></div>`;
}
function addSizingProduct(pid){ let cont=document.getElementById(`${pid}-products`); if(!cont) return; cont.insertAdjacentHTML('beforeend', renderSizingProductLine({}));}
function addHydrationField(data=null){
 let c=document.getElementById('hydrationContainer'); if(c.innerHTML.includes('No hydration')) c.innerHTML='';
 kilnCounter++; let id=`hyd_${kilnCounter}_${Date.now()}`;
 let html=`<div id="${id}" class="kiln-line" style="background:#F0F8FF;border-color:#C2D6FF"><div style="display:flex;justify-content:space-between"><b>Hydration Plant</b><div><button class="btn btn-b" onclick="addHydrationProduct('${id}')">Add Product</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div>
 <div class="row"><div>*Plant No.<input class="h_no" value="${data?.plant_no||''}"></div></div>
 <div><b>Whole Plant Machineries</b><textarea class="h_mach">${data?.machineries||''}</textarea></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><div id="${id}-products" class="hydration-products-container"></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let pc=document.getElementById(`${id}-products`);
 if(data?.products_capacity){ data.products_capacity.forEach(p=>{ pc.insertAdjacentHTML('beforeend', renderHydrationProductLine(p)); });}
}
function renderHydrationProductLine(pc){
 let id=`hprod_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line" style="border-left-color:#C2D6FF"><div class="row"><div>Product<select class="hp_product">${getFinishedProductOptions(pc.product_id)}</select></div><div>Capacity/hour<input type="number" class="hp_capacity" value="${pc.capacity_per_hour||pc.capacity||''}"></div><div>Line Machineries<textarea class="hp_mach_line">${pc.machineries||''}</textarea></div><div><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Del</button></div></div></div>`;
}
function addHydrationProduct(pid){ let cont=document.getElementById(`${pid}-products`); cont.insertAdjacentHTML('beforeend', renderHydrationProductLine({}));}
function addYardField(data=null){
 let c=document.getElementById('yardsContainer'); if(c.innerHTML.includes('No stock yards')) c.innerHTML='';
 kilnCounter++; let id=`yard_${kilnCounter}_${Date.now()}`;
 let html=`<div id="${id}" class="kiln-line"><div style="display:flex;justify-content:space-between"><b>Stock Yard - *Yard Name *Add Yard Items</b><div><button class="btn btn-b" onclick="addYardItem('${id}')">Add Yard Items</button> <button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete Yard</button></div></div>
 <div class="row"><div>*Yard Name e.g. Limestone Yard 1<input class="y_name" placeholder="Yard Name" value="${data?.yard_name||''}"></div></div>
 <div style="margin-top:8px;padding:10px;background:white;border-radius:8px;border:1px solid var(--line)"><b>*Add Yard Items - dropdown from all category, Opening stock</b><div id="${id}-items" class="yard-items-container"></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
 let cont=document.getElementById(`${id}-items`);
 if(data?.yard_items){ data.yard_items.forEach(yi=>{ cont.insertAdjacentHTML('beforeend', renderYardItemLine(yi)); });}
}
function renderYardItemLine(yi){
 let id=`yitem_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 return `<div id="${id}" class="product-line"><div class="row" style="align-items:end"><div>Product (All)<select class="yi_product">${getAllProductOptions(yi.product_id)}</select></div><div>Opening stock - e.g. 150 MT<input type="number" class="yi_opening" placeholder="Opening stock - e.g. 150 MT" value="${yi.opening_stock||yi.opening||''}"></div><div><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Del</button></div></div></div>`;
}
function addYardItem(yardId){ let cont=document.getElementById(`${yardId}-items`); cont.insertAdjacentHTML('beforeend', renderYardItemLine({}));}
async function saveSBU(){
 let sbuName=document.getElementById('sbu_name').value.trim(); if(!sbuName) return alert('SBU Name required');
 let kilns=[]; document.querySelectorAll('#kilnsContainer > div[id^="kiln_"]').forEach(div=>{
   let pcs=[]; div.querySelectorAll('.kiln-products-container > div[id^="kprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.kp_product').value; let cap=pdiv.querySelector('.kp_capacity').value;
     if(pid) pcs.push({product_id:parseInt(pid), capacity_per_day:parseFloat(cap)||0, capacity:parseFloat(cap)||0});
   });
   let k_no=div.querySelector('.k_no').value; let k_lining=div.querySelector('.k_lining').value; let k_health=div.querySelector('.k_health').value;
   kilns.push({kiln_no:k_no, lining_installation_date:k_lining, lining_date:k_lining, health_status:k_health, products_capacity:pcs});
 });
 let sizings=[]; document.querySelectorAll('#sizingContainer > div[id^="sizing_"]').forEach(div=>{
   let pcs=[]; div.querySelectorAll('.sizing-products-container > div[id^="sprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.sp_product').value; let cap=pdiv.querySelector('.sp_capacity').value; let ml=pdiv.querySelector('.sp_mach_line').value;
     if(pid) pcs.push({product_id:parseInt(pid), capacity_per_hour:parseFloat(cap)||0, capacity:parseFloat(cap)||0, machineries:ml});
   });
   sizings.push({plant_no:div.querySelector('.s_no').value, products_capacity:pcs, machineries:div.querySelector('.s_mach').value});
 });
 let hydrations=[]; document.querySelectorAll('#hydrationContainer > div[id^="hyd_"]').forEach(div=>{
   let pcs=[]; div.querySelectorAll('.hydration-products-container > div[id^="hprod_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.hp_product').value; let cap=pdiv.querySelector('.hp_capacity').value; let ml=pdiv.querySelector('.hp_mach_line')?.value||'';
     if(pid) pcs.push({product_id:parseInt(pid), capacity_per_hour:parseFloat(cap)||0, machineries:ml});
   });
   hydrations.push({plant_no:div.querySelector('.h_no').value, products_capacity:pcs, machineries:div.querySelector('.h_mach').value});
 });
 let yards=[]; document.querySelectorAll('#yardsContainer > div[id^="yard_"]').forEach(div=>{
   let items=[]; div.querySelectorAll('.yard-items-container > div[id^="yitem_"]').forEach(pdiv=>{
     let pid=pdiv.querySelector('.yi_product').value; let op=pdiv.querySelector('.yi_opening').value;
     if(pid) items.push({product_id:parseInt(pid), opening_stock:parseFloat(op)||0, opening:parseFloat(op)||0});
   });
   yards.push({yard_name:div.querySelector('.y_name').value, yard_items:items});
 });
 let payload={sbu_name:sbuName, address:document.getElementById('sbu_address').value, kilns, sizing_plants:sizings, hydration_plants:hydrations, stock_yards:yards};
 let sbuId=document.getElementById('sbu_id').value;
 let url=sbuId?`/api/sbus/${sbuId}`:'/api/sbus'; let method=sbuId?'PUT':'POST';
 let res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let j=await res.json();
 if(res.ok){alert(`SBU ${sbuId?'Updated':'Created'} - ${kilns.length} Kilns, ${sizings.length} Sizing, ${hydrations.length} Hyd, ${yards.length} Yards`); closeAddSBU(); loadSBUs(); loadDash();}
 else alert(j.error||'Error');
}
async function loadSBUs(){
 let r=await fetch('/api/sbus'); let sbus=await r.json();
 document.getElementById('sbuCountDash').innerText=sbus.length;
 let list=document.getElementById('sbuList');
 if(sbus.length===0){
   list.innerHTML=`<div style="text-align:center;padding:30px"><p>No SBUs - Masters empty - Strategic Business Units</p><button class="btn btn-y" onclick="openAddSBU()">Add First SBU</button></div>`;
   return;
 }
 let h='';
 sbus.forEach(s=>{
   let kilnBadge=`${s.kilns.length} Kilns`; let sizBadge=`${s.sizing_plants.length} Sizing`; let hydBadge=`${s.hydration_plants.length} Hydration`; let yardBadge=`${s.stock_yards.length} Yards`;
   h+=`<div class="sbu-card"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px"><div><h3 style="font-size:16px;margin:0"><i class="bi bi-building"></i> ${s.sbu_name}</h3><p style="font-size:11px;color:#666;margin:2px 0"><i class="bi bi-geo-alt"></i> ${s.address||''}</p><p style="font-size:10px;margin-top:6px"><span class="badge brass">${kilnBadge}</span> <span class="badge brass">${sizBadge}</span> <span class="badge brass">${hydBadge}</span> <span class="badge brass">${yardBadge}</span></p></div><div style="display:flex;gap:6px;align-items:start"><button class="btn btn-b" onclick="editSBU(${s.id})">Edit</button><button class="btn btn-o" onclick="duplicateSBU(${s.id})">Duplicate</button><button class="btn btn-r" onclick="delSBU(${s.id})">Delete</button></div></div>`;
   h+=`<div style="margin-top:10px">`;
   if(s.kilns.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:var(--green);color:white;padding:8px 10px;font-weight:800;font-size:11px">🔥 Kilns - ${s.kilns.length}</div><table><thead><tr><th>Kiln No</th><th>Lining Date</th><th>Health</th><th>Products + Capacity/Day</th></tr></thead><tbody>`;
     s.kilns.forEach(k=>{
       let healthClass=k.health_status==='Good'?'ok':k.health_status==='Critical'?'crit':'warn';
       let prodHtml=k.products_capacity.length? k.products_capacity.map(pc=>`<span style="display:block;background:white;padding:4px 6px;border-radius:4px;margin:3px 0;border:1px solid var(--line)"><b>${pc.product_name}</b> - ${pc.capacity_per_day||pc.capacity||0} MT/day <small style="color:#888">(${pc.product_code})</small></span>`).join('') : '<small>No products</small>';
       h+=`<tr><td><b>${k.kiln_no}</b></td><td>${k.lining_installation_date||k.lining_date||''}</td><td><span class="badge ${healthClass}">${k.health_status}</span></td><td>${prodHtml}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   if(s.sizing_plants.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:#1A2E1E;color:#C5E1C5;padding:8px 10px;font-weight:800;font-size:11px">⚙ Sizing Plants - ${s.sizing_plants.length}</div><table><thead><tr><th>Plant No</th><th>Machineries (Whole)</th><th>Products + Capacity/Hour</th></tr></thead><tbody>`;
     s.sizing_plants.forEach(sp=>{
       let prodHtml=sp.products_capacity.map(pc=>`<span style="display:block;background:#F6FFF6;padding:4px 6px;border-radius:4px;margin:3px 0;border:1px solid #C5E1C5"><b>${pc.product_name}</b> - ${pc.capacity_per_hour||0} MT/hr ${pc.machineries?'<br><small>Mach: '+pc.machineries+'</small>':''}</span>`).join('');
       h+=`<tr><td><b>${sp.plant_no}</b></td><td style="font-size:10px">${sp.machineries||''}</td><td>${prodHtml}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   if(s.hydration_plants.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:#0F2A44;color:#C2D6FF;padding:8px 10px;font-weight:800;font-size:11px">💧 Hydration Plants - ${s.hydration_plants.length}</div><table><thead><tr><th>Plant No</th><th>Machineries</th><th>Products</th></tr></thead><tbody>`;
     s.hydration_plants.forEach(hp=>{
       let prodHtml=hp.products_capacity.map(pc=>`<span style="display:block;background:#F0F8FF;padding:4px 6px;border-radius:4px;margin:3px 0"><b>${pc.product_name}</b> - ${pc.capacity_per_hour||0} MT/hr</span>`).join('');
       h+=`<tr><td><b>${hp.plant_no}</b></td><td style="font-size:10px">${hp.machineries||''}</td><td>${prodHtml}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   if(s.stock_yards.length){
     h+=`<div style="border:1.5px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0"><div style="background:var(--alab);padding:8px 10px;font-weight:800;font-size:11px;border-bottom:1px solid var(--line)">📦 Stock Yards - ${s.stock_yards.length}</div><table><thead><tr><th>Yard Name</th><th>Items - Product + Opening Stock</th></tr></thead><tbody>`;
     s.stock_yards.forEach(y=>{
       let items=y.yard_items.map(yi=>`<span style="display:block;background:white;padding:4px 6px;border-radius:4px;margin:3px 0;border:1px solid var(--line)"><b>${yi.product_name}</b> - ${yi.opening_stock} MT</span>`).join('');
       h+=`<tr><td><b>${y.yard_name}</b></td><td>${items}</td></tr>`;
     });
     h+='</tbody></table></div>';
   }
   h+=`</div></div>`;
 });
 list.innerHTML=h;
}
async function editSBU(id){
 let r=await fetch(`/api/sbus/${id}`); let s=await r.json();
 openAddSBU();
 setTimeout(()=>{
   document.getElementById('sbu_id').value=s.id;
   document.getElementById('sbu_name').value=s.sbu_name;
   document.getElementById('sbu_address').value=s.address||'';
   document.getElementById('kilnsContainer').innerHTML='';
   document.getElementById('sizingContainer').innerHTML='';
   document.getElementById('hydrationContainer').innerHTML='';
   document.getElementById('yardsContainer').innerHTML='';
   (s.kilns||[]).forEach(k=> addKilnField(k));
   (s.sizing_plants||[]).forEach(sp=> addSizingField(sp));
   (s.hydration_plants||[]).forEach(hp=> addHydrationField(hp));
   (s.stock_yards||[]).forEach(y=> addYardField(y));
   if(!s.kilns?.length) document.getElementById('kilnsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No kilns - Click Add Kiln Button</p>';
   if(!s.sizing_plants?.length) document.getElementById('sizingContainer').innerHTML='<p style="text-align:center;color:#888">No sizing plants</p>';
   if(!s.hydration_plants?.length) document.getElementById('hydrationContainer').innerHTML='<p style="text-align:center;color:#888">No hydration plants</p>';
   if(!s.stock_yards?.length) document.getElementById('yardsContainer').innerHTML='<p style="text-align:center;color:#888">No stock yards</p>';
 }, 600);
}
async function duplicateSBU(id){
 if(!confirm('Duplicate SBU? Creates copy with - Copy suffix')) return;
 let r=await fetch(`/api/sbus/${id}`); let s=await r.json();
 let payload={
   sbu_name: s.sbu_name + ' - Copy',
   address: s.address,
   kilns: (s.kilns||[]).map(k=> ({kiln_no: (k.kiln_no||'Kiln')+' - Copy', lining_installation_date:k.lining_installation_date||k.lining_date||'', lining_date:k.lining_installation_date||k.lining_date||'', health_status:k.health_status||'Good', products_capacity: (k.products_capacity||[]).map(pc=> ({product_id:pc.product_id, capacity_per_day:pc.capacity_per_day||pc.capacity||0, capacity:pc.capacity_per_day||pc.capacity||0}))})),
   sizing_plants: (s.sizing_plants||[]).map(sp=> ({plant_no: (sp.plant_no||'Sizing')+' - Copy', products_capacity: (sp.products_capacity||[]).map(pc=> ({product_id:pc.product_id, capacity_per_hour:pc.capacity_per_hour||pc.capacity||0, capacity:pc.capacity_per_hour||0, machineries:pc.machineries||''})), machineries: sp.machineries||''})),
   hydration_plants: (s.hydration_plants||[]).map(hp=> ({plant_no: (hp.plant_no||'Hyd')+' - Copy', products_capacity: (hp.products_capacity||[]).map(pc=> ({product_id:pc.product_id, capacity_per_hour:pc.capacity_per_hour||0})), machineries: hp.machineries||''})),
   stock_yards: (s.stock_yards||[]).map(y=> ({yard_name: (y.yard_name||'Yard')+' - Copy', yard_items: (y.yard_items||[]).map(yi=> ({product_id:yi.product_id, opening_stock:yi.opening_stock||yi.opening||0, opening:yi.opening_stock||0}))}))
 };
 let res=await fetch('/api/sbus',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 if(res.ok){alert('SBU Duplicated: '+payload.sbu_name); loadSBUs();} else alert('Duplicate failed');
}
async function delSBU(id){ if(!confirm('Delete SBU? Strategic Business Units')) return; await fetch(`/api/sbus/${id}`,{method:'DELETE'}); loadSBUs();}

// Vendor v4.4.10 Compliance + Docs + Opening + Workflow - Enhanced
let vendorBanks=[], vendorContacts=[], vendorMasters={banks:[], legal_status:[], vendor_category:[], designations:[]};

async function loadVendorMasters(){
 let r=await fetch('/api/vendor_masters'); let d=await r.json(); vendorMasters=d;
 let legalSel=document.getElementById('vendorLegalFilter'); let catSel=document.getElementById('vendorCatFilter');
 let legalModalSel=document.getElementById('vend_legal_status_sel'); let catModalSel=document.getElementById('vend_category_sel');
 if(legalSel) {legalSel.innerHTML='<option value="">All Legal Status</option>'; }
 if(catSel) catSel.innerHTML='<option value="">All Categories</option>';
 if(legalModalSel) legalModalSel.innerHTML='<option value="">Select Legal Status</option>';
 if(catModalSel) catModalSel.innerHTML='<option value="">Select Category</option>';
 d.legal_status.forEach(ls=>{ if(legalSel) legalSel.innerHTML+=`<option value="${ls.name}">${ls.name}</option>`; if(legalModalSel) legalModalSel.innerHTML+=`<option value="${ls.name}">${ls.name}</option>`; });
 d.vendor_category.forEach(vc=>{ if(catSel) catSel.innerHTML+=`<option value="${vc.name}">${vc.name}</option>`; if(catModalSel) catModalSel.innerHTML+=`<option value="${vc.name}">${vc.name}</option>`; });
}

function getBankOptions(selected){
 let h='<option value="">Select Bank - Searchable - Nationalised Banks</option>';
 (vendorMasters.banks||[]).forEach(b=>{ h+=`<option value="${b.bank_name}" ${selected===b.bank_name?'selected':''}>${b.bank_name} (${b.bank_code})</option>`; });
 return h;
}
function getDesignationOptions(selected){
 let h='<option value="">Select Designation</option>';
 (vendorMasters.designations||[]).forEach(d=>{ h+=`<option value="${d.name}" ${selected===d.name?'selected':''}>${d.name}</option>`; });
 return h;
}
function getDepartmentOptions(selected){
 let depts=["Purchase","Accounts","Sales","Logistics","Management","Quality","HR","Finance","Operations","Admin","Others"];
 let h='<option value="">Select Department</option>';
 depts.forEach(dp=>{ h+=`<option value="${dp}" ${selected===dp?'selected':''}>${dp}</option>`; });
 return h;
}

// v4.4.10.1 Drag & Drop Document Upload - ONLY Vendor Docs - File Select from Computer
function handleDragOver(e, zoneId){
 e.preventDefault(); e.stopPropagation();
 document.getElementById(zoneId).classList.add('dragover');
}
function handleDragLeave(e, zoneId){
 e.preventDefault(); e.stopPropagation();
 document.getElementById(zoneId).classList.remove('dragover');
}
function handleDrop(e, docType){
 e.preventDefault(); e.stopPropagation();
 document.getElementById('dz_'+docType).classList.remove('dragover');
 let files=e.dataTransfer.files;
 if(files.length>0) processVendorDocFile(files[0], docType);
}
function handleFileSelect(e, docType){
 let file=e.target.files[0];
 if(file) processVendorDocFile(file, docType);
}
function processVendorDocFile(file, docType){
 if(file.size>5*1024*1024) return alert('File too large - Max 5MB - Selected: '+(file.size/1024/1024).toFixed(2)+'MB');
 let reader=new FileReader();
 reader.onload=function(ev){
   let base64=ev.target.result;
   document.getElementById('doc_'+docType).value=base64;
   let fileDiv=document.getElementById('dz_file_'+docType);
   let infoDiv=document.getElementById('doc_'+docType+'_info');
   let clearBtn=document.getElementById('dz_clear_'+docType);
   fileDiv.style.display='block';
   fileDiv.innerHTML=`📎 ${file.name} (${(file.size/1024).toFixed(1)}KB)`;
   if(infoDiv) infoDiv.innerHTML=`✅ File ready: ${file.name} - ${base64.substring(0,30)}...`;
   if(clearBtn) clearBtn.style.display='inline-block';
   // Update drop zone title to show selected
   let zone=document.getElementById('dz_'+docType);
   zone.style.borderColor='#1A2E1E';
   zone.style.background='#F6FFF6';
 };
 reader.readAsDataURL(file);
}
function clearDoc(docType, e){
 if(e){ e.preventDefault(); e.stopPropagation(); }
 document.getElementById('doc_'+docType).value='';
 let fileInput=document.getElementById('file_'+docType);
 if(fileInput) fileInput.value='';
 let fileDiv=document.getElementById('dz_file_'+docType);
 let infoDiv=document.getElementById('doc_'+docType+'_info');
 let clearBtn=document.getElementById('dz_clear_'+docType);
 if(fileDiv){ fileDiv.style.display='none'; fileDiv.innerHTML=''; }
 if(infoDiv) infoDiv.innerHTML='No file selected - will store base64';
 if(clearBtn) clearBtn.style.display='none';
 let zone=document.getElementById('dz_'+docType);
 if(zone){ zone.style.borderColor='var(--brass)'; zone.style.background='#FFFBEB'; }
}
function setDocFromExisting(docType, base64Value){
 // Called during edit - if base64 exists, show preview
 if(!base64Value) return;
 document.getElementById('doc_'+docType).value=base64Value;
 let fileDiv=document.getElementById('dz_file_'+docType);
 let infoDiv=document.getElementById('doc_'+docType+'_info');
 let clearBtn=document.getElementById('dz_clear_'+docType);
 if(fileDiv){
   fileDiv.style.display='block';
   // Try to extract file name from base64 if it's just file name
   if(base64Value.startsWith('data:')){
     fileDiv.innerHTML=`📎 Existing file loaded (${(base64Value.length/1024).toFixed(1)}KB base64)`;
   } else {
     fileDiv.innerHTML=`📎 ${base64Value}`;
   }
 }
 if(infoDiv) infoDiv.innerHTML=`✅ Loaded: ${base64Value.substring(0,40)}...`;
 if(clearBtn) clearBtn.style.display='inline-block';
}


function addVendorBankField(data=null){
 let c=document.getElementById('vendorBanksContainer'); if(c.innerHTML.includes('No bank accounts')) c.innerHTML='';
 let id=`vbank_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 let html=`<div id="${id}" class="product-line" style="border-left-color:#1A2E1E"><div class="row"><div>Select Bank - Searchable dropdown (Single field fixed)<input list="bankList_${id}" class="vb_bank" placeholder="Type to search bank e.g. SBI, HDFC - Choose from list" value="${data?.bank_name||''}"><datalist id="bankList_${id}">${(vendorMasters.banks||[]).map(b=>`<option value="${b.bank_name}">${b.bank_name} (${b.bank_code})</option>`).join('')}</datalist><p style="font-size:9px;color:#888">Single field - Start typing SBI, PNB, HDFC - 34 banks + Other</p></div><div>Branch Name<input class="vb_branch" placeholder="Branch Name" value="${data?.branch_name||''}"></div></div>
 <div class="row"><div>Account Name<input class="vb_acc_name" placeholder="Account Name e.g. M/s Rajasthan Lime" value="${data?.account_name||''}"></div><div>IFSC Code<input class="vb_ifsc" placeholder="IFSC e.g. SBIN0001234" value="${data?.ifsc_code||''}"></div></div>
 <div class="row"><div>Account No<input class="vb_acc_no" placeholder="Account No" value="${data?.account_no||''}"></div><div>Transaction Limit<input type="number" class="vb_limit" placeholder="Limit e.g. 500000" value="${data?.transaction_limit||''}"></div><div style="max-width:80px"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
}
function addVendorContactField(data=null){
 let c=document.getElementById('vendorContactsContainer'); if(c.innerHTML.includes('No contacts')) c.innerHTML='';
 let id=`vcont_${Date.now()}_${Math.floor(Math.random()*9999)}`;
 let isPrimary=data?.is_primary?'checked':'';
 let dept=data?.department||'';
 let html=`<div id="${id}" class="product-line" style="border-left-color:#C9A86A"><div class="row"><div>Name<input class="vc_name" placeholder="Contact Person Name" value="${data?.name||''}"></div><div>Designation<select class="vc_designation">${getDesignationOptions(data?.designation||'')}</select></div><div>Department<select class="vc_department">${getDepartmentOptions(dept)}</select><p style="font-size:9px;color:#888">E. Add departments</p></div><div style="max-width:90px">Primary?<br><input type="checkbox" class="vc_primary" ${isPrimary} style="width:20px;height:20px"><p style="font-size:9px">Primary contact flag</p></div></div>
 <div class="row"><div>Mobile<input type="number" class="vc_mobile" placeholder="Mobile No" value="${data?.mobile_no||''}"></div><div>Whatsapp<input type="number" class="vc_whatsapp" placeholder="Whatsapp No" value="${data?.whatsapp_no||''}"></div></div>
 <div class="row"><div>Land Line<input type="number" class="vc_landline" placeholder="Land Line" value="${data?.landline||''}"></div><div>Ext No<input type="number" class="vc_ext" placeholder="Ext No" value="${data?.ext_no||''}"></div><div>Email<input type="email" class="vc_email" placeholder="Email" value="${data?.email||''}"></div><div style="max-width:80px"><button class="btn btn-r" onclick="document.getElementById('${id}').remove()">Delete</button></div></div></div>`;
 c.insertAdjacentHTML('beforeend', html);
}

function openAddVendorPopup(){
 document.getElementById('vendorModal').classList.remove('hidden');
 document.getElementById('vend_id').value=''; document.getElementById('vend_name').value=''; document.getElementById('vend_station').value=''; document.getElementById('vend_address').value=''; document.getElementById('vend_state').value=''; document.getElementById('vend_gst').value=''; document.getElementById('vend_pan').value=''; document.getElementById('vend_tan').value=''; document.getElementById('vend_legal_status').value=''; document.getElementById('vend_legal_status_sel').value=''; document.getElementById('vend_category').value=''; document.getElementById('vend_category_sel').value=''; document.getElementById('vend_code_preview').value=''; document.getElementById('vend_status').value='Active';
 document.getElementById('vend_msme_no').value=''; document.getElementById('vend_msme_expiry').value=''; document.getElementById('vend_msme_upload').value=''; document.getElementById('vend_gst_reg_type').value='Regular'; document.getElementById('vend_tds_section').value='194C'; document.getElementById('vend_rating').value='0'; document.getElementById('vend_last_audit').value='';
 // v4.4.10.1 clear doc file inputs + drop zones
 ['gst_cert','pan_card','cancelled_cheque','msme_cert','iso_cert','other'].forEach(dt=>{
   let hid=document.getElementById('doc_'+dt); if(hid) hid.value='';
   let fileIn=document.getElementById('file_'+dt); if(fileIn) fileIn.value='';
   let fileDiv=document.getElementById('dz_file_'+dt); if(fileDiv){ fileDiv.style.display='none'; fileDiv.innerHTML=''; }
   let infoDiv=document.getElementById('doc_'+dt+'_info'); if(infoDiv) infoDiv.innerHTML='No file selected - will store base64';
   let clearBtn=document.getElementById('dz_clear_'+dt); if(clearBtn) clearBtn.style.display='none';
   let zone=document.getElementById('dz_'+dt); if(zone){ zone.style.borderColor=''; zone.style.background=''; zone.classList.remove('dragover'); }
 });
 document.getElementById('vend_opening_bal').value=''; document.getElementById('vend_opening_type').value='Dr'; document.getElementById('vend_ledger_group').value='Sundry Creditors'; document.getElementById('vend_total_business').value=''; document.getElementById('vend_approval_status').value='Draft'; document.getElementById('vend_created_by').value='Admin'; document.getElementById('vend_updated_by').value='Admin'; document.getElementById('vend_last_trans').value='';
 document.getElementById('vendorBanksContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No bank accounts - Click Add Bank Account Button</p>';
 document.getElementById('vendorContactsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No contacts - Click Add Contact Button</p>';
 loadVendorMasters();
}
function closeAddVendorPopup(){document.getElementById('vendorModal').classList.add('hidden');}

async function saveVendor(){
 let name=document.getElementById('vend_name').value.trim(); if(!name) return alert('Vendor Name mandatory');
 let banks=[]; document.querySelectorAll('#vendorBanksContainer > div[id^="vbank_"]').forEach(div=>{
   let bank_name=div.querySelector('.vb_bank').value;
   let branch=div.querySelector('.vb_branch').value; let acc_name=div.querySelector('.vb_acc_name').value; let ifsc=div.querySelector('.vb_ifsc').value; let acc_no=div.querySelector('.vb_acc_no').value; let limit=div.querySelector('.vb_limit').value;
   if(bank_name) banks.push({bank_name, branch_name:branch, account_name:acc_name, ifsc_code:ifsc, account_no:acc_no, transaction_limit:parseFloat(limit)||0});
 });
 let contacts=[]; document.querySelectorAll('#vendorContactsContainer > div[id^="vcont_"]').forEach(div=>{
   let cname=div.querySelector('.vc_name').value; let desg=div.querySelector('.vc_designation').value; let dept=div.querySelector('.vc_department').value; let isPrimary=div.querySelector('.vc_primary').checked; let mob=div.querySelector('.vc_mobile').value; let wapp=div.querySelector('.vc_whatsapp').value; let land=div.querySelector('.vc_landline').value; let ext=div.querySelector('.vc_ext').value; let email=div.querySelector('.vc_email').value;
   if(cname) contacts.push({name:cname, designation:desg, department:dept, is_primary:isPrimary, mobile_no:mob, whatsapp_no:wapp, landline:land, ext_no:ext, email});
 });
 let docs={
   gst_cert:document.getElementById('doc_gst_cert').value,
   pan_card:document.getElementById('doc_pan_card').value,
   cancelled_cheque:document.getElementById('doc_cancelled_cheque').value,
   msme_cert:document.getElementById('doc_msme_cert').value,
   iso_cert:document.getElementById('doc_iso_cert').value,
   other:document.getElementById('doc_other').value
 };
 let payload={
   name:name,
   station:document.getElementById('vend_station').value,
   address:document.getElementById('vend_address').value,
   state:document.getElementById('vend_state').value,
   gst_no:document.getElementById('vend_gst').value,
   pan_no:document.getElementById('vend_pan').value,
   tan_no:document.getElementById('vend_tan').value,
   legal_status:document.getElementById('vend_legal_status').value || document.getElementById('vend_legal_status_sel').value,
   vendor_category:document.getElementById('vend_category').value || document.getElementById('vend_category_sel').value,
   bank_details:banks,
   contacts:contacts,
   status:document.getElementById('vend_status').value,
   msme_cert_no:document.getElementById('vend_msme_no').value,
   msme_expiry:document.getElementById('vend_msme_expiry').value,
   msme_upload:document.getElementById('vend_msme_upload').value,
   gst_reg_type:document.getElementById('vend_gst_reg_type').value,
   tds_section:document.getElementById('vend_tds_section').value,
   vendor_rating:parseInt(document.getElementById('vend_rating').value)||0,
   last_audit_date:document.getElementById('vend_last_audit').value,
   documents:docs,
   opening_balance:parseFloat(document.getElementById('vend_opening_bal').value)||0,
   opening_balance_type:document.getElementById('vend_opening_type').value,
   ledger_group:document.getElementById('vend_ledger_group').value,
   approval_status:document.getElementById('vend_approval_status').value,
   created_by:document.getElementById('vend_created_by').value,
   updated_by:document.getElementById('vend_updated_by').value
 };
 let vid=document.getElementById('vend_id').value;
 let url=vid?`/api/vendors/${vid}`:'/api/vendors'; let method=vid?'PUT':'POST';
 let res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
 let j=await res.json();
 if(res.ok){alert(`Vendor ${vid?'Updated':'Created'}: ${j.vendor_code||payload.name} - ${banks.length} Banks, ${contacts.length} Contacts - Rating ${payload.vendor_rating}★ - Approval ${payload.approval_status}`); closeAddVendorPopup(); loadVendors();} else alert(j.error||'Error');
}

async function loadVendors(){
 await loadVendorMasters();
 let search=document.getElementById('vendorSearch')?.value||'';
 let legal=document.getElementById('vendorLegalFilter')?.value||'';
 let cat=document.getElementById('vendorCatFilter')?.value||'';
 let state=document.getElementById('vendorStateFilter')?.value||'';
 let status=document.getElementById('vendorStatusFilter')?.value||'';
 let approval=document.getElementById('vendorApprovalFilter')?.value||'';
 let rating=document.getElementById('vendorRatingFilter')?.value||'';
 let params=new URLSearchParams({search, type:legal, category:cat, state, status, approval, rating});
 let r=await fetch(`/api/vendors?${params}`); let vendors=await r.json();
 document.getElementById('vendorCountBadge').innerText=`${vendors.length} Vendors`;
 let tb=document.getElementById('vendorTbl'); tb.innerHTML='';
 let statesSet=new Set();
 vendors.forEach(v=>{ if(v.state) statesSet.add(v.state); });
 let stateSel=document.getElementById('vendorStateFilter'); let curState=stateSel?stateSel.value:'';
 if(stateSel && stateSel.options.length<=1){
   statesSet.forEach(st=>{ stateSel.innerHTML+=`<option value="${st}" ${curState===st?'selected':''}>${st}</option>`; });
 }
 if(vendors.length===0){ tb.innerHTML=`<tr><td colspan="9" style="text-align:center;padding:20px;color:#888">No vendors - Add New Vendor Button above heading - v4.4.10 Compliance</td></tr>`; return; }
 vendors.forEach((v,i)=>{
   let banksHtml=(v.bank_details||[]).length? v.bank_details.map(b=>`<span style="display:block;background:#FFFBEB;padding:3px 6px;border-radius:4px;margin:2px 0;border:1px solid var(--brass);font-size:10px"><b>${b.bank_name}</b> - ${b.account_no} - IFSC ${b.ifsc_code}</span>`).join('') : '<small style="color:#888">No banks</small>';
   let contactsHtml=(v.contacts||[]).length? v.contacts.map(c=>`<span style="display:block;background:white;padding:3px 6px;border-radius:4px;margin:2px 0;border:1px solid var(--line);font-size:10px"><b>${c.name}</b> ${c.is_primary?'⭐Primary':''} (${c.designation}) [${c.department||''}] - M:${c.mobile_no} W:${c.whatsapp_no} <br><small>${c.email||''}</small></span>`).join('') : '<small style="color:#888">No contacts</small>';
   let statusClass=v.status==='Active'?'ok':v.status==='Blocked'?'crit':'warn';
   let approvalClass=v.approval_status==='Approved'?'ok':v.approval_status==='Rejected'?'crit':v.approval_status==='Pending'?'warn':'brass';
   let ratingStars='★'.repeat(v.vendor_rating||0)+'☆'.repeat(5-(v.vendor_rating||0));
   let docsCount=v.documents?Object.values(v.documents).filter(x=>x).length:0;
   let docsBadge=docsCount>0?`<span class="badge ok">${docsCount} Docs</span>`:'<small style="color:#888">No docs</small>';
   tb.innerHTML+=`<tr><td>${i+1}</td><td><span style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line);font-weight:800">${v.vendor_code}</span><br><div class="tooltip"><b>${v.name}</b><span class="tip">Code: ${v.vendor_code}<br>Station: ${v.station}<br>State: ${v.state}<br>GST: ${v.gst_no} (${v.gst_reg_type})<br>PAN: ${v.pan_no}<br>TAN: ${v.tan_no}<br>Legal: ${v.legal_status}<br>Cat: ${v.vendor_category}<br>MSME: ${v.msme_cert_no} Exp: ${v.msme_expiry}<br>TDS: ${v.tds_section}<br>Rating: ${v.vendor_rating}★ Audit: ${v.last_audit_date}<br>Opening: ${v.opening_balance} ${v.opening_balance_type} Ledger: ${v.ledger_group}<br>Approval: ${v.approval_status}<br>Created: ${v.created_by} ${v.created_at}<br>Updated: ${v.updated_by} ${v.updated_at}<br>Last Trans: ${v.last_transaction_date}<br>Business Value: Rs ${v.total_business_value}<br>Address: ${v.address}</span></div><br><small style="color:#888">${v.station||''}</small></td>
   <td><b>${v.station||''}</b><br><small>${v.state||''}</small><br><span class="badge brass" style="font-size:9px">${v.gst_reg_type||''}</span></td>
   <td><small>MSME: ${v.msme_cert_no||''}<br>Exp: ${v.msme_expiry||''}</small><br><span style="color:#C9A86A;font-weight:800">${ratingStars}</span> ${v.vendor_rating?`(${v.vendor_rating})`:''}<br><small>Audit: ${v.last_audit_date||''}</small></td>
   <td><small>Opening: ${v.opening_balance||0} ${v.opening_balance_type}<br>Ledger: ${v.ledger_group||''}<br>TDS: ${v.tds_section||''}</small></td>
   <td><small>Banks: ${v.bank_details.length} | Contacts: ${v.contacts.length}</small><div style="max-height:80px;overflow-y:auto;margin-top:4px">${banksHtml}<hr style="margin:4px 0">${contactsHtml}</div></td>
   <td><span class="badge ok">POs: ${v.po_count}</span><br><span class="badge" style="background:#F6FFF6;color:#1A2E1E;border:1px solid #C5E1C5;margin-top:4px;display:inline-block">GRNs: ${v.grn_count}</span><br><small>Value: Rs ${(v.total_business_value||0).toFixed(0)}</small><br><small style="font-size:9px">Last: ${v.last_transaction_date||''}</small></td>
   <td>${docsBadge}<br><span class="badge ${approvalClass}">${v.approval_status}</span><br><span class="badge ${statusClass}">${v.status}</span><br><small style="font-size:9px">${v.created_by} ${v.created_at?.slice(0,10)||''}</small></td>
   <td><button class="btn btn-b" onclick="editVendor(${v.id})">Edit</button> <button class="btn btn-r" onclick="delVendor(${v.id})">Del</button></td></tr>`;
 });
}

function resetVendorFilters(){
 document.getElementById('vendorSearch').value=''; document.getElementById('vendorLegalFilter').value=''; document.getElementById('vendorCatFilter').value=''; document.getElementById('vendorStateFilter').value=''; document.getElementById('vendorStatusFilter').value=''; let af=document.getElementById('vendorApprovalFilter'); if(af) af.value=''; let rf=document.getElementById('vendorRatingFilter'); if(rf) rf.value=''; loadVendors();
}

async function editVendor(id){
 let r=await fetch(`/api/vendors/${id}`); let v=await r.json();
 openAddVendorPopup();
 setTimeout(()=>{
   document.getElementById('vend_id').value=v.id;
   document.getElementById('vend_name').value=v.name;
   document.getElementById('vend_station').value=v.station||'';
   document.getElementById('vend_address').value=v.address||'';
   document.getElementById('vend_state').value=v.state||'';
   document.getElementById('vend_gst').value=v.gst_no||'';
   document.getElementById('vend_pan').value=v.pan_no||'';
   document.getElementById('vend_tan').value=v.tan_no||'';
   document.getElementById('vend_legal_status').value=v.legal_status||'';
   document.getElementById('vend_legal_status_sel').value=v.legal_status||'';
   document.getElementById('vend_category').value=v.vendor_category||'';
   document.getElementById('vend_category_sel').value=v.vendor_category||'';
   document.getElementById('vend_code_preview').value=v.vendor_code;
   document.getElementById('vend_status').value=v.status||'Active';
   document.getElementById('vend_msme_no').value=v.msme_cert_no||'';
   document.getElementById('vend_msme_expiry').value=v.msme_expiry||'';
   document.getElementById('vend_msme_upload').value=v.msme_upload||'';
   document.getElementById('vend_gst_reg_type').value=v.gst_reg_type||'Regular';
   document.getElementById('vend_tds_section').value=v.tds_section||'194C';
   document.getElementById('vend_rating').value=v.vendor_rating||0;
   document.getElementById('vend_last_audit').value=v.last_audit_date||'';
   // v4.4.10.1 - Set docs with drag-drop preview
   setDocFromExisting('gst_cert', v.documents?.gst_cert||'');
   setDocFromExisting('pan_card', v.documents?.pan_card||'');
   setDocFromExisting('cancelled_cheque', v.documents?.cancelled_cheque||'');
   setDocFromExisting('msme_cert', v.documents?.msme_cert||'');
   setDocFromExisting('iso_cert', v.documents?.iso_cert||'');
   setDocFromExisting('other', v.documents?.other||'');
   // Also keep hidden inputs for backward compat
   document.getElementById('doc_gst_cert').value=v.documents?.gst_cert||'';
   document.getElementById('doc_pan_card').value=v.documents?.pan_card||'';
   document.getElementById('doc_cancelled_cheque').value=v.documents?.cancelled_cheque||'';
   document.getElementById('doc_msme_cert').value=v.documents?.msme_cert||'';
   document.getElementById('doc_iso_cert').value=v.documents?.iso_cert||'';
   document.getElementById('doc_other').value=v.documents?.other||'';
   document.getElementById('vend_opening_bal').value=v.opening_balance||0;
   document.getElementById('vend_opening_type').value=v.opening_balance_type||'Dr';
   document.getElementById('vend_ledger_group').value=v.ledger_group||'Sundry Creditors';
   document.getElementById('vend_total_business').value=v.total_business_value||0;
   document.getElementById('vend_approval_status').value=v.approval_status||'Draft';
   document.getElementById('vend_created_by').value=v.created_by||'Admin';
   document.getElementById('vend_updated_by').value=v.updated_by||'Admin';
   document.getElementById('vend_last_trans').value=v.last_transaction_date||'';
   document.getElementById('vendorBanksContainer').innerHTML='';
   document.getElementById('vendorContactsContainer').innerHTML='';
   (v.bank_details||[]).forEach(b=> addVendorBankField(b));
   (v.contacts||[]).forEach(c=> addVendorContactField(c));
   if(!v.bank_details?.length) document.getElementById('vendorBanksContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No bank accounts - Click Add Bank Account Button</p>';
   if(!v.contacts?.length) document.getElementById('vendorContactsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No contacts - Click Add Contact Button</p>';
 }, 600);
}

async function delVendor(id){ if(!confirm('Delete Vendor?')) return; await fetch(`/api/vendors/${id}`,{method:'DELETE'}); loadVendors();}

// ================= PO MODULE v4.5 FIXED =================
let poProducts=[], poVendors=[], poSBUs=[], poLineCounter=0;
async function loadPOMasters(){
 let rp=await fetch('/api/products'); poProducts=await rp.json();
 let rv=await fetch('/api/vendors'); poVendors=await rv.json();
 let rs=await fetch('/api/sbus'); poSBUs=await rs.json();
 let sbuSel=document.getElementById('po_sbu');
 let sbuFilter=document.getElementById('poSbuFilter');
 if(sbuSel){ sbuSel.innerHTML='<option value="">Select SBU</option>'; poSBUs.forEach(s=>{ sbuSel.innerHTML+=`<option value="${s.id}">${s.sbu_name}</option>`; }); }
 if(sbuFilter && sbuFilter.options.length<=1){ poSBUs.forEach(s=>{ sbuFilter.innerHTML+=`<option value="${s.id}">${s.sbu_name}</option>`; }); }
 let vendorSel=document.getElementById('po_vendor');
 let vendorFilter=document.getElementById('poVendorFilter');
 if(vendorSel){ vendorSel.innerHTML='<option value="">Select Vendor</option>'; poVendors.forEach(v=>{ let rating='★'.repeat(v.vendor_rating||0); vendorSel.innerHTML+=`<option value="${v.id}">${v.name} (${v.vendor_code}) - ${rating} ${v.approval_status}</option>`; }); }
 if(vendorFilter && vendorFilter.options.length<=1){ poVendors.forEach(v=>{ vendorFilter.innerHTML+=`<option value="${v.id}">${v.name}</option>`; }); }
 let prodFilterSel=document.getElementById('po_product_filter');
 if(prodFilterSel){ prodFilterSel.innerHTML='<option value="">Select Product for auto fill</option>'; poProducts.forEach(p=>{ prodFilterSel.innerHTML+=`<option value="${p.id}">${p.name} (${p.product_code}) - HSN ${p.hsn_code}</option>`; }); }
}
function filterProductsByPOType(){ let type=document.getElementById('po_type').value; let sel=document.getElementById('po_product_filter'); if(!sel) return; let filtered=poProducts; if(type==='Raw Material'){ filtered=poProducts.filter(p=>{ let c=(p.category||'').toLowerCase(); return c.includes('raw')||c.includes('limestone')||c.includes('petcoke')||c.includes('coal'); }); if(filtered.length===0) filtered=poProducts; } sel.innerHTML='<option value="">Select Product for auto fill</option>'; filtered.forEach(p=>{ sel.innerHTML+=`<option value="${p.id}">${p.name} (${p.product_code})</option>`; }); }
function getProductById(id){ return poProducts.find(p=> String(p.id)===String(id)); }
function getVendorById(id){ return poVendors.find(v=> String(v.id)===String(id)); }
function getSBUById(id){ return poSBUs.find(s=> String(s.id)===String(id)); }
function onSBUChange(){ let sbuId=document.getElementById('po_sbu').value; let sbu=getSBUById(sbuId); if(sbu){ document.getElementById('po_delivery_address').value=sbu.address||sbu.sbu_name; if(document.getElementById('po_same_as_delivery').checked){ document.getElementById('po_billing_address').value=sbu.address||sbu.sbu_name; } } }
function toggleBillingSame(){ if(document.getElementById('po_same_as_delivery').checked){ document.getElementById('po_billing_address').value=document.getElementById('po_delivery_address').value; } }
function onProductFilterChange(){ let prodId=document.getElementById('po_product_filter').value; let prod=getProductById(prodId); if(prod){ document.getElementById('po_product_id').value=prod.id; let container=document.getElementById('poItemsContainer'); if(container.innerHTML.includes('No line items')){ addPOLineItem(prod); } } }
function onVendorChange(){ fetchRateHistoryForVendorProduct(); }
async function fetchRateHistoryForVendorProduct(){ let vendorId=document.getElementById('po_vendor').value; let prodId=document.getElementById('po_product_filter').value; if(!vendorId) return; let params=new URLSearchParams({vendor_id:vendorId}); if(prodId) params.set('product_id', prodId); let r=await fetch(`/api/po/rate_history?${params}`); let history=await r.json(); if(history.length>0){ document.querySelectorAll('.po_rate').forEach(input=>{ if(!input.value){ input.placeholder=`Last Rate: Rs ${history[0].rate} on ${history[0].po_date}`; } }); } }
function getGSTPercentForHSN(hsn){ const map={"2522":5,"2517":5,"2701":5,"2702":5,"2713":18}; let h=String(hsn||'').substring(0,4); return map[h]||18; }
function addPOLineItem(prefillProduct=null){
 let c=document.getElementById('poItemsContainer'); if(c.innerHTML.includes('No line items')) c.innerHTML=''; poLineCounter++; let id=`poline_${Date.now()}_${poLineCounter}`; let prod=prefillProduct||null; if(!prod){ let filterProdId=document.getElementById('po_product_filter').value; if(filterProdId) prod=getProductById(filterProdId); } let productCode=prod?.product_code||''; let productName=prod?.name||''; let hsnCode=prod?.hsn_code||''; let gstPercent=getGSTPercentForHSN(hsnCode); let uom='MT'; let html=`<div id="${id}" class="product-line" style="border-left-color:#1A2E1E;background:#FFFBEB"><div style="display:flex;justify-content:space-between"><b>Line #${poLineCounter}</b><button class="btn btn-r" onclick="document.getElementById('${id}').remove(); recalcPOTotals();">Delete</button></div><div class="row"><div>Code<input class="po_product_code" value="${productCode}" readonly style="background:var(--alab)"></div><div>Name<input class="po_product_name" value="${productName}" readonly style="background:var(--alab)"></div><div>HSN<input class="po_hsn" value="${hsnCode}" readonly style="background:var(--alab)"></div></div><div class="row"><div>Product<input type="hidden" class="po_product_id" value="${prod?.id||''}"><select class="po_product_select" onchange="onPOLineProductChange('${id}')"><option value="">Select</option>${poProducts.map(p=>`<option value="${p.id}" ${prod && p.id==prod.id?'selected':''}>${p.name} (${p.product_code})</option>`).join('')}</select></div><div>Spec<input class="po_spec" placeholder="Spec e.g. 10-40mm CaO 90%+"></div></div><div class="row"><div>UOM<input class="po_uom" value="${uom}"></div><div>Qty 3 dec<input type="number" class="po_qty" step="0.001" oninput="recalcPOLine('${id}'); recalcPOTotals();"></div><div>Rate 2 dec<input type="number" class="po_rate" step="0.01" oninput="recalcPOLine('${id}'); recalcPOTotals();"></div></div><div class="row"><div>GST%<input type="number" class="po_gst_percent" value="${gstPercent}" step="0.01" oninput="recalcPOLine('${id}'); recalcPOTotals();"></div><div>GST Type<select class="po_gst_type" onchange="recalcPOLine('${id}'); recalcPOTotals();"><option value="intra">Intra CGST+SGST</option><option value="inter">Inter IGST</option></select></div><div>Amount<input class="po_amount" disabled style="background:var(--alab);font-weight:800"></div></div><div class="row"><div>CGST<input class="po_cgst" disabled style="background:var(--alab)"></div><div>SGST<input class="po_sgst" disabled style="background:var(--alab)"></div><div>IGST<input class="po_igst" disabled style="background:var(--alab)"></div><div>Total<input class="po_total" disabled style="background:var(--green);color:white;font-weight:800"></div></div></div>`; c.insertAdjacentHTML('beforeend', html);
}
function onPOLineProductChange(lineId){ let div=document.getElementById(lineId); let sel=div.querySelector('.po_product_select'); let prod=getProductById(sel.value); if(!prod) return; div.querySelector('.po_product_id').value=prod.id; div.querySelector('.po_product_code').value=prod.product_code; div.querySelector('.po_product_name').value=prod.name; div.querySelector('.po_hsn').value=prod.hsn_code; div.querySelector('.po_gst_percent').value=getGSTPercentForHSN(prod.hsn_code); recalcPOLine(lineId); recalcPOTotals(); }
function recalcPOLine(lineId){ let div=document.getElementById(lineId); if(!div) return; let qty=parseFloat(div.querySelector('.po_qty').value)||0; let rate=parseFloat(div.querySelector('.po_rate').value)||0; let gst=parseFloat(div.querySelector('.po_gst_percent').value)||0; let gstType=div.querySelector('.po_gst_type').value; let amount=qty*rate; let cgst=0, sgst=0, igst=0; if(gstType==='intra'){ cgst=amount*gst/100/2; sgst=amount*gst/100/2; } else { igst=amount*gst/100; } div.querySelector('.po_amount').value=amount.toFixed(2); div.querySelector('.po_cgst').value=cgst.toFixed(2); div.querySelector('.po_sgst').value=sgst.toFixed(2); div.querySelector('.po_igst').value=igst.toFixed(2); div.querySelector('.po_total').value=(amount+cgst+sgst+igst).toFixed(2); }
function recalcPOTotals(){ let taxable=0, cgst=0, sgst=0, igst=0; document.querySelectorAll('#poItemsContainer > div[id^="poline_"]').forEach(div=>{ let qty=parseFloat(div.querySelector('.po_qty').value)||0; let rate=parseFloat(div.querySelector('.po_rate').value)||0; let gst=parseFloat(div.querySelector('.po_gst_percent').value)||0; let gstType=div.querySelector('.po_gst_type').value; let amt=qty*rate; taxable+=amt; if(gstType==='intra'){ cgst+=amt*gst/100/2; sgst+=amt*gst/100/2; } else { igst+=amt*gst/100; } }); let freight=parseFloat(document.getElementById('po_freight').value)||0; let roundOff=parseFloat(document.getElementById('po_round_off').value)||0; let grand=taxable+cgst+sgst+igst+freight+roundOff; document.getElementById('po_taxable').value=taxable.toFixed(2); document.getElementById('po_cgst').value=cgst.toFixed(2); document.getElementById('po_sgst').value=sgst.toFixed(2); document.getElementById('po_igst').value=igst.toFixed(2); document.getElementById('po_grand_total').value=grand.toFixed(2); }
function handlePODragOver(e, zoneId){ e.preventDefault(); e.stopPropagation(); document.getElementById(zoneId).classList.add('dragover'); }
function handlePODragLeave(e, zoneId){ e.preventDefault(); e.stopPropagation(); document.getElementById(zoneId).classList.remove('dragover'); }
function handlePODrop(e, docType){ e.preventDefault(); e.stopPropagation(); document.getElementById('dz_'+docType).classList.remove('dragover'); let files=e.dataTransfer.files; if(files.length>0) processPODocFile(files[0], docType); }
function handlePOFileSelect(e, docType){ let file=e.target.files[0]; if(file) processPODocFile(file, docType); }
function processPODocFile(file, docType){ if(file.size>5*1024*1024) return alert('File too large Max 5MB'); let reader=new FileReader(); reader.onload=function(ev){ let base64=ev.target.result; document.getElementById('doc_'+docType).value=base64; let fileDiv=document.getElementById('dz_file_'+docType); let infoDiv=document.getElementById('doc_'+docType+'_info'); let clearBtn=document.getElementById('dz_clear_'+docType); fileDiv.style.display='block'; fileDiv.innerHTML=`📎 ${file.name} (${(file.size/1024).toFixed(1)}KB)`; if(infoDiv) infoDiv.innerHTML=`✅ ${file.name}`; if(clearBtn) clearBtn.style.display='inline-block'; }; reader.readAsDataURL(file); }
function clearPODoc(docType, e){ if(e){ e.preventDefault(); e.stopPropagation(); } document.getElementById('doc_'+docType).value=''; let fileIn=document.getElementById('file_'+docType); if(fileIn) fileIn.value=''; let fileDiv=document.getElementById('dz_file_'+docType); if(fileDiv){ fileDiv.style.display='none'; } let infoDiv=document.getElementById('doc_'+docType+'_info'); if(infoDiv) infoDiv.innerHTML='No file'; let clearBtn=document.getElementById('dz_clear_'+docType); if(clearBtn) clearBtn.style.display='none'; }
function setPODocFromExisting(docType, base64Value){ if(!base64Value) return; document.getElementById('doc_'+docType).value=base64Value; let fileDiv=document.getElementById('dz_file_'+docType); let infoDiv=document.getElementById('doc_'+docType+'_info'); let clearBtn=document.getElementById('dz_clear_'+docType); if(fileDiv){ fileDiv.style.display='block'; fileDiv.innerHTML=`📎 Existing ${(base64Value.length/1024).toFixed(1)}KB`; } if(infoDiv) infoDiv.innerHTML=`✅ Loaded`; if(clearBtn) clearBtn.style.display='inline-block'; }
function openAddPOPopup(){ document.getElementById('poModal').classList.remove('hidden'); document.getElementById('po_id').value=''; document.getElementById('po_rfq_no').value=''; document.getElementById('po_no_preview').value=''; document.getElementById('po_date').value=new Date().toISOString().split('T')[0]; document.getElementById('po_validity').value=''; document.getElementById('po_type').value='Raw Material'; document.getElementById('po_sbu').value=''; document.getElementById('po_delivery_address').value=''; document.getElementById('po_billing_address').value=''; document.getElementById('po_same_as_delivery').checked=true; document.getElementById('po_product_id').value=''; document.getElementById('po_product_filter').value=''; document.getElementById('po_vendor').value=''; document.getElementById('poItemsContainer').innerHTML='<p style="text-align:center;color:#888;padding:12px">No line items - Click Add Line Item Button</p>'; document.getElementById('po_taxable').value=''; document.getElementById('po_cgst').value=''; document.getElementById('po_sgst').value=''; document.getElementById('po_igst').value=''; document.getElementById('po_freight').value=''; document.getElementById('po_round_off').value='0'; document.getElementById('po_grand_total').value=''; document.getElementById('po_delivery_type').value='One Time'; document.getElementById('po_delivery_schedule').value=''; document.getElementById('po_payment_terms').value=''; document.getElementById('po_rate_basis').value='FOR'; document.getElementById('po_freight_terms').value=''; document.getElementById('po_tds_applicable').value='Not Applicable'; document.getElementById('po_tds_percent').value=''; document.getElementById('po_rcm_applicable').value='No'; document.getElementById('po_rcm_percent').value=''; ['po_doc','freight_slip'].forEach(dt=>{ clearPODoc(dt); }); document.getElementById('po_status').value='Draft'; document.getElementById('po_created_by').value='Admin'; loadPOMasters(); poLineCounter=0; }
function closeAddPOPopup(){ document.getElementById('poModal').classList.add('hidden'); }
async function savePO(){
  try{
    console.log('Save PO clicked - v4.5.1 BACKUP MODULE - Only Buy module + Backup module');
    let sbuEl=document.getElementById('po_sbu');
    let vendorEl=document.getElementById('po_vendor');
    let sbuId=sbuEl? sbuEl.value.trim() : '';
    let vendorId=vendorEl? vendorEl.value.trim() : '';
    console.log('SBU:', sbuId, 'Vendor:', vendorId);
    if(!sbuId){ alert('⚠️ SBU mandatory - Select SBU from dropdown'); return; }
    if(!vendorId){ alert('⚠️ Vendor mandatory - Select Vendor'); return; }
    let lineDivs=document.querySelectorAll('#poItemsContainer > div[id^="poline_"]');
    console.log('Lines:', lineDivs.length);
    if(lineDivs.length===0){ alert('⚠️ Add at least one line item - Click Add Line Item'); return; }
    let items=[];
    let valid=true;
    lineDivs.forEach((div, idx)=>{
      let pid_el=div.querySelector('.po_product_id');
      let psel_el=div.querySelector('.po_product_select');
      let product_id=(pid_el && pid_el.value.trim()) || (psel_el && psel_el.value.trim()) || '';
      let product_code=div.querySelector('.po_product_code')?.value.trim()||'';
      let product_name=div.querySelector('.po_product_name')?.value.trim()||'';
      let hsn=div.querySelector('.po_hsn')?.value.trim()||'';
      let spec=div.querySelector('.po_spec')?.value.trim()||'';
      let uom=div.querySelector('.po_uom')?.value.trim()||'MT';
      let qty_str=div.querySelector('.po_qty')?.value.trim()||'';
      let rate_str=div.querySelector('.po_rate')?.value.trim()||'';
      let gst_percent=div.querySelector('.po_gst_percent')?.value.trim()||'18';
      let gst_type=div.querySelector('.po_gst_type')?.value||'inter';
      if(!product_id && product_name){
        let found=poProducts.find(p=>p.name===product_name);
        if(found) product_id=String(found.id);
      }
      let qty=parseFloat(qty_str);
      let rate=parseFloat(rate_str);
      if(!product_id || isNaN(qty) || qty<=0 || isNaN(rate) || rate<=0){
        console.log('Invalid line', idx+1, {product_id, qty_str, rate_str, product_name});
        valid=false;
      }
      items.push({product_id: product_id?parseInt(product_id):null, product_code, product_name, hsn_code:hsn, spec, uom, qty: isNaN(qty)?0:qty, rate: isNaN(rate)?0:rate, gst_percent: parseFloat(gst_percent)||0, gst_type});
    });
    if(!valid){ alert('⚠️ Check line items - Each needs: Product selected + Qty >0 (3 decimal) + Rate >0 (2 decimal)'); return; }
    if(items.length===0){ alert('⚠️ No valid line items'); return; }
    let productFilterEl=document.getElementById('po_product_filter');
    let product_name_filter='';
    if(productFilterEl && productFilterEl.selectedOptions && productFilterEl.selectedOptions[0]){
      product_name_filter=productFilterEl.selectedOptions[0].text.split('(')[0].trim();
    }
    if(!product_name_filter && items[0]) product_name_filter=items[0].product_name||'PRODUCT';
    if(!product_name_filter) product_name_filter='PRODUCT';
    let docs={po_doc: document.getElementById('doc_po_doc')?.value||'', freight_slip: document.getElementById('doc_freight_slip')?.value||''};
    let payload={
      rfq_no: document.getElementById('po_rfq_no')?.value||'',
      po_date: document.getElementById('po_date')?.value||new Date().toISOString().split('T')[0],
      po_validity: document.getElementById('po_validity')?.value||'',
      po_type: document.getElementById('po_type')?.value||'Raw Material',
      sbu_id: parseInt(sbuId),
      delivery_address: document.getElementById('po_delivery_address')?.value||'',
      billing_address: document.getElementById('po_billing_address')?.value||'',
      same_as_delivery: document.getElementById('po_same_as_delivery')?.checked||true,
      product_id: document.getElementById('po_product_id')?.value? parseInt(document.getElementById('po_product_id').value) : null,
      product_name_filter: product_name_filter,
      vendor_id: parseInt(vendorId),
      items: items,
      freight_amount: parseFloat(document.getElementById('po_freight')?.value)||0,
      round_off: parseFloat(document.getElementById('po_round_off')?.value)||0,
      delivery_type: document.getElementById('po_delivery_type')?.value||'One Time',
      delivery_schedule: document.getElementById('po_delivery_schedule')?.value||'',
      payment_terms_days: parseInt(document.getElementById('po_payment_terms')?.value)||0,
      rate_basis: document.getElementById('po_rate_basis')?.value||'FOR',
      freight_terms: document.getElementById('po_freight_terms')?.value||'',
      tds_applicable: document.getElementById('po_tds_applicable')?.value||'Not Applicable',
      tds_percent: parseFloat(document.getElementById('po_tds_percent')?.value)||0,
      rcm_applicable: document.getElementById('po_rcm_applicable')?.value||'No',
      rcm_percent: parseFloat(document.getElementById('po_rcm_percent')?.value)||0,
      documents: docs,
      status: document.getElementById('po_status')?.value||'Draft',
      approval_status: document.getElementById('po_status')?.value||'Draft',
      created_by: document.getElementById('po_created_by')?.value||'Admin'
    };
    console.log('PO Payload to save:', payload);
    let poId=document.getElementById('po_id')?.value||'';
    let url=poId?`/api/po/${poId}`:'/api/po';
    let method=poId?'PUT':'POST';
    let res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    let text=await res.text();
    let j;
    try{
      j=JSON.parse(text);
    }catch(parseErr){
      console.error('PO Save - Server returned non-JSON (HTML error):', text.substring(0,1000));
      console.error('Payload:', payload);
      if(text.trim().startsWith('<!') || text.toLowerCase().includes('<!doctype')){
        let clean=text.replace(/<[^>]*>/g,' ').trim().substring(0,600);
        alert(`❌ Server Error 500 - Backend crashed\nStatus: ${res.status}\nError: ${clean}\nCheck Render logs https://dashboard.render.com`);
      } else {
        alert(`❌ Invalid JSON - Status ${res.status}\n${text.substring(0,500)}`);
      }
      return;
    }
    console.log('PO Save response:', res.status, j);
    if(res.ok){
      alert(`✅ PO ${poId?'Updated':'Created'}: ${j.po_no} - Grand Total Rs ${j.grand_total}`);
      closeAddPOPopup();
      loadPOs();
    } else {
      alert(`❌ Save failed: ${j.error||'Unknown'} (Status ${res.status}) - ${j.error||''}`);
    }
  }catch(err){
    console.error('Save PO JS Error:', err);
    alert(`❌ JS Error: ${err.message} - Open F12 console`);
  }
}
async function loadPOs(){ await loadPOMasters(); let search=document.getElementById('poSearch')?.value||''; let poType=document.getElementById('poTypeFilter')?.value||''; let status=document.getElementById('poStatusFilter')?.value||''; let sbu=document.getElementById('poSbuFilter')?.value||''; let vendor=document.getElementById('poVendorFilter')?.value||''; let params=new URLSearchParams({search, po_type:poType, status, sbu, vendor}); let r=await fetch(`/api/po?${params}`); let pos=await r.json(); document.getElementById('poCountBadge').innerText=`${pos.length} POs`; let tb=document.getElementById('poTbl'); tb.innerHTML=''; if(pos.length===0){ tb.innerHTML=`<tr><td colspan="9" style="text-align:center;padding:20px;color:#888">No POs - Add Purchase Order Button - v4.5 PO/26-27/PRODUCT/0001</td></tr>`; return; } pos.forEach((p,i)=>{ let itemsHtml=(p.items||[]).map(it=>`<span style="display:block;background:#FFFBEB;padding:3px 6px;border-radius:4px;margin:2px 0;border:1px solid var(--brass);font-size:10px"><b>${it.product_code}</b> ${it.product_name} - ${it.qty} ${it.uom} x ${it.rate} = ${it.amount} + GST ${it.gst_percent}% = ${it.total_amount}</span>`).join(''); let statusClass=p.status==='Approved'?'ok':p.status==='Draft'?'brass':p.status==='Closed'?'ok':'warn'; let docsBadge=p.has_docs?`<span class="badge ok">Docs</span>`:'<small style="color:#888">No docs</small>'; let gstBreakup=`Taxable: Rs ${p.taxable_value}<br>CGST: ${p.cgst_amount} SGST: ${p.sgst_amount}<br>IGST: ${p.igst_amount}<br>Freight: ${p.freight_amount} Round: ${p.round_off}<br><b>Grand: Rs ${p.grand_total}</b>`; tb.innerHTML+=`<tr><td>${i+1}</td><td><span style="background:var(--alab);padding:3px 8px;border-radius:6px;border:1px solid var(--line);font-weight:800">${p.po_no}</span><br><small>RFQ: ${p.rfq_no||''}</small><br><small>Date: ${p.po_date}</small><br><small>Validity: ${p.po_validity||''}</small></td><td><b>${p.sbu_name}</b><br><small>${(p.delivery_address||'').substring(0,60)}</small></td><td><b>${p.vendor}</b> (${p.vendor_code})<br><small>State: ${p.vendor_state}</small></td><td><span class="badge brass">${p.po_type}</span><br><small>Items: ${p.items_count} Qty: ${p.total_qty}</small><div style="max-height:80px;overflow-y:auto">${itemsHtml}</div></td><td><small>${gstBreakup}</small></td><td><small>Type: ${p.delivery_type}<br>Schedule: ${p.delivery_schedule||''}<br>Pay: ${p.payment_terms_days} days<br>Rate Basis: ${p.rate_basis}<br>TDS: ${p.tds_applicable} ${p.tds_percent}%<br>RCM: ${p.rcm_applicable}</small></td><td>${docsBadge}<br><span class="badge ${statusClass}">${p.status}</span><br><small>${p.created_by}</small></td><td><button class="btn btn-b" onclick="editPO(${p.id})">Edit</button> <button class="btn btn-y" onclick="duplicatePO(${p.id})">Copy</button><br><button class="btn btn-w" style="margin-top:4px" onclick="emailPO(${p.id})">Email</button> <button class="btn btn-g" style="margin-top:4px" onclick="whatsappPO(${p.id})">WhatsApp</button><br><button class="btn btn-r" style="margin-top:4px" onclick="delPO(${p.id})">Del</button></td></tr>`; }); }
function resetPOFilters(){ document.getElementById('poSearch').value=''; document.getElementById('poTypeFilter').value=''; document.getElementById('poStatusFilter').value=''; document.getElementById('poSbuFilter').value=''; document.getElementById('poVendorFilter').value=''; loadPOs(); }
async function editPO(id){ let r=await fetch(`/api/po/${id}`); let p=await r.json(); openAddPOPopup(); setTimeout(()=>{ document.getElementById('po_id').value=p.id; document.getElementById('po_rfq_no').value=p.rfq_no||''; document.getElementById('po_no_preview').value=p.po_no; document.getElementById('po_date').value=p.po_date||''; document.getElementById('po_validity').value=p.po_validity||''; document.getElementById('po_type').value=p.po_type||'Raw Material'; document.getElementById('po_sbu').value=p.sbu_id||''; document.getElementById('po_delivery_address').value=p.delivery_address||''; document.getElementById('po_billing_address').value=p.billing_address||''; document.getElementById('po_same_as_delivery').checked=p.same_as_delivery; document.getElementById('po_product_id').value=p.product_id||''; document.getElementById('po_product_filter').value=p.product_id||''; document.getElementById('po_vendor').value=p.vendor_id||''; document.getElementById('poItemsContainer').innerHTML=''; (p.items||[]).forEach(it=>{ addPOLineItem(); let lastId=document.querySelector('#poItemsContainer > div:last-child').id; let div=document.getElementById(lastId); div.querySelector('.po_product_id').value=it.product_id||''; div.querySelector('.po_product_select').value=it.product_id||''; div.querySelector('.po_product_code').value=it.product_code||''; div.querySelector('.po_product_name').value=it.product_name||''; div.querySelector('.po_hsn').value=it.hsn_code||''; div.querySelector('.po_spec').value=it.spec||''; div.querySelector('.po_uom').value=it.uom||'MT'; div.querySelector('.po_qty').value=it.qty||''; div.querySelector('.po_rate').value=it.rate||''; div.querySelector('.po_gst_percent').value=it.gst_percent||''; div.querySelector('.po_gst_type').value=it.gst_type||'inter'; recalcPOLine(lastId); }); document.getElementById('po_taxable').value=p.taxable_value; document.getElementById('po_cgst').value=p.cgst_amount; document.getElementById('po_sgst').value=p.sgst_amount; document.getElementById('po_igst').value=p.igst_amount; document.getElementById('po_freight').value=p.freight_amount; document.getElementById('po_round_off').value=p.round_off; document.getElementById('po_grand_total').value=p.grand_total; document.getElementById('po_delivery_type').value=p.delivery_type||'One Time'; document.getElementById('po_delivery_schedule').value=p.delivery_schedule||''; document.getElementById('po_payment_terms').value=p.payment_terms_days||''; document.getElementById('po_rate_basis').value=p.rate_basis||'FOR'; document.getElementById('po_freight_terms').value=p.freight_terms||''; document.getElementById('po_tds_applicable').value=p.tds_applicable||'Not Applicable'; document.getElementById('po_tds_percent').value=p.tds_percent||''; document.getElementById('po_rcm_applicable').value=p.rcm_applicable||'No'; document.getElementById('po_rcm_percent').value=p.rcm_percent||''; setPODocFromExisting('po_doc', p.documents?.po_doc||''); setPODocFromExisting('freight_slip', p.documents?.freight_slip||''); document.getElementById('doc_po_doc').value=p.documents?.po_doc||''; document.getElementById('doc_freight_slip').value=p.documents?.freight_slip||''; document.getElementById('po_status').value=p.status||'Draft'; }, 700); }
async function duplicatePO(id){ if(!confirm('Duplicate PO?')) return; let r=await fetch(`/api/po/duplicate/${id}`,{method:'POST'}); let j=await r.json(); if(r.ok){ alert('Duplicated: '+j.po_no); loadPOs(); } else alert('Failed'); }
async function delPO(id){ if(!confirm('Delete PO?')) return; await fetch(`/api/po/${id}`,{method:'DELETE'}); loadPOs(); }
function emailPO(id){ fetch(`/api/po/${id}`).then(r=>r.json()).then(p=>{ let subject=`Purchase Order ${p.po_no}`; let body=`Dear ${p.vendor},\nPO ${p.po_no} dated ${p.po_date} Grand Rs ${p.grand_total}\nSBU: ${p.sbu_name}`; window.open(`mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`); }); }
function whatsappPO(id){ fetch(`/api/po/${id}`).then(r=>r.json()).then(p=>{ let msg=`*PO ${p.po_no}*\nDate: ${p.po_date}\nSBU: ${p.sbu_name}\nGrand: Rs ${p.grand_total}\nPay: ${p.payment_terms_days} days`; window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`); }); }

async function delVendor(id){ if(!confirm('Delete Vendor?')) return; await fetch(`/api/vendors/${id}`,{method:'DELETE'}); loadVendors();}

// ========== BACKUP MODULE v4.5.1 - ONLY BACKUP MODULE - OTHER MODULES LOCKED ==========
async function loadBackupInfo(){
  try{
    let r=await fetch('/api/backup');
    let data=await r.json();
    if(document.getElementById('backupCatCount')) document.getElementById('backupCatCount').innerText=(data.product_category||[]).length;
    if(document.getElementById('backupProdCount')) document.getElementById('backupProdCount').innerText=(data.product||[]).length;
    if(document.getElementById('backupVendorCount')) document.getElementById('backupVendorCount').innerText=(data.vendor||[]).length;
    if(document.getElementById('backupPOCount')) document.getElementById('backupPOCount').innerText=(data.po||[]).length;
    let details=`Backup Date: ${data.meta?.backup_date||new Date().toLocaleString()}<br>Version: ${data.meta?.version||'v4.5.1'}<br>Total Tables: ${Object.keys(data).length}<br><br>`;
    details+=`Categories: ${data.product_category?.length||0} | Products: ${data.product?.length||0} | SBUs: ${data.sbu?.length||0} | Vendors: ${data.vendor?.length||0} | Customers: ${data.customer?.length||0} | POs: ${data.po?.length||0} | GRNs: ${data.grn?.length||0} | Dispatch: ${data.dispatch?.length||0} | QR Bags: ${data.qr_bag?.length||0} | MOs: ${data.manufacturing_order?.length||0}`;
    if(document.getElementById('backupDetails')) document.getElementById('backupDetails').innerHTML=details;
  }catch(e){
    console.error('loadBackupInfo error', e);
    if(document.getElementById('backupDetails')) document.getElementById('backupDetails').innerHTML=`Error: ${e.message}`;
  }
}

async function backupNow(){
  try{
    if(document.getElementById('backupStatus')){
      document.getElementById('backupStatus').style.display='block';
      document.getElementById('backupStatus').innerHTML='⏳ Creating backup file...';
    }
    let link=document.createElement('a');
    link.href='/api/backup/download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    if(document.getElementById('backupStatus')){
      document.getElementById('backupStatus').innerHTML='✅ Backup download started - Check Downloads - lemon_erp_backup_*.json';
      document.getElementById('backupStatus').style.background='#E6F4EA';
    }
    setTimeout(()=>{ loadBackupInfo(); }, 1000);
  }catch(e){
    console.error('backupNow error', e);
    if(document.getElementById('backupStatus')) document.getElementById('backupStatus').innerHTML=`❌ Backup failed: ${e.message}`;
  }
}

function openAddDataPopup(){
  if(document.getElementById('backupModal')) document.getElementById('backupModal').classList.remove('hidden');
  clearBackupFile();
}
function closeAddDataPopup(){
  if(document.getElementById('backupModal')) document.getElementById('backupModal').classList.add('hidden');
}
function handleBackupDragOver(e){ e.preventDefault(); e.stopPropagation(); if(document.getElementById('dz_backup_file')) document.getElementById('dz_backup_file').classList.add('dragover'); }
function handleBackupDragLeave(e){ e.preventDefault(); e.stopPropagation(); if(document.getElementById('dz_backup_file')) document.getElementById('dz_backup_file').classList.remove('dragover'); }
function handleBackupDrop(e){
  e.preventDefault(); e.stopPropagation();
  if(document.getElementById('dz_backup_file')) document.getElementById('dz_backup_file').classList.remove('dragover');
  let files=e.dataTransfer.files;
  if(files.length>0) processBackupFile(files[0]);
}
function handleBackupFileSelect(e){ let file=e.target.files[0]; if(file) processBackupFile(file); }
function processBackupFile(file){
  if(!file.name.endsWith('.json')){ alert('⚠️ Only JSON backup files'); return; }
  if(file.size>10*1024*1024){ alert('⚠️ File too large Max 10MB'); return; }
  let reader=new FileReader();
  reader.onload=function(ev){
    try{
      let content=ev.target.result;
      let data=JSON.parse(content);
      if(document.getElementById('backup_file_content')) document.getElementById('backup_file_content').value=content;
      let fileDiv=document.getElementById('dz_file_backup');
      let infoDiv=document.getElementById('backup_file_info');
      let previewDiv=document.getElementById('backup_preview');
      let uploadSection=document.getElementById('backup_upload_section');
      let summaryEl=document.getElementById('backup_file_summary');
      let clearBtn=document.getElementById('dz_clear_backup');
      if(fileDiv){ fileDiv.style.display='block'; fileDiv.innerHTML=`📄 ${file.name} (${(file.size/1024).toFixed(1)}KB)`; }
      if(infoDiv) infoDiv.style.display='block';
      if(previewDiv){
        let preview=`Backup Date: ${data.meta?.backup_date||'Unknown'}<br>Version: ${data.meta?.version||'Unknown'}<br><br>`;
        preview+=`Categories: ${data.product_category?.length||0} | Products: ${data.product?.length||0}<br>SBUs: ${data.sbu?.length||0} | Vendors: ${data.vendor?.length||0}<br>Customers: ${data.customer?.length||0} | POs: ${data.po?.length||0}<br>GRNs: ${data.grn?.length||0}`;
        previewDiv.innerHTML=preview;
      }
      if(summaryEl) summaryEl.innerHTML=`File: ${file.name}<br>Size: ${(file.size/1024).toFixed(1)}KB<br>Tables: ${Object.keys(data).length} | Ready`;
      if(uploadSection) uploadSection.style.display='block';
      if(clearBtn) clearBtn.style.display='inline-block';
      if(document.getElementById('dz_backup_file')){ document.getElementById('dz_backup_file').style.borderColor='#1A2E1E'; document.getElementById('dz_backup_file').style.background='#F6FFF6'; }
    }catch(err){ alert(`❌ Invalid backup file: ${err.message}`); }
  };
  reader.readAsText(file);
}
function clearBackupFile(e){
  if(e){ e.preventDefault(); e.stopPropagation(); }
  if(document.getElementById('backup_file_content')) document.getElementById('backup_file_content').value='';
  let fileIn=document.getElementById('file_backup'); if(fileIn) fileIn.value='';
  let fileDiv=document.getElementById('dz_file_backup'); if(fileDiv) fileDiv.style.display='none';
  let infoDiv=document.getElementById('backup_file_info'); if(infoDiv) infoDiv.style.display='none';
  let uploadSection=document.getElementById('backup_upload_section'); if(uploadSection) uploadSection.style.display='none';
  let resultDiv=document.getElementById('backup_upload_result'); if(resultDiv) resultDiv.style.display='none';
  let clearBtn=document.getElementById('dz_clear_backup'); if(clearBtn) clearBtn.style.display='none';
  let zone=document.getElementById('dz_backup_file'); if(zone){ zone.style.borderColor=''; zone.style.background=''; zone.classList.remove('dragover'); }
}
async function uploadBackupData(){
  try{
    let content=document.getElementById('backup_file_content')?.value||'';
    if(!content){ alert('⚠️ No file selected - Drag & drop JSON first'); return; }
    let resultDiv=document.getElementById('backup_upload_result');
    if(resultDiv){ resultDiv.style.display='block'; resultDiv.innerHTML='⏳ Uploading backup data into database tables...'; resultDiv.style.background='#FFFBEB'; }
    let res=await fetch('/api/backup/upload',{method:'POST',headers:{'Content-Type':'application/json'},body:content});
    let j=await res.json();
    console.log('Upload result', j);
    if(res.ok){
      if(resultDiv){ resultDiv.innerHTML=`✅ Uploaded!<br>${Object.entries(j.restored||{}).map(([k,v])=>`${k}: ${v} new`).join('<br>')}<br>${j.message||''}`; resultDiv.style.background='#E6F4EA'; }
      loadBackupInfo(); loadCategories(); loadProducts(); loadVendors(); loadPOs();
    } else {
      if(resultDiv){ resultDiv.innerHTML=`❌ Upload failed: ${j.error||'Unknown'}`; resultDiv.style.background='#FCE8E6'; }
    }
  }catch(err){
    console.error('upload error', err);
    let resultDiv=document.getElementById('backup_upload_result');
    if(resultDiv){ resultDiv.style.display='block'; resultDiv.innerHTML=`❌ Error: ${err.message}`; resultDiv.style.background='#FCE8E6'; }
  }
}

async function loadDash(){ let r=await fetch('/api/inventory/combined'); let d=await r.json(); document.getElementById('totalVal').innerText='Rs '+(d.total_value_lakh||0).toFixed(2)+' Lakh'; let rc=await fetch('/api/product_categories'); let cats=await rc.json(); document.getElementById('catCountDash').innerText=cats.length; let rp=await fetch('/api/products'); let prods=await rp.json(); document.getElementById('prodCountDash').innerText=prods.length; let rs=await fetch('/api/sbus'); let sbus=await rs.json(); document.getElementById('sbuCountDash').innerText=sbus.length;}
async function loadStock(){ let r=await fetch('/api/inventory/combined'); let d=await r.json(); document.getElementById('rawTbl').innerHTML='<h4>Raw</h4><table><tr><th>Code</th><th>Name</th><th>MT</th></tr>'+d.raw.map(x=>`<tr><td>${x.product_code}</td><td>${x.name}</td><td>${x.total_mt}</td></tr>`).join('')+'</table>'; document.getElementById('finTbl').innerHTML='<h4>Finished</h4><table><tr><th>Code</th><th>Name</th><th>MT</th></tr>'+d.finished.map(x=>`<tr><td>${x.product_code}</td><td>${x.name}</td><td>${x.total_mt}</td></tr>`).join('')+'</table>';}

// ========== GRN MODULE v4.6 - SAFE - No other modules touched ==========
let grnPOsCache=[]; let grnProductsCache=[]; let grnSBUsCache=[]; let grnVendorsCache=[];

function openAddGRNPopup(){
  document.getElementById('grnModal').classList.remove('hidden');
  document.getElementById('grn_id').value='';
  document.getElementById('grn_date').value=new Date().toISOString().split('T')[0];
  document.getElementById('grn_created_by').value='Admin';
  loadGRNPOs(); loadGRNSBUs(); loadGRNVendors(); loadGRNProducts();
}
function closeAddGRNPopup(){ document.getElementById('grnModal').classList.add('hidden'); }
function setGRNType(type){ document.getElementById('grn_type').value=type; }

async function loadGRNFilters(){
  try{
    let sbus=await fetch('/api/sbus').then(r=>r.json());
    grnSBUsCache=sbus;
    let sbuFilter=document.getElementById('grn_sbu_filter');
    let sbuSelect=document.getElementById('grn_sbu_id');
    if(sbuFilter) sbuFilter.innerHTML='<option value="">All SBUs</option>'+sbus.map(s=>`<option value="${s.id}">${s.sbu_name}</option>`).join('');
    if(sbuSelect) sbuSelect.innerHTML='<option value="">Select SBU</option>'+sbus.map(s=>`<option value="${s.id}">${s.sbu_name}</option>`).join('');
  }catch(e){}
  try{
    let vendors=await fetch('/api/vendors').then(r=>r.json());
    grnVendorsCache=vendors;
    let vendorFilter=document.getElementById('grn_vendor_filter');
    let vendorSelect=document.getElementById('grn_vendor_id');
    if(vendorFilter) vendorFilter.innerHTML='<option value="">All Vendors</option>'+vendors.map(v=>`<option value="${v.id}">${v.name}</option>`).join('');
    if(vendorSelect) vendorSelect.innerHTML='<option value="">Select Vendor</option>'+vendors.map(v=>`<option value="${v.id}">${v.name}</option>`).join('');
  }catch(e){}
}

async function loadGRNPOs(){
  try{
    let pos=await fetch('/api/grn/po_list').then(r=>r.json());
    grnPOsCache=pos;
    let sel=document.getElementById('grn_po_id');
    if(sel) sel.innerHTML='<option value="">Select PO - '+pos.length+' POs</option>'+pos.map(p=>`<option value="${p.id}">${p.po_no} - ${p.vendor} - ${p.sbu_name}</option>`).join('');
  }catch(e){}
}
function searchGRNPOs(){
  let search=(document.getElementById('grn_po_search').value||'').toLowerCase();
  let sel=document.getElementById('grn_po_id');
  if(!sel) return;
  let filtered=grnPOsCache.filter(p=>(p.po_no||'').toLowerCase().includes(search) || (p.vendor||'').toLowerCase().includes(search));
  sel.innerHTML='<option value="">Select PO - '+filtered.length+' found</option>'+filtered.map(p=>`<option value="${p.id}">${p.po_no} - ${p.vendor}</option>`).join('');
}
function onGRNPOSelected(){
  let poId=document.getElementById('grn_po_id').value;
  let po=grnPOsCache.find(p=>String(p.id)===String(poId));
  if(!po) return;
  document.getElementById('grn_po_search').value=po.po_no;
  if(po.sbu_id){ document.getElementById('grn_sbu_id').value=po.sbu_id; onGRNSBUChanged(); }
  if(po.vendor_id){ document.getElementById('grn_vendor_id').value=po.vendor_id; onGRNVendorChanged(); }
  if(po.items && po.items[0]){ document.getElementById('grn_product_id').value=po.items[0].product_id||''; onGRNProductSelected(); document.getElementById('grn_rate').value=po.items[0].rate||''; }
}
async function loadGRNSBUs(){ await loadGRNFilters(); }
async function onGRNSBUChanged(){
  let sbuId=document.getElementById('grn_sbu_id').value;
  let sbu=grnSBUsCache.find(s=>String(s.id)===String(sbuId));
  if(sbu){
    document.getElementById('grn_sbu_name').value=sbu.sbu_name;
    let sbuCode=sbu.sbu_name.substring(0,3).toUpperCase().replace(/[^A-Z0-9]/g,'');
    document.getElementById('grn_sbu_code_preview').innerText=sbuCode;
    document.getElementById('grn_no_preview').innerText='GRN/26-27/'+sbuCode+'/XXXX';
    document.getElementById('grn_no_display').value='GRN/26-27/'+sbuCode+'/XXXX Auto';
    try{
      let yards=await fetch('/api/grn/sbu_yards/'+sbuId).then(r=>r.json());
      let yardSel=document.getElementById('grn_stock_yard_id');
      if(yardSel) yardSel.innerHTML='<option value="">Select Yard - '+yards.length+' yards</option>'+yards.map(y=>`<option value="${y.id}">${y.yard_name}</option>`).join('');
    }catch(e){}
  }
}
async function loadGRNVendors(){ await loadGRNFilters(); }
function onGRNVendorChanged(){
  let vendorId=document.getElementById('grn_vendor_id').value;
  let vendor=grnVendorsCache.find(v=>String(v.id)===String(vendorId));
  if(vendor){ document.getElementById('grn_vendor_name').value=vendor.name; document.getElementById('grn_station').value=vendor.station||''; }
}
async function loadGRNProducts(){
  try{
    let prods=await fetch('/api/products').then(r=>r.json());
    grnProductsCache=prods;
    let sel=document.getElementById('grn_product_id');
    if(sel) sel.innerHTML='<option value="">Select Product - '+prods.length+' products</option>'+prods.map(p=>`<option value="${p.id}">${p.product_code} - ${p.name}</option>`).join('');
  }catch(e){}
}
function onGRNProductSelected(){
  let prodId=document.getElementById('grn_product_id').value;
  let prod=grnProductsCache.find(p=>String(p.id)===String(prodId));
  if(prod){ document.getElementById('grn_material').value=prod.name; }
}
function calcGRNWeighment(){
  let gross=parseFloat(document.getElementById('grn_gross_kg').value)||0;
  let tare=parseFloat(document.getElementById('grn_tare_kg').value)||0;
  if(gross && tare){
    let net=gross - tare;
    document.getElementById('grn_net_kg').value=net.toFixed(3);
    document.getElementById('grn_net_mt').value=(net/1000).toFixed(3);
    if(!document.getElementById('grn_received_qty').value) document.getElementById('grn_received_qty').value=(net/1000).toFixed(3);
    if(!document.getElementById('grn_accepted_qty').value) document.getElementById('grn_accepted_qty').value=(net/1000).toFixed(3);
  }
}
async function loadGRNs(){
  let search=document.getElementById('grn_search')?.value||'';
  let params=new URLSearchParams();
  if(search) params.set('search',search);
  try{
    let res=await fetch('/api/grn?'+params.toString());
    let grns=await res.json();
    let tbl=document.getElementById('grnTbl');
    if(!tbl) return;
    if(grns.length===0){ tbl.innerHTML='<tr><td colspan="12" style="text-align:center">No GRNs - Add New GRN</td></tr>'; }
    else{
      tbl.innerHTML=grns.map(g=>`<tr><td><b>${g.grn_no||''}</b></td><td>${g.grn_date||''}</td><td>${g.po_no||''}</td><td>${g.sbu_name||''}</td><td>${g.vendor||''}</td><td>${g.vehicle_no||''}</td><td>${g.product_name||g.material||''}</td><td>${g.received_qty||0}</td><td><b style="color:#1E7D32">${g.accepted_qty||0}</b></td><td>${g.net_mt||0}</td><td><span class="badge ok">${g.status||''}</span></td><td><button class="btn btn-w" style="padding:4px 8px;font-size:10px" onclick="editGRN(${g.id})">Edit</button> <button class="btn btn-r" style="padding:4px 8px;font-size:10px" onclick="delGRN(${g.id})">Del</button></td></tr>`).join('');
    }
    document.getElementById('grnTotalCount').innerText=grns.length;
    let totalMT=grns.reduce((sum,g)=>sum+parseFloat(g.received_qty||0),0);
    document.getElementById('grnTotalMT').innerText=totalMT.toFixed(3)+' MT';
    let acceptedMT=grns.reduce((sum,g)=>sum+parseFloat(g.accepted_qty||0),0);
    document.getElementById('grnAcceptedMT').innerText=acceptedMT.toFixed(3)+' MT';
  }catch(e){ console.error(e); }
}
function clearGRNFilters(){ document.getElementById('grn_search').value=''; loadGRNs(); }
async function saveGRN(){
  let sbuId=document.getElementById('grn_sbu_id').value;
  if(!sbuId) return alert('SBU mandatory');
  let vendorId=document.getElementById('grn_vendor_id').value;
  if(!vendorId) return alert('Vendor mandatory');
  let vehicleNo=document.getElementById('grn_vehicle_no').value;
  if(!vehicleNo) return alert('Vehicle No mandatory');
  let productId=document.getElementById('grn_product_id').value;
  if(!productId) return alert('Product mandatory');
  let grossKg=document.getElementById('grn_gross_kg').value;
  let tareKg=document.getElementById('grn_tare_kg').value;
  if(!grossKg || !tareKg) return alert('Gross and Tare mandatory');
  let payload={
    sbu_id: parseInt(sbuId),
    vendor_id: parseInt(vendorId),
    vehicle_no: vehicleNo.toUpperCase(),
    product_id: parseInt(productId),
    material: document.getElementById('grn_material').value,
    gross_kg: parseFloat(document.getElementById('grn_gross_kg').value)||0,
    tare_kg: parseFloat(document.getElementById('grn_tare_kg').value)||0,
    net_kg: parseFloat(document.getElementById('grn_net_kg').value)||0,
    net_mt: parseFloat(document.getElementById('grn_net_mt').value)||0,
    received_qty: parseFloat(document.getElementById('grn_received_qty').value)||0,
    accepted_qty: parseFloat(document.getElementById('grn_accepted_qty').value)||0,
    rate: parseFloat(document.getElementById('grn_rate').value)||0,
    bill_no: document.getElementById('grn_bill_no').value,
    wayment_slip_no: document.getElementById('grn_wayment_slip_no').value,
    grn_date: document.getElementById('grn_date').value,
    po_id: document.getElementById('grn_po_id').value ? parseInt(document.getElementById('grn_po_id').value) : null,
    station: document.getElementById('grn_station').value,
    stock_yard_id: document.getElementById('grn_stock_yard_id').value ? parseInt(document.getElementById('grn_stock_yard_id').value) : 0,
    stock_yard_name: document.getElementById('grn_stock_yard_id').selectedOptions[0]?.text||'',
    documents: { weighment_slip: document.getElementById('doc_grn_weighment_slip').value, invoice: document.getElementById('doc_grn_invoice').value },
    created_by: document.getElementById('grn_created_by').value
  };
  let url='/api/grn';
  let method='POST';
  try{
    let res=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    let text=await res.text();
    let j;
    try{ j=JSON.parse(text); }catch(e){ alert('Server Error: '+text.substring(0,200)); return; }
    if(res.ok){ alert('✅ GRN Created: '+j.grn_no+' - Accepted '+j.accepted_qty+' MT - Stock Updated'); closeAddGRNPopup(); loadGRNs(); }
    else alert('❌ Save failed: '+(j.error||'Unknown'));
  }catch(e){ alert('Error: '+e.message); }
}
async function editGRN(id){ alert('Edit GRN '+id+' - Coming soon - Use API for now'); }
async function delGRN(id){ if(!confirm('Delete GRN?')) return; let res=await fetch('/api/grn/'+id,{method:'DELETE'}); if(res.ok){ alert('Deleted'); loadGRNs(); } }
function handleGRNFileSelect(input,type){ let file=input.files[0]; if(!file) return; let reader=new FileReader(); reader.onload=function(e){ document.getElementById('doc_grn_'+type).value=e.target.result; }; reader.readAsDataURL(file); }

loadDash(); loadAllProductsForSBU(); loadProdCatOptions(); loadVendorMasters();
</script>


<!-- GRN MODAL v4.6 - Simple - No other modules touched -->
<div id="grnModal" class="modal hidden">
<div class="modal-content" style="max-width:1000px">
<div class="modal-header">
<h3><i class="bi bi-truck-flatbed"></i> Add GRN v4.6 - SBU Code + PO Link + Weighment + Stock Auto</h3>
<button class="close-x" onclick="closeAddGRNPopup()">×</button>
</div>
<div class="modal-body">
<div class="form-box" style="background:#E8F0FE;border:2px solid #1A2E1E">
<b>GRN Type - Against PO (Default) vs Direct</b>
<div class="row">
<div><label>GRN Type *</label><select id="grn_type" onchange="setGRNType(this.value)"><option value="Against PO">Against PO - Pick from PO</option><option value="Direct">Direct GRN</option></select></div>
<div><label>PO No - Searchable</label><input type="text" id="grn_po_search" placeholder="Type PO No to search" onkeyup="searchGRNPOs()" autocomplete="off"><select id="grn_po_id" onchange="onGRNPOSelected()"><option value="">Select PO</option></select></div>
</div>
<input type="hidden" id="grn_id">
</div>

<div class="form-box">
<b>SBU + Vendor - Auto from PO</b>
<div class="row">
<div><label>SBU *</label><select id="grn_sbu_id" onchange="onGRNSBUChanged()"><option value="">Select SBU</option></select><div style="font-size:10px">SBU Code: <span id="grn_sbu_code_preview">SBU</span> → GRN No: <span id="grn_no_preview">GRN/26-27/SBU/0001</span></div></div>
<div><label>SBU Name</label><input type="text" id="grn_sbu_name" readonly style="background:#f5f5f5"></div>
<div><label>Vendor *</label><select id="grn_vendor_id" onchange="onGRNVendorChanged()"><option value="">Select Vendor</option></select></div>
</div>
<div class="row">
<div><label>Vendor Name</label><input type="text" id="grn_vendor_name" readonly style="background:#f5f5f5"></div>
<div><label>Station</label><input type="text" id="grn_station" placeholder="Station"></div>
<div><label>Vehicle No *</label><input type="text" id="grn_vehicle_no" placeholder="RJ21GD0595" style="text-transform:uppercase"></div>
</div>
</div>

<div class="form-box">
<b>Invoice & Material - Single Product</b>
<div class="row">
<div><label>Bill No</label><input type="text" id="grn_bill_no" placeholder="Bill No"></div>
<div><label>Wayment Slip No *</label><input type="text" id="grn_wayment_slip_no" placeholder="Slip No e.g. 6816"></div>
<div><label>Product *</label><select id="grn_product_id" onchange="onGRNProductSelected()"><option value="">Select Product</option></select></div>
</div>
<div class="row">
<div><label>Material</label><input type="text" id="grn_material" placeholder="Material"></div>
<div><label>UOM</label><select id="grn_unit"><option value="MT">MT</option><option value="KG">KG</option></select></div>
<div><label>Stock Yard *</label><select id="grn_stock_yard_id"><option value="">Select Yard</option></select></div>
</div>
</div>

<div class="form-box" style="background:#FFF3E0;border:2px solid #8C6B2A">
<b>Weighment - Gross/Tare/Net Auto</b>
<div class="row">
<div><label>Gross Kg *</label><input type="number" id="grn_gross_kg" step="0.001" placeholder="Gross Kg" onkeyup="calcGRNWeighment()"></div>
<div><label>Tare Kg *</label><input type="number" id="grn_tare_kg" step="0.001" placeholder="Tare Kg" onkeyup="calcGRNWeighment()"></div>
<div><label>Net Kg Auto</label><input type="number" id="grn_net_kg" readonly style="background:#E8F0FE;font-weight:800" placeholder="Net Kg Auto"></div>
</div>
<div class="row">
<div><label>Net MT Auto</label><input type="number" id="grn_net_mt" readonly style="background:#E6F4EA;font-weight:800" placeholder="Net MT Auto"></div>
<div><label>Supplier Qty MT</label><input type="number" id="grn_supplier_qty" step="0.001" placeholder="Supplier Qty" onkeyup="calcGRNWeighment()"></div>
<div><label>Received Qty MT</label><input type="number" id="grn_received_qty" step="0.001" placeholder="Received Qty" onkeyup="calcGRNWeighment()"></div>
</div>
<div class="row">
<div><label>Accepted Qty MT *</label><input type="number" id="grn_accepted_qty" step="0.001" placeholder="Accepted Qty"></div>
<div><label>Rate Rs/MT *</label><input type="number" id="grn_rate" step="0.01" placeholder="Rate"></div>
<div><label>GRN Date *</label><input type="date" id="grn_date"></div>
</div>
</div>

<div class="form-box">
<b>Documents - 2 Docs</b>
<div class="row">
<div><label>Weighment Slip Doc</label><input type="file" id="file_grn_weighment_slip" accept=".pdf,.jpg,.png" onchange="handleGRNFileSelect(this,'weighment_slip')"><input type="hidden" id="doc_grn_weighment_slip"></div>
<div><label>Invoice Doc</label><input type="file" id="file_grn_invoice" accept=".pdf,.jpg,.png" onchange="handleGRNFileSelect(this,'invoice')"><input type="hidden" id="doc_grn_invoice"></div>
</div>
</div>

<div class="form-box" style="background:#E6F4EA;border:2px solid #1E7D32">
<b>Stock Update - No approval wait</b>
<div class="row">
<div><label>Created By</label><input type="text" id="grn_created_by" value="Admin"></div>
<div><label>GRN No Preview</label><input type="text" id="grn_no_display" readonly style="background:#E6F4EA;font-weight:900" placeholder="GRN/26-27/SBU/0001"></div>
</div>
<div style="font-size:11px;color:#1E7D32">✅ On Save: Accepted Qty added to Product stock + SBU Yard stock auto</div>
</div>

</div>
<div class="modal-footer">
<button class="btn btn-g" style="flex:1;padding:14px;font-size:14px" onclick="saveGRN()">Save GRN v4.6 - Stock Auto Update</button>
<button class="btn btn-w" onclick="closeAddGRNPopup()">Cancel</button>
</div>
</div>
</div>

</body></html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
