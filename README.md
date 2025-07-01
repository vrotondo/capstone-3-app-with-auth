# 🥋 DojoTracker

**A full-stack web application for martial artists to track their training sessions, monitor technique progress, manage workout plans, and analyze their improvement over time.**

![DojoTracker](https://img.shields.io/badge/Status-Production%20Ready-green)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-blue)
![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB)
![Flask](https://img.shields.io/badge/Backend-Flask-000000)

## ✨ Features

### 🔐 **Authentication & User Management**
- Secure user registration and login system
- JWT-based authentication with token management
- Protected routes and user session handling
- User profile management

### 🥋 **Training & Technique Management**
- **Training Session Logging** - Record duration, intensity, techniques, and notes
- **Technique Progress Tracking** - Monitor proficiency levels and mastery status
- **Technique Library** - Browse and bookmark martial arts techniques
- **Personal Technique Collection** - Save and organize your favorite techniques

### 💪 **Exercise & Workout Management**
- **Exercise Database** - Access thousands of exercises via wger API integration
- **Favorites System** - Save your favorite exercises for quick access
- **Workout Plan Creation** - Build custom workout routines
- **Exercise Categorization** - Filter by muscle groups, equipment, and difficulty
- **Martial Arts Focus** - Exercises specifically relevant for martial arts training

### 📊 **Analytics & Progress**
- **Dashboard Analytics** - View training statistics and recent activity
- **Progress Tracking** - Monitor improvement over time
- **Data Filtering** - Filter sessions by style, date range, and other criteria

### 🌐 **Integration & Compatibility**
- **wger API Integration** - Access professional exercise database
- **Responsive Design** - Works seamlessly on desktop and mobile devices
- **External API Support** - Ready for future integrations (Fitbit, Google Fit, etc.)

## 🛠️ Tech Stack

### **Backend**
- **Flask** - Python web framework
- **PostgreSQL** - Production-ready relational database
- **SQLAlchemy** - Database ORM with model relationships
- **JWT Extended** - Secure authentication tokens
- **Flask-CORS** - Cross-origin resource sharing
- **psycopg2** - PostgreSQL adapter
- **python-dotenv** - Environment variable management

### **Frontend**
- **React 19** - Modern user interface library
- **React Router** - Client-side routing and navigation
- **Axios** - HTTP client for API communication
- **CSS3** - Custom styling with CSS variables
- **Vite** - Fast development build tool

### **External APIs**
- **wger API** - Exercise database and workout management
- **RESTful Architecture** - Clean API design patterns

## 📁 Project Structure

```
dojotracker/
├── backend/
│   ├── app.py                      # Main Flask application
│   ├── models/
│   │   ├── user.py                 # User and authentication models
│   │   ├── training.py             # Training session models
│   │   ├── technique_library.py    # Technique and bookmark models
│   │   ├── exercise.py             # Exercise and category models
│   │   └── workout.py              # Workout plans and favorites
│   ├── routes/
│   │   ├── auth.py                 # Authentication endpoints
│   │   ├── training.py             # Training session routes
│   │   ├── techniques.py           # Technique management
│   │   ├── exercises.py            # Exercise database routes
│   │   ├── workout.py              # Workout plans and favorites
│   │   ├── wger.py                 # wger API integration
│   │   └── user.py                 # User profile management
│   ├── services/
│   │   └── wger_api.py             # wger API service layer
│   ├── .env                        # Environment configuration
│   ├── requirements.txt            # Python dependencies
│   └── migrate_sqlite_to_postgresql.py # Database migration tool
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── features/           # Feature-specific components
│   │   │   ├── layout/             # Layout components
│   │   │   └── common/             # Reusable components
│   │   ├── pages/                  # Main page components
│   │   ├── services/               # API service layers
│   │   ├── context/                # React context providers
│   │   └── styles/                 # CSS stylesheets
│   ├── package.json                # Node.js dependencies
│   └── vite.config.js              # Vite configuration
├── README.md                       # Project documentation
└── start_dev.py                    # Development server launcher
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8+
- Node.js 16+
- PostgreSQL 15+
- npm or yarn

### **1. Clone Repository**
```bash
git clone <repository-url>
cd dojotracker
```

### **2. Database Setup**

#### **Install PostgreSQL**
1. Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Remember your postgres user password during installation
3. Note the port (usually 5432 or 5433)

#### **Create Database**
```bash
# Using psql command line (adjust path and port as needed)
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -p 5433 -c "CREATE DATABASE dojotracker;"
```

### **3. Backend Setup**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **4. Environment Configuration**

Create `backend/.env` file:
```env
# Environment Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Secret Keys (CHANGE IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5433/dojotracker

# API Keys
WGER_API_KEY=your_wger_api_key_here

# Server Configuration
PORT=8000
HOST=127.0.0.1
```

### **5. Frontend Setup**

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### **6. Start Backend**

```bash
# In backend directory with virtual environment activated
python app.py
```

## 🌐 Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Documentation**: http://localhost:8000/api/debug/routes

## 🔧 Development

### **Running Tests**
```bash
# Backend API tests
cd backend
python test_connection.py
```

### **Database Migration**
If migrating from SQLite to PostgreSQL:
```bash
cd backend
python migrate_sqlite_to_postgresql.py
```

### **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | Flask session secret | Yes |
| `JWT_SECRET_KEY` | JWT token signing key | Yes |
| `WGER_API_KEY` | wger API access key | Optional |
| `FLASK_ENV` | Development/production mode | No |

## 📡 API Endpoints

### **Authentication**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile

### **Training Sessions**
- `GET /api/training/sessions` - Get training sessions
- `POST /api/training/sessions` - Create training session
- `GET /api/training/sessions/:id` - Get specific session
- `PUT /api/training/sessions/:id` - Update training session
- `DELETE /api/training/sessions/:id` - Delete training session

### **Techniques**
- `GET /api/techniques` - Browse technique library
- `POST /api/techniques/bookmark` - Bookmark technique
- `GET /api/techniques/bookmarks` - Get user bookmarks
- `DELETE /api/techniques/bookmark/:id` - Remove bookmark

### **Exercises & Workouts**
- `GET /api/exercises` - Browse exercise database
- `GET /api/exercises/search?q=query` - Search exercises
- `GET /api/workout/favorites` - Get favorite exercises
- `POST /api/workout/favorites` - Add exercise to favorites
- `DELETE /api/workout/favorites/:id` - Remove from favorites
- `GET /api/workout/plans` - Get workout plans
- `POST /api/workout/plans` - Create workout plan
- `POST /api/workout/plans/:id/exercises` - Add exercise to workout

### **Statistics**
- `GET /api/training/stats` - Get training statistics
- `GET /api/training/styles` - Get user's martial arts styles

## 🛠️ Production Deployment

### **Environment Variables for Production**
```env
FLASK_ENV=production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:password@host:port/database
JWT_SECRET_KEY=your-production-jwt-secret
```

### **Database Configuration**
- Use PostgreSQL with SSL enabled
- Set up connection pooling
- Configure backup strategy
- Enable query optimization

### **Build Frontend**
```bash
cd frontend
npm run build
```

### **Deploy Backend**
- Use a WSGI server (Gunicorn, uWSGI)
- Configure reverse proxy (Nginx)
- Set up SSL certificates
- Monitor with logging and health checks

## 🔍 Troubleshooting

### **Common Issues**

#### **Database Connection Failed**
- Verify PostgreSQL is running
- Check port configuration (5432 vs 5433)
- Confirm database exists and credentials are correct
- Test connection: `psql -U postgres -d dojotracker`

#### **JWT Token Issues**
- Clear browser localStorage/cookies
- Check JWT secret keys match between requests
- Verify token expiration settings

#### **wger API Issues**
- Verify API key in environment variables
- Check network connectivity
- Monitor API rate limits

#### **Frontend Build Issues**
- Delete `node_modules` and run `npm install`
- Check Node.js version compatibility
- Verify all dependencies are installed

### **Debug Endpoints**
- `GET /api/health` - API health check
- `GET /api/debug/jwt` - JWT configuration
- `GET /api/debug/routes` - All registered routes
- `GET /api/database/info` - Database connection status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **wger Project** - Exercise database and API ([wger.de](https://wger.de))
- **Flask Community** - Web framework and extensions
- **React Team** - Frontend library and ecosystem
- **PostgreSQL** - Robust database system

## 📞 Support

For support and questions:
- Check the [Issues](../../issues) page
- Run debug endpoints for troubleshooting
- Review the troubleshooting section above

---

**Happy Training! 🥋💪**