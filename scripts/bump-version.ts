import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { parse as parseToml } from 'smol-toml';
import { parse as parseYaml } from 'yaml';

export interface VersionTarget {
  file: string;
  format: 'json' | 'toml' | 'yaml';
  path: string;
}

export interface VersionBumpConfig {
  sourceOfTruth: {
    file: string;
    path: string;
  };
  targets: VersionTarget[];
  syncPluginManifests?: boolean;
  audit?: {
    exclude?: string[];
  };
}

const SEMVER_RE = /^(\d+)\.(\d+)\.(\d+)(-[0-9A-Za-z.-]+)?$/;

export function computeNextVersion(current: string, bumpArg: string): string {
  if (SEMVER_RE.test(bumpArg)) {
    return bumpArg;
  }
  const match = SEMVER_RE.exec(current);
  if (!match) {
    throw new Error(`Invalid current semver version: "${current}"`);
  }
  const major = Number(match[1]);
  const minor = Number(match[2]);
  const patch = Number(match[3]);

  if (bumpArg === 'major') {
    return `${major + 1}.0.0`;
  }
  if (bumpArg === 'minor') {
    return `${major}.${minor + 1}.0`;
  }
  if (bumpArg === 'patch') {
    return `${major}.${minor}.${patch + 1}`;
  }
  throw new Error(
    `Invalid version argument "${bumpArg}". Use "patch", "minor", "major", or explicit "X.Y.Z".`,
  );
}

function getByDotPath(obj: unknown, dotPath: string): unknown {
  let cursor: unknown = obj;
  for (const segment of dotPath.split('.')) {
    if (cursor === null || cursor === undefined || typeof cursor !== 'object') {
      return undefined;
    }
    cursor = (cursor as Record<string, unknown>)[segment];
  }
  return cursor;
}

function setByDotPath(obj: Record<string, unknown>, dotPath: string, value: string): void {
  const segments = dotPath.split('.');
  let cursor: Record<string, unknown> = obj;
  for (let i = 0; i < segments.length - 1; i += 1) {
    const key = segments[i];
    const next = cursor[key];
    if (typeof next !== 'object' || next === null) {
      throw new Error(`Path "${dotPath}" does not exist in target object`);
    }
    cursor = next as Record<string, unknown>;
  }
  const finalKey = segments[segments.length - 1];
  cursor[finalKey] = value;
}

function discoverDynamicTargets(rootDir: string, config: VersionBumpConfig): VersionTarget[] {
  const targets: VersionTarget[] = [...config.targets];
  if (!config.syncPluginManifests) {
    return targets;
  }

  // Also keep Claude marketplace per-plugin version entries in lockstep.
  const claudeMarketplacePath = path.join(rootDir, '.claude-plugin', 'marketplace.json');
  if (fs.existsSync(claudeMarketplacePath)) {
    const marketplace = JSON.parse(fs.readFileSync(claudeMarketplacePath, 'utf8')) as {
      plugins?: Array<{ version?: string }>;
    };
    if (Array.isArray(marketplace.plugins)) {
      marketplace.plugins.forEach((plugin, index) => {
        if (typeof plugin.version === 'string') {
          targets.push({
            file: '.claude-plugin/marketplace.json',
            format: 'json',
            path: `plugins.${index}.version`,
          });
        }
      });
    }
  }

  // Discover all plugin manifests under plugins/<id>/.
  const pluginsDir = path.join(rootDir, 'plugins');
  if (!fs.existsSync(pluginsDir)) {
    return targets;
  }

  const candidateJsonFiles = [
    '.claude-plugin/plugin.json',
    '.cursor-plugin/plugin.json',
    '.codex-plugin/plugin.json',
    '.antigravity-plugin/plugin.json',
    'plugin.json',
    '.kimi-plugin/plugin.json',
    'kimi.plugin.json',
  ];

  for (const entry of fs.readdirSync(pluginsDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) {
      continue;
    }
    const pluginDir = path.join(pluginsDir, entry.name);
    for (const relManifest of candidateJsonFiles) {
      const fullPath = path.join(pluginDir, relManifest);
      if (!fs.existsSync(fullPath)) {
        continue;
      }
      const parsed = JSON.parse(fs.readFileSync(fullPath, 'utf8')) as Record<string, unknown>;
      if (typeof parsed.version === 'string') {
        targets.push({
          file: `plugins/${entry.name}/${relManifest}`,
          format: 'json',
          path: 'version',
        });
      }
    }
  }

  return targets;
}

function readTargetVersion(rootDir: string, target: VersionTarget): string | undefined {
  const fullPath = path.join(rootDir, target.file);
  if (!fs.existsSync(fullPath)) {
    return undefined;
  }
  const raw = fs.readFileSync(fullPath, 'utf8');
  if (target.format === 'json') {
    const value = getByDotPath(JSON.parse(raw), target.path);
    return typeof value === 'string' ? value : undefined;
  }
  if (target.format === 'toml') {
    const value = getByDotPath(parseToml(raw), target.path);
    return typeof value === 'string' ? value : undefined;
  }
  const value = getByDotPath(parseYaml(raw), target.path);
  return typeof value === 'string' ? value : undefined;
}

function writeTargetVersion(rootDir: string, target: VersionTarget, nextVersion: string): void {
  const fullPath = path.join(rootDir, target.file);
  const raw = fs.readFileSync(fullPath, 'utf8');

  if (target.format === 'json') {
    const parsed = JSON.parse(raw) as Record<string, unknown>;
    setByDotPath(parsed, target.path, nextVersion);
    fs.writeFileSync(fullPath, `${JSON.stringify(parsed, null, 2)}\n`, 'utf8');
    return;
  }

  if (target.format === 'toml') {
    const key = target.path.split('.').at(-1) ?? 'version';
    const regex = new RegExp(`^(\\s*${key}\\s*=\\s*["'])([^"']+)(["'])`, 'm');
    if (!regex.test(raw)) {
      throw new Error(`Could not find TOML key "${key}" in ${target.file}`);
    }
    fs.writeFileSync(fullPath, raw.replace(regex, `$1${nextVersion}$3`), 'utf8');
    return;
  }

  const key = target.path.split('.').at(-1) ?? 'version';
  const regex = new RegExp(`^(\\s*${key}:\\s*["']?)([^"'\\r\\n]+)(["']?)`, 'm');
  if (!regex.test(raw)) {
    throw new Error(`Could not find YAML key "${key}" in ${target.file}`);
  }
  fs.writeFileSync(fullPath, raw.replace(regex, `$1${nextVersion}$3`), 'utf8');
}

export function loadBumpConfig(rootDir: string): VersionBumpConfig {
  const configPath = path.join(rootDir, '.version-bump.json');
  if (!fs.existsSync(configPath)) {
    throw new Error('Missing .version-bump.json at repository root');
  }
  return JSON.parse(fs.readFileSync(configPath, 'utf8')) as VersionBumpConfig;
}

export function checkVersions(rootDir: string = process.cwd()): {
  expected: string;
  mismatches: string[];
  checked: number;
} {
  const config = loadBumpConfig(rootDir);
  const expected = readTargetVersion(rootDir, {
    file: config.sourceOfTruth.file,
    format: 'json',
    path: config.sourceOfTruth.path,
  });
  if (!expected) {
    throw new Error(
      `Could not read source-of-truth version from ${config.sourceOfTruth.file}:${config.sourceOfTruth.path}`,
    );
  }

  const targets = discoverDynamicTargets(rootDir, config);
  const mismatches: string[] = [];

  for (const target of targets) {
    const actual = readTargetVersion(rootDir, target);
    if (actual !== expected) {
      mismatches.push(
        `${target.file} (${target.path}): expected "${expected}", found "${actual ?? 'missing'}"`,
      );
    }
  }

  return { expected, mismatches, checked: targets.length };
}

export function auditStaleVersions(
  rootDir: string = process.cwd(),
  staleVersion?: string,
): {
  expected: string;
  mismatches: string[];
  staleHits: string[];
} {
  const check = checkVersions(rootDir);
  const config = loadBumpConfig(rootDir);
  const excluded = new Set(config.audit?.exclude ?? []);
  const staleHits: string[] = [];

  if (!staleVersion || staleVersion === check.expected) {
    return { expected: check.expected, mismatches: check.mismatches, staleHits };
  }

  const scanDir = (dir: string): void => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const fullPath = path.join(dir, entry.name);
      const relative = path.relative(rootDir, fullPath).replaceAll('\\', '/');
      if (excluded.has(entry.name) || excluded.has(relative)) {
        continue;
      }
      if (entry.isDirectory()) {
        scanDir(fullPath);
      } else if (entry.isFile()) {
        const content = fs.readFileSync(fullPath, 'utf8');
        if (content.includes(staleVersion)) {
          staleHits.push(`${relative}: still references "${staleVersion}"`);
        }
      }
    }
  };

  scanDir(rootDir);
  return { expected: check.expected, mismatches: check.mismatches, staleHits };
}

export function bumpVersions(
  bumpArg: string,
  rootDir: string = process.cwd(),
): { previous: string; next: string; updatedFiles: string[] } {
  const config = loadBumpConfig(rootDir);
  const previous = readTargetVersion(rootDir, {
    file: config.sourceOfTruth.file,
    format: 'json',
    path: config.sourceOfTruth.path,
  });
  if (!previous) {
    throw new Error(`Could not read current version from ${config.sourceOfTruth.file}`);
  }

  const next = computeNextVersion(previous, bumpArg);
  const targets = discoverDynamicTargets(rootDir, config);
  const updated = new Set<string>();

  for (const target of targets) {
    writeTargetVersion(rootDir, target, next);
    updated.add(target.file);
  }

  return { previous, next, updatedFiles: [...updated] };
}

function isMainModule(): boolean {
  const entry = process.argv[1];
  return Boolean(entry && import.meta.url === pathToFileURL(path.resolve(entry)).href);
}

if (isMainModule()) {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(
      [
        'Usage:',
        '  node scripts/bump-version.ts <patch|minor|major|X.Y.Z>',
        '  node scripts/bump-version.ts --check',
        '  node scripts/bump-version.ts --audit [stale-version]',
      ].join('\n'),
    );
    process.exit(0);
  }

  if (args[0] === '--check') {
    const result = checkVersions(process.cwd());
    if (result.mismatches.length > 0) {
      for (const m of result.mismatches) {
        console.error(`MISMATCH: ${m}`);
      }
      process.exit(1);
    }
    console.log(`Version check passed: ${result.expected} (${result.checked} target(s) in sync).`);
    process.exit(0);
  }

  if (args[0] === '--audit') {
    const result = auditStaleVersions(process.cwd(), args[1]);
    if (result.mismatches.length > 0 || result.staleHits.length > 0) {
      for (const m of result.mismatches) {
        console.error(`MISMATCH: ${m}`);
      }
      for (const h of result.staleHits) {
        console.error(`STALE: ${h}`);
      }
      process.exit(1);
    }
    console.log(`Version audit passed: ${result.expected} (no drift or stale references).`);
    process.exit(0);
  }

  const { previous, next, updatedFiles } = bumpVersions(args[0], process.cwd());
  console.log(`Bumped version ${previous} -> ${next}`);
  for (const file of updatedFiles) {
    console.log(`  updated ${file}`);
  }
  console.log(`\nNext steps: update RELEASE-NOTES.md, commit, and tag v${next}.`);
}
