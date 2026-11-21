import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { describe, it } from 'node:test';
import { checkVersions } from '../scripts/bump-version.ts';
import { scaffoldPlugin } from '../scripts/new-plugin.ts';
import { validateRepository } from '../scripts/validate.ts';

describe('new-plugin scaffolder', () => {
  it('scaffolds a valid multi-provider plugin that passes validation and version check', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-scaffold-'));
    try {
      for (const rel of [
        '.claude-plugin',
        '.cursor-plugin',
        '.agents',
        '.kimi-plugin',
        'schemas',
        'docs',
      ]) {
        const src = path.join(process.cwd(), rel);
        if (fs.existsSync(src)) {
          fs.cpSync(src, path.join(tempDir, rel), { recursive: true });
        }
      }
      fs.copyFileSync(path.join(process.cwd(), 'package.json'), path.join(tempDir, 'package.json'));
      fs.copyFileSync(
        path.join(process.cwd(), '.version-bump.json'),
        path.join(tempDir, '.version-bump.json'),
      );
      fs.mkdirSync(path.join(tempDir, 'plugins'), { recursive: true });

      const scaffold = scaffoldPlugin({
        id: 'sample-kit',
        name: 'Sample Kit',
        category: 'development',
        description: 'A starter plugin for verifying multi-provider marketplace integration.',
        rootDir: tempDir,
      });

      assert.ok(scaffold.createdFiles.length >= 9);
      assert.ok(scaffold.createdFiles.includes('plugins/sample-kit/.antigravity-plugin/README.md'));
      const agyManifest = JSON.parse(
        fs.readFileSync(
          path.join(tempDir, 'plugins', 'sample-kit', '.antigravity-plugin', 'plugin.json'),
          'utf8',
        ),
      ) as Record<string, unknown>;
      assert.equal(agyManifest.$schema, 'https://antigravity.google/schemas/v1/plugin.json');
      assert.equal(agyManifest.license, 'MIT');

      const validation = validateRepository(tempDir);
      assert.deepEqual(validation.errors, []);

      const versions = checkVersions(tempDir);
      assert.deepEqual(versions.mismatches, []);
      assert.ok(versions.checked >= 7);
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
