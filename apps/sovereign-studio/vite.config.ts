import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import fs from 'fs/promises';

// API plugin for file operations
function studioApiPlugin() {
  const APPS_DIR = '/Users/jeremyserna/truth_forge/apps';
  const DESKTOP = '/Users/jeremyserna/Desktop';

  return {
    name: 'studio-api',
    configureServer(server: any) {
      server.middlewares.use(async (req: any, res: any, next: any) => {
        // Create app from generated code
        if (req.url === '/api/create-app' && req.method === 'POST') {
          let body = '';
          req.on('data', (chunk: any) => { body += chunk; });
          req.on('end', async () => {
            try {
              const { name, files } = JSON.parse(body);
              const appDir = path.join(APPS_DIR, name.toLowerCase().replace(/\s+/g, '-'));

              // Create app directory
              await fs.mkdir(appDir, { recursive: true });
              await fs.mkdir(path.join(appDir, 'src'), { recursive: true });

              // Write all files
              for (const file of files) {
                const filePath = path.join(appDir, file.path);
                const dir = path.dirname(filePath);
                await fs.mkdir(dir, { recursive: true });
                await fs.writeFile(filePath, file.content, 'utf-8');
              }

              // Run npm install
              const { exec } = await import('child_process');
              await new Promise((resolve, reject) => {
                exec('npm install', { cwd: appDir }, (err) => {
                  if (err) reject(err);
                  else resolve(true);
                });
              });

              // Create desktop launcher
              const launcherName = name.replace(/[^a-zA-Z0-9\s]/g, '') + '.command';
              const launcherPath = path.join(DESKTOP, launcherName);
              const port = 3000 + Math.floor(Math.random() * 100);
              const launcherContent = `#!/bin/bash
# ${name} - Double-click to run
cd "${appDir}"
npm run dev -- --port ${port} &
sleep 3
open http://localhost:${port}
echo "========================================"
echo "  ${name} is running"
echo "  http://localhost:${port}"
echo "========================================"
echo "To stop: close this window"
wait
`;
              await fs.writeFile(launcherPath, launcherContent, 'utf-8');
              await fs.chmod(launcherPath, '755');

              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                success: true,
                appDir,
                launcher: launcherPath,
                port
              }));
            } catch (e: any) {
              res.statusCode = 500;
              res.end(JSON.stringify({ error: e.message }));
            }
          });
          return;
        }

        // Launch an app
        if (req.url?.startsWith('/api/launch?')) {
          const urlParams = new URL(req.url, 'http://localhost').searchParams;
          const launcher = urlParams.get('launcher');
          if (launcher) {
            const { exec } = await import('child_process');
            exec(`open "${launcher}"`);
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify({ success: true }));
            return;
          }
        }

        next();
      });
    }
  };
}

export default defineConfig({
  plugins: [react(), studioApiPlugin()],
  server: {
    port: 3010,
    host: '0.0.0.0'
  }
});
