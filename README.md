# DojoTracker - Martial Arts Training Logger

A full-stack web application for martial artists to track their training sessions, monitor technique progress, and analyze their improvement over time.

## Features

### ✅ Completed Features
- **User Authentication** - Secure registration and login system
- **Training Session Logging** - Record duration, intensity, techniques, and notes
- **Technique Progress Tracking** - Monitor proficiency levels and mastery status
- **Dashboard Analytics** - View training statistics and recent activity
- **Responsive Design** - Works on desktop and mobile devices
- **Data Filtering** - Filter sessions by style, date range, and other criteria

### 🚧 Planned Features
- **External API Integrations** (Fitbit, Google Fit, etc.)
- **Advanced Analytics** - Charts and detailed progress reports
- **Social Features** - Share achievements and connect with other martial artists
- **Goal Setting** - Set and track training goals
- **Video Integration** - Attach technique demonstration videos

## Tech Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication tokens
- **SQLite** - Database (development)
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React 19** - User interface library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **CSS3** - Styling with custom CSS variables
- **Date-fns** - Date manipulation

## Project Structure

```
dojotracker/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── models/
│   │   ├── user.py           # User model
│   │   └── training.py       # Training and technique models
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   └── training.py       # Training session routes
│   ├── config.py             # Configuration settings
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── context/         # React context providers
│   │   └── styles/          # CSS styles
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── start_dev.py             # Development server startup script
├── test_connection.py       # Backend API testing script
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.8+ 
- Node.js 16+
- npm or yarn

### Option 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dojotracker
   ```

2. **Start development servers**
   ```bash
   python start_dev.py
   ```
   This will:
   - Check requirements
   - Install frontend dependencies
   - Start backend on http://localhost:8000
   - Start frontend on http://localhost:3000

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server**
   ```bash
   python app.py
   ```
   Backend will run on http://localhost:8000

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   Frontend will run on http://localhost:3000

## Testing

### Backend API Testing

Run the comprehensive backend test suite:

```bash
python test_connection.py
```

This will test:
- Basic API endpoints
- User registration and authentication
- Training session CRUD operations
- Technique progress tracking
- Statistics endpoints

### Manual Testing

1. **Open the application**
   - Visit http://localhost:3000
   - Register a new account
   - Log in with your credentials

2. **Test core features**
   - Create a training session
   - Add techniques to your library
   - View dashboard statistics
   - Filter and search sessions

## API Documentation

### Authentication Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate user
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile

### Training Endpoints

- `GET /api/training/sessions` - Get training sessions
- `POST /api/training/sessions` - Create training session
- `GET /api/training/sessions/:id` - Get specific session
- `PUT /api/training/sessions/:id` - Update training session
- `DELETE /api/training/sessions/:id` - Delete training session

### Technique Endpoints

- `GET /api/training/techniques` - Get technique progress
- `POST /api/training/techniques` - Create technique entry
- `PUT /api/training/techniques/:id` - Update technique progress
- `DELETE /api/training/techniques/:id` - Delete technique

### Analytics Endpoints

- `GET /api/training/stats` - Get training statistics
- `GET /api/training/styles` - Get user's martial arts styles

## Development

### Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///dojotracker.db
JWT_SECRET_KEY=your-jwt-secret-here
```

### Database Management

The SQLite database is automatically created when you first run the application. To reset the database:

```bash
cd backend
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"
```

### Adding New Features

1. **Backend Changes**
   - Add new models in `backend/models/`
   - Create new routes in `backend/routes/`
   - Update database schema if needed

2. **Frontend Changes**
   - Add new components in `frontend/src/components/`
   - Create new pages in `frontend/src/pages/`
   - Add new services in `frontend/src/services/`
   - Update styles in `frontend/src/styles/`

## Deployment

### Backend Deployment

1. **Production Environment**
   - Use PostgreSQL instead of SQLite
   - Set production environment variables
   - Use a proper WSGI server (Gunicorn, uWSGI)

2. **Environment Variables for Production**
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:password@host:port/database
   JWT_SECRET_KEY=your-production-jwt-secret
   ```

### Frontend Deployment

1. **Build for production**
   ```bash
   cd frontend
   npm run build
   ```

2. **Deploy built files**
   - Upload `dist/` folder to your web server
   - Configure proper routing for SPA

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python version (3.8+ required)
   - Ensure virtual environment is activated
   - Verify all dependencies are installed

2. **Frontend won't start**
   - Check Node.js version (16+ required)
   - Delete `node_modules` and run `npm install`
   - Check for port conflicts

3. **API connection fails**
   - Ensure backend is running on port 8000
   - Check CORS settings
   - Verify API base URL in frontend

4. **Database issues**
   - Delete `dojotracker.db` and restart backend
   - Check database permissions
   - Verify SQLAlchemy configuration

### Getting Help

- Check the [Issues](https://github.com/your-repo/dojotracker/issues) page
- Run the test script: `python test_connection.py`
- Check browser console for frontend errors
- Check backend logs for API errors

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with modern web technologies
- Designed for martial artists, by martial artists
- Open source and community-driven

---

**Happy Training! 🥋**