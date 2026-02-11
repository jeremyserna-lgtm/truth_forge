import { readdir } from 'fs/promises';
import { join } from 'path';
import type { VercelRequest, VercelResponse } from '@vercel/node';

const APP_ROOT = process.cwd();

// Extensions to include
const INCLUDE_EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx', '.css', '.json', '.md'];

// Directories to exclude
const EXCLUDE_DIRS = ['node_modules', 'dist', '.git', '.next', '.vercel'];

async function getFiles(dir: string, basePath: string = ''): Promise<string[]> {
  const files: string[] = [];
  const entries = await readdir(join(APP_ROOT, dir), { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = join(basePath, entry.name);

    if (entry.isDirectory()) {
      if (!EXCLUDE_DIRS.includes(entry.name)) {
        const subFiles = await getFiles(join(dir, entry.name), fullPath);
        files.push(...subFiles);
      }
    } else if (entry.isFile()) {
      const ext = entry.name.slice(entry.name.lastIndexOf('.'));
      if (INCLUDE_EXTENSIONS.includes(ext)) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const files = await getFiles('.');
    return res.status(200).json(files);
  } catch (error) {
    console.error('Error listing files:', error);
    return res.status(500).json({ error: 'Failed to list files' });
  }
}
