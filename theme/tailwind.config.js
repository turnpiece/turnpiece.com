const path = require('path');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    '../templates/**/*.html',
    '../core/templates/**/*.html',
    '../projects/templates/**/*.html',
    '../blog/templates/**/*.html',
  ],
  safelist: [
    'icon-apple',
    'icon-android', 
    'icon-api',
    'icon-website',
    'icon-database',
    'icon-code',
    'icon',
    'icon-sm',
    'icon-md',
    'icon-lg',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 