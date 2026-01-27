/**
 * Website Consumer - Module Federation Host Configuration
 *
 * This configuration consumes the NOT-ME chat component from the
 * shared remote. Use this as a template for:
 * - truth-forge.ai
 * - credential-atlas.ai
 * - not-me.ai
 * - primitive-engine.ai
 *
 * Industry standard per RESEARCH_FINDINGS.md:
 * - Module Federation with Next.js
 * - Dynamic remote loading
 * - Fallback handling
 *
 * @see https://module-federation.io/
 * @see docs/WEB_ARCHITECTURE.md
 */

const NextFederationPlugin = require('@module-federation/nextjs-mf');

/**
 * Get remote URL based on environment
 * @param {string} remoteName - Name of the remote module
 * @returns {string} Full URL to remote entry
 */
function getRemoteUrl(remoteName) {
  const remotes = {
    not_me_chat: {
      development: 'http://localhost:3001',
      staging: 'https://chat-staging.truth-forge.ai',
      production: 'https://chat.truth-forge.ai',
    },
  };

  const env = process.env.NODE_ENV === 'production'
    ? (process.env.DEPLOY_ENV || 'production')
    : 'development';

  const baseUrl = remotes[remoteName]?.[env] || remotes[remoteName]?.development;
  return `${baseUrl}/_next/static/chunks/remoteEntry.js`;
}

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  webpack(config, options) {
    const { isServer } = options;

    config.plugins.push(
      new NextFederationPlugin({
        // This app's name (change per website)
        name: 'truth_forge_website', // or: credential_atlas, not_me, primitive_engine

        // Remote modules to consume
        remotes: {
          // NOT-ME Chat component
          not_me_chat: `not_me_chat@${getRemoteUrl('not_me_chat')}`,
        },

        // Shared dependencies - MUST match remote configuration
        shared: {
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
        },

        // Extra options
        extraOptions: {
          automaticAsyncBoundary: true,
        },
      })
    );

    return config;
  },
};

module.exports = nextConfig;

/**
 * Usage in pages/components:
 *
 * ```tsx
 * // Dynamic import with loading fallback
 * import dynamic from 'next/dynamic';
 *
 * const NotMeChat = dynamic(
 *   () => import('not_me_chat/Chat'),
 *   {
 *     ssr: false,
 *     loading: () => <ChatSkeleton />,
 *   }
 * );
 *
 * // In your component
 * export default function HomePage() {
 *   return (
 *     <div>
 *       <h1>Welcome to Truth Forge</h1>
 *       <NotMeChat
 *         siteId="truth-forge"
 *         userId={user?.id}
 *         onMessage={(msg) => console.log('Message:', msg)}
 *       />
 *     </div>
 *   );
 * }
 * ```
 *
 * With provider for shared state:
 *
 * ```tsx
 * import { ChatProvider } from 'not_me_chat/ChatProvider';
 * import Chat from 'not_me_chat/Chat';
 *
 * function App({ children }) {
 *   return (
 *     <ChatProvider
 *       config={{
 *         siteId: 'truth-forge',
 *         learningEnabled: true,
 *         apiEndpoint: process.env.NEXT_PUBLIC_CHAT_API,
 *       }}
 *     >
 *       {children}
 *     </ChatProvider>
 *   );
 * }
 * ```
 */
