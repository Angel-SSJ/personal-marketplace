import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const currentDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(currentDir, '..', '..');

/**
 * Discovers all plugin skill directories registered under `plugins/<id>/skills`.
 * @param {string} [rootDir]
 * @returns {string[]}
 */
export function discoverPluginSkillDirs(rootDir = repoRoot) {
  const pluginsDir = path.join(rootDir, 'plugins');
  if (!fs.existsSync(pluginsDir)) {
    return [];
  }

  /** @type {string[]} */
  const skillDirs = [];
  for (const entry of fs.readdirSync(pluginsDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }
    const candidate = path.join(pluginsDir, entry.name, 'skills');
    if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) {
      skillDirs.push(candidate);
    }
  }
  return skillDirs.sort();
}

/**
 * OpenCode plugin entrypoint compatible with OpenCode V1 (`package.json` main)
 * and OpenCode V2 (root `index.js` re-export).
 */
export async function PersonalMarketplacePlugin() {
  const skillDirs = discoverPluginSkillDirs();
  return {
    name: 'personal-marketplace',
    skillDirs,
  };
}

export default PersonalMarketplacePlugin;
