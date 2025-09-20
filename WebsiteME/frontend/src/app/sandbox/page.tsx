'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, Save, Share, Download, Code, Terminal, FileText, Settings } from 'lucide-react';

// Mock code execution for demonstration
const executeCode = async (code: string, language: string): Promise<{ output: string; error?: string }> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  // Mock execution results based on language
  if (language === 'javascript') {
    if (code.includes('console.log')) {
      return { output: 'Hello, World!\n42\n[1, 2, 3, 4, 5]' };
    }
  } else if (language === 'python') {
    if (code.includes('print')) {
      return { output: 'Hello, World!\n42\n[1, 2, 3, 4, 5]' };
    }
  }
  
  return { output: 'Code executed successfully!' };
};

const codeTemplates = {
  javascript: {
    basic: `// JavaScript Basic Example
console.log("Hello, World!");

// Variables and Functions
const add = (a, b) => a + b;
console.log(add(20, 22));

// Array operations
const numbers = [1, 2, 3, 4, 5];
console.log(numbers);`,
    
    react: `// React Component Example
import React, { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={() => setCount(count + 1)}>
        Click me
      </button>
    </div>
  );
}

export default Counter;`,
    
    async: `// Async/Await Example
async function fetchUserData(userId) {
  try {
    const response = await fetch(\`/api/users/\${userId}\`);
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Error fetching user data:', error);
    return null;
  }
}

// Usage
fetchUserData(123).then(user => {
  console.log('User data:', user);
});`
  },
  
  python: {
    basic: `# Python Basic Example
print("Hello, World!")

# Variables and Functions
def add(a, b):
    return a + b

print(add(20, 22))

# List operations
numbers = [1, 2, 3, 4, 5]
print(numbers)`,
    
    class: `# Python Class Example
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name} and I'm {self.age} years old"
    
    def have_birthday(self):
        self.age += 1
        return f"Happy birthday! Now I'm {self.age}"

# Usage
person = Person("Alice", 25)
print(person.greet())
print(person.have_birthday())`,
    
    dataScience: `# Python Data Science Example
import pandas as pd
import numpy as np

# Create sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'salary': [50000, 60000, 70000, 55000]
}

df = pd.DataFrame(data)
print("Original DataFrame:")
print(df)

# Calculate statistics
print("\\nAverage age:", df['age'].mean())
print("Average salary:", df['salary'].mean())

# Filter data
high_earners = df[df['salary'] > 55000]
print("\\nHigh earners:")
print(high_earners)`
  },
  
  java: {
    basic: `// Java Basic Example
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        
        // Variables and Methods
        int result = add(20, 22);
        System.out.println("Result: " + result);
        
        // Array operations
        int[] numbers = {1, 2, 3, 4, 5};
        System.out.println("Array length: " + numbers.length);
    }
    
    public static int add(int a, int b) {
        return a + b;
    }
}`
  }
};

export default function SandboxPage() {
  const [selectedLanguage, setSelectedLanguage] = useState('javascript');
  const [selectedTemplate, setSelectedTemplate] = useState('basic');
  const [code, setCode] = useState(codeTemplates.javascript.basic);
  const [output, setOutput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState('');

  const languages = [
    { id: 'javascript', name: 'JavaScript', extension: 'js' },
    { id: 'python', name: 'Python', extension: 'py' },
    { id: 'java', name: 'Java', extension: 'java' },
  ];

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language);
    setSelectedTemplate('basic');
    // @ts-ignore
    setCode(codeTemplates[language]?.basic || '// No template available');
    setOutput('');
    setError('');
  };

  const handleTemplateChange = (template: string) => {
    setSelectedTemplate(template);
    // @ts-ignore
    setCode(codeTemplates[selectedLanguage]?.[template] || '// Template not found');
    setOutput('');
    setError('');
  };

  const handleExecute = async () => {
    setIsExecuting(true);
    setError('');
    setOutput('Executing code...');
    
    try {
      const result = await executeCode(code, selectedLanguage);
      setOutput(result.output);
      if (result.error) {
        setError(result.error);
      }
    } catch (err) {
      setError('Execution failed. Please check your code and try again.');
      setOutput('');
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-4">Code Sandbox</h1>
        <p className="text-lg text-muted-foreground max-w-2xl">
          Write, test, and share code in multiple programming languages. 
          Secure execution environment with real-time output.
        </p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Language Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Language</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {languages.map((lang) => (
                <Button
                  key={lang.id}
                  variant={selectedLanguage === lang.id ? "default" : "outline"}
                  className="w-full justify-start"
                  onClick={() => handleLanguageChange(lang.id)}
                >
                  <Code className="mr-2 h-4 w-4" />
                  {lang.name}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Templates */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Templates</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {/* @ts-ignore */}
              {Object.keys(codeTemplates[selectedLanguage] || {}).map((template) => (
                <Button
                  key={template}
                  variant={selectedTemplate === template ? "default" : "outline"}
                  size="sm"
                  className="w-full justify-start text-xs"
                  onClick={() => handleTemplateChange(template)}
                >
                  <FileText className="mr-2 h-3 w-3" />
                  {template}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="default"
                className="w-full"
                onClick={handleExecute}
                disabled={isExecuting}
              >
                <Play className="mr-2 h-4 w-4" />
                {isExecuting ? 'Running...' : 'Run Code'}
              </Button>
              
              <Button variant="outline" className="w-full">
                <Save className="mr-2 h-4 w-4" />
                Save Snippet
              </Button>
              
              <Button variant="outline" className="w-full">
                <Share className="mr-2 h-4 w-4" />
                Share Code
              </Button>
              
              <Button variant="outline" className="w-full">
                <Download className="mr-2 h-4 w-4" />
                Download
              </Button>
            </CardContent>
          </Card>

          {/* Sandbox Info */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Sandbox Info</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div className="flex justify-between">
                <span>Execution Time:</span>
                <span>5s limit</span>
              </div>
              <div className="flex justify-between">
                <span>Memory:</span>
                <span>128MB limit</span>
              </div>
              <div className="flex justify-between">
                <span>Network:</span>
                <span>Restricted</span>
              </div>
              <div className="flex justify-between">
                <span>File System:</span>
                <span>Read-only</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Editor Area */}
        <div className="xl:col-span-3 space-y-6">
          {/* Code Editor */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Code Editor</CardTitle>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {languages.find(l => l.id === selectedLanguage)?.name} 
                  </span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="w-full h-96 p-4 font-mono text-sm border rounded-md resize-none bg-slate-50 dark:bg-slate-900"
                  placeholder="Write your code here..."
                />
                <div className="absolute bottom-2 right-2 text-xs text-muted-foreground">
                  Lines: {code.split('\n').length} | Characters: {code.length}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Output */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center">
                <Terminal className="mr-2 h-5 w-5" />
                Output
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-black text-green-400 p-4 rounded-md font-mono text-sm min-h-32">
                {error ? (
                  <div className="text-red-400">
                    <div className="font-bold">Error:</div>
                    <div>{error}</div>
                  </div>
                ) : (
                  <pre className="whitespace-pre-wrap">{output || 'Click "Run Code" to see output...'}</pre>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Code Examples */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Popular Examples</CardTitle>
              <CardDescription>
                Explore these curated code examples and challenges
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { title: "Binary Search Algorithm", difficulty: "Medium", language: "JavaScript" },
                  { title: "React Component Lifecycle", difficulty: "Beginner", language: "JavaScript" },
                  { title: "Data Analysis with Pandas", difficulty: "Intermediate", language: "Python" },
                  { title: "RESTful API Design", difficulty: "Advanced", language: "Node.js" },
                ].map((example, index) => (
                  <div key={index} className="p-4 border rounded-md hover:bg-accent cursor-pointer">
                    <h4 className="font-medium">{example.title}</h4>
                    <div className="flex items-center space-x-2 mt-2 text-sm text-muted-foreground">
                      <span className={`px-2 py-1 rounded text-xs ${
                        example.difficulty === 'Beginner' ? 'bg-green-100 text-green-800' :
                        example.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {example.difficulty}
                      </span>
                      <span>{example.language}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}