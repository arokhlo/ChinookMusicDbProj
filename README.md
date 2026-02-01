# 🎵 Chinook Music Database

A comprehensive music database web application built with Django that allows users to explore, manage, and interact with music data including artists, albums, and tracks.

## 🌟 Features

### User Features
- **User Registration & Authentication**: Secure signup with security questions
- **Password Recovery**: Security question-based password reset (no email required)
- **Profile Management**: Update profile information and avatar
- **Music Exploration**: Browse artists, albums, and tracks
- **Search Functionality**: Search by artist, album, or track name
- **Review System**: Rate and review tracks
- **Responsive Design**: Mobile-friendly interface

### Admin Features
- **User Management**: Activate/deactivate users, assign roles
- **Content Management**: Add, update, and delete artists and albums
- **Security Groups**: Admin, Superuser, Staff, and Regular user roles
- **Protected Users**: Special protection for admin accounts

### Security Features
- Security question authentication
- Role-based access control
- Protected user accounts
- Secure password handling
- CSRF protection

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL (for production) or SQLite (for development)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chinook-music-db.git
   cd chinook-music-db