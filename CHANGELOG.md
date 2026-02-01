# Changelog

All notable changes to the Chinook Music Database project will be documented in this file.

## [1.0.0] - 2024-01-15

### Added
- Initial project setup with Django framework
- User authentication system with allauth
- Security question-based password reset
- CRUD operations for Artists, Albums, and Tracks
- User profile management with avatar upload
- Admin user management interface
- Review system for tracks
- Responsive Bootstrap 5 UI
- Deployment configuration for Heroku

### Security Fixes
- Removed sensitive data from codebase
- Implemented environment variables for all secrets
- Added proper .gitignore to exclude sensitive files
- Fixed DEBUG mode to be False in production
- Added CSRF and security middleware

### UX Improvements
- Fixed avatar image display issues
- Enhanced navigation from artists to albums
- Improved track browsing experience
- Added proper error messages and user feedback
- Enhanced responsive design for mobile devices

### Technical Improvements
- Code cleanup and validation
- Added comprehensive documentation
- Improved error handling
- Enhanced security decorators
- Added proper logging configuration

## [0.9.0] - 2024-01-10

### Added
- Basic CRUD functionality
- User authentication
- Security questions feature
- Initial deployment to Heroku

### Known Issues
- Avatar images not displaying
- Sensitive data exposed in codebase
- Incomplete UX documentation