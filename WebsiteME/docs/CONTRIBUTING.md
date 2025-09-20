# Contributing to WebsiteME

Thank you for your interest in contributing to WebsiteME! This guide will help you get started with contributing to our technology platform.

## 🚀 Getting Started

### Prerequisites
- Node.js 18 or higher
- npm 8 or higher
- MongoDB 5.0 or higher
- Git
- A code editor (VS Code recommended)

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/WebsiteME.git
   cd WebsiteME
   ```

2. **Install Dependencies**
   ```bash
   # Backend dependencies
   cd backend
   npm install
   
   # Frontend dependencies
   cd ../frontend
   npm install
   ```

3. **Environment Setup**
   ```bash
   # Backend environment
   cd backend
   cp .env.example .env
   # Edit .env with your configuration
   
   # Start MongoDB (if running locally)
   mongod
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   cd backend
   npm run dev
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## 📋 Development Workflow

### Branch Strategy
- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/[feature-name]` - New features
- `fix/[issue-description]` - Bug fixes
- `docs/[doc-update]` - Documentation updates

### Commit Guidelines
We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(auth): add user registration endpoint
fix(forum): resolve post creation validation error
docs(api): update authentication flow documentation
style(frontend): apply consistent button styling
refactor(backend): improve error handling middleware
test(sandbox): add code execution unit tests
chore(deps): update Next.js to latest version
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

2. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   # Frontend tests
   cd frontend
   npm run lint
   npm run type-check
   npm run build
   
   # Backend tests
   cd backend
   npm run lint
   npm run build
   ```

4. **Commit and Push**
   ```bash
   git add .
   git commit -m "feat(component): add new awesome feature"
   git push origin feature/amazing-new-feature
   ```

5. **Create Pull Request**
   - Use the PR template
   - Include clear description
   - Reference related issues
   - Add screenshots for UI changes

## 🎯 Areas for Contribution

### 🔥 High Priority
- [ ] User authentication implementation
- [ ] Real-time news fetching
- [ ] Code sandbox security enhancements
- [ ] Search functionality implementation
- [ ] Mobile responsiveness improvements

### 🛠️ Backend Tasks
- [ ] MongoDB model implementations
- [ ] API endpoint completions
- [ ] Rate limiting refinements
- [ ] Test suite development
- [ ] Error handling improvements
- [ ] OpenAI API integration
- [ ] External API integrations (GitHub, Stack Overflow)

### 🎨 Frontend Tasks
- [ ] Component library expansion
- [ ] Page implementations (forum, Q&A, admin)
- [ ] Form validation and handling
- [ ] State management setup
- [ ] Real-time features (WebSockets)
- [ ] Accessibility improvements
- [ ] Performance optimizations

### 📚 Documentation
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Component documentation (Storybook)
- [ ] Deployment guides
- [ ] User guides and tutorials
- [ ] Architecture decision records

### 🧪 Testing
- [ ] Unit tests for components
- [ ] Integration tests for APIs
- [ ] E2E tests for user flows
- [ ] Performance testing
- [ ] Security testing

## 📝 Coding Standards

### TypeScript/JavaScript
```typescript
// Use meaningful variable names
const userAuthenticationToken = jwt.sign(payload, secret);

// Prefer const over let, avoid var
const user = await User.findById(id);

// Use async/await over promises
const fetchUserData = async (userId: string) => {
  try {
    const user = await User.findById(userId);
    return user;
  } catch (error) {
    logger.error('Failed to fetch user:', error);
    throw new Error('User not found');
  }
};

// Type everything in TypeScript
interface UserProfile {
  id: string;
  username: string;
  email: string;
  reputation: number;
}

// Use JSDoc for complex functions
/**
 * Calculates user reputation based on activity
 * @param userId - The user's unique identifier
 * @param timeframe - Time period for calculation
 * @returns Promise resolving to reputation score
 */
const calculateReputation = async (
  userId: string, 
  timeframe: 'week' | 'month' | 'year' = 'month'
): Promise<number> => {
  // Implementation
};
```

### React Components
```typescript
// Use functional components with TypeScript
interface ButtonProps {
  variant?: 'primary' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  onClick 
}) => {
  return (
    <button 
      className={cn(
        'font-medium rounded-md transition-colors',
        variants[variant],
        sizes[size]
      )}
      onClick={onClick}
    >
      {children}
    </button>
  );
};

// Use custom hooks for logic
const useUserAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    checkAuthStatus().then(setUser).finally(() => setLoading(false));
  }, []);
  
  return { user, loading };
};
```

### CSS/Styling
```css
/* Use Tailwind utility classes */
<div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">

/* For complex styles, use CSS variables */
:root {
  --primary-color: #3b82f6;
  --secondary-color: #6b7280;
}

/* Responsive design mobile-first */
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

## 🔍 Code Review Guidelines

### For Contributors
- Keep PRs focused and reasonably sized
- Include clear commit messages
- Add comments for complex logic
- Ensure all tests pass
- Update documentation

### For Reviewers
- Be constructive and helpful
- Focus on code quality and maintainability
- Check for security implications
- Verify test coverage
- Consider performance impact

### Review Checklist
- [ ] Code follows established patterns
- [ ] No obvious security vulnerabilities
- [ ] Appropriate error handling
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No console.log statements in production code
- [ ] TypeScript types are properly defined
- [ ] Responsive design considered

## 🧪 Testing Guidelines

### Frontend Testing
```typescript
// Component testing with React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Backend Testing
```javascript
// API testing with supertest
const request = require('supertest');
const app = require('../src/app');

describe('POST /api/auth/login', () => {
  it('should authenticate valid user', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password123'
      })
      .expect(200);

    expect(response.body).toHaveProperty('token');
    expect(response.body.user).toHaveProperty('email', 'test@example.com');
  });

  it('should reject invalid credentials', async () => {
    await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'wrongpassword'
      })
      .expect(401);
  });
});
```

## 📚 Resources

### Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Express.js Guide](https://expressjs.com/en/guide/)
- [MongoDB Manual](https://www.mongodb.com/docs/manual/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Tools
- [VS Code Extensions](https://code.visualstudio.com/docs/editor/extension-marketplace)
  - ES7+ React/Redux/React-Native snippets
  - Prettier - Code formatter
  - ESLint
  - TypeScript Importer
  - Tailwind CSS IntelliSense
- [Postman](https://www.postman.com/) - API testing
- [MongoDB Compass](https://www.mongodb.com/products/compass) - Database GUI

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Special mentions in project updates

## 📞 Getting Help

- **Discord**: Join our development Discord server
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: dev@websiteme.com for private inquiries

## 📄 License

By contributing to WebsiteME, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to WebsiteME! Together, we're building the ultimate technology platform for developers worldwide. 🚀