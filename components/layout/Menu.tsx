import React from 'react';
import Link from 'next/link';
import { Button } from '../ui/button';

const menuItems = [
  { href: '/', label: 'Home' },
  { href: '/history', label: 'History' },
  { href: '/settings', label: 'Settings' },
];

export function Menu() {
  return (
    <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
      {menuItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className="transition-colors hover:text-foreground/80 text-foreground/60"
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
} 