# 🎓 Education Consultation Management

A backend-focused **Education Consultation Management API** built with **Django, Django REST Framework, PostgreSQL, and Docker**.

> 🎯 **Main Goal:** Learning by Building — with a focus on **Django REST Framework, backend architecture, appointment scheduling, permissions, business logic, and database-driven systems**.

---

## 📌 About The Project

**Education Consultation Management** is a backend system designed for managing educational advisors, consultation schedules, time slots, and online appointments.

The project focuses on building a reliable scheduling workflow where advisors can define their availability, automatically generate consultation slots, and manage their appointments while students can browse and book available time slots.

Rather than implementing simple CRUD operations, the project focuses on applying real backend concepts such as **role-based permissions, ownership validation, transactional operations, scheduling logic, and database relationships**.

---

## ✨ Features

* 🔐 Authentication & role-based permissions
* 👨‍🏫 Advisor schedule management
* 📅 Automatic appointment slot generation
* 🕐 Online consultation booking
* 🔄 Slot status management
* 👨‍🎓 Student appointment management
* 🛡️ Advisor ownership validation
* 🗄️ PostgreSQL database
* 📖 Swagger / OpenAPI documentation
* 🐳 Docker & Docker Compose

---

## 🧠 Core Scheduling System

The scheduling system is one of the main components of the project.

Instead of manually creating every available appointment, advisors can define their working time and scheduling rules. The backend then generates the appropriate consultation slots automatically.

```text
Schedule
   │
   ├── Start / End Time
   ├── Slot Duration
   ├── Break Duration
   └── Maximum Slots
          │
          ▼
   Slot Generation Service
          │
          ▼
   Available Appointment Slots
```

This approach separates the **schedule definition** from the actual **appointment slots**, making the scheduling workflow easier to manage and extend.

---

## 📅 Appointment Booking

Students can book available consultation slots through the API.

The booking flow is based on slot availability:

```text
AVAILABLE
    │
    ▼
  BOOKED
    │
    ▼
 CANCELED
```

The backend validates the booking before creating the appointment and prevents invalid state transitions.

Appointments are created only when a student successfully books an available slot.

---

## 🔐 Authentication & Permissions

The application uses role-based access control with two main roles:

### 👨‍💼 ADMIN

Represents an educational advisor.

Advisors can:

* Create and manage their schedules
* Generate and manage their slots
* Change valid slot statuses
* Manage their own appointment availability

### 👨‍🎓 STUDENT

Students can:

* View available consultation slots
* Book available consultation slots
* Manage their own appointments according to the defined business rules

Access control is enforced at the API level, including **advisor ownership validation** to prevent one advisor from modifying another advisor's schedules or slots.

---

## ⚙️ Business Logic

A major focus of the project was keeping scheduling rules inside the backend rather than relying on the client.

Examples include:

* Preventing students from booking unavailable slots
* Preventing invalid slot status changes
* Preventing modifications to past slots
* Validating that a slot belongs to the correct schedule
* Validating advisor ownership
* Ensuring appointment creation happens only after successful booking

This keeps the API responsible for maintaining the consistency of the scheduling system.

---

## 🛠️ Tech Stack

| Technology               | Purpose             |
| ------------------------ | ------------------- |
| 🐍 Django                | Backend framework   |
| 🚀 Django REST Framework | REST API            |
| 🐘 PostgreSQL            | Relational database |
| 🐳 Docker                | Containerization    |
| 📖 drf-spectacular       | Swagger / OpenAPI   |
| 🧪 Django Test Framework | Automated testing   |

---

## 🐳 Running With Docker

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Education-Consultation-Management
```

### 2. Start the application

```bash
docker compose up --build
```

### 3. Run migrations

```bash
docker compose exec web python manage.py migrate
```

The application can then be accessed through the configured API port.

---

## 📚 API Documentation

The project uses **drf-spectacular** to provide OpenAPI documentation and Swagger UI.

Swagger provides an interactive interface for exploring and testing the API endpoints.

---

## 🎯 Learning Focus

This project was primarily built as a **hands-on learning project** to gain practical experience with Django and backend engineering.

The main learning areas were:

* 🐍 Django & Django REST Framework
* 🏗️ Backend architecture
* 🔐 Authentication & permissions
* 🗄️ Django ORM & PostgreSQL
* 📅 Scheduling and appointment systems
* ⚙️ Business logic implementation
* 🐳 Dockerized development
* 📖 API documentation

The project helped me move beyond basic CRUD development and understand how to implement **real-world backend workflows and business rules**.

---

## 🚀 Future Improvements

Possible improvements for a more production-ready version include:

* [ ] Advanced appointment cancellation workflows
* [ ] Notification system for appointments
* [ ] Redis caching
* [ ] Background task processing
* [ ] CI/CD pipeline
* [ ] Production deployment
* [ ] More comprehensive test coverage

> **Build it. Test it. Understand it. Improve it. 🚀**
