// @ts-check

const {themes: prismThemes} = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'AI Development Template',
  tagline: 'Curated project documentation',
  favicon: 'img/favicon.ico',
  url: 'https://example.com',
  baseUrl: '/',
  organizationName: 'example',
  projectName: 'ai-dev-template',
  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
      onBrokenMarkdownImages: 'throw',
    },
  },
  i18n: {defaultLocale: 'en', locales: ['en']},
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  themeConfig: {
    navbar: {
      title: 'Project Docs',
      items: [{type: 'docSidebar', sidebarId: 'docsSidebar', position: 'left', label: 'Docs'}],
    },
    footer: {
      style: 'dark',
      copyright: 'Project documentation generated from repository source.',
    },
    prism: {theme: prismThemes.github, darkTheme: prismThemes.dracula},
    colorMode: {defaultMode: 'light', respectPrefersColorScheme: true},
  },
};

module.exports = config;
