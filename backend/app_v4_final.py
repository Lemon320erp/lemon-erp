🍋 LEMON ERP - MASTER WORKFLOW PROMPT - v4.4.7
Use this prompt as base for all future versions. Edit/Add to this prompt for v4.4.8, v4.4.9 etc. Do not miss any detail.

---
ROLE: You are building Lemon ERP - Lime Manufacturing ERP for Quicklime (CaO) plants with multiple SBUs (Strategic Business Units).

BASE VERSION: v4.4.7 = v4.4.6 + SBUs Fixed - Lining once per kiln + Edit bug fixed + Duplicate SBU + Tabular Clean + Removed extra P tags. Stable working version on https://lemon-erp.onrender.com - File: backend/app_v4_final.py - Previous base v4.4.3 Products refined kept.

DATABASE: Single SQLite file - lemon_erp_v44_1_category.db - Do not change other databases unless explicitly asked. All tables created via db.create_all() in Flask.

---
1. PRODUCT CATEGORY MODULE - DB FILE FOR FURTHER USE - v4.4.3 Unchanged:

DB File Name: lemon_erp_v44_1_category.db
Table Name: product_category
Fields:
- id INTEGER PRIMARY KEY AUTOINCREMENT
- category_name VARCHAR(100) UNIQUE NOT NULL - 1 input field only
- created_at VARCHAR(30) DEFAULT datetime.now() timestamp

Landing Page:
- Heading: Product Category
- Form Box: background #FFFBEB border 2px solid var(--brass) #C9A86A
  - Title: Add Product Category - 1 Input Field
  - Hidden field: cat_id
  - Input: Category Name * - placeholder "Category Name e.g. Raw Materials, Finished Goods, CAPEX, Packeging Materials"
  - Buttons: Save Category (btn-g green #1A2E1E) + Reset (btn-w white)
- List: Table - Columns: # | Category Name | Created At | DB File (lemon_erp_v44_1_category.db / product_category / ID) | Actions (Edit, Del)

API:
- GET /api/product_categories - list desc
- POST /api/product_categories - body {category_name} - check unique, return 400 if exists
- GET /api/product_categories/<id> - single
- PUT /api/product_categories/<id> - update category_name
- DELETE /api/product_categories/<id>

---
2. PRODUCTS MODULE - REFINED v4.4.3 - KEEP EXACT SAME:

DB Table: product
Fields:
- id PK
- name VARCHAR(100) - Product Name Mandatory
- category VARCHAR(100) - Product Category - Dropdown from product_category database - Mandatory
- product_code VARCHAR(50) UNIQUE - Auto Generate when product is saved - e.g. RAW-0001, FINI-0001, FIN-0002 - Format: First 4 alnum chars of category upper + dash + 4-digit count. Ensure uniqueness by incrementing count if exists.
- hsn_code VARCHAR(20) - HSN Code Mandatory - e.g. 2522, 2521
- description TEXT - Product Description Mandatory - Shows narration when roll mouse over name in list - Tooltip
- loose_stock_mt, jumbo_mt, hdpe_40kg_mt, total_stock_mt FLOAT default 0
- min_stock, reorder_level, sale_price, purchase_price FLOAT
- location VARCHAR(100)

Landing Page:
- Heading centrally aligned: Products - 22px font-weight 900 - Icon bi-bag
- Subtext: Landing Page Heading Products centrally aligned - HSN + Description + Auto Code + Category-wise + Hover narration - v4.4.3 Unchanged - 11px gray #666
- Button: Add New Product - Centered - Padding 12px 28px font 14px weight 800 - btn-y background var(--lemon) #F2E863 color var(--green) - onclick openAddProductPopup()
- List: Category-wise grouping - For each category: border 1.5px solid var(--line) #E8E0D5 border-radius 10px margin 12px 0 overflow hidden - Header: background var(--green) #1A2E1E color var(--brass) #C9A86A padding 10px 14px font 800 12px - Text: "{cat} - {count} Products"
- Inside: Table columns: Product Code (badge background var(--alab) #FAF6F0 padding 3px 8px border-radius 6px border 1px solid var(--line)) | HSN (badge ok green #E6F4EA color #1E7D32) | Product Name - Hover for Narration (tooltip with product_code, hsn_code, category, description - background var(--green) color white width 260px border-radius 8px padding 10px position absolute bottom 125% left 50% margin-left -130px) | Description (10px max-width 200px overflow hidden ellipsis nowrap) | Actions (Edit, Del)

Popup: id productModal - class modal hidden - onclick if event.target===this closeProductPopup() - modal-content max-width 620px - Header: Add Product - HSN + Description + Auto Code - v4.4.3 + X button class close-x - Body: hidden prod_id + form-box background #FFFBEB border 2px brass
  - Product Name * (Mandatory) - input id prod_name
  - Product Category - Dropdown from product_category database * (Mandatory) - select id prod_cat - Subtext DB File: lemon_erp_v44_1_category.db - Table: product_category
  - HSN Code * (Mandatory) + Product Code (Auto Generate when saved) disabled background var(--alab) font 800 - ids prod_hsn, prod_code_preview
  - Product Description * (Mandatory) - Narration on hover - textarea id prod_desc placeholder "Product Description - Mandatory - Shows narration when roll mouse over name in list"
- Footer: Save Product - Auto Code Generate (btn-g flex 1 padding 13px) + Cancel (btn-w)

API:
- GET /api/products - order by id desc - fields id, name, category, product_code, hsn_code, description
- POST /api/products - validate name, category, hsn_code, description mandatory - generate product_code via generate_product_code(category, count) - ensure unique - return id, name, product_code, hsn_code, category
- GET/PUT/DELETE /api/products/<pid> - same validation

---
3. SBUs MODULE - KILNS RENAMED TO SBUs - v4.4.7 FINAL FIXED SPEC:

DB Tables:
- sbu: id PK, sbu_name VARCHAR(100), address TEXT, created_at VARCHAR(30)
- kiln_asset: id PK, sbu_id FK sbu.id, kiln_no VARCHAR(50), lining_installation_date VARCHAR(20), health_status VARCHAR(50), products_capacity TEXT JSON - v4.4.7 FIX: list of {product_id, capacity_per_day, capacity} ONLY - Lining and Health NOT inside product, they are kiln-level columns
- sizing_plant_asset: id PK, sbu_id FK, plant_no VARCHAR(50), products_capacity TEXT JSON - list of {product_id, capacity_per_hour, capacity, machineries}, machineries TEXT whole plant
- hydration_plant_asset: id PK, sbu_id FK, plant_no, products_capacity TEXT JSON, machineries TEXT
- stock_yard_asset: id PK, sbu_id FK, yard_name VARCHAR(100), yard_items TEXT JSON - list of {product_id, opening_stock, opening}

Landing Page: id sbus - class tabcontent (active)
- Card text-align center padding 24px
  - H1: Strategic Business Units - 26px weight 900 icon bi-building - margin 0 0 14px - text-align center
  - Button: Add New SBU - padding 14px 36px font 15px weight 800 btn-y lemon - onclick openAddSBU()
  - REMOVED in v4.4.7: P "Module name Kilns renamed to SBUs..." and P "b-Add New SBU Button Below Heading - Popup with X..." - Keep only H1 + Button
- Div id sbuList: Loading SBUs...

Popup: id sbuModal - class modal hidden - onclick if event.target===this closeAddSBU() - modal-content max-width 1000px max-height 94vh flex column - Header: Add SBU - Strategic Business Units - v4.4.7 Fixed - Popup with X + close-x button x - Body: hidden sbu_id + form-box SBU Details background #FFFBEB border 2px brass
  - SBU Name - e.g. Unit 1 72MT, Jodhpur Plant * - input id sbu_name
  - Address - Full address field - textarea id sbu_address placeholder "Address - Full address field e.g. Plot 123, RIICO Industrial Area, Jodhpur, Rajasthan 342001"
  - Asset Section 1: class asset-section background white border 1.5px solid var(--line) border-radius 12px padding 14px margin 14px 0
    - Header: h4 🔥 Kilns - v4.4.7 Fixed - Lining & Health once per kiln - Add Kiln Button -> Button Add Kiln onclick addKilnField()
    - P: When clicked Add Kiln - Add new line of input field as *Kiln No. *Lining Installation Date *Health Status *Products and Capacity *Add Product Button *Delete button. Products only ask Product + Capacity. - 10px gray
    - Container: id kilnsContainer - P No kilns - Click Add Kiln Button
  - Asset Section 2: ⚙ Sizing Plants - Add Sizing Plant Button -> *Plant No. *Products and Capacity *Add Product Button - Button Add Sizing Plant - Container sizingContainer
  - Asset Section 3: 💧 Hydration Plants - Add Hydration Plant Button - Container hydrationContainer
  - Asset Section 4: 📦 Stock Yards - Add Stock Yard Button -> *Yard Name *Add Yard Items - Button Add Stock Yard btn-y - Container yardsContainer

Kiln Field: function addKilnField(data=null) - v4.4.7 FIXED:
- Container kilnsContainer - if includes No kilns clear
- kilnCounter++ - id = kiln_${counter}_${Date.now()}
- HTML: div id=${id} class kiln-line background #FFFBEB border 1.5px solid var(--brass) border-radius 10px padding 12px margin 10px 0
  - Top row: flex justify space-between wrap - b Kiln Line - *Kiln No. *Lining Date *Health + Products - Buttons: Add Product onclick addKilnProduct('${id}') btn-b + Delete Kiln btn-r
  - Row: 3 columns: *Kiln No. - e.g. Kiln 1, K-01 - input class k_no placeholder "Kiln No." value data.kiln_no
          *Lining Installation Date - Date picker - input class k_lining type date value data.lining_installation_date || data.lining_date
          *Health Status Good, Needs Repair, Critical, New - select class k_health selected data.health_status
  - Products Section: margin-top 8px padding 10px background white border-radius 8px border 1px solid var(--line) - b *Products and Capacity - v4.4.7 Fixed (Product + Capacity only) - Container kiln-products-container - If data.products_capacity map renderKilnProductLine else P No products - Click Add Product -> Inset Product name, Capacity/Day, Delete

Kiln Product Line: function renderKilnProductLine(pc) - v4.4.7 FIXED:
- id kprod_${Date.now()}_${random}
- div id product-line background white border 1px dashed var(--brass) border-radius 8px padding 10px margin 8px 0 margin-left 12px border-left 4px solid var(--brass)
  - Row align end: Product name (selected from Finished Product List) - select class kp_product options from finishedProducts getFinishedProductOptions(product_id) - Capacity/Day MT/day e.g. 15 - input class kp_capacity type number placeholder "Capacity/Day - MT/day e.g. 15" value capacity_per_day - Delete button btn-r margin-top 18px onclick remove
  - REMOVED: Lining Date, Health Status from product line

Sizing Field: addSizingField(data=null) - similar - kiln-line background #F6FFF6 border-color #C5E1C5 - b Sizing Plant - *Plant No. *Products and Capacity *Add Product Button - Buttons Add Product addSizingProduct + Delete - Row Plant No. e.g. Sizing 1, SP-01 input class s_no - Products container sizing-products-container - renderSizingProductLine - Row Machineries whole plant textarea class s_mach placeholder "List of Machineries - Whole plant - e.g. Crusher, Vibrating Screen 10-40mm, Conveyor 20m, Dust Collector"

Sizing Product Line: renderSizingProductLine(pc) - Product name Finished List select sp_product - Capacity/hour input sp_capacity - Delete - Row List of Machineries for this product line textarea sp_mach_line

Hydration Field: addHydrationField - kiln-line background #F0F8FF border #C2D6FF - Plant No. h_no - hydration-products-container - renderHydrationProductLine - h_mach whole plant

Yard Field: addYardField(data=null) - kiln-line background #FFFBEB - b Stock Yard - *Yard Name *Add Yard Items - Delete button for line - Buttons Add Yard Items addYardItem + Delete Yard - Row Yard Name e.g. Limestone Yard 1 input y_name - Products section b *Add Yard Items - Container yard-items-container - renderYardItemLine

Yard Item Line: renderYardItemLine(yi) - Dropdown selection field (take data of products from all category) select yi_product getAllProductOptions(product_id) - allProducts - Opening stock MT e.g. 150 input yi_opening type number placeholder "Opening stock - e.g. 150 MT stored in this yard" - Delete

JS Helpers:
- loadAllProductsForSBU(): fetch /api/products -> window.allProducts, window.finishedProducts filter category includes finish/quicklime/CaO else all
- getFinishedProductOptions(selectedId): options from finishedProducts map <option value id selected>name (product_code) - category</option>
- getAllProductOptions(selectedId): options from allProducts
- addKilnProduct(kilnId): find kilnDiv, container kiln-products-container, if No products clear, insertAdjacentHTML renderKilnProductLine({})
- addSizingProduct, addHydrationProduct, addYardItem similar

Save SBU: async saveSBU() - v4.4.7 FIXED:
- sbuName = sbu_name trim - alert if empty
- kilns = querySelectorAll #kilnsContainer > div[id^="kiln_"] - for each div: k_no = querySelector .k_no value, k_lining = .k_lining value, k_health = .k_health value, products_capacity = querySelectorAll .kiln-products-container > div[id^="kprod_"] - for each pdiv: pid kp_product value, cap kp_capacity - if pid push {product_id parseInt, capacity_per_day parseFloat, capacity}
- kilns push {kiln_no: k_no, lining_installation_date: k_lining, lining_date: k_lining, health_status: k_health, products_capacity}
- sizings similarly - sp_product, sp_capacity, sp_mach_line - push plant_no s_no, products_capacity, machineries s_mach
- hydrations - hp_product, hp_capacity, hp_mach_line - plant_no h_no, products_capacity, machineries h_mach
- yards - yi_product, yi_opening - yard_items push product_id, opening_stock, opening - push yard_name y_name, yard_items
- payload = {sbu_name, address sbu_address value, kilns, sizing_plants, hydration_plants, stock_yards}
- sbuId = sbu_id value - url sbuId ? /api/sbus/+sbuId : /api/sbus - method PUT : POST - fetch JSON - alert SBU Created/Updated + counts - closeAddSBU(), loadSBUs(), loadDash()

Load SBUs: async loadSBUs() - v4.4.7 TABULAR CLEAN:
- fetch /api/sbus - sbus array
- sbuCountDash = length
- if length 0: sbuList innerHTML div center padding 30px P No SBUs - Masters empty - Strategic Business Units - Forget v4.4.4 and v4.4.5 - Take v4.4.3 as base + Button Add First SBU
- else h = '' for s in sbus: kilnBadge = s.kilns length etc - h+= card sbu-card flex justify space-between wrap gap 10px - div h3 16px bi-building s.sbu_name + p 11px gray geo-alt address + p 10px margin-top 6px badges brass 3 Kilns etc + div buttons Edit onclick editSBU(s.id) + Duplicate btn-o onclick duplicateSBU(s.id) + Delete delSBU
  - Tabular: For each SBU, after header, create divs with border 1.5px solid var(--line) border-radius 10px overflow hidden margin 10px 0
    - Kilns: Header div background var(--green) color white padding 8px 10px font 800 11px "🔥 Kilns - {count}" + Table th Kiln No, Lining Date, Health, Products + Capacity/Day - Rows map k => tr td b kiln_no + td lining_date + td badge ok/crit/warn health_status + td map products_capacity => span display block background white padding 4px 6px border-radius 4px margin 3px 0 border 1px line b product_name - capacity MT/day - Product name Finished List
    - Sizing: Header background #1A2E1E color #C5E1C5 + Table th Plant No, Machineries Whole, Products + Capacity/Hour + rows
    - Hydration: Header background #0F2A44 color #C2D6FF + Table th Plant No, Machineries, Products + rows
    - Stock Yards: Header background var(--alab) + Table th Yard Name, Items Product + Opening Stock + rows
  - p 10px gray margin-top 10px c- SBU card with SBU Name + Address + Badges + Edit / Duplicate / Delete buttons - Base v4.4.3 Products refined kept - v4.4.7 Tabular

Edit SBU: async editSBU(id) - v4.4.7 BUG FIXED:
- fetch /api/sbus/id - s
- openAddSBU() FIRST - Do NOT set fields before opening
- setTimeout 600ms: set sbu_id = s.id, sbu_name = s.sbu_name, sbu_address = s.address, kilnsContainer innerHTML='', sizingContainer='', hydrationContainer='', yardsContainer='' - forEach k addKilnField(k), sp addSizingField(sp), hp addHydrationField(hp), y addYardField(y) - if empty show No kilns etc placeholders
- Keep edit button

Duplicate SBU: v4.4.7 NEW:
- duplicateSBU(id): confirm Duplicate SBU? Creates copy with - Copy suffix - fetch /api/sbus/id - s
- payload = {sbu_name: s.sbu_name + ' - Copy', address: s.address, kilns: s.kilns.map(k => {kiln_no: k.kiln_no + ' - Copy', lining_installation_date: k.lining_installation_date || k.lining_date, lining_date same, health_status k.health_status, products_capacity: k.products_capacity.map(pc => {product_id, capacity_per_day, capacity})}), sizing_plants: s.sizing_plants.map(sp => {plant_no: sp.plant_no + ' - Copy', products_capacity: sp.products_capacity.map(pc => {product_id, capacity_per_hour, capacity, machineries}), machineries: sp.machineries}), hydration_plants: similar plant_no + ' - Copy', stock_yards: s.stock_yards.map(y => {yard_name: y.yard_name + ' - Copy', yard_items: y.yard_items.map(yi => {product_id, opening_stock, opening})})}
- POST /api/sbus - Alert Duplicated - loadSBUs() - Add button Duplicate btn-o in SBU card next to Edit Delete

Delete SBU: delSBU(id) confirm Delete SBU? Strategic Business Units - DELETE /api/sbus/id - loadSBUs()

API:
- GET /api/sbus - all SBUs with resolved product names: all_products dict id->product, resolve_pc function json loads products_capacity -> list product_id, product_name, product_code, capacity_per_day, capacity_per_hour, capacity, machineries - resolve_yard similarly opening_stock - return list sbu id, sbu_name, address, kilns list kiln_no, lining_installation_date, lining_date, health_status, products_capacity resolved, sizing_plants plant_no, products_capacity resolved, machineries, hydration_plants same, stock_yards yard_name, yard_items resolved
- POST /api/sbus - body sbu_name, address, kilns array kiln_no, lining_installation_date, health_status, products_capacity, sizing_plants plant_no, products_capacity, machineries, hydration_plants same, stock_yards yard_name, yard_items - create SBU flush, create KilnAsset sbu_id, kiln_no, lining_installation_date, health_status, products_capacity json dumps, SizingPlantAsset, HydrationPlantAsset, StockYardAsset - commit - return id, sbu_name
- GET /api/sbus/<sid> - single with same resolve + raw json fields products_capacity_raw, yard_items_raw
- PUT /api/sbus/<sid> - update sbu_name, address, delete existing KilnAsset, SizingPlantAsset, HydrationPlantAsset, StockYardAsset where sbu_id, recreate from payload - commit
- DELETE /api/sbus/<sid> - delete assets then SBU

---
4. OTHER MODULES - KEEP EXACT SAME AS v4.4.6 - DO NOT CHANGE:

- Stock: id stock - card Stock - v4.4 Unchanged - Row select fUnit All Units, Unit 1 72MT, Unit 2 84MT, Unit 3 125MT + Filter button loadStock() - Cards Raw, WIP, Finished - divs rawTbl, wipTbl, finTbl - API /api/inventory/combined - raw, wip, finished - product_code, hsn_code, total_mt, status badge - Filter by location includes unit number

- Make: id make - card Make - v4.4 Unchanged - form-box Row make_wc select SBU options loadWCOptions(), make_type select Kiln/Sizing/Hydration, make_unit input placeholder Unit e.g. Unit 1 72MT value Unit 1 72MT - Row make_lime number Limestone MT, make_pet Petcoke MT, make_out Output MT - Row make_waste Wastage, make_inProd Input Product, make_outProd Output Product - Row make_op Operator + Create MO button createMO() - moList - API /api/manufacturing_orders GET/POST, /api/mo/total

- Buy: id buy - card Buy - v4.4 Unchanged - form-box New PO - Row po_vendor select vendors loadVendorsOpt(), po_mat Material, po_qty Qty, po_rate Rate - Row po_unit Unit 1/2/3, po_status Draft/Sent/Received, Create PO createPO() - form-box New GRN - Row g_vehicle Vehicle No, g_material Material, g_unit Unit 1/2/3 - Row g_gross Gross kg, g_tare Tare kg, g_vendor select, Save GRN createGRN() - Cards PO List poList, GRN List grnList - API /api/po, /api/grn

- Sell: id sell - card Sell - v4.4 Unchanged - form-box Row d_customer select customers loadCustomersOpt(), d_vehicle Vehicle No, d_product select products loadProductsOpt(), d_qty Qty MT - Row d_qr QR Bags, d_unit Unit 1/2/3, Create Dispatch createDispatch() - Card Dispatch List dispatchList - API /api/dispatch

- Vendors: id vendors - card Vendors - v4.4 Unchanged - form-box hidden vend_id + Row vend_name Name, vend_type select Limestone/Petcoke/Packaging/Transport/Trading, vend_gst GST No + Row vend_contact Contact, vend_credit Credit Limit, vend_due Pending Due, Save Vendor saveVendor() Reset resetVendForm() - vendorTbl - API /api/vendors GET/POST/PUT/DELETE

- Customers: id customers - similar - cust_id, cust_name, cust_type select Cement/Steel/Chemical/Trader, cust_gst, cust_contact, cust_recv Pending Receivable - customerTbl - API /api/customers

- Pack: id pack - pack_id, pack_type Bag Type, pack_cat select 40kg/Jumbo, pack_cap Capacity MT, pack_closing Closing, pack_min Min, pack_rate Rate, pack_unit Unit 1/2/3 - packTbl - API /api/packaging

- QR: id qr - qr_product select products, qr_weight number value 1.2, qr_unit Unit 1/2/3, Generate QR genQR() - qrResult, qrImg base64 - qrList - API /api/qr_generate POST product weight unit -> bag_id JMB-{prod}-2026-{count:05d} qr_data bag_id|product|weight MT|unit qrcode box_size 8 border 3 fill #1A2E1E back #FAF6F0 base64 + entry QRBag, /api/qr_list

- Cost: id cost - costVal Rs Lakh, costTbl - loadCost() fetch inventory combined total_value_lakh

- Mobile: id mobile - placeholder

- Dash: id dash - card Dash - v4.4.7 etc - kpi-grid 4 cards Total Value totalVal Rs Lakh, SBUs sbuCountDash, Products prodCountDash, Categories catCountDash - card v4.4.3 Base + SBUs Final description - card Alerts alerts - loadDash() fetch inventory combined total_value_lakh, alerts, mo total, product_categories count, products count, sbus count

---
5. COMMON UI:

- CSS variables: --green #1A2E1E, --brass #C9A86A, --alab #FAF6F0, --lemon #F2E863, --line #E8E0D5, --gray #F6F5F3
- Topnav: background var(--green) color white padding 0 14px display flex justify space-between align center height 44px sticky top 0 z-index 200 - brand font weight 900 15px lemon span color var(--lemon) - Reload button btn-y
- Layout: display flex - Sidebar width 210px background white border-right 1px solid var(--line) padding 10px 0 sticky top 44px height calc(100vh - 44px) overflow-y auto - h4 10px gray #888 margin 14px 10px 4px uppercase letter-spacing 0.6px - menu padding 7px 10px margin 2px 6px border-radius 7px cursor pointer display flex align center gap 8px font weight 600 12px color #444 hover background var(--alab) active background var(--green) color var(--brass)
- Content: flex 1 padding 14px max-width 1500px
- Card: background white border-radius 10px padding 14px margin 8px 0 box-shadow 0 2px 6px rgba(0,0,0,0.04) border 1px solid var(--line) - h3 margin 0 0 10px font 13px weight 800
- KPI: border-left 4px solid var(--brass) padding 12px val font 20px weight 900
- Buttons: btn padding 7px 12px border-radius 7px border none cursor pointer font weight 700 11px - btn-g background var(--green) color white, btn-y background var(--lemon) color var(--green), btn-w background white color var(--green) border 1px solid var(--line), btn-r background #C5221F color white, btn-b background #E8F0FE color #1A2E1E border 1px #C2D6FF, btn-o background #FFF3E0 color #8C6B2A border 1px var(--brass)
- Badge: padding 3px 8px border-radius 12px font 10px weight 800 - ok background #E6F4EA color #1E7D32, warn #FEF3CD #9C6F00, crit #FCE8E6 #C5221F, brass #FFFBEB #8C6B2A border 1px var(--brass)
- Table: width 100% border-collapse collapse font 12px - th background #F8F6F3 padding 8px 6px text-left weight 700 border-bottom 2px var(--line) - td padding 7px 6px border-bottom 1px #F0EBE2 vertical top
- Input/select/textarea: padding 8px 10px border-radius 7px border 1.5px solid var(--line) width 100% font 12px margin 4px 0
- Row: display flex gap 8px flex-wrap wrap - >* flex 1 min-width 140px
- Hidden: display none !important
- Form-box: background var(--alab) padding 12px border-radius 8px border 1px dashed var(--brass) margin-bottom 10px
- Modal: position fixed top 0 left 0 width 100% height 100% background rgba(26,46,30,0.65) z-index 1000 display flex align center justify center padding 16px backdrop-filter blur 4px - modal-content background white border-radius 14px width 100% max-width 1000px max-height 94vh display flex flex-direction column box-shadow 0 24px 64px rgba(0,0,0,0.35) border 1px solid var(--brass) animation slideUp 0.25s ease - modal-header padding 16px 20px border-bottom 2px solid var(--line) display flex justify space-between align center background var(--alab) border-radius 14px 14px 0 0 sticky top 0 z-index 2 - modal-body padding 16px 20px overflow-y auto flex 1 - modal-footer padding 14px 20px border-top 2px solid var(--line) background var(--alab) border-radius 0 0 14px 14px display flex gap 10px sticky bottom 0 z-index 2 - close-x background white border 1.5px solid var(--line) border-radius 50% width 34px height 34px display flex align center justify center cursor pointer font weight 900 font 18px hover background #FCE8E6 color #C5221F border-color #C5221F
- Asset-section, kiln-line, product-line, tooltip, sbu-card, detail-grid etc as defined above

- JS: openTab(id) - hidden all tabcontent, remove hidden for id, active menu, load functions based on id

- Backend Flask: app Flask, secret_key lemon-erp-v44-7-sbus-fixed-tabular-duplicate, SQLALCHEMY_DATABASE_URI sqlite:///lemon_erp_v44_1_category.db, TRACK_MODIFICATIONS False, db SQLAlchemy - All models as listed - db.create_all() in app_context - generate_product_code function - All API routes as defined - health route /api/health status LIVE version v4.4.7 etc db_file lemon_erp_v44_1_category.db url https://lemon-erp.onrender.com

- Main route / returns HTML string with all above

- Run: if __name__=='__main__': app.run host 0.0.0.0 port 5000 debug True

---
INSTRUCTIONS FOR FUTURE VERSIONS - v4.4.7 UPDATED:

- Keep code same as v4.4.7 for all modules unless explicitly asked to change that module.
- v4.4.7 fixes are: Kiln lining+health once per kiln (not per product), Edit bug fixed openAddSBU() first then populate, Duplicate SBU feature btn-o, Removed 2 extra P tags in SBUs landing, Tabular clean SBU list.
- When user says "keep everything unchanged in v4.4.7 except these changes in SBUs" - only change SBUs module - Do not change Product Category, Products, Stock, Make, Buy, Sell, Vendors, Customers, Pack, QR, Cost, Mobile, Dash, CSS, other DB tables.
- For any new version, increment version number in title, topnav, secret_key, health route, comment.
- Always keep DB file name same - lemon_erp_v44_1_category.db - unless user says change database file.
- Provide file download link after changes.
- Deploy instructions: GitHub -> backend/app_v4_final.py -> Paste new version -> Commit message "v4.4.x ..." -> Wait 2 min -> https://lemon-erp.onrender.com

---
END OF MASTER PROMPT v4.4.7
