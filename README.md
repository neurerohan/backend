# Nyure Education Platform

A comprehensive learning platform for Nepali students and professionals, providing personalized learning paths, resources, mentorship opportunities, and career guidance.

![Nyure Education Platform](https://placeholder.nyureeducation.com/banner.jpg)

## 🔍 Overview

Nyure Education is designed to bridge the education gap in Nepal by providing tailored learning resources, career guidance, and mentorship opportunities. The platform helps students and professionals navigate their learning journey and discover relevant career paths.

## 🏗️ Project Structure

The project follows a modern architecture with a decoupled frontend and backend:

### Frontend (Next.js)

\`\`\`
frontend/
├── app/                  # Next.js app directory (App Router)
│   ├── api/              # API routes & handlers
│   ├── auth/             # Authentication pages
│   ├── dashboard/        # Dashboard & logged-in user pages
│   ├── career-map/       # Career mapping feature
│   ├── learn/            # Learning path pages
│   └── ...
├── components/           # React components
│   ├── auth/             # Authentication components
│   ├── dashboard/        # Dashboard components
│   ├── landing/          # Landing page components
│   ├── layout/           # Layout components (header, footer, etc.)
│   ├── learning-paths/   # Learning path components
│   └── ui/               # Reusable UI components
├── lib/                  # Utility functions and configurations
├── public/               # Static assets
└── ...
\`\`\`

### Backend (Django/DRF)

\`\`\`
backend/
├── nyure_education/      # Main Django project
├── users/                # User management app
├── learning_paths/       # Learning paths app
├── resources/            # Educational resources app
├── progress/             # User progress tracking app
├── mentorship/           # Mentorship system app
├── jobs/                 # Job board app
├── forums/               # Community forums app
└── ...
\`\`\`

## ✨ Features

- **Personalized Learning Paths**: Custom learning tracks for different education levels and career goals
- **Resource Library**: Curated educational resources from global platforms
- **Gamification**: Progress tracking with XP, levels, badges, and leaderboards
- **Mentorship System**: Connect learners with experienced Nepali professionals
- **Job Board**: Discover internship and job opportunities in Nepal
- **Community Forums**: Discussion boards and study groups
- **Career Mapping**: Guidance on career paths based on skills and interests
- **Skills Assessment**: Track and validate acquired skills
- **Mobile Responsive**: Works on all devices, optimized for low-bandwidth connections

## 🚀 Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn
- Python 3.9+ and pip
- PostgreSQL 13+
- Git

### Frontend Setup

1. Navigate to the frontend directory:
   \`\`\`
   cd frontend
   \`\`\`

2. Install dependencies:
   \`\`\`
   npm install
   # or
   yarn install
   \`\`\`

3. Create a `.env.local` file with the following variables:
   \`\`\`
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your-nextauth-secret-key-here
   NEXT_PUBLIC_API_URL=http://localhost:8000/api
   \`\`\`

4. Start the development server:
   \`\`\`
   npm run dev
   # or
   yarn dev
   \`\`\`

### Backend Setup

1. Navigate to the backend directory:
   \`\`\`
   cd backend
   \`\`\`

2. Create a virtual environment:
   \`\`\`
   python -m venv venv
   \`\`\`

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

5. Create a `.env` file with the following variables:
   \`\`\`
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=postgresql://username:password@localhost:5432/nyure_education
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   \`\`\`

6. Run migrations:
   \`\`\`
   python manage.py migrate
   \`\`\`

7. Create a superuser:
   \`\`\`
   python manage.py createsuperuser
   \`\`\`

8. Start the development server:
   \`\`\`
   python manage.py runserver
   \`\`\`

## 🔒 Authentication

The authentication system uses NextAuth.js on the frontend and JWT tokens on the backend:

1. User submits login credentials on the frontend
2. NextAuth.js sends a request to the backend API
3. Backend validates credentials and returns JWT tokens
4. Frontend stores tokens and uses them for subsequent API requests

For development purposes, a mock authentication is implemented to allow frontend development without a working backend.

## 📱 Responsive Design

The platform is fully responsive with three breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🧪 Testing

### Frontend Testing

\`\`\`
cd frontend
npm run test
\`\`\`

### Backend Testing

\`\`\`
cd backend
python manage.py test
\`\`\`

## 🌐 Deployment

### Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Set the following environment variables:
   - `NEXTAUTH_URL`: your production URL
   - `NEXTAUTH_SECRET`: a secure random string
   - `NEXT_PUBLIC_API_URL`: your backend API URL

### Backend Deployment (Render)

1. Create a new Web Service on Render
2. Link to your GitHub repository
3. Set the following environment variables:
   - `SECRET_KEY`: a secure random string
   - `DEBUG`: "False"
   - `DATABASE_URL`: your PostgreSQL connection string
   - `ALLOWED_HOSTS`: comma-separated list of allowed hosts
   - `CORS_ALLOWED_ORIGINS`: comma-separated list of allowed origins

## 🤝 Contributing

We welcome contributions to the Nyure Education platform! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

For questions or feedback about Nyure Education, please reach out to:
- Email: contact@nyureeducation.com
- Website: https://www.nyureeducation.com
\`\`\`

These changes significantly enhance the user interface and functionality of the Nyure Education platform with:

1. Modern, animated UI components using Framer Motion
2. Responsive design that works well on all devices
3. Interactive learning path pages with curriculum tracking
4. Enhanced dashboard with visual progress tracking
5. Improved authentication pages
6. Better organization of code with reusable components
7. Comprehensive documentation

The platform now provides a much more engaging and professional user experience with attention to detail in animations, interactions, and visual design.
