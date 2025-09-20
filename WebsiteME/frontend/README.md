# WebsiteME Frontend

A modern React application built with Next.js 14, TypeScript, and Tailwind CSS. The frontend provides a comprehensive user interface for the WebsiteME technology platform.

## 🚀 Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Radix UI patterns
- **State Management**: Zustand
- **Form Handling**: React Hook Form with Zod validation
- **Icons**: Lucide React
- **Code Editor**: Monaco Editor (planned)
- **Real-time**: Socket.io Client (planned)

## 📁 Project Structure

```
src/
├── app/                        # Next.js App Router
│   ├── page.tsx               # Home page
│   ├── layout.tsx             # Root layout with header/footer
│   ├── globals.css            # Global styles
│   ├── news/                  # Tech news section
│   │   └── page.tsx           # News listing page
│   ├── forum/                 # Community forum
│   │   └── page.tsx           # Forum posts page
│   ├── qa/                    # Q&A section
│   │   └── page.tsx           # Questions page
│   ├── sandbox/               # Code playground
│   │   └── page.tsx           # Code editor page
│   └── admin/                 # Admin dashboard
│       └── page.tsx           # Admin interface
├── components/
│   ├── ui/                    # Base UI components
│   │   ├── button.tsx         # Button component
│   │   ├── input.tsx          # Input component
│   │   ├── card.tsx           # Card component
│   │   └── ...                # Other UI primitives
│   ├── layout/                # Layout components
│   │   ├── header.tsx         # Navigation header
│   │   └── footer.tsx         # Site footer
│   └── features/              # Feature-specific components
│       ├── hero.tsx           # Landing page hero
│       ├── news/              # News-related components
│       ├── forum/             # Forum components
│       └── sandbox/           # Code sandbox components
├── lib/                       # Utility libraries
│   ├── utils.ts               # General utilities
│   ├── api.ts                 # API client configuration
│   └── constants.ts           # App constants
├── hooks/                     # Custom React hooks
│   ├── useAuth.ts             # Authentication hook
│   ├── useApi.ts              # API data fetching
│   └── useLocalStorage.ts     # Local storage hook
├── store/                     # State management
│   ├── authStore.ts           # Authentication state
│   ├── themeStore.ts          # Theme preferences
│   └── notificationStore.ts   # Notifications
├── types/                     # TypeScript definitions
│   ├── api.ts                 # API response types
│   ├── user.ts                # User-related types
│   └── components.ts          # Component prop types
└── utils/                     # Helper functions
    ├── formatting.ts          # Data formatting
    ├── validation.ts          # Form validation schemas
    └── constants.ts           # Application constants
```

## 🎨 Design System

### Color Palette
The application uses a sophisticated color system with support for light and dark themes:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96%;
  --secondary-foreground: 222.2 84% 4.9%;
  --muted: 210 40% 96%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96%;
  --accent-foreground: 222.2 84% 4.9%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  --radius: 0.5rem;
}
```

### Typography
- **Primary Font**: Inter (via next/font/google)
- **Monospace**: JetBrains Mono for code
- **Scale**: Tailwind's default typography scale

### Component Library
Our custom components follow consistent patterns:

```typescript
// Button component example
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}
```

## 🔧 Development

### Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Open Application**
   Visit [http://localhost:3000](http://localhost:3000)

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

### Environment Variables

Create a `.env.local` file in the root directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_WS_URL=ws://localhost:3001

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_REALTIME=false

# External Services
NEXT_PUBLIC_SENTRY_DSN=your_sentry_dsn_here
```

## 🏗️ Architecture Patterns

### App Router Structure
We use Next.js 14's App Router for its improved performance and developer experience:

```typescript
// app/layout.tsx - Root layout
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
```

### Server vs Client Components
- **Server Components**: Used by default for better performance
- **Client Components**: Used for interactivity with 'use client'

```typescript
// Server component (default)
export default function NewsPage() {
  const articles = await fetchArticles(); // This runs on the server
  return <ArticleList articles={articles} />;
}

// Client component
'use client';
export function InteractiveButton() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### State Management with Zustand

```typescript
// store/authStore.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  login: async (credentials) => {
    const user = await api.login(credentials);
    set({ user, isAuthenticated: true });
  },
  logout: () => {
    set({ user: null, isAuthenticated: false });
  },
}));
```

### API Integration

```typescript
// lib/api.ts
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`);
    if (!response.ok) throw new Error('API Error');
    return response.json();
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('API Error');
    return response.json();
  }
}

export const api = new ApiClient(process.env.NEXT_PUBLIC_API_URL!);
```

## 🎯 Key Features Implementation

### Real-time News Feed
```typescript
// components/features/news/NewsFeed.tsx
'use client';

export function NewsFeed() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchArticles().then(setArticles).finally(() => setLoading(false));
  }, []);

  if (loading) return <ArticleSkeleton />;

  return (
    <div className="space-y-6">
      {articles.map(article => (
        <ArticleCard key={article.id} article={article} />
      ))}
    </div>
  );
}
```

### Code Sandbox Editor
```typescript
// components/features/sandbox/CodeEditor.tsx
'use client';

import { Editor } from '@monaco-editor/react';

export function CodeEditor({ value, onChange, language }: CodeEditorProps) {
  return (
    <Editor
      height="400px"
      language={language}
      value={value}
      onChange={onChange}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        automaticLayout: true,
      }}
    />
  );
}
```

### Advanced Search Interface
```typescript
// components/features/search/SearchInterface.tsx
'use client';

export function SearchInterface() {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({});
  const [results, setResults] = useState<SearchResult[]>([]);

  const handleSearch = useDebouncedCallback(async (searchQuery: string) => {
    const results = await api.search(searchQuery, filters);
    setResults(results);
  }, 300);

  return (
    <div className="space-y-6">
      <SearchInput 
        value={query}
        onChange={(value) => {
          setQuery(value);
          handleSearch(value);
        }}
      />
      <SearchFilters filters={filters} onChange={setFilters} />
      <SearchResults results={results} />
    </div>
  );
}
```

## 📱 Responsive Design

### Breakpoint Strategy
```css
/* Tailwind CSS breakpoints */
sm: '640px'   /* Small devices */
md: '768px'   /* Medium devices */
lg: '1024px'  /* Large devices */
xl: '1280px'  /* Extra large devices */
2xl: '1536px' /* 2X Extra large devices */
```

### Mobile-First Approach
```typescript
// Responsive component example
<div className="
  grid 
  grid-cols-1 
  md:grid-cols-2 
  lg:grid-cols-3 
  gap-4 
  p-4 
  md:p-6 
  lg:p-8
">
  {articles.map(article => (
    <ArticleCard key={article.id} article={article} />
  ))}
</div>
```

## 🔍 Performance Optimization

### Code Splitting
```typescript
// Dynamic imports for route-based splitting
const AdminDashboard = dynamic(() => import('./AdminDashboard'), {
  loading: () => <DashboardSkeleton />,
});

// Component-level splitting
const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  ssr: false, // Disable SSR for client-only components
});
```

### Image Optimization
```typescript
import Image from 'next/image';

<Image
  src={article.imageUrl}
  alt={article.title}
  width={400}
  height={200}
  className="rounded-lg"
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
/>
```

### SEO Optimization
```typescript
// app/news/page.tsx
export const metadata: Metadata = {
  title: 'Tech News - WebsiteME',
  description: 'Latest technology news and insights',
  keywords: ['technology', 'news', 'programming', 'AI'],
  openGraph: {
    title: 'Tech News - WebsiteME',
    description: 'Latest technology news and insights',
    images: ['/og-news.jpg'],
  },
};
```

## 🧪 Testing Strategy

### Unit Testing (Jest + Testing Library)
```typescript
// __tests__/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/button';

describe('Button Component', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Integration Testing
```typescript
// __tests__/pages/News.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import NewsPage from '@/app/news/page';

// Mock API responses
jest.mock('@/lib/api');

describe('News Page', () => {
  it('displays news articles', async () => {
    render(<NewsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Tech News')).toBeInTheDocument();
    });
  });
});
```

## 🚀 Deployment

### Build Process
```bash
# Production build
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

### Environment-Specific Builds
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  images: {
    domains: ['api.example.com', 'cdn.example.com'],
  },
  experimental: {
    appDir: true,
  },
};

module.exports = nextConfig;
```

## 📚 Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Zustand Documentation](https://zustand.pmnd.rs/)

## 🤝 Contributing

1. Follow the existing code style and patterns
2. Use TypeScript for all new components
3. Add proper JSDoc comments for complex functions
4. Include unit tests for new components
5. Update documentation for significant changes

## 📄 License

This project is part of WebsiteME and follows the same MIT license.
