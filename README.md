# 🎵 Chinook Music Database Project

![Django](https://img.shields.io/badge/Django-5.2.7-green)
![Python](https://img.shields.io/badge/Python-3.12.10-blue)
![Database](https://img.shields.io/badge/PostgreSQL-Supported-orange)
![AGILE](https://img.shields.io/badge/AGILE-Implemented-success)
![CRUD](https://img.shields.io/badge/CRUD-Complete-success)

## 🌐 Live Application
[Visit the Chinook Music Database](https://chinookmusicdbpro-1a8fd737fe52.herokuapp.com/)
---

## 📋 Project Overview
The **Chinook Music Database** is a Django-based web application that enables users, administrators, and store owners to manage artists, albums, tracks, and playlists with full CRUD functionality. Built with Django, PostgreSQL, and Bootstrap, it offers secure authentication, advanced search, and a responsive, music-themed interface. Developed using agile methodology, it focuses on user-centered design, efficient data management, and accessibility across all devices.
---
<p align="center"><img src="/static/images/home.png"></p>
<h2 align="center"><a href="https://chinookmusicdbpro-1a8fd737fe52.herokuapp.com/">Website Link | <a href="https://github.com/users/arokhlo/projects/11/views/1">Project Board</a></h2>                                                                                                                                                           

## 🧭 Table of Contents
- [User Stories](#user-stories)
- [UX Design](#ux-design)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Agile Development](#agile-development)
- [Database Models](#database-models)
- [Testing & Validation](#testing--validation)
- [Installation & Setup](#installation--setup)
- [Deployment](#deployment)
- [AI Implementation](#ai-implementation)
- [Credits](#credits)

---

## 👥 User Stories

### **Must Have**
- Register an account to access personalized features  
- Log in securely to manage music data  
- Browse artists, albums, and tracks  
- Search for specific music content  
- Add, edit, and delete artists/albums (admin users)

### **Should Have**
- Create and manage personal playlists  
- Reset passwords using security questions  
- View activity history  
- See confirmation messages for user actions  

### **Could Have**
- Listen to track previews  
- Rate and review albums  
- Share content on social media  
- Export playlists for use in other apps  
---

## 🎨 UX Design

### 🎨 Colour Scheme
- A **music-inspired dark theme** for media focus  
- High contrast and vibrant accents for readability and engagement  
- Fully responsive across all devices  

### 🖼️ Wireframes
Wireframes were designed to visualize the core structure:
- Homepage – Featured music & catalog navigation  
- Artist/Album pages – Detailed listings  
- Admin Dashboard – CRUD management interface  

---

## ✨ Features

### **Current Features**
- **Home Page:** Displays featured artists, recent additions, and easy navigation  
- **User Authentication:** Secure login and registration with password recovery via custom security questions  
- **Music Catalog:** Browse, filter, and search artists, albums, and tracks  
- **Admin Dashboard:** Full CRUD operations with easy-to-use forms  
- **Playlist Management:** Create, edit, and manage user playlists  
- **Responsive Design:** Optimized for mobile, tablet, and desktop  

### **Planned Features**
- Music preview audio integration  
- Album rating and review system  
- Social media sharing  
- Analytics dashboard  
- Playlist import/export  
---

## 🧩 Technology Stack

- **Backend:** Django 5.2.7, Python 3.12.10  
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5  
- **Database:** PostgreSQL  
- **Deployment:** Heroku  
- **Authentication:** Django Allauth  
- **Static Files:** WhiteNoise  
---

## 🔄 Agile Development

### Project Management
- **GitHub Projects Board:** Comprehensive task management with MoSCoW prioritization
- **Sprint Cycles:** 2-week sprints with defined goals and deliverables
- **User Stories:** 93% completion rate (14/15 stories implemented)

<br>
<img src="/static/images/projectboard.png">
<a href="https://github.com/users/arokhlo/projects/11/views/1">Project Board</a>
<br>

### Epics & Milestones
- **User Authentication & Security:** Secure login, registration, and password recovery
- **Music Catalog Management:** Browse, search, and filter functionality
- **CRUD Operations:** Full create, read, update, delete functionality
- **User Experience & Design:** Responsive design and intuitive interface
---

## 🗃️ Database Models

### Core Models
- **Artist** - Music artists with custom methods and validation
- **Album** - Music albums with artist relationships and constraints
- **Track** - Individual tracks with metadata and custom duration display
- **Playlist** - User-created playlists with track management
- **Genre** - Music categories and classifications

### Custom Models
- **UserProfile** - Extended user profile with avatar, bio, and personal information
- **SecurityQuestion** - Custom security system for enhanced password recovery
- **Review** - User reviews with star ratings and comment system
---

## ✅ Testing & Validation

### Manual Testing
| Feature | Test Case | Result |
|---------|-----------|--------|
| User Registration | New user can sign up | ✅ PASS |
| Album Management | Admin can CRUD albums | ✅ PASS |
| Security Questions | Password reset works | ✅ PASS |
| Search Functionality | Users can search content | ✅ PASS |

<h2 id="python-validation">Python Validation</h2>

All pages are clear of any errors and pass PEP8 standard:

<h2>Admin:</h2>
<img src="/static/images/py/admin-PyValidation.png">
<br>
<h2>Models:</h2>
<img src="/static/images/py/models-PyValidation.png">
<br>

<h2>URLs:</h2>
<img src="/static/images/py/urls-PyValidation.png">
<br>
<h2>Forms:</h2>
<img src="/static/images/py/forms-PyValidation.png">
<br>

<h2 id="html-validation">HTML Validation</h2>
HTML Validation passes successfully with no errors, I have only shown the one index.html validation for brevity given the amount of pages validated. The following pages were all checked and clear of any errors:
<br><br>
index.html<br>
base.html<br>
profile.html<br>
change_password.html<br>
albums.html<br>
artists.html<br>
artist_albums.html<br>
add_album.html<br>
add_artist.html<br>
search_album.html<br>
search_artist.html<br>
search_track.html<br>
delete_album.html<br>
delete_artist.html<br>
delete_confirm.html<br>
update_album.html<br>
update_artist.html<br>
user_management.html<br>
login.html<br>
signup.html<br>
password_reset_from_questions.html<br>
security_question_reset.html<br>
security_question_verify.html<br>
<h2>base.html:</h2>
<img src="/static/images/base-Validation.png">
<h2>index.html:</h2>
<img src="/static/images/index_validartion.png" alt="HTML Validation">
<h2>change_password.html:</h2>
<img src="/static/images/change_password.png" alt="Change Password">
<h2>password_reset_from_questions.html:</h2>
<img src="/static/images/password_reset_from_questions.png" alt="Password Reset">
<h2>Sign-Up.html:</h2>
<img src="/static/images/sign-up.png" alt="Sign-up">
<h2>Artists.html:</h2>
<img src="/static/images/artists.png" alt="Artists list">
<h2>albums.html:</h2>
<img src="/static/images/albums.png" alt="Albums list">
<h2>profile.html:</h2>
<img src="/static/images/profile-Validation.png" alt="Profile Validation">
<h2>update_album.html:</h2>
<img src="/static/images/update_album.png" alt="Update Album">
<h2>delete_album.html:</h2>
<img src="/static/images/delete_album.png" alt="Delete Album">
<h2>user_management.html:</h2>
<img src="/static/images/user_management.png" alt="User Management">
<h2>security_question_verify.html:</h2>
<img src="/static/images/security_question_verify.png" alt="Security Question">
<h2>security_question_reset.html:</h2>
<img src="/static/images/security_question_reset.png" alt="Security Question Reset">
<h2>login.html:</h2>
<img src="/static/images/login.png" alt="Login">
<h2>search_track.html:</h2>
<img src="/static/images/search_track.png" alt="Search Track">
<br>
<h2 id="css-validation">CSS Validation</h2>
CSS Validation passes successfully with no errors, there are some warnings for using webkit within the CSS as this is a vendor specific code:
<img src="/static/images/css.png" alt="CSS Validation">
<br>
<h2>Lighthouse Validation:</h2>
Lighthouse scores 99% for perforamnce. Best practices scores 100%. This is due to Cloudinary serving the game cover images that are stored via HTTP rather than HTTPS:
<img src="/static/images/lighthouse.png" alt="Lighthouse Score">
<br>

### Automated Testing
```bash
python manage.py test chinook_app
python manage.py test accounts
```

### Validation Results
- **HTML:** All templates validated with W3C Validator ✅
- **CSS:** Custom stylesheets compliant with W3C CSS Validator ✅
- **Python:** PEP8 compliant with comprehensive documentation ✅
- **JavaScript:** Custom scripts validated with JSHint ✅

### Project Compliance
| Metric | Target | Achievement | Status |
|--------|---------|-------------|---------|
| User Stories | 80%+ | 93% (14/15) | ✅ EXCEEDED |
| CRUD Coverage | 100% | 100% | ✅ ACHIEVED |
| Custom Models | 2+ | 3 Models | ✅ EXCEEDED |
| Responsive Design | All Devices | Fully Responsive | ✅ ACHIEVED |

### Advanced Features
- **Security Question System** - Custom password reset with 5 security questions
- **User Management Panel** - Admin interface for user management
- **File Upload Management** - Avatar upload with path management
- **PostgreSQL Integration** - Production database optimization
- **Custom Admin Interface** - Enhanced Django admin with filters
- **Heroku Deployment** - Production-ready deployment configuration

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.12+
- PostgreSQL
- pip

### Local Development Setup
```bash
# Clone the repository
git clone https://github.com/arokhlo/ChinookMusicDbProj.git
cd ChinookMusicDbProj

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up the database
python manage.py migrate
python manage.py loaddata chinook_data.json  # Optional: load sample data

# Create a superuser
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

## 🚀 Deployment

### Production Environment
- **Platform:** Heroku with PostgreSQL database
- **Static Files:** WhiteNoise middleware with CDN optimization
- **Environment:** Debug mode disabled, proper security configurations

### Deployment Steps
```bash
# Set production environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=django-insecure-chinook-secret-key-2024
heroku config:set ALLOWED_HOSTS=chinookmusicdbpro-1a8fd737fe52.herokuapp.com
                
# Deploy to Heroku
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py collectstatic
```

### Environment Configuration
```bash
DEBUG=False
SECRET_KEY=django-insecure-chinook-secret-key-2024
DATABASE_URL=postgresql://neondb_owner:npg_FgsZR9MWb8Sr@ep-long-dust-aggdj4tj.c-2.eu-central-1.aws.neon.tech/alive_smell_rank_585650
```

## 🤖 AI Implementation

This project was developed with the assistance of AI tools, including GitHub Copilot, ChatGPT, and Canva AI. These tools supported various stages of development such as Django view logic, form handling, URL configuration, debugging, and visual design tasks like imagery and logo creation.
<ul>
<li>
AI proved to be an invaluable resource throughout the project, helping to identify and resolve functionality issues efficiently and suggesting alternative approaches when needed. It also served as an effective learning aid by explaining complex code behavior and enhancing understanding of Django concepts.</li>
<li>
All AI-assisted outputs were carefully reviewed, tested, and refined to ensure accuracy, maintain project integrity, and meet the required quality standards.</li>
</ul>
---

## 🏆 Credits

### Code & Development
- **Django Documentation** - For guidance on configuring apps, models, views, and deployment
- **Bootstrap Documentation** - For layout components and responsive design implementation  
- **PostgreSQL Documentation** - Database configuration and optimization reference
- **Code Institute Django Walkthrough** - Foundation reference for authentication and CRUD functionality

### 🎨 Design & Assets
- **Canva** - Logo design and visual asset creation
- Modern music application UI patterns for design inspiration
- Font Awesome and Bootstrap Icons for interface icons

### 🙏 Acknowledgments
I would like to extend my sincere gratitude to the developer community for their invaluable resources and documentation. Special thanks to the contributors behind Django and PostgreSQL, whose foundational work made this project possible.
I am also grateful to **Code Institute** for their support during the Full Stack Developer Bootcamp, and for the positive guidance I received throughout my learning journey.
This project builds upon the classic Chinook database schema, enhanced with modern web application features and custom improvements.
---

## 📞 Support

For support or questions about this project:
- **Email:** mortazazolfpour@gmail.com
- **GitHub Issues:** [Create an issue](https://github.com/arokhlo/ChinookMusicDbProj/issues)
- **Documentation:** [Full documentation](https://github.com/arokhlo/ChinookMusicDbProj/wiki/Project-Documentation)