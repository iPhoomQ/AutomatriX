'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Clock, ExternalLink, Filter, TrendingUp, Zap, Globe, BookOpen } from 'lucide-react';

// Mock news data
const newsArticles = [
  {
    id: 1,
    title: "Revolutionary AI Model Achieves Breakthrough in Code Generation",
    summary: "A new artificial intelligence model has demonstrated unprecedented capabilities in generating production-ready code across multiple programming languages. The model, trained on millions of code repositories, can understand context and generate complex algorithms with minimal prompts.",
    content: "The breakthrough represents a significant advancement in AI-assisted development tools...",
    source: "TechCrunch",
    author: "Sarah Chen",
    publishedAt: "2024-01-20T10:30:00Z",
    category: "AI/ML",
    tags: ["artificial-intelligence", "machine-learning", "code-generation", "programming"],
    imageUrl: "https://via.placeholder.com/400x200?text=AI+Code+Generation",
    readTime: "5 min read",
    views: 2340,
    likes: 127
  },
  {
    id: 2,
    title: "Web3 Development Frameworks See 300% Growth in Adoption",
    summary: "Blockchain development tools and frameworks have experienced massive growth as developers increasingly build decentralized applications. New tools are making Web3 development more accessible to traditional web developers.",
    content: "The rise of user-friendly Web3 development frameworks...",
    source: "The Verge",
    author: "Michael Rodriguez",
    publishedAt: "2024-01-20T08:15:00Z",
    category: "Web3",
    tags: ["blockchain", "web3", "development", "frameworks"],
    imageUrl: "https://via.placeholder.com/400x200?text=Web3+Development",
    readTime: "4 min read",
    views: 1890,
    likes: 95
  },
  {
    id: 3,
    title: "Rust Programming Language Gains Momentum in Enterprise",
    summary: "Major tech companies are increasingly adopting Rust for system-level programming due to its memory safety guarantees and performance characteristics. The language is becoming a go-to choice for critical infrastructure.",
    content: "Rust's unique approach to memory management...",
    source: "InfoWorld",
    author: "David Kim",
    publishedAt: "2024-01-20T06:00:00Z",
    category: "Programming",
    tags: ["rust", "programming", "enterprise", "systems"],
    imageUrl: "https://via.placeholder.com/400x200?text=Rust+Programming",
    readTime: "6 min read",
    views: 1650,
    likes: 78
  },
  {
    id: 4,
    title: "Edge Computing Transforms Real-Time Application Development",
    summary: "The shift towards edge computing is enabling new possibilities for real-time applications. Developers can now build ultra-low latency applications that process data closer to users.",
    content: "Edge computing represents a fundamental shift...",
    source: "IEEE Spectrum",
    author: "Lisa Park",
    publishedAt: "2024-01-19T22:45:00Z",
    category: "Cloud",
    tags: ["edge-computing", "cloud", "real-time", "performance"],
    imageUrl: "https://via.placeholder.com/400x200?text=Edge+Computing",
    readTime: "7 min read",
    views: 1420,
    likes: 89
  }
];

const categories = ["All", "AI/ML", "Web3", "Programming", "Cloud", "Security", "Mobile"];

export default function NewsPage() {
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredArticles = newsArticles.filter(article => {
    const matchesCategory = selectedCategory === "All" || article.category === selectedCategory;
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         article.summary.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return "Just now";
    if (diffInHours < 24) return `${diffInHours}h ago`;
    return `${Math.floor(diffInHours / 24)}d ago`;
  };

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Tech News</h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          Stay updated with the latest developments in technology. Real-time news from trusted sources 
          with AI-powered summaries to help you stay informed.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="mb-8 space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search articles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            Advanced Filters
          </Button>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </Button>
          ))}
        </div>
      </div>

      {/* Trending Section */}
      <div className="mb-8">
        <div className="flex items-center space-x-2 mb-4">
          <TrendingUp className="h-5 w-5 text-primary" />
          <h2 className="text-2xl font-semibold">Trending Now</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {newsArticles.slice(0, 3).map((article) => (
            <Card key={`trending-${article.id}`} className="cursor-pointer hover:shadow-lg transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
                  <span className="bg-red-500/10 text-red-600 px-2 py-1 rounded-md text-xs font-medium">
                    TRENDING
                  </span>
                  <Zap className="h-3 w-3" />
                </div>
                <CardTitle className="text-lg line-clamp-2">{article.title}</CardTitle>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{formatDate(article.publishedAt)}</span>
                  <span>•</span>
                  <span>{article.readTime}</span>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>

      {/* Articles Grid */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold">Latest Articles</h2>
          <span className="text-sm text-muted-foreground">
            {filteredArticles.length} articles found
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredArticles.map((article) => (
            <Card key={article.id} className="cursor-pointer hover:shadow-lg transition-shadow overflow-hidden">
              <div className="aspect-video relative bg-muted">
                <img
                  src={article.imageUrl}
                  alt={article.title}
                  className="object-cover w-full h-full"
                />
                <div className="absolute top-3 left-3">
                  <span className="bg-primary/90 text-primary-foreground px-2 py-1 rounded-md text-xs font-medium">
                    {article.category}
                  </span>
                </div>
              </div>
              
              <CardHeader>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-2">
                  <Globe className="h-3 w-3" />
                  <span>{article.source}</span>
                  <span>•</span>
                  <span>by {article.author}</span>
                  <span>•</span>
                  <Clock className="h-3 w-3" />
                  <span>{formatDate(article.publishedAt)}</span>
                </div>
                
                <CardTitle className="line-clamp-2 hover:text-primary transition-colors">
                  {article.title}
                </CardTitle>
                
                <CardDescription className="line-clamp-3">
                  {article.summary}
                </CardDescription>
              </CardHeader>

              <CardContent>
                <div className="flex flex-wrap gap-1 mb-4">
                  {article.tags.slice(0, 3).map((tag, index) => (
                    <span 
                      key={index}
                      className="bg-secondary text-secondary-foreground px-2 py-1 rounded-md text-xs"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <span>{article.readTime}</span>
                    <span>•</span>
                    <span>{article.views} views</span>
                    <span>•</span>
                    <span>{article.likes} likes</span>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Button size="sm" variant="outline">
                      <Zap className="mr-1 h-3 w-3" />
                      AI Summary
                    </Button>
                    <Button size="sm">
                      <BookOpen className="mr-1 h-3 w-3" />
                      Read More
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Load More */}
        <div className="text-center pt-8">
          <Button variant="outline" size="lg">
            Load More Articles
          </Button>
        </div>
      </div>
    </div>
  );
}