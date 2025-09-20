import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/header";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: 'swap',
  fallback: ['system-ui', 'arial'],
});

export const metadata: Metadata = {
  title: "WebsiteME - The Ultimate Tech Hub",
  description: "Stay updated with real-time tech news, engage in expert forums, code in our live sandbox, and connect with developers worldwide.",
  keywords: ["technology", "news", "programming", "forum", "code", "sandbox", "developers"],
  authors: [{ name: "WebsiteME Team" }],
  creator: "WebsiteME",
  publisher: "WebsiteME",
  openGraph: {
    title: "WebsiteME - The Ultimate Tech Hub",
    description: "Stay updated with real-time tech news, engage in expert forums, code in our live sandbox, and connect with developers worldwide.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "WebsiteME - The Ultimate Tech Hub",
    description: "Stay updated with real-time tech news, engage in expert forums, code in our live sandbox, and connect with developers worldwide.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased min-h-screen bg-background`}>
        <div className="relative flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">
            {children}
          </main>
          <footer className="border-t bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container py-6 text-center text-sm text-muted-foreground">
              © 2024 WebsiteME. Built with Next.js, Express, and MongoDB.
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
