/// <reference types="vitest" />
import path from 'path';
import fs from 'fs/promises';
import { defineConfig, loadEnv, Plugin } from 'vite';
import react from '@vitejs/plugin-react';

// Code Assistant API plugin for development
function codeAssistantPlugin(): Plugin {
  const APP_ROOT = process.cwd();
  const INCLUDE_EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx', '.css', '.json', '.md'];
  const EXCLUDE_DIRS = ['node_modules', 'dist', '.git', '.next', '.vercel'];

  async function getFiles(dir: string, basePath: string = ''): Promise<string[]> {
    const files: string[] = [];
    try {
      const entries = await fs.readdir(path.join(APP_ROOT, dir), { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(basePath, entry.name);
        if (entry.isDirectory()) {
          if (!EXCLUDE_DIRS.includes(entry.name)) {
            const subFiles = await getFiles(path.join(dir, entry.name), fullPath);
            files.push(...subFiles);
          }
        } else if (entry.isFile()) {
          const ext = entry.name.slice(entry.name.lastIndexOf('.'));
          if (INCLUDE_EXTENSIONS.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    } catch (e) {
      console.error('Error reading directory:', dir, e);
    }
    return files;
  }

  return {
    name: 'code-assistant-api',
    configureServer(server) {
      server.middlewares.use(async (req, res, next) => {
        // List files
        if (req.url === '/api/code/files') {
          try {
            const files = await getFiles('.');
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify(files));
          } catch (e) {
            res.statusCode = 500;
            res.end(JSON.stringify({ error: 'Failed to list files' }));
          }
          return;
        }

        // Read file
        if (req.url?.startsWith('/api/code/read?')) {
          const urlParams = new URL(req.url, 'http://localhost').searchParams;
          const filePath = urlParams.get('path');
          if (!filePath) {
            res.statusCode = 400;
            res.end(JSON.stringify({ error: 'Missing path parameter' }));
            return;
          }
          try {
            // Security: prevent path traversal
            const safePath = path.normalize(filePath).replace(/^(\.\.[\/\\])+/, '');
            const fullPath = path.join(APP_ROOT, safePath);
            if (!fullPath.startsWith(APP_ROOT)) {
              res.statusCode = 403;
              res.end(JSON.stringify({ error: 'Access denied' }));
              return;
            }
            const content = await fs.readFile(fullPath, 'utf-8');
            res.setHeader('Content-Type', 'text/plain');
            res.end(content);
          } catch (e) {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: `File not found: ${filePath}` }));
          }
          return;
        }

        // Write file
        if (req.url === '/api/code/write' && req.method === 'POST') {
          let body = '';
          req.on('data', chunk => { body += chunk; });
          req.on('end', async () => {
            try {
              const { path: filePath, content } = JSON.parse(body);
              const safePath = path.normalize(filePath).replace(/^(\.\.[\/\\])+/, '');
              const fullPath = path.join(APP_ROOT, safePath);
              if (!fullPath.startsWith(APP_ROOT)) {
                res.statusCode = 403;
                res.end(JSON.stringify({ error: 'Access denied' }));
                return;
              }
              await fs.writeFile(fullPath, content, 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true }));
            } catch (e) {
              res.statusCode = 500;
              res.end(JSON.stringify({ error: 'Failed to write file' }));
            }
          });
          return;
        }

        next();
      });
    }
  };
}

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react(), codeAssistantPlugin()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      },
      test: {
        globals: true,
        environment: 'jsdom',
        setupFiles: ['./tests/setup.ts'],
        include: ['tests/**/*.test.ts', 'tests/**/*.test.tsx'],
        coverage: {
          reporter: ['text', 'json', 'html'],
          include: ['services/**/*.ts'],
        }
      }
    };
});
