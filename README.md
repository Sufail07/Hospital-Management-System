# Hospital Management System

A Django-based backend system for managing hospitals, including modules for doctors, patients, appointments, medical history, and payments. This project is designed to streamline hospital operations by providing secure APIs for core hospital functionalities.

## Features

- **User Management:** Custom user model with roles for patients, doctors, and administrators.
- **Doctor Module:** Manage doctor profiles, specializations, schedules, and consultation fees.
- **Patient Module:** Register patients, store personal and insurance details, and manage emergency contacts.
- **Appointments:** Schedule, track, and manage appointments between patients and doctors.
- **Medical History:** Record and retrieve diagnoses, medications, allergies, and treatment history for each patient.
- **Payments:** Integrated with Stripe for secure payment processing for consultations and prescriptions.
- **Authentication & Permissions:** JWT-based authentication with REST framework permission classes.
- **API-First:** All functionalities exposed via RESTful APIs with browsable and JSON renderers.
- **CORS Enabled:** Ready for frontend integration (e.g., React at `localhost:3000`).

## Technologies Used

- **Backend Framework:** Django 5.2.4
- **API:** Django REST Framework
- **Authentication:** Simple JWT
- **Database:** SQLite (default, customizable)
- **Payment Gateway:** Stripe
- **Other:** django-cors-headers, django-filter

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Sufail07/Hospital-Management-System.git
   cd Hospital-Management-System
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   - Create `.env` file and add your Stripe keys.
     ```
     STRIPE_SECRET_KEY=your_stripe_secret_key
     STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
     ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser**
   ```bash
   python manage.py createsuperuser
   ```


7. **Create an Admin Object for the Superuser**
   Open the Django shell:

   ```bash
   python manage.py shell
   ```

   Then run the following in the shell, replacing `your_superuser_username` with your created superuser's username:

   ```python
   from django.contrib.auth import get_user_model
   from adminpanel.models import Admin  

   User = get_user_model()
   user = User.objects.get(username='your_superuser_username')
   Admin.objects.create(user=user)
   ```

   Exit the shell:

   ```python
   exit()
   ```

8. **Start the Server**
   ```bash
   python manage.py runserver
   ```

## Usage

- **Admin Panel:** `/admin/` for admin operations.
- **API Endpoints:** REST APIs for patients, doctors, appointments, medical history, and payments.
- **CORS:** By default, allows requests from `http://localhost:3000` for frontend integration.

## Project Structure

```
Hospital-Management-System/
│
├── Hospitality/         # Django project settings
├── core/                # Custom user models and authentication
├── doctors/             # Doctor models, views, serializers
├── patients/            # Patient models, views, serializers
├── adminpanel/          # Administration utilities
├── manage.py
└── requirements.txt
```

## Contribution Guidelines

Contributions are welcome! Please follow these steps:

1. Fork this repository.
2. Create your feature branch (`git checkout -b feature/my-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/my-feature`).
5. Open a pull request.

## License

This project is for educational and demonstration purposes. Please contact the repository owner for license details.


---

## 👨‍💻 Author

Built with ❤️ by [Sufail07](https://github.com/Sufail07) :))
