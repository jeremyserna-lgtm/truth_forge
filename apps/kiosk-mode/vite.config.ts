import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs/promises';
import path from 'path';
import { exec } from 'child_process';

// API plugin for the kiosk's "hands" - ways to reach outside
function kioskHandsPlugin() {
  return {
    name: 'kiosk-hands',
    configureServer(server: any) {
      server.middlewares.use(async (req: any, res: any, next: any) => {

        // Write a file
        if (req.url === '/api/write-file' && req.method === 'POST') {
          let body = '';
          req.on('data', (chunk: any) => { body += chunk; });
          req.on('end', async () => {
            try {
              const { path: filePath, content } = JSON.parse(body);
              await fs.mkdir(path.dirname(filePath), { recursive: true });
              await fs.writeFile(filePath, content, 'utf-8');
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true }));
            } catch (e: any) {
              res.statusCode = 500;
              res.end(JSON.stringify({ error: e.message }));
            }
          });
          return;
        }

        // Create a mini site
        if (req.url === '/api/create-site' && req.method === 'POST') {
          let body = '';
          req.on('data', (chunk: any) => { body += chunk; });
          req.on('end', async () => {
            try {
              const { name, html, description } = JSON.parse(body);
              const sitesDir = '/Users/jeremyserna/truth_forge/apps/kiosk-sites';
              const siteDir = path.join(sitesDir, name);

              await fs.mkdir(siteDir, { recursive: true });
              await fs.writeFile(path.join(siteDir, 'index.html'), html, 'utf-8');
              await fs.writeFile(path.join(siteDir, 'README.md'), `# ${name}\n\n${description}`, 'utf-8');

              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true, path: siteDir }));
            } catch (e: any) {
              res.statusCode = 500;
              res.end(JSON.stringify({ error: e.message }));
            }
          });
          return;
        }

        // Open a URL in the default browser
        if (req.url === '/api/open-url' && req.method === 'POST') {
          let body = '';
          req.on('data', (chunk: any) => { body += chunk; });
          req.on('end', () => {
            try {
              const { url } = JSON.parse(body);
              exec(`open "${url}"`);
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({ success: true }));
            } catch (e: any) {
              res.statusCode = 500;
              res.end(JSON.stringify({ error: e.message }));
            }
          });
          return;
        }

        next();
      });
    }
  };
}

export default defineConfig({
  plugins: [react(), kioskHandsPlugin()],
  server: {
    port: 3020,
    host: '0.0.0.0'
  }
});
