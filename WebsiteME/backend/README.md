# WebsiteME Backend API

A comprehensive Node.js/Express backend API for the WebsiteME technology platform featuring real-time tech news, interactive forums, code sandbox, and advanced search capabilities.

## 🚀 Features

### Core APIs
- **Authentication & User Management**: JWT-based auth with role-based access control
- **Real-time Tech News**: Aggregation from multiple sources with AI-powered summaries  
- **Interactive Forums**: Q&A platform with reputation system and moderation
- **Live Code Sandbox**: Secure code execution environment with multiple language support
- **Advanced Search**: Full-text search across all content types with faceted filtering
- **External Integrations**: GitHub and Stack Overflow API integrations
- **Admin Dashboard**: Comprehensive administration interface with analytics

### Technical Features
- **Database**: MongoDB with Mongoose ODM
- **Authentication**: JWT tokens with refresh mechanism
- **Rate Limiting**: Configurable limits for different endpoints
- **Security**: Helmet.js security headers, CORS, input validation
- **Monitoring**: Health checks and performance metrics
- **Caching**: Redis integration for improved performance
- **Real-time**: Socket.io support for live features

## 📋 API Endpoints

### Authentication (`/api/auth`)
- `POST /register` - User registration
- `POST /login` - User login  
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /refresh` - Refresh JWT token

### News (`/api/news`)
- `GET /tech` - Get latest tech news with pagination
- `POST /summarize` - Generate AI-powered article summaries
- `GET /trending` - Get trending tech topics

### Forum (`/api/forum`)
- `GET /posts` - Get forum posts with filters
- `POST /posts` - Create new forum post
- `GET /posts/:id` - Get single post with replies
- `POST /posts/:id/reply` - Reply to a post
- `GET /qa` - Get Q&A section posts

### Code Sandbox (`/api/sandbox`)
- `POST /execute` - Execute code in secure sandbox
- `GET /templates` - Get code templates for different languages
- `GET /examples` - Get curated code examples and challenges
- `POST /save` - Save code snippet to user collection

### Search (`/api/search`)
- `GET /` - Advanced search across all content
- `GET /suggestions` - Get search autocomplete suggestions
- `GET /trending` - Get trending search terms
- `POST /track` - Track search analytics

### Integrations (`/api/integrations`)
- `GET /github/repos` - Get trending GitHub repositories
- `GET /github/user/:username` - Get GitHub user profile
- `GET /stackoverflow/questions` - Get trending Stack Overflow questions
- `GET /tech-feeds` - Aggregate tech content from multiple sources

### Admin (`/api/admin`)
- `GET /dashboard` - Get admin dashboard statistics
- `GET /users` - Get users list with management options
- `GET /content/moderation` - Get content moderation queue
- `GET /analytics` - Get detailed analytics and reports
- `GET /system/health` - Get system health metrics

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ 
- MongoDB 5.0+
- Redis (optional, for caching)

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Server
PORT=3001
NODE_ENV=development

# Database  
MONGODB_URI=mongodb://localhost:27017/websiteme

# Authentication
JWT_SECRET=your_super_secure_jwt_secret_here
JWT_EXPIRES_IN=7d

# External APIs
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_API_TOKEN=your_github_token_here
NEWSAPI_KEY=your_newsapi_key_here
```

### Installation
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Start production server  
npm start
```

## 📁 Project Structure

```
backend/
├── src/
│   ├── app.js                 # Main application entry point
│   ├── config/
│   │   └── database.js        # MongoDB connection configuration
│   ├── controllers/           # Route controllers (TODO)
│   ├── middleware/
│   │   ├── auth.js           # Authentication middleware
│   │   └── rateLimiter.js    # Rate limiting configurations
│   ├── models/
│   │   ├── User.js           # User model with authentication
│   │   └── Post.js           # Forum post model
│   ├── routes/
│   │   ├── auth.js           # Authentication routes
│   │   ├── news.js           # Tech news routes
│   │   ├── forum.js          # Forum and Q&A routes
│   │   ├── sandbox.js        # Code execution routes
│   │   ├── search.js         # Search and filtering routes
│   │   ├── integrations.js   # External API integrations
│   │   └── admin.js          # Admin dashboard routes
│   └── utils/                # Utility functions (TODO)
├── .env.example              # Environment variables template
└── package.json              # Project dependencies and scripts
```

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication with secure token handling
- Role-based access control (user, moderator, admin)
- Password hashing with bcrypt
- Account status management (active, suspended, pending)

### Rate Limiting
- General API: 100 requests per 15 minutes
- Authentication: 5 attempts per 15 minutes  
- Code execution: 10 runs per minute
- Search: 30 queries per minute
- Post creation: 10 posts per 15 minutes

### Security Headers & Validation
- Helmet.js for security headers
- CORS configuration
- Input validation and sanitization
- MongoDB injection prevention

## 🚀 Development

### Running in Development
```bash
npm run dev
```

### Code Quality
```bash
npm run lint
```

### Health Check
```bash
curl http://localhost:3001/health
```

## 📈 Future Enhancements

### Planned Features
- [ ] Real-time notifications with Socket.io
- [ ] File upload and management system
- [ ] Email notification system
- [ ] Advanced caching with Redis
- [ ] Elasticsearch integration for search
- [ ] API documentation with Swagger
- [ ] Comprehensive test suite
- [ ] Docker containerization
- [ ] CI/CD pipeline setup

### External Integrations
- [ ] NewsAPI.org for real-time news
- [ ] OpenAI API for article summaries
- [ ] GitHub API for repository data
- [ ] Stack Overflow API for Q&A content
- [ ] Social media APIs for trend analysis

## 🤝 Contributing

1. Create feature branch from `main`
2. Follow existing code style and patterns
3. Add comprehensive comments for new features
4. Test API endpoints thoroughly
5. Update documentation as needed

## 📄 License

MIT License - see LICENSE file for details