import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import AjvModule from 'ajv';
import addFormatsModule from 'ajv-formats';
import { XMLValidator } from 'fast-xml-parser';
import matter from 'gray-matter';
import { parse as parseToml } from 'smol-toml';
import { parse as parseYaml } from 'yaml';

// Normalize ESM/CJS default interop cleanly for Node 24/25 + TS 7 (nodenext).
type AjvClass = typeof AjvModule.default;
type AddFormatsFn = typeof addFormatsModule.default;

const AjvCtor: AjvClass =
  typeof AjvModule === 'function' ? (AjvModule as unknown as AjvClass) : AjvModule.default;
const addFormats: AddFormatsFn =
  typeof addFormatsModule === 'function'
    ? (addFormatsModule as unknown as AddFormatsFn)
    : addFormatsModule.default;

export interface ValidationResult {
  errors: string[];
  warnings: string[];
  checkedFiles: number;
}

const IGNORED_DIRS = new Set([
  '.git',
  'node_modules',
  'dist',
  'coverage',
  '.scratch',
  'tmp',
  'temp',
]);

const KEBAB_CASE_RE = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const RESERVED_BRAND_PREFIX_RE = /^(antigravity|gemini|claude|cursor)\b/i;
const PLUGIN_ROOT_TOKEN = ['$', '{PLUGIN_ROOT}'].join('');
const VALID_RULE_TRIGGERS = new Set(['always_on', 'model_decision', 'glob', 'manual']);
const VALID_AGENT_MODELS = new Set(['inherit', 'flash_lite', 'flash', 'pro']);
const VALID_EXEC_POLICIES = new Set(['off', 'auto', 'eager', 'sandbox']);

function readJson(filePath: string): unknown {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function walkFiles(dir: string, predicate: (filePath: string) => boolean): string[] {
  if (!fs.existsSync(dir)) {
    return [];
  }
  const results: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORED_DIRS.has(entry.name)) {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...walkFiles(fullPath, predicate));
    } else if (entry.isFile() && predicate(fullPath)) {
      results.push(fullPath);
    }
  }
  return results;
}

function rel(rootDir: string, filePath: string): string {
  return path.relative(rootDir, filePath).replaceAll('\\', '/');
}

function formatAjvErrors(
  errors: Array<{ instancePath?: string; message?: string }> | null | undefined,
): string {
  if (!errors || errors.length === 0) {
    return 'unknown schema error';
  }
  return errors.map((e) => `${e.instancePath || '/'} ${e.message ?? ''}`.trim()).join('; ');
}

function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Validates all repository manifests, enums, TOML/YAML entity files,
 * plugin manifests, SKILL.md frontmatter, cross-file references, and SVG XML.
 */
export function validateRepository(rootDir: string = process.cwd()): ValidationResult {
  const errors: string[] = [];
  const warnings: string[] = [];
  let checkedFiles = 0;

  const schemasDir = path.join(rootDir, 'schemas');
  const ajv = new AjvCtor({ allErrors: true, strict: false });
  addFormats(ajv);

  const loadSchema = (name: string) => {
    const schemaPath = path.join(schemasDir, name);
    if (!fs.existsSync(schemaPath)) {
      throw new Error(`Missing required schema: ${rel(rootDir, schemaPath)}`);
    }
    return readJson(schemaPath) as Record<string, unknown>;
  };

  // 1. Validate root native marketplace manifests across providers.
  const rootMarketplaceChecks: Array<{ file: string; schema: string }> = [
    { file: '.claude-plugin/marketplace.json', schema: 'claude-marketplace.schema.json' },
    { file: '.cursor-plugin/marketplace.json', schema: 'cursor-marketplace.schema.json' },
    { file: '.agents/plugins/marketplace.json', schema: 'codex-marketplace.schema.json' },
    { file: '.agents/plugins.json', schema: 'antigravity-plugins.schema.json' },
    { file: '.kimi-plugin/marketplace.json', schema: 'kimi-marketplace.schema.json' },
  ];

  for (const check of rootMarketplaceChecks) {
    const targetPath = path.join(rootDir, check.file);
    if (!fs.existsSync(targetPath)) {
      errors.push(`Missing required marketplace manifest: ${check.file}`);
      continue;
    }
    checkedFiles += 1;
    try {
      const data = readJson(targetPath);
      const validate = ajv.compile(loadSchema(check.schema));
      if (!validate(data)) {
        errors.push(`${check.file}: ${formatAjvErrors(validate.errors)}`);
      }
    } catch (err) {
      errors.push(`${check.file}: invalid JSON (${(err as Error).message})`);
    }
  }

  // 2. Validate enum JSON files under schemas/enums/.
  const enumsDir = path.join(schemasDir, 'enums');
  for (const enumFile of walkFiles(enumsDir, (p) => p.endsWith('.json'))) {
    checkedFiles += 1;
    try {
      const parsed = readJson(enumFile);
      if (
        !isObjectRecord(parsed) ||
        !Array.isArray(parsed.values) ||
        parsed.values.length === 0 ||
        !parsed.values.every((v) => typeof v === 'string' && v.length > 0)
      ) {
        errors.push(`${rel(rootDir, enumFile)}: must contain a non-empty string[] "values" field`);
      }
    } catch (err) {
      errors.push(`${rel(rootDir, enumFile)}: invalid JSON (${(err as Error).message})`);
    }
  }

  // 3. Validate TOML entity files under plugins/ and entities/.
  const entitySchema = loadSchema('entity-entry.schema.json');
  const validateEntity = ajv.compile(entitySchema);

  for (const baseFolder of ['plugins', 'entities']) {
    const dir = path.join(rootDir, baseFolder);
    for (const tomlFile of walkFiles(dir, (p) => p.endsWith('.toml'))) {
      checkedFiles += 1;
      try {
        const parsed = parseToml(fs.readFileSync(tomlFile, 'utf8'));
        if (!validateEntity(parsed)) {
          errors.push(`${rel(rootDir, tomlFile)}: ${formatAjvErrors(validateEntity.errors)}`);
        } else if (isObjectRecord(parsed) && typeof parsed.entry === 'string') {
          const entryPath = path.resolve(path.dirname(tomlFile), parsed.entry);
          if (!fs.existsSync(entryPath)) {
            errors.push(
              `${rel(rootDir, tomlFile)}: referenced entry "${parsed.entry}" does not exist`,
            );
          }
        }
      } catch (err) {
        errors.push(`${rel(rootDir, tomlFile)}: invalid TOML (${(err as Error).message})`);
      }
    }
  }

  // 4. Validate YAML files syntax everywhere + schema under plugins/ & entities/.
  const yamlFiles = walkFiles(
    rootDir,
    (p) => (p.endsWith('.yml') || p.endsWith('.yaml')) && path.basename(p) !== 'pnpm-lock.yaml',
  );
  for (const yamlFile of yamlFiles) {
    checkedFiles += 1;
    try {
      const parsed = parseYaml(fs.readFileSync(yamlFile, 'utf8'));
      const relative = rel(rootDir, yamlFile);
      if (
        (relative.startsWith('plugins/') || relative.startsWith('entities/')) &&
        !relative.includes('/.hermes-plugin/') &&
        !relative.includes('/agents/')
      ) {
        if (!validateEntity(parsed)) {
          errors.push(`${relative}: ${formatAjvErrors(validateEntity.errors)}`);
        }
      }
    } catch (err) {
      errors.push(`${rel(rootDir, yamlFile)}: invalid YAML (${(err as Error).message})`);
    }
  }

  // 5. Validate per-plugin native provider manifests and cross-file references.
  const pluginManifestSchema = loadSchema('plugin-manifest.schema.json');
  ajv.addSchema(pluginManifestSchema, 'plugin-manifest.schema.json');
  const validateAgyMcp = ajv.compile(loadSchema('antigravity-mcp-config.schema.json'));
  const validateAgyHooks = ajv.compile(loadSchema('antigravity-hooks.schema.json'));

  const pluginsDir = path.join(rootDir, 'plugins');
  if (fs.existsSync(pluginsDir)) {
    const providerManifestMap: Array<{
      provider: 'claude' | 'cursor' | 'codex' | 'antigravity' | 'kimi';
      relPaths: string[];
    }> = [
      { provider: 'claude', relPaths: ['.claude-plugin/plugin.json'] },
      { provider: 'cursor', relPaths: ['.cursor-plugin/plugin.json'] },
      { provider: 'codex', relPaths: ['.codex-plugin/plugin.json'] },
      { provider: 'antigravity', relPaths: ['.antigravity-plugin/plugin.json', 'plugin.json'] },
      { provider: 'kimi', relPaths: ['.kimi-plugin/plugin.json', 'kimi.plugin.json'] },
    ];

    for (const entry of fs.readdirSync(pluginsDir, { withFileTypes: true })) {
      if (!entry.isDirectory()) {
        continue;
      }
      const pluginDir = path.join(pluginsDir, entry.name);
      const pluginRel = rel(rootDir, pluginDir);

      if (!KEBAB_CASE_RE.test(entry.name)) {
        errors.push(`${pluginRel}: plugin folder name must be lowercase kebab-case`);
      }

      const hasClaudeHooks = fs.existsSync(path.join(pluginDir, 'hooks', 'hooks.json'));

      for (const item of providerManifestMap) {
        const foundRel = item.relPaths.find((candidate) =>
          fs.existsSync(path.join(pluginDir, candidate)),
        );
        if (!foundRel) {
          continue;
        }
        const manifestPath = path.join(pluginDir, foundRel);
        checkedFiles += 1;
        try {
          const data = readJson(manifestPath);
          const validate = ajv.getSchema(
            `plugin-manifest.schema.json#/definitions/${item.provider}`,
          );
          if (validate && !validate(data)) {
            errors.push(`${rel(rootDir, manifestPath)}: ${formatAjvErrors(validate.errors)}`);
          }

          if (isObjectRecord(data)) {
            // Cross-file reference check for logo / skills paths.
            if (typeof data.logo === 'string' && !data.logo.startsWith('http')) {
              const logoTarget = path.resolve(pluginDir, data.logo);
              if (!fs.existsSync(logoTarget)) {
                errors.push(
                  `${rel(rootDir, manifestPath)}: referenced logo "${data.logo}" does not exist`,
                );
              }
            }
            if (typeof data.skills === 'string') {
              const skillsTarget = path.resolve(pluginDir, data.skills);
              if (!fs.existsSync(skillsTarget)) {
                errors.push(
                  `${rel(rootDir, manifestPath)}: referenced skills path "${data.skills}" does not exist`,
                );
              }
            } else if (Array.isArray(data.skills)) {
              for (const skillPathEntry of data.skills) {
                if (typeof skillPathEntry === 'string') {
                  const target = path.resolve(pluginDir, skillPathEntry);
                  if (!fs.existsSync(target)) {
                    errors.push(
                      `${rel(rootDir, manifestPath)}: referenced skills path "${skillPathEntry}" does not exist`,
                    );
                  }
                }
              }
            }
            // Antigravity Marketplace branding rule.
            if (item.provider === 'antigravity') {
              if (typeof data.name === 'string' && RESERVED_BRAND_PREFIX_RE.test(data.name)) {
                errors.push(
                  `${rel(rootDir, manifestPath)}: Antigravity plugin "name" must not start with a provider name (Antigravity, Gemini, Claude, Cursor)`,
                );
              }
              if (
                typeof data.displayName === 'string' &&
                RESERVED_BRAND_PREFIX_RE.test(data.displayName)
              ) {
                errors.push(
                  `${rel(rootDir, manifestPath)}: Antigravity plugin "displayName" must not start with a provider name (Antigravity, Gemini, Claude, Cursor)`,
                );
              }
            }
            // Codex trap from obra/superpowers: prevent accidental Claude hook auto-discovery.
            if (item.provider === 'codex' && hasClaudeHooks && data.hooks === undefined) {
              errors.push(
                `${rel(rootDir, manifestPath)}: plugin contains hooks/hooks.json; explicitly set "hooks": {} in .codex-plugin/plugin.json to prevent Codex from auto-loading Claude hooks`,
              );
            }
          }
        } catch (err) {
          errors.push(`${rel(rootDir, manifestPath)}: invalid JSON (${(err as Error).message})`);
        }
      }

      // 5b. Antigravity plugin component validations (mcp_config.json, hooks.json, rules/*.md, agents/*.md).
      const mcpConfigPath = path.join(pluginDir, 'mcp_config.json');
      if (fs.existsSync(mcpConfigPath)) {
        checkedFiles += 1;
        try {
          const mcpData = readJson(mcpConfigPath);
          if (!validateAgyMcp(mcpData)) {
            errors.push(
              `${rel(rootDir, mcpConfigPath)}: ${formatAjvErrors(validateAgyMcp.errors)}`,
            );
          } else if (isObjectRecord(mcpData) && isObjectRecord(mcpData.mcpServers)) {
            for (const [serverName, serverDef] of Object.entries(mcpData.mcpServers)) {
              if (isObjectRecord(serverDef) && isObjectRecord(serverDef.env)) {
                if ('PLUGIN_ROOT' in serverDef.env || 'PLUGIN_DATA' in serverDef.env) {
                  errors.push(
                    `${rel(rootDir, mcpConfigPath)}: mcpServers.${serverName}.env must not redeclare built-in PLUGIN_ROOT or PLUGIN_DATA`,
                  );
                }
              }
            }
          }
        } catch (err) {
          errors.push(`${rel(rootDir, mcpConfigPath)}: invalid JSON (${(err as Error).message})`);
        }
      }

      const rootHooksPath = path.join(pluginDir, 'hooks.json');
      if (fs.existsSync(rootHooksPath)) {
        checkedFiles += 1;
        try {
          const hooksRaw = fs.readFileSync(rootHooksPath, 'utf8');
          const hooksData = JSON.parse(hooksRaw);
          if (!validateAgyHooks(hooksData)) {
            errors.push(
              `${rel(rootDir, rootHooksPath)}: ${formatAjvErrors(validateAgyHooks.errors)}`,
            );
          }
          if (hooksRaw.includes(PLUGIN_ROOT_TOKEN)) {
            errors.push(
              `${rel(rootDir, rootHooksPath)}: use relative script paths (./scripts/...) instead of ${PLUGIN_ROOT_TOKEN} in Antigravity hooks.json`,
            );
          }
        } catch (err) {
          errors.push(`${rel(rootDir, rootHooksPath)}: invalid JSON (${(err as Error).message})`);
        }
      }

      const rulesDir = path.join(pluginDir, 'rules');
      for (const ruleFile of walkFiles(rulesDir, (p) => p.endsWith('.md'))) {
        const base = path.basename(ruleFile);
        if (base === 'AGENTS.md' || base === 'GEMINI.md') {
          continue;
        }
        checkedFiles += 1;
        const relative = rel(rootDir, ruleFile);
        try {
          const fm = matter(fs.readFileSync(ruleFile, 'utf8')).data;
          if (fm.trigger !== undefined) {
            if (typeof fm.trigger !== 'string' || !VALID_RULE_TRIGGERS.has(fm.trigger)) {
              errors.push(
                `${relative}: invalid rule trigger "${String(fm.trigger)}" (allowed: always_on, model_decision, glob, manual)`,
              );
            } else if (fm.trigger === 'glob') {
              if (typeof fm.globs !== 'string' || fm.globs.trim().length === 0) {
                errors.push(
                  `${relative}: rule with trigger "glob" must define "globs" as a comma-separated string (not an array)`,
                );
              }
            } else if (fm.trigger === 'model_decision') {
              if (typeof fm.description !== 'string' || fm.description.trim().length === 0) {
                errors.push(
                  `${relative}: rule with trigger "model_decision" requires "description"`,
                );
              }
            }
          }
        } catch (err) {
          errors.push(`${relative}: failed to parse rule frontmatter (${(err as Error).message})`);
        }
      }

      const agentsDir = path.join(pluginDir, 'agents');
      for (const agentFile of walkFiles(agentsDir, (p) => p.endsWith('.md'))) {
        checkedFiles += 1;
        const relative = rel(rootDir, agentFile);
        try {
          const fm = matter(fs.readFileSync(agentFile, 'utf8')).data;
          if (typeof fm.name !== 'string' || !KEBAB_CASE_RE.test(fm.name)) {
            errors.push(`${relative}: agent frontmatter requires kebab-case "name"`);
          }
          if (typeof fm.description !== 'string' || fm.description.trim().length === 0) {
            errors.push(`${relative}: agent frontmatter requires non-empty "description"`);
          }
          if (
            fm.model !== undefined &&
            (typeof fm.model !== 'string' || !VALID_AGENT_MODELS.has(fm.model))
          ) {
            errors.push(
              `${relative}: invalid agent model "${String(fm.model)}" (allowed: inherit, flash_lite, flash, pro)`,
            );
          }
          if (
            fm.commandExecutionPolicy !== undefined &&
            (typeof fm.commandExecutionPolicy !== 'string' ||
              !VALID_EXEC_POLICIES.has(fm.commandExecutionPolicy))
          ) {
            errors.push(
              `${relative}: invalid commandExecutionPolicy "${String(fm.commandExecutionPolicy)}"`,
            );
          }
        } catch (err) {
          errors.push(`${relative}: failed to parse agent frontmatter (${(err as Error).message})`);
        }
      }
    }
  }

  // 6. Validate SKILL.md YAML frontmatter across the repository.
  const skillFiles = walkFiles(rootDir, (p) => path.basename(p) === 'SKILL.md');
  for (const skillFile of skillFiles) {
    checkedFiles += 1;
    const relative = rel(rootDir, skillFile);
    try {
      const parsed = matter(fs.readFileSync(skillFile, 'utf8'));
      const fm = parsed.data;
      const parentDirName = path.basename(path.dirname(skillFile));

      if (typeof fm.name !== 'string' || fm.name.trim().length === 0) {
        errors.push(`${relative}: missing required frontmatter field "name"`);
      } else {
        if (!KEBAB_CASE_RE.test(fm.name) || fm.name.length > 64) {
          errors.push(
            `${relative}: frontmatter "name" ("${fm.name}") must be kebab-case (1-64 chars)`,
          );
        }
        if (fm.name !== parentDirName) {
          errors.push(
            `${relative}: frontmatter "name" ("${fm.name}") must match parent directory ("${parentDirName}")`,
          );
        }
      }

      if (typeof fm.description !== 'string' || fm.description.trim().length === 0) {
        errors.push(`${relative}: missing required frontmatter field "description"`);
      } else if (fm.description.length > 1024) {
        errors.push(
          `${relative}: frontmatter "description" exceeds 1024 chars (${fm.description.length})`,
        );
      }
    } catch (err) {
      errors.push(`${relative}: failed to parse frontmatter (${(err as Error).message})`);
    }
  }

  // 7. Validate SVG XML well-formedness & <svg> root tag.
  const svgFiles = walkFiles(rootDir, (p) => p.endsWith('.svg'));
  for (const svgFile of svgFiles) {
    checkedFiles += 1;
    const relative = rel(rootDir, svgFile);
    const content = fs.readFileSync(svgFile, 'utf8');
    const xmlCheck = XMLValidator.validate(content);
    if (xmlCheck !== true) {
      errors.push(
        `${relative}: invalid XML (${xmlCheck.err.msg} at line ${xmlCheck.err.line}, col ${xmlCheck.err.col})`,
      );
    } else if (!/<svg[\s>]/i.test(content)) {
      errors.push(`${relative}: valid XML but missing root <svg> element`);
    }
  }

  return { errors, warnings, checkedFiles };
}

function isMainModule(): boolean {
  const entry = process.argv[1];
  return Boolean(entry && import.meta.url === pathToFileURL(path.resolve(entry)).href);
}

if (isMainModule()) {
  const result = validateRepository(process.cwd());
  for (const warning of result.warnings) {
    console.warn(`WARN: ${warning}`);
  }
  if (result.errors.length > 0) {
    for (const error of result.errors) {
      console.error(`ERROR: ${error}`);
    }
    console.error(
      `\nValidation failed with ${result.errors.length} error(s) across ${result.checkedFiles} checked file(s).`,
    );
    process.exit(1);
  }
  console.log(`Validation passed (${result.checkedFiles} file(s) checked).`);
}
