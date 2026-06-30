# 🎓 EduSphere – Unified Academic, Portfolio & Career Development Platform

EduSphere is a full-stack web application built with **Python, Django, Bootstrap, JavaScript, and SQLite** that unifies academic management, portfolio creation, faculty verification, and placement activities into a single platform.

The platform enables students to build verified digital portfolios throughout their academic journey while helping faculty and placement officers efficiently manage academics, achievements, internships, and recruitment processes.

---

## 🌐 Live Demo

🚀 **Live Website:** https://edusphere-zwqh.onrender.com/

💻 **GitHub Repository:** https://github.com/Hrutuja-11/EduSphere

---

# 📌 Key Features

## 👨‍🎓 Student Portal

- Secure Login & Registration
- Personal Dashboard
- Update Profile & Profile Picture
- Academic Information
- Portfolio Management
- Add Projects
- Add Certifications
- Add Achievements
- Skills Management
- Public Portfolio
- Resume Generation
- Transcript Generation

---

## 👩‍🏫 Faculty Portal

- Verify Student Projects
- Verify Certifications
- Verify Achievements
- Add Student Endorsements
- Upload Grades
- Mark Attendance

---

## 👨‍💼 HOD Portal

- Department Management
- Faculty Assignment
- Academic Monitoring

---

## 💼 Placement Officer Portal

- Placement Drive Management
- Internship Tracking
- Student Shortlisting
- Verified Portfolio Access

---

## 🔐 Authentication & Security

- Custom User Model
- Role-Based Access Control (RBAC)
- Django Authentication
- Session Management
- Password Hashing
- CSRF Protection

---

# 🛠 Tech Stack

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Django Templates

### Backend

- Python
- Django
- Django ORM

### Database

- SQLite

### Libraries

- Pillow
- WhiteNoise
- Gunicorn

### Tools

- Django Admin
- Git
- GitHub
- Render

---

# 🏗 System Architecture

```
                       Users
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
   Student           Faculty             HOD
      │                  │                  │
      └──────────────────┼──────────────────┘
                         │
                 Authentication
                         │
             Role-Based Access Control
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
  Academics         Portfolio         Placements
      │                  │                  │
      └──────────────────┼──────────────────┘
                         │
                   SQLite Database
```

---

# 📂 Project Modules

### Users

- Authentication
- User Profiles
- Role Management

### Academics

- Courses
- Departments
- Attendance
- Grades
- Timetable

### Portfolio

- Projects
- Certifications
- Skills
- Achievements
- Public Portfolio
- Faculty Verification

### Placements

- Placement Drives
- Internship Tracking
- Student Eligibility

---

# 📊 Database Models

- CustomUser
- StudentProfile
- FacultyProfile
- HODProfile
- PlacementOfficerProfile
- Department
- Course
- Attendance
- Project
- Certification
- Achievement
- Skill
- PlacementDrive

---

# ✨ Highlights

- Full-Stack Django Application
- Custom Authentication System
- Role-Based Authorization (RBAC)
- Dynamic Portfolio Generation
- Faculty Verification Workflow
- CRUD Operations
- File Upload Support
- Responsive UI
- Modular Project Structure
- Django Admin Integration

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/Hrutuja-11/EduSphere.git
```

## Navigate to Project

```bash
cd EduSphere
```

## Create Virtual Environment

```bash
python -m venv .venv
```

## Activate Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Apply Migrations

```bash
python manage.py migrate
```

## Collect Static Files

```bash
python manage.py collectstatic
```

## Run Development Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000
```

---


# 🔮 Future Enhancements

- PostgreSQL Integration
- Django REST Framework APIs
- React Frontend
- JWT Authentication
- AI Resume Analyzer
- AI Career Recommendations
- Email Notifications
- Cloud Storage (AWS S3 / Cloudinary)
- Docker Support
- CI/CD Pipeline
- Analytics Dashboard

---

# 📚 Learning Outcomes

This project helped strengthen my understanding of:

- Python Programming
- Django Framework
- Django ORM
- Model-View-Template (MVT) Architecture
- Authentication & Authorization
- Role-Based Access Control
- CRUD Operations
- File Upload Handling
- Static & Media File Management
- Database Relationships
- Git & GitHub
- Deployment on Render

-
