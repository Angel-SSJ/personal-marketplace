import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { describe, it } from 'node:test';
import { lintHtmlFiles } from '../scripts/lint-html.ts';
import { validateRepository } from '../scripts/validate.ts';

function copyMinimalRepo(tempDir: string): void {
  const dirsToCopy = ['.claude-plugin', '.cursor-plugin', '.agents', '.kimi-plugin', 'schemas'];
  for (const relDir of dirsToCopy) {
    fs.cpSync(path.join(process.cwd(), relDir), path.join(tempDir, relDir), { recursive: true });
  }
  fs.mkdirSync(path.join(tempDir, 'plugins'), { recursive: true });
}

describe('validateRepository', () => {
  it('passes on the current repository skeleton', () => {
    const result = validateRepository(process.cwd());
    assert.deepEqual(result.errors, []);
    assert.ok(result.checkedFiles >= 8);
  });

  it('catches invalid SKILL.md frontmatter (mismatched dir & long description)', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-validate-skill-'));
    try {
      copyMinimalRepo(tempDir);
      const skillDir = path.join(tempDir, 'plugins', 'demo', 'skills', 'real-skill');
      fs.mkdirSync(skillDir, { recursive: true });
      fs.writeFileSync(
        path.join(skillDir, 'SKILL.md'),
        `---\nname: wrong-name\ndescription: "${'x'.repeat(1025)}"\n---\n\n# Demo\n`,
        'utf8',
      );
      const result = validateRepository(tempDir);
      assert.ok(result.errors.some((e) => e.includes('must match parent directory')));
      assert.ok(result.errors.some((e) => e.includes('exceeds 1024 chars')));
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it('catches malformed SVG XML and invalid TOML / YAML entity entries', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-validate-assets-'));
    try {
      copyMinimalRepo(tempDir);
      const pluginDir = path.join(tempDir, 'plugins', 'demo');
      fs.mkdirSync(path.join(pluginDir, 'assets'), { recursive: true });
      fs.writeFileSync(path.join(pluginDir, 'assets', 'broken.svg'), '<svg><rect></svg>', 'utf8');
      fs.writeFileSync(
        path.join(pluginDir, 'entity.toml'),
        'id = "Invalid_ID"\nname = "Bad"\ntype = "plugin"\nentry = "missing.md"\n',
        'utf8',
      );
      fs.writeFileSync(
        path.join(pluginDir, 'entity.yml'),
        'id: demo-yaml\nname: Demo\ntype: unknown-type\nentry: missing.md\n',
        'utf8',
      );
      const result = validateRepository(tempDir);
      assert.ok(result.errors.some((e) => e.includes('broken.svg') && e.includes('invalid XML')));
      assert.ok(result.errors.some((e) => e.includes('entity.toml')));
      assert.ok(result.errors.some((e) => e.includes('entity.yml')));
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it('catches forbidden extra keys in Antigravity and Codex hook collision', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-validate-providers-'));
    try {
      copyMinimalRepo(tempDir);
      const pluginDir = path.join(tempDir, 'plugins', 'demo');
      fs.mkdirSync(path.join(pluginDir, '.antigravity-plugin'), { recursive: true });
      fs.mkdirSync(path.join(pluginDir, '.codex-plugin'), { recursive: true });
      fs.mkdirSync(path.join(pluginDir, 'hooks'), { recursive: true });

      fs.writeFileSync(path.join(pluginDir, 'hooks', 'hooks.json'), '{}\n', 'utf8');
      fs.writeFileSync(
        path.join(pluginDir, '.antigravity-plugin', 'plugin.json'),
        JSON.stringify({
          name: 'demo',
          description: 'Demo plugin',
          logo: 'assets/missing.svg',
          unknownField: true,
        }),
        'utf8',
      );
      fs.writeFileSync(
        path.join(pluginDir, '.codex-plugin', 'plugin.json'),
        JSON.stringify({
          name: 'demo',
          version: '0.1.0',
          description: 'Demo plugin',
        }),
        'utf8',
      );

      const result = validateRepository(tempDir);
      assert.ok(result.errors.some((e) => e.includes('additional properties')));
      assert.ok(result.errors.some((e) => e.includes('referenced logo')));
      assert.ok(result.errors.some((e) => e.includes('explicitly set "hooks": {}')));
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it('lints valid and invalid HTML assets via lintHtmlFiles', async () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-validate-html-'));
    try {
      fs.copyFileSync(
        path.join(process.cwd(), '.htmlvalidate.json'),
        path.join(tempDir, '.htmlvalidate.json'),
      );
      fs.writeFileSync(
        path.join(tempDir, 'invalid.html'),
        '<!DOCTYPE html><html lang="en"><head><title>Bad</title></head><body><img src="x.png"></body></html>\n',
        'utf8',
      );
      const result = await lintHtmlFiles(tempDir);
      assert.equal(result.checked, 1);
      assert.ok(result.errors.length > 0);
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });

  it('catches Antigravity Marketplace & component pitfalls (branding, mcp_config, hooks, rules, agents)', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-validate-agy-'));
    try {
      copyMinimalRepo(tempDir);
      const pluginDir = path.join(tempDir, 'plugins', 'demo-kit');
      fs.mkdirSync(path.join(pluginDir, '.antigravity-plugin'), { recursive: true });
      fs.mkdirSync(path.join(pluginDir, 'rules'), { recursive: true });
      fs.mkdirSync(path.join(pluginDir, 'agents'), { recursive: true });

      fs.writeFileSync(
        path.join(pluginDir, '.antigravity-plugin', 'plugin.json'),
        JSON.stringify({
          $schema: 'https://antigravity.google/schemas/v1/plugin.json',
          name: 'antigravity-helper',
          displayName: 'Antigravity Helper',
          version: '0.1.0',
          description: 'Invalid branded name test.',
        }),
        'utf8',
      );
      const pluginRootToken = ['$', '{PLUGIN_ROOT}'].join('');
      fs.writeFileSync(
        path.join(pluginDir, 'mcp_config.json'),
        JSON.stringify({
          mcpServers: {
            helper: {
              command: 'node',
              args: [`${pluginRootToken}/scripts/server.js`],
              env: { PLUGIN_ROOT: '/bad' },
            },
          },
        }),
        'utf8',
      );
      fs.writeFileSync(
        path.join(pluginDir, 'hooks.json'),
        JSON.stringify({
          guard: {
            Stop: [{ type: 'command', command: `node ${pluginRootToken}/scripts/stop.js` }],
          },
        }),
        'utf8',
      );
      fs.writeFileSync(
        path.join(pluginDir, 'rules', 'infra.md'),
        '---\ntrigger: glob\nglobs:\n  - "**/*.tf"\n---\n\n# Rule\n',
        'utf8',
      );
      fs.writeFileSync(
        path.join(pluginDir, 'agents', 'reviewer.md'),
        '---\nname: reviewer\ndescription: Reviews code\nmodel: ultra-invalid\n---\n\n# Agent\n',
        'utf8',
      );

      const result = validateRepository(tempDir);
      assert.ok(result.errors.some((e) => e.includes('must not start with a provider name')));
      assert.ok(result.errors.some((e) => e.includes('must not redeclare built-in PLUGIN_ROOT')));
      assert.ok(result.errors.some((e) => e.includes(`instead of ${pluginRootToken}`)));
      assert.ok(result.errors.some((e) => e.includes('comma-separated string')));
      assert.ok(result.errors.some((e) => e.includes('invalid agent model')));
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
