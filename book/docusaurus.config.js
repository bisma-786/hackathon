// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Bisma',
  tagline: 'An AI-Driven Textbook on Embodied Intelligence',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://your-docusaurus-site.example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'facebook', // Usually your GitHub org/user name.
  projectName: 'docusaurus', // Usually your repo name.

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Ai Driven Book',
        logo: {
          alt: '',
          src: '/img/bbh.png',
          height:200,
          

          
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'textbookSidebar',
            position: 'left',
            label: 'Textbook',
          },
          // {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/bisma-786',
            label: 'GitHub',
            position: 'right',
          },
          {
            href: 'https://www.facebook.com/RunWithBissu/',
            label: 'Facebook',
            position: 'right',
          },
{
  href: 'https://wa.me/923342018716?text=Hello%20I%20would%20like%20to%20get%20in%20touch',
  label: 'Whatsapp',
  position: 'right',
},
        ],
      },
 footer: {
  style: 'dark',
  links: [
    {
      title: 'Textbook',
      items: [
        { label: 'Module 1: Fundamentals', to: '/docs/module-1' },
        { label: 'Module 2: Digital Twin', to: '/docs/module-2' },
        { label: 'Module 3: Ai Robot Brain', to: '/docs/module-3' },
        { label: 'Module 4: Vision Language Action', to: '/docs/module-4' },
      ],
    },
    {
      title: 'Community',
      items: [
        { label: 'Github', href: 'https://github.com/bisma-786' },
        { label: 'Facebook', href: 'https://www.facebook.com/RunWithBissu/' },
        { label: 'Whatsapp', href: 'https://wa.me/923342018716' },
      ],
    },
    {
      title: 'More',
      items: [
        { label: 'Blog (Coming Soon!)', href: '#' }
      ],
    },
  ],
  copyright: 'Copyright © BuiltByHer 2025 Physical AI & Humanoid Robotics Textbook.',
},

      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
