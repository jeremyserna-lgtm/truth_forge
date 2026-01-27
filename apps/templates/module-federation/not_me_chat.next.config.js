/**
 * NOT-ME Chat - Module Federation Remote Configuration
 *
 * This configuration exposes the NOT-ME chat component for use across
 * all truth_forge websites (truth-forge.ai, credential-atlas.ai,
 * not-me.ai, primitive-engine.ai).
 *
 * Industry standard per RESEARCH_FINDINGS.md:
 * - Module Federation with Next.js
 * - Singleton React instances
 * - Lazy loading for performance
 *
 * @see https://module-federation.io/
 * @see docs/WEB_ARCHITECTURE.md
 */

const NextFederationPlugin = require('@module-federation/nextjs-mf');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  webpack(config, options) {
    const { isServer } = options;

    config.plugins.push(
      new NextFederationPlugin({
        // Remote name - used by consumers to reference this module
        name: 'not_me_chat',

        // Remote entry file location
        filename: 'static/chunks/remoteEntry.js',

        // Components exposed to consumers
        exposes: {
          // Main chat component
          './Chat': './components/Chat/index.tsx',

          // Chat context provider (for state management)
          './ChatProvider': './components/Chat/ChatProvider.tsx',

          // Individual sub-components (for customization)
          './ChatInput': './components/Chat/ChatInput.tsx',
          './ChatMessages': './components/Chat/ChatMessages.tsx',
          './ChatHeader': './components/Chat/ChatHeader.tsx',

          // Hooks for integration
          './useChat': './hooks/useChat.ts',
          './useLearning': './hooks/useLearning.ts',

          // Types for TypeScript consumers
          './types': './types/chat.ts',
        },

        // Shared dependencies - CRITICAL for React apps
        shared: {
          // React MUST be singleton to avoid hooks errors
          react: {
            singleton: true,
            requiredVersion: '^18.0.0',
            eager: !isServer,
          },
          'react-dom': {
            singleton: true,
            requiredVersion: '^18.0.0',
            eager: !isServer,
          },

          // State management (if using)
          // 'zustand': { singleton: true },

          // Styling (if using styled-components/emotion)
          // '@emotion/react': { singleton: true },
          // '@emotion/styled': { singleton: true },
        },

        // Extra options
        extraOptions: {
          // Enable automatic public path detection
          automaticAsyncBoundary: true,
        },
      })
    );

    return config;
  },

  // Enable cross-origin for module federation
  async headers() {
    return [
      {
        source: '/static/chunks/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ];
  },

  // Environment variables for learning persistence
  env: {
    // API endpoint for learning persistence service
    LEARNING_API_URL: process.env.LEARNING_API_URL || 'https://api.truth-forge.ai/learning',

    // Enable cross-site learning sync
    ENABLE_LEARNING_SYNC: process.env.ENABLE_LEARNING_SYNC || 'true',
  },
};

module.exports = nextConfig;
