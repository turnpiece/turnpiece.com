const path = require('path');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    '../templates/**/*.html',
    '../core/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 