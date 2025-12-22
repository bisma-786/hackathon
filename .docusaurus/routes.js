import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/blog',
    component: ComponentCreator('/blog', 'b2f'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '182'),
    exact: true
  },
  {
    path: '/blog/authors',
    component: ComponentCreator('/blog/authors', '0b7'),
    exact: true
  },
  {
    path: '/blog/authors/all-sebastien-lorber-articles',
    component: ComponentCreator('/blog/authors/all-sebastien-lorber-articles', '4a1'),
    exact: true
  },
  {
    path: '/blog/authors/yangshun',
    component: ComponentCreator('/blog/authors/yangshun', 'a68'),
    exact: true
  },
  {
    path: '/blog/first-blog-post',
    component: ComponentCreator('/blog/first-blog-post', '89a'),
    exact: true
  },
  {
    path: '/blog/long-blog-post',
    component: ComponentCreator('/blog/long-blog-post', '9ad'),
    exact: true
  },
  {
    path: '/blog/mdx-blog-post',
    component: ComponentCreator('/blog/mdx-blog-post', 'e9f'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', '287'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus',
    component: ComponentCreator('/blog/tags/docusaurus', '704'),
    exact: true
  },
  {
    path: '/blog/tags/facebook',
    component: ComponentCreator('/blog/tags/facebook', '858'),
    exact: true
  },
  {
    path: '/blog/tags/hello',
    component: ComponentCreator('/blog/tags/hello', '299'),
    exact: true
  },
  {
    path: '/blog/tags/hola',
    component: ComponentCreator('/blog/tags/hola', '00d'),
    exact: true
  },
  {
    path: '/blog/welcome',
    component: ComponentCreator('/blog/welcome', 'd2b'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '348'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '219'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '8cd'),
            routes: [
              {
                path: '/docs/category/tutorial---basics',
                component: ComponentCreator('/docs/category/tutorial---basics', '20e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/category/tutorial---extras',
                component: ComponentCreator('/docs/category/tutorial---extras', '9ad'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-1/',
                component: ComponentCreator('/docs/module-1/', '651'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-1/actuator-control-systems',
                component: ComponentCreator('/docs/module-1/actuator-control-systems', 'ac4'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-1/embodied-intelligence-concepts',
                component: ComponentCreator('/docs/module-1/embodied-intelligence-concepts', '4fa'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-1/introduction-to-physical-ai',
                component: ComponentCreator('/docs/module-1/introduction-to-physical-ai', '41c'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-1/module-1-capstone',
                component: ComponentCreator('/docs/module-1/module-1-capstone', '8ee'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-1/ros2-fundamentals',
                component: ComponentCreator('/docs/module-1/ros2-fundamentals', 'bb9'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-1/sensor-integration-basics',
                component: ComponentCreator('/docs/module-1/sensor-integration-basics', 'df6'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/',
                component: ComponentCreator('/docs/module-2/', 'edc'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/gazebo-physics-simulation',
                component: ComponentCreator('/docs/module-2/gazebo-physics-simulation', '434'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/introduction-to-simulation-environments',
                component: ComponentCreator('/docs/module-2/introduction-to-simulation-environments', '742'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/module-2-capstone',
                component: ComponentCreator('/docs/module-2/module-2-capstone', '72e'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/nvidia-isaac-sim',
                component: ComponentCreator('/docs/module-2/nvidia-isaac-sim', 'f1e'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/placeholder',
                component: ComponentCreator('/docs/module-2/placeholder', '0f4'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/sim-to-real-transfer-challenges',
                component: ComponentCreator('/docs/module-2/sim-to-real-transfer-challenges', '0c5'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-2/unity-robotics-integration',
                component: ComponentCreator('/docs/module-2/unity-robotics-integration', '0cf'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-3/',
                component: ComponentCreator('/docs/module-3/', 'dfb'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-3/3.1-nvidia-isaac-sim',
                component: ComponentCreator('/docs/module-3/3.1-nvidia-isaac-sim', 'b30'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-3/3.2-isaac-ros-vslam',
                component: ComponentCreator('/docs/module-3/3.2-isaac-ros-vslam', 'ac1'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-3/3.3-navigation-nav2',
                component: ComponentCreator('/docs/module-3/3.3-navigation-nav2', '396'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-3/placeholder',
                component: ComponentCreator('/docs/module-3/placeholder', 'c39'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/module-4/',
                component: ComponentCreator('/docs/module-4/', '71a'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-4/4.1-voice-to-action-whisper',
                component: ComponentCreator('/docs/module-4/4.1-voice-to-action-whisper', '1ab'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-4/4.2-cognitive-planning-llm',
                component: ComponentCreator('/docs/module-4/4.2-cognitive-planning-llm', 'a99'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-4/4.3-capstone-autonomous-humanoid',
                component: ComponentCreator('/docs/module-4/4.3-capstone-autonomous-humanoid', 'b45'),
                exact: true,
                sidebar: "textbookSidebar"
              },
              {
                path: '/docs/module-4/placeholder',
                component: ComponentCreator('/docs/module-4/placeholder', 'f8f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/congratulations',
                component: ComponentCreator('/docs/tutorial-basics/congratulations', '458'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/create-a-blog-post',
                component: ComponentCreator('/docs/tutorial-basics/create-a-blog-post', '108'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/create-a-document',
                component: ComponentCreator('/docs/tutorial-basics/create-a-document', '8fc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/create-a-page',
                component: ComponentCreator('/docs/tutorial-basics/create-a-page', '951'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/deploy-your-site',
                component: ComponentCreator('/docs/tutorial-basics/deploy-your-site', '4f5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-basics/markdown-features',
                component: ComponentCreator('/docs/tutorial-basics/markdown-features', 'b05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-extras/manage-docs-versions',
                component: ComponentCreator('/docs/tutorial-extras/manage-docs-versions', '978'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/tutorial-extras/translate-your-site',
                component: ComponentCreator('/docs/tutorial-extras/translate-your-site', 'f9a'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '2e1'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
