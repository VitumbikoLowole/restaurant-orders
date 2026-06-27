# Tambala Kitchen — Restaurant Menu & Customer Orders

A Django 4.2 + Django REST Framework web application for managing a
restaurant's menu and customer orders. Built for **Project 9** by
**LOWOLE Vitumbiko**.

It lets staff manage categories, menu items, customers and orders; lets a
customer place an order of several items with quantities and an auto-calculated
total; produces a daily sales report; searches the menu by category and price
range; accepts photo uploads for menu items; and exposes a small JSON API.


---

## 1. Tech stack

| Layer         | Choice                                            |
|---------------|---------------------------------------------------|
| Framework     | Django 4.2 (LTS)                                  |
| API           | Django REST Framework 3.14                        |
| Database      | MySQL 8 (SQLite fallback for local dev)           |
| Frontend      | Hand-written HTML5 / CSS3 / vanilla JS templates  |
| Server (prod) | Gunicorn behind Nginx on Ubuntu                   |
| Images        | Pillow (`ImageField` uploads)                     |
| Config        | `python-dotenv` (`.env` file)                     |

---

## 2. Data model at a glance

```
auth.User ──1:1── Customer ──1:M── Order ──M:N (through OrderItem)── MenuItem ──M:1── MenuCategory
```

* **OneToOneField** — `Customer.user → auth.User`
* **ForeignKey** — `MenuItem.category`, `Order.customer`, `OrderItem.order`, `OrderItem.menu_item`
* **ManyToManyField** — `Order.items → MenuItem` resolved `through=OrderItem`
  (the join row carries `quantity` and a `unit_price` snapshot)

Five tables total (`menucategory`, `menuitem`, `customer`, `order`,
`orderitem`) satisfying the "≥ 3 related tables" rule.

---

## 3. Quick start (local, SQLite — no MySQL needed)

```bash
# 1. create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure environment
cp .env.example .env
#    then open .env and set:  DJANGO_DB_ENGINE=sqlite

# 4. create the database schema
python manage.py migrate

# 5. load demo data (4 categories, 12 items, 5 customers, 15 orders)
python manage.py seed_data

# 6. create an admin login
python manage.py createsuperuser

# 7. run the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/>.

Demo customers created by `seed_data`: **username `customer1` … `customer5`**,
password **`demopass123`** for all. Admin: **`admin` / `adminpass123`**.

> **MySQL instead of SQLite?** Leave `DJANGO_DB_ENGINE=mysql` in `.env`,
> fill in `DB_NAME` / `DB_USER` / `DB_PASSWORD`, create that database in
> MySQL, then run the same `migrate → seed_data` steps.

---

## 4. Where to click

| URL                       | What it does                                        |
|---------------------------|-----------------------------------------------------|
| `/`                       | Dashboard                                           |
| `/menu/`                  | Menu list + **search** (name, category, price range)|
| `/menu/new/`              | Create a menu item (with **photo upload**)          |
| `/categories/`            | Category CRUD                                       |
| `/customers/`             | Customer list (login required)                      |
| `/orders/`                | Order list                                          |
| `/orders/new/`            | **Place an order** — multi-item, live total         |
| `/reports/daily/`         | **Daily sales report**                              |
| `/accounts/register/`     | Registration (creates User **+** Customer)          |
| `/accounts/login/`        | Login                                               |
| `/admin/`                 | Django admin                                        |
| `/api/menu-items/`        | **REST**: GET list / POST create                    |
| `/api/orders/today/`      | **REST**: today's orders as JSON                    |

---

## 5. Requirement → where it lives

| Requirement                                   | Implementation                                             |
|-----------------------------------------------|-----------------------------------------------------------|
| Django 4.x + DRF                              | `requirements.txt`, `restaurant_orders/settings.py`       |
| MySQL, ≥ 3 related tables                     | `settings.py`, `menu/models.py`                           |
| OneToOne / FK / M2M all used                  | `menu/models.py`                                          |
| CRUD for ≥ 3 entities                         | `menu/views.py` (category, menu item, customer, order)    |
| Auth (login / logout / register)              | `menu/auth_views.py`, `templates/registration/`           |
| Search, ≥ 2 criteria, **Q objects**           | `MenuItemListView.get_queryset` in `menu/views.py`        |
| Image / File upload                           | `MenuItem.photo` (`ImageField`)                           |
| `select_related` / `prefetch_related`         | list/detail views + API views                             |
| DRF endpoint (GET list + POST create)         | `menu/api_views.MenuItemListCreateAPI`                    |
| Relationships in forms (dropdown / formset)   | `menu/forms.py`, `order_form.html`                        |
| Place order, multi-item, auto total           | `views.order_create`, `Order.recalc_total`                |
| Daily sales report                            | `views.daily_sales_report`                                |
| API for today's orders                        | `menu/api_views.TodaysOrdersAPI`                          |
| Nginx + Gunicorn on Ubuntu                    | `deploy/` folder                                          |
| 200–300 word reflection                       | `REFLECTION.md`           |

---

## 6. Project layout

```
restaurant_orders/
├── restaurant_orders/      # Django project config (settings, root URLs, WSGI)
├── menu/                   # the one application
│   ├── models.py           # 5 tables + all relationship logic
│   ├── views.py            # CRUD + order placement + sales report
│   ├── forms.py            # model forms + search form + order formset
│   ├── serializers.py      # DRF JSON serializers
│   ├── api_views.py        # DRF endpoints
│   ├── api_urls.py         # API URL routing
│   ├── urls.py             # HTML page URL routing
│   ├── admin.py            # admin panel registration
│   ├── apps.py             # app config + signal wiring
│   ├── signals.py          # auto-creates Customer when User is saved
│   ├── auth_views.py       # registration view
│   ├── migrations/         # database migration files
│   ├── management/commands/seed_data.py
│   ├── templates/menu/     # all HTML templates
│   └── static/menu/        # style.css + main.js
├── templates/registration/ # login.html + register.html
├── deploy/                 # nginx conf + gunicorn systemd units
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md               # this file
├── REFLECTION.md          # 200 - 300 reflection
```

---

## 7. Deployment (short version)

The production stack is:

```
Browser → Nginx → Gunicorn → Django → MySQL
                ↓
         /static/ and /media/ served directly by Nginx off disk
```

Key commands on the Ubuntu VM:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
sudo cp deploy/restaurant_orders.socket  /etc/systemd/system/
sudo cp deploy/restaurant_orders.service /etc/systemd/system/
sudo systemctl enable --now restaurant_orders.socket
sudo cp deploy/nginx_restaurant_orders.conf /etc/nginx/sites-available/restaurant_orders
sudo ln -s /etc/nginx/sites-available/restaurant_orders /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```
