'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { TrendingUp, Clock, ExternalLink, Zap, Users, Code, Search, Sparkles } from 'lucide-react';
import Link from 'next/link';

// Mock data for demonstration
const featuredNews = [
  {
    id: 1,
    title: "AI Breakthrough: New Language Model Achieves Human-Level Performance",
    summary: "Researchers unveil a revolutionary language model that demonstrates unprecedented understanding and reasoning capabilities...",
    source: "TechCrunch",
    publishedAt: "2 hours ago",
    category: "AI/ML",
    readTime: "4 min read"
  },
  {
    id: 2,
    title: "Web3 Development Tools See Massive Adoption",
    summary: "Developer adoption of blockchain development frameworks has increased by 300% this quarter...",
    source: "The Verge",
    publishedAt: "4 hours ago",
    category: "Web3",
    readTime: "3 min read"
  }
];

const trendingTopics = [
  "Large Language Models",
  "Next.js 14",
  "Rust Programming",
  "WebAssembly",
  "Edge Computing"
];

const featuredForumPosts = [
  {
    id: 1,
    title: "How to optimize React re-renders in large applications?",
    author: "reactdev123",
    replies: 23,
    views: 1250,
    tags: ["react", "performance", "optimization"]
  },
  {
    id: 2,
    title: "Understanding Rust ownership and borrowing",
    author: "rustguru",
    replies: 15,
    views: 890,
    tags: ["rust", "memory-management", "beginner"]
  }
];

export function Hero() {
  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="container py-24 md:py-32">
        <div className="flex flex-col items-center text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
              The Ultimate
              <span className="text-primary"> Tech Hub</span>
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
              Stay updated with real-time tech news, engage in expert forums, code in our live sandbox, 
              and connect with developers worldwide. Everything you need in one platform.
            </p>
          </div>

          {/* Search Bar */}
          <div className="w-full max-w-2xl">
            <div className="flex space-x-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search news, posts, code examples..."
                  className="pl-10 h-12"
                />
              </div>
              <Button className="h-12 px-8">
                <Search className="h-4 w-4 mr-2" />
                Search
              </Button>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl mt-16">
            <Card className="text-center">
              <CardHeader>
                <TrendingUp className="h-12 w-12 mx-auto text-primary" />
                <CardTitle className="text-lg">Real-time News</CardTitle>
                <CardDescription>
                  Stay updated with the latest tech news from trusted sources
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Users className="h-12 w-12 mx-auto text-primary" />
                <CardTitle className="text-lg">Expert Forums</CardTitle>
                <CardDescription>
                  Engage with developers and get answers to your questions
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Code className="h-12 w-12 mx-auto text-primary" />
                <CardTitle className="text-lg">Live Sandbox</CardTitle>
                <CardDescription>
                  Write, test, and share code in multiple programming languages
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Sparkles className="h-12 w-12 mx-auto text-primary" />
                <CardTitle className="text-lg">AI Summaries</CardTitle>
                <CardDescription>
                  Get AI-powered summaries of complex technical articles
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Content Sections */}
      <section className="container py-16 space-y-16">
        {/* Featured News */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Featured News</h2>
              <p className="text-muted-foreground">Latest developments in technology</p>
            </div>
            <Link href="/news">
              <Button variant="outline">
                View All News
                <ExternalLink className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {featuredNews.map((article) => (
              <Card key={article.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <span className="bg-primary/10 text-primary px-2 py-1 rounded-md">{article.category}</span>
                    <Clock className="h-3 w-3" />
                    <span>{article.publishedAt}</span>
                    <span>•</span>
                    <span>{article.readTime}</span>
                  </div>
                  <CardTitle className="line-clamp-2">{article.title}</CardTitle>
                  <CardDescription className="line-clamp-3">
                    {article.summary}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{article.source}</span>
                    <Button variant="ghost" size="sm">
                      Read More
                      <ExternalLink className="ml-1 h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Trending Topics */}
        <div>
          <h2 className="text-2xl font-bold tracking-tight mb-6">Trending Topics</h2>
          <div className="flex flex-wrap gap-2">
            {trendingTopics.map((topic, index) => (
              <Button key={index} variant="outline" size="sm">
                <TrendingUp className="mr-2 h-3 w-3" />
                {topic}
              </Button>
            ))}
          </div>
        </div>

        {/* Featured Forum Posts */}
        <div>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold tracking-tight">Popular Discussions</h2>
              <p className="text-muted-foreground">Join the conversation with fellow developers</p>
            </div>
            <Link href="/forum">
              <Button variant="outline">
                View All Posts
                <ExternalLink className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>

          <div className="space-y-4">
            {featuredForumPosts.map((post) => (
              <Card key={post.id} className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold mb-2">{post.title}</h3>
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-3">
                        <span>by {post.author}</span>
                        <span>{post.replies} replies</span>
                        <span>{post.views} views</span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {post.tags.map((tag, index) => (
                          <span 
                            key={index}
                            className="bg-secondary text-secondary-foreground px-2 py-1 rounded-md text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      <ExternalLink className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}