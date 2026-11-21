import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export interface NewPluginOptions {
  id: string;
  name: string;
  category: string;
  description: string;
  rootDir?: string;
}

const OWNER_NAME = 'Angel Ramirez';
const OWNER_EMAIL = 'angelgabriel.16ra@gmail.com';
const REPO_URL = 'https://github.com/Angel-SSJ/personal-marketplace';
const ANTIGRAVITY_SCHEMA_URL = 'https://antigravity.google/schemas/v1/plugin.json';
const KEBAB_CASE_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const RESERVED_BRAND_PREFIX_RE = /^(antigravity|gemini|claude|cursor)\b/i;

function writeJson(filePath: string, data: unknown): void {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

function readJson<T>(filePath: string): T {
  return JSON.parse(fs.readFileSync(filePath, 'utf8')) as T;
}

function createStarterLogoSvg(displayName: string): string {
  const initial = displayName.trim().charAt(0).toUpperCase() || 'P';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" width="128" height="128" role="img" aria-label="${displayName} logo">
  <rect x="12" y="12" width="104" height="104" rx="24" fill="#111827" />
  <text x="64" y="80" text-anchor="middle" font-family="system-ui, sans-serif" font-size="56" font-weight="700" fill="#f9fafb">${initial}</text>
</svg>
`;
}

/**
 * Scaffolds a new multi-provider plugin under `plugins/<id>/` with native
 * manifests for all 6 AI providers and registers it across marketplace catalogs.
 */
export function scaffoldPlugin(options: NewPluginOptions): {
  pluginDir: string;
  createdFiles: string[];
} {
  const rootDir = options.rootDir ?? process.cwd();
  const { id, name, category, description } = options;

  if (!KEBAB_CASE_RE.test(id)) {
    throw new Error(
      `Invalid plugin id "${id}". Must be lowercase kebab-case (^[a-z0-9]+(-[a-z0-9]+)*$).`,
    );
  }
  if (RESERVED_BRAND_PREFIX_RE.test(id) || RESERVED_BRAND_PREFIX_RE.test(name.trim())) {
    throw new Error(
      `Plugin id/name must not start with reserved provider names ("Antigravity", "Gemini", "Claude", or "Cursor").`,
    );
  }
  if (!name.trim()) {
    throw new Error('Plugin display name (--name) is required.');
  }
  if (!description.trim() || description.length > 1024) {
    throw new Error('Plugin description (--description) must be 1..1024 characters.');
  }

  const categoriesFile = path.join(rootDir, 'schemas', 'enums', 'categories.json');
  const categories = readJson<{ values: string[] }>(categoriesFile).values;
  if (!categories.includes(category)) {
    throw new Error(`Invalid category "${category}". Allowed values: ${categories.join(', ')}`);
  }

  const pkg = readJson<{ version: string }>(path.join(rootDir, 'package.json'));
  const version = pkg.version;
  const pluginDir = path.join(rootDir, 'plugins', id);

  if (fs.existsSync(pluginDir)) {
    throw new Error(`Plugin directory already exists: plugins/${id}`);
  }

  const createdFiles: string[] = [];
  const track = (filePath: string) => {
    createdFiles.push(path.relative(rootDir, filePath).replaceAll('\\', '/'));
  };

  // 1. Claude Code & Cowork manifest
  const claudeManifestPath = path.join(pluginDir, '.claude-plugin', 'plugin.json');
  writeJson(claudeManifestPath, {
    name: id,
    version,
    description,
    author: { name: OWNER_NAME, email: OWNER_EMAIL },
    repository: REPO_URL,
    skills: './skills/',
  });
  track(claudeManifestPath);

  // 2. Cursor native manifest (closed schema)
  const cursorManifestPath = path.join(pluginDir, '.cursor-plugin', 'plugin.json');
  writeJson(cursorManifestPath, {
    name: id,
    displayName: name,
    description,
    version,
    publisher: OWNER_NAME,
    author: { name: OWNER_NAME, email: OWNER_EMAIL },
    repository: REPO_URL,
    logo: 'assets/logo.svg',
    category,
    keywords: [category, id],
    skills: './skills/',
  });
  track(cursorManifestPath);

  // 3. OpenAI Codex native manifest (explicit hooks: {} prevents Claude hook collisions)
  const codexManifestPath = path.join(pluginDir, '.codex-plugin', 'plugin.json');
  writeJson(codexManifestPath, {
    name: id,
    version,
    description,
    author: { name: OWNER_NAME, email: OWNER_EMAIL },
    repository: REPO_URL,
    keywords: [category, id],
    skills: './skills/',
    hooks: {},
    interface: {
      displayName: name,
      shortDescription: description,
      developerName: OWNER_NAME,
      category,
      logo: 'assets/logo.svg',
    },
  });
  track(codexManifestPath);

  // 4. Antigravity native manifest (aligned with https://antigravity.google/schemas/v1/plugin.json)
  const agyManifestPath = path.join(pluginDir, '.antigravity-plugin', 'plugin.json');
  writeJson(agyManifestPath, {
    $schema: ANTIGRAVITY_SCHEMA_URL,
    name: id,
    displayName: name,
    version,
    description,
    logo: 'assets/logo.svg',
    suggestedPrompts: [
      `Use ${name} to review this workspace`,
      `Show available workflows in ${name}`,
      `Run the ${id} checklist on my current changes`,
    ],
    author: { name: OWNER_NAME, email: OWNER_EMAIL },
    homepage: `${REPO_URL}/tree/main/plugins/${id}`,
    repository: REPO_URL,
    license: 'MIT',
    keywords: [category, id],
  });
  track(agyManifestPath);

  // 4b. Antigravity Marketplace pre-install detail README (scoped inside plugin, never root README.md)
  const agyReadmePath = path.join(pluginDir, '.antigravity-plugin', 'README.md');
  fs.writeFileSync(
    agyReadmePath,
    `# ${name}

${description}

## Included Capabilities

- **Skill:** \`/${id}\` (\`skills/${id}/SKILL.md\`)

## Installation in Antigravity

\`\`\`bash
agy plugin validate ./plugins/${id}
agy plugin install ./plugins/${id}
\`\`\`
`,
    'utf8',
  );
  track(agyReadmePath);

  // 5. Kimi Code native manifest
  const kimiManifestPath = path.join(pluginDir, '.kimi-plugin', 'plugin.json');
  writeJson(kimiManifestPath, {
    name: id,
    version,
    description,
    keywords: [category, id],
    author: { name: OWNER_NAME, email: OWNER_EMAIL },
    skills: './skills/',
    interface: {
      displayName: name,
      shortDescription: description,
      developerName: OWNER_NAME,
    },
  });
  track(kimiManifestPath);

  // 6. Starter logo SVG asset
  const logoPath = path.join(pluginDir, 'assets', 'logo.svg');
  fs.mkdirSync(path.dirname(logoPath), { recursive: true });
  fs.writeFileSync(logoPath, createStarterLogoSvg(name), 'utf8');
  track(logoPath);

  // 7. Harness-agnostic SKILL.md (Agent Skills open standard)
  const skillPath = path.join(pluginDir, 'skills', id, 'SKILL.md');
  fs.mkdirSync(path.dirname(skillPath), { recursive: true });
  fs.writeFileSync(
    skillPath,
    `---
name: ${id}
description: ${description}
---

# ${name}

## When to Use

Use this skill when working on tasks related to **${name}**.

## Procedure

1. Inspect the relevant workspace files and confirm scope.
2. Execute the workflow using the active harness's native file and command tools.
3. Verify outcomes before concluding.
`,
    'utf8',
  );
  track(skillPath);

  // 8. Plugin-level human guide
  const guidePath = path.join(pluginDir, 'GUIDE.md');
  fs.writeFileSync(
    guidePath,
    `# ${name}

${description}

## Metadata

- **ID:** \`${id}\`
- **Category:** \`${category}\`
- **Version:** \`${version}\`
- **Providers:** Codex, Claude, Antigravity, Cursor, Kimi Code, OpenCode
`,
    'utf8',
  );
  track(guidePath);

  // 9. Register in root provider marketplace manifests.
  const claudeMarketPath = path.join(rootDir, '.claude-plugin', 'marketplace.json');
  const claudeMarket = readJson<{ plugins: Array<Record<string, unknown>> }>(claudeMarketPath);
  claudeMarket.plugins.push({
    name: id,
    displayName: name,
    description,
    version,
    category,
    author: { name: OWNER_NAME, email: OWNER_EMAIL },
    strict: true,
    source: `./plugins/${id}`,
  });
  writeJson(claudeMarketPath, claudeMarket);

  const cursorMarketPath = path.join(rootDir, '.cursor-plugin', 'marketplace.json');
  const cursorMarket = readJson<{ plugins: Array<Record<string, unknown>> }>(cursorMarketPath);
  cursorMarket.plugins.push({
    name: id,
    source: `plugins/${id}`,
    description,
    minClientVersions: {},
  });
  writeJson(cursorMarketPath, cursorMarket);

  const codexMarketPath = path.join(rootDir, '.agents', 'plugins', 'marketplace.json');
  const codexMarket = readJson<{ plugins: Array<Record<string, unknown>> }>(codexMarketPath);
  codexMarket.plugins.push({
    name: id,
    source: { source: 'local', path: `./plugins/${id}` },
    policy: { installation: 'AVAILABLE', authentication: 'NONE' },
    category,
  });
  writeJson(codexMarketPath, codexMarket);

  const kimiMarketPath = path.join(rootDir, '.kimi-plugin', 'marketplace.json');
  const kimiMarket = readJson<{ plugins: Array<Record<string, unknown>> }>(kimiMarketPath);
  kimiMarket.plugins.push({
    id,
    displayName: name,
    source: `./plugins/${id}`,
    clients: ['cli', 'desktop'],
    platforms: ['macos', 'windows', 'linux'],
  });
  writeJson(kimiMarketPath, kimiMarket);

  // 10. Append row to docs/CATALOG.md if present.
  const catalogPath = path.join(rootDir, 'docs', 'CATALOG.md');
  if (fs.existsSync(catalogPath)) {
    const existing = fs.readFileSync(catalogPath, 'utf8');
    const row = `| \`${id}\` | ${name} | \`${category}\` | All 6 | ${description} |`;
    const placeholderRe = /^\| [_*]\(none yet\)[_*]\s*\|.*$/m;
    const updated = placeholderRe.test(existing)
      ? existing.replace(placeholderRe, row)
      : `${existing.trimEnd()}\n${row}\n`;
    fs.writeFileSync(catalogPath, updated, 'utf8');
  }

  return { pluginDir, createdFiles };
}

function parseCliArgs(argv: string[]): NewPluginOptions {
  const map = new Map<string, string>();
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg.startsWith('--') && i + 1 < argv.length) {
      map.set(arg.slice(2), argv[i + 1]);
      i += 1;
    }
  }
  return {
    id: map.get('id') ?? '',
    name: map.get('name') ?? '',
    category: map.get('category') ?? 'development',
    description: map.get('description') ?? '',
  };
}

function isMainModule(): boolean {
  const entry = process.argv[1];
  return Boolean(entry && import.meta.url === pathToFileURL(path.resolve(entry)).href);
}

if (isMainModule()) {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(
      'Usage: pnpm run plugin:new -- --id <kebab-id> --name "<Display Name>" --category <category> --description "<description>"',
    );
    process.exit(0);
  }
  const options = parseCliArgs(args);
  const result = scaffoldPlugin(options);
  console.log(`Scaffolded plugin "${options.id}" (${result.createdFiles.length} file(s) created):`);
  for (const file of result.createdFiles) {
    console.log(`  + ${file}`);
  }
}
