🍋 LEMON ERP - MASTER WORKFLOW PROMPT - V1 - DEFAULT MASTERS SEEDED - FROM SCREENSHOTS
BASE VERSION: V1 = v4.4.6 SBUs Final Base v4.4.3 + v4.5 PO Module Fixed + Default Masters Seeded from Screenshots product_catagorys.png, finished_products.png, pack_and_raw_materials.png - 3 Categories + 18 Products - DB lemon_erp_v44_1_category.db - https://lemon-erp.onrender.com - File backend/app_v4_final.py

V1 DEFAULT MASTERS SEEDED - EXACT DATA FROM SCREENSHOTS:

Product Categories (3) - Table product_category - id PK, category_name Unique, created_at timestamp - DB File: lemon_erp_v44_1_category.db
1. Packeging Materials - Note spelling as in screenshot Packeging (not Packaging) - Created At 2026-08-26 23:51:09 ID:3
2. Finished Products - Created At 2026-08-26 23:50:49 ID:2
3. Raw Materials - Created At 2026-08-26 23:50:32 ID:1

Seeding Logic: In with app.app_context(): db.create_all() + check if existing_cats <3 then add missing default_categories ["Packeging Materials","Finished Products","Raw Materials"] if not in existing_cats, commit

Products - 18 Products - Category wise with product_code auto, hsn_code, product_name & shows narration when roll mouse over name - Table product - id, name, category, product_code unique, hsn_code, description, loose_stock_mt, jumbo_mt, hdpe_40kg_mt, total_stock_mt, min_stock, reorder_level, sale_price, purchase_price, location

Finished Products - 12 Products - Category wise:
FINI-0018 - HSN 25222000 - Hydrate Lime 75% - Description hydrate from waste
FINI-0017 - 25222000 - Silica - waste of Hydrate plant
FINI-0016 - 25222000 - Hydrate Lime 80% - Pulviser material from calsined lime
FINI-0015 - 25222000 - Hydrate Lime 90% - Classifier from quick Lime
FINI-0014 - 25222000 - Quick Lime Powder 200 mesh - fghj
FINI-0013 - 25222000 - Quick Lime Fines 0-3 mm - sinter fines
FINI-0012 - 25222000 - Quick Lime Lumps 10-60 mm - dfgh
FINI-0011 - 25222000 - Quick Lime Lumps 40-60 mm - dfg
FINI-0010 - 25221000 - Quick Lime Lumps 10-40 mm - sizing plant processed
FINI-0009 - 25221000 - Gulli - Unburnt and over burnt
FINI-0008 - 25221000 - Chunna - Waste Klin Powder
FINI-0007 - 25221000 - Quick Lime - From Klins

Packeging Materials - 4 Products:
PACK-0006 - 1000000 - Jumbo Bags 48" - fghj
PACK-0005 - 1000000 - Hydrate Lime Valve Bags - fds
PACK-0004 - 1000000 - Repol 1st - f
PACK-0003 - 1000000 - Jumbo Bags 52" - dd

Raw Materials - 2 Products:
RAWM-0002 - 18000000 - Pet Coke - dd
RAWM-0001 - 25221000 - Lime Stone - fff

Seeding Logic: If Product.query.count()==0 then for each default_products list check if not exists by product_code then add Product(name, category, product_code exact as screenshot, hsn_code, description, loose_stock_mt 0 etc), commit, print Seeded 18 Products

Also seeds hidden masters LegalStatusMaster, VendorCategoryMaster, BankMaster if empty

Everything else from v4.5 PO Module Fixed kept:
- PO Module v4.5 with PO No PO/26-27/PRODUCT/0001 without spaces, RFQ No, PO Date, PO Validity, PO Type Raw etc, SBU dropdown delivery location, delivery_address auto, billing_address same as delivery checkbox, Product filter dropdown raw materials auto fill line, Vendor searchable dropdown rating approval station, Add Line Item button Code Name HSN Spec UOM MT Qty 3 dec Rate 2 dec GST% auto HSN mapping GST Type intra inter Amount auto CGST SGST IGST Total, Totals taxable cgst sgst igst freight round off grand total, Delivery Type Partial One Time, Delivery Schedule, Payment Terms days manual, Rate Basis FOR Ex-factory etc, Freight Terms, TDS Applicable %, RCM Yes/No %, Docs drag-drop po_doc freight_slip base64, Status Draft Pending Approved Sent to Vendor Partially Received Closed, Duplicate Copy Email Whatsapp, Rate History auto suggest
- SBUs Final v4.4.6 Base v4.4.3 + Kilns->SBUs + X + Delete + Yard Items
- Vendor Master v4.4.10.1 Docs Drag Drop File Select
- Other modules Stock Make Buy Sell Pack QR Cost Mobile

DB: lemon_erp_v44_1_category.db persistent DATABASE_PATH env
Secret key: lemon-erp-v1-default-masters
File: backend/app_v4_final.py
URL: https://lemon-erp.onrender.com

INSTRUCTIONS FOR FUTURE VERSIONS:
- Keep V1 seeding logic in with app.app_context() - if ProductCategory count<3 add missing, if Product count==0 seed 18 products exact codes as above
- For any new version increment version in title topnav secret_key comment dashboard card docstring but keep seeding logic
- Always keep DB file name same lemon_erp_v44_1_category.db
- Provide 2 files: app_v4_final.py deploy + MASTER WORKFLOW txt
- Deploy: GitHub backend/app_v4_final.py Paste Commit V1 Default Masters Seeded Wait 2 min https://lemon-erp.onrender.com

END OF MASTER PROMPT V1
