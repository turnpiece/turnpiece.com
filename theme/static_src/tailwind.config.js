const path = require('path');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    path.join(__dirname, '../../templates/**/*.html'),
    path.join(__dirname, '../../core/templates/**/*.html'),
    '../templates/base.html',
    '../core/templates/core/home.html',
    '../core/templates/core/support.html',
    '../core/templates/core/contact.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 