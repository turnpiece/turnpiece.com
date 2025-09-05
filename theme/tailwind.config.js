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
  theme: {
    extend: {},
  },
  plugins: [],
} 