# 🚀 Coderr – Django Backend API

This is the backend for **Coderr**, a simple marketplace platform where business users can offer services and customer users can place orders and leave reviews.
Developed as part of a **training project for the Developer Akademie**, intended for educational purposes only.

> ❗ **Important:** This project is part of a course exercise at the Developer Akademie.
> It is **not** intended for production use and does **not** include a license.

---

## 🔑 Authentication

All protected endpoints use **token-based authentication** via Django REST Framework’s `authtoken`.
After logging in or registering, you will receive a token. Include it in the `Authorization` header for subsequent requests:

```
Authorization: Token <your_token_here>
```

---

## 🚀 Features

* ✅ **User registration & login** (token issuance)
* 👤 **Profile management** (CRUD for business and customer profiles)
* 🛒 **Offers**: create/list/filter/search/paginate offers with multiple detail-options
* 📄 **OfferDetail**: retrieve individual pricing/delivery/feature options
* 📝 **Orders**: customers place orders, business users update status, staff can delete
* 📊 **Order counts**: endpoints to fetch in-progress and completed order counts per business
* ⭐ **Reviews**: customers leave one review per business; business and reviewer filtering
* 📈 **Base info**: aggregated site statistics (total reviews, avg. rating, business count, offer count)

---

## 🧱 Tech Stack

* **Python** 3.10+
* **Django** 5.x
* **Django REST Framework**
* **django-filter** for queryset filtering
* **SQLite** (default; easily switchable to PostgreSQL/MySQL)
* **Token authentication** via `rest_framework.authtoken`

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-org>/coderr-backend.git
   cd coderr-backend
   ```

2. **Set up a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access)

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

---

## 📚 API Endpoints

| Endpoint                                         | Method             | Description                                                                                          |
| ------------------------------------------------ | ------------------ | ---------------------------------------------------------------------------------------------------- |
| `/api/registration/`                             | POST               | Register a new user (customer or business)                                                           |
| `/api/login/`                                    | POST               | Log in and receive an authentication token                                                           |
| `/api/base-info/`                                | GET                | Get aggregated site statistics (reviews, avg rating, businesses, offers)                             |
| `/api/profile/{pk}/`                             | GET, PATCH         | Retrieve or update your own profile (customer or business)                                           |
| `/api/profiles/business/`                        | GET                | List all business profiles                                                                           |
| `/api/profiles/customer/`                        | GET                | List all customer profiles                                                                           |
| `/api/offers/`                                   | GET, POST          | List all offers (with filtering, search, ordering, pagination) or create a new offer (business only) |
| `/api/offers/{id}/`                              | GET, PATCH, DELETE | Retrieve, update (owner only), or delete (owner only) an offer                                       |
| `/api/offerdetails/{id}/`                        | GET                | Retrieve a single OfferDetail (price, delivery, features)                                            |
| `/api/orders/`                                   | GET, POST          | List all your orders or create a new order (customer only)                                           |
| `/api/orders/{id}/`                              | GET, PATCH, DELETE | Retrieve, update status (business only), or delete (staff only) an order                             |
| `/api/order-count/{business_user_id}/`           | GET                | Get count of in-progress orders for a given business user                                            |
| `/api/completed-order-count/{business_user_id}/` | GET                | Get count of completed orders for a given business user                                              |
| `/api/reviews/`                                  | GET, POST          | List all reviews (with filtering/ordering) or create a new review (customer only, no duplicates)     |
| `/api/reviews/{id}/`                             | GET, PATCH, DELETE | Retrieve, update (reviewer only), or delete (reviewer only) a review                                 |

---

## ⚙️ Project Structure

```
coderr-backend/
├── auth_app/            # Registration & login endpoints
├── base_info_app/       # Aggregated site-wide info endpoint
├── profile_app/         # BusinessProfile & CustomerProfile models, serializers, views
├── offers_app/          # Offers & OfferDetail models, serializers, views
├── orders_app/          # Order models, serializers, views, and count endpoints
├── reviews_app/         # Review models, serializers, views
├── core/                # Django project settings and root URL configuration
├── manage.py            # Django management CLI
└── requirements.txt     # Python dependencies
```

---

## ❌ License

This project is part of a learning exercise at the Developer Akademie.
There is **no license** associated with this code.

---

## 🙌 Contributing

This repository is for training purposes. Contributions are not expected.
