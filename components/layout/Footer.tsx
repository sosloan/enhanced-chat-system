import React from 'react';
import Link from 'next/link';

export function Footer() {
  return (
    <footer className="border-t border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 max-w-screen-2xl items-center justify-between py-12">
        <div className="flex flex-col space-y-4 md:flex-row md:space-y-0 md:space-x-8">
          <div>
            <h3 className="text-lg font-semibold">Blog Scraper</h3>
            <p className="text-sm text-muted-foreground">
              AI-powered blog post analysis and research
            </p>
          </div>
          <div className="space-y-2">
            <h4 className="text-sm font-semibold">Links</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="text-muted-foreground hover:text-foreground">
                  About
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-foreground">
                  Privacy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="text-muted-foreground hover:text-foreground">
                  Terms
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="text-sm text-muted-foreground">
          © {new Date().getFullYear()} Blog Scraper. All rights reserved.
        </div>
      </div>
    </footer>
  );
} 