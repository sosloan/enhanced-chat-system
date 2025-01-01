import React from 'react';

export function Footer() {
  return (
    <footer className="container mx-auto px-4 py-8 text-center text-gray-400 border-t border-gray-800">
      <p>© {new Date().getFullYear()} Your Company. All rights reserved.</p>
    </footer>
  );
}