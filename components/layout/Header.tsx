import React from 'react';
import Link from 'next/link';
import { Button } from '../ui/button';
import { Menu } from './Menu';

export function Header() {
  return (
    <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center">
        <div className="mr-4 flex">
          <Link href="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold text-xl">Blog Scraper</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <nav className="flex items-center">
            <Menu />
          </nav>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Link href="https://github.com/yourusername/blog-scraper">
                GitHub
              </Link>
            </Button>
            <Button size="sm">
              <Link href="/docs">
                Documentation
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
} 