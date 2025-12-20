import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import React, { Suspense } from 'react';
import Spline from '@splinetool/react-spline';


import styles from './index.module.css';
function HomepageHeader() {
  return (
    <header className={styles.heroBanner}>
      <div className={styles.heroBackground} />

      <div className={styles.heroContainer}>
        {/* LEFT: Text Content */}
        <div className={styles.heroContent}>
          <Heading as="h1" className={styles.heroTitle}>
            AI DRIVEN BOOK
          </Heading>

          <p className={styles.heroSubtitle}>
            Your gateway to advanced robotics and embodied intelligence
          </p>

          <Link
            className={styles.ctaButton}
            to="/docs/module-1/"
          >
            <span>Start Learning</span>
            <span className={styles.arrow}>→</span>
          </Link>
        </div>

        
        <div className={styles.splineContainer}>
          <Suspense fallback={null}>
            <Spline scene="https://prod.spline.design/wdWtfwPX42k321Yu/scene.splinecode" />
          </Suspense>
        </div>
      </div>
    </header>
  );
}

function ModuleCards() {
  const modules = [
    {
      id: 'module-1',
      title: 'Module 1: ROS 2 Nervous System',
      description: 'ROS 2 nodes, topics, services, URDF, and control pipelines.',
      image: '/img/eye.png.jpg',
      link: '/docs/module-1/',
    },
    {
      id: 'module-2',
      title: 'Module 2: Digital Twin',
      description: 'Gazebo physics, Unity environments, sensor simulation.',
      image: '/img/digitaltwin.png.jpg',
      link: '/docs/module-2/',
    },
    {
      id: 'module-3',
      title: 'Module 3: AI Robot Brain',
      description: 'Isaac Sim, Isaac ROS, Nav2, perception & navigation.',
      image: '/img/nervous.png.jpg',
      link: '/docs/module-3/',
    },
    {
      id: 'module-4',
      title: 'Module 4: Vision-Language-Action',
      description: 'LLMs, voice control, cognitive planning, capstone.',
      image: '/img/robot.png.jpg',
      link: '/docs/module-4/',
    },
  ];

  return (
    <section className={styles.moduleSection}>
      <div className="container">
        <div className={styles.moduleGrid}>
          {modules.map((module) => (
            <Link
              key={module.id}
              to={module.link}
              className={styles.moduleCard}
            >
              <div className={styles.imageWrapper}>
                <img
                  src={module.image}
                  alt={module.title}
                  className={styles.moduleImage}
                />
              </div>

              <div className={styles.cardContent}>
                <h3>{module.title}</h3>
                <p>{module.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <Layout
      title="AI Driven Humanoid Robotics Book"
      description="A technical guide to humanoid robotics and embodied AI"
    >
      <HomepageHeader />
      <main>
        <ModuleCards />
      </main>
    </Layout>
  );
}
