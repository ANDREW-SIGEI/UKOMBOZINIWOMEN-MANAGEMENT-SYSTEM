# UKOMBOZINI WOMEN MANAGEMENT SYSTEM

## Overview
A comprehensive management system for Ukombozini Women's Group that helps track members, manage meetings, handle finances, and coordinate community projects.

## Features
- **Member Management**: Track member details, roles, and participation
- **Meeting Management**: Schedule, document, and track meetings with agenda items
- **Financial Tracking**: Record contributions, expenses, and financial reports
- **Project Management**: Organize and track community development projects
- **Dashboard**: View key metrics and upcoming activities
- **Community Engagement**: Connect members and share announcements

## Technology Stack
- **Backend**: Django, Python
- **Frontend**: Bootstrap, JavaScript, HTML, CSS
- **Database**: SQLite (development), PostgreSQL (production)

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Pip package manager
- Virtual environment (recommended)

### Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/ANDREW-SIGEI/UKOMBOZINIWOMEN-MANAGEMENT-SYSTEM.git
   cd UKOMBOZINIWOMEN-MANAGEMENT-SYSTEM
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Project Structure
- **accounts**: User authentication and profile management
- **members**: Member information and management
- **meetings**: Meeting scheduling and documentation
- **finances**: Financial records and reporting
- **projects**: Community project tracking
- **dashboard**: Overview and analytics
- **community**: Announcements and communication

## Contributing
1. Fork the repository
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For any inquiries, please contact Ukombozini Women's Group at andrewsigei684@gmail.com.

## Acknowledgements
- All contributors who have helped build this system
- Ukombozini Women's Group leadership for their guidance 