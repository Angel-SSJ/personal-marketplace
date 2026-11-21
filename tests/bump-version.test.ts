import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { describe, it } from 'node:test';
import {
  auditStaleVersions,
  bumpVersions,
  checkVersions,
  computeNextVersion,
} from '../scripts/bump-version.ts';

describe('bump-version', () => {
  it('computes patch, minor, major, and explicit semver values', () => {
    assert.equal(computeNextVersion('0.1.0', 'patch'), '0.1.1');
    assert.equal(computeNextVersion('0.1.0', 'minor'), '0.2.0');
    assert.equal(computeNextVersion('0.1.0', 'major'), '1.0.0');
    assert.equal(computeNextVersion('0.1.0', '2.3.4'), '2.3.4');
  });

  it('syncs JSON, TOML, and YAML targets in lockstep and detects drift/stale strings', () => {
    const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'pm-bump-'));
    try {
      fs.mkdirSync(path.join(tempDir, '.claude-plugin'), { recursive: true });
      fs.writeFileSync(
        path.join(tempDir, 'package.json'),
        `${JSON.stringify({ name: 'test-repo', version: '0.1.0' }, null, 2)}\n`,
        'utf8',
      );
      fs.writeFileSync(
        path.join(tempDir, '.claude-plugin', 'marketplace.json'),
        `${JSON.stringify({ name: 'test-repo', metadata: { version: '0.1.0' }, plugins: [] }, null, 2)}\n`,
        'utf8',
      );
      fs.writeFileSync(
        path.join(tempDir, 'entity.toml'),
        'id = "sample"\nversion = "0.1.0"\n',
        'utf8',
      );
      fs.writeFileSync(path.join(tempDir, 'entity.yml'), 'id: sample\nversion: "0.1.0"\n', 'utf8');
      fs.writeFileSync(
        path.join(tempDir, '.version-bump.json'),
        JSON.stringify(
          {
            sourceOfTruth: { file: 'package.json', path: 'version' },
            targets: [
              { file: 'package.json', format: 'json', path: 'version' },
              { file: '.claude-plugin/marketplace.json', format: 'json', path: 'metadata.version' },
              { file: 'entity.toml', format: 'toml', path: 'version' },
              { file: 'entity.yml', format: 'yaml', path: 'version' },
            ],
            syncPluginManifests: false,
            audit: { exclude: ['.version-bump.json'] },
          },
          null,
          2,
        ),
        'utf8',
      );

      assert.deepEqual(checkVersions(tempDir).mismatches, []);

      const bumped = bumpVersions('minor', tempDir);
      assert.equal(bumped.previous, '0.1.0');
      assert.equal(bumped.next, '0.2.0');
      assert.deepEqual(checkVersions(tempDir).mismatches, []);

      // Introduce a stale doc reference and confirm --audit catches it.
      fs.writeFileSync(path.join(tempDir, 'stale.md'), 'Still referencing 0.1.0\n', 'utf8');
      const audit = auditStaleVersions(tempDir, '0.1.0');
      assert.equal(audit.staleHits.length, 1);
      assert.ok(audit.staleHits[0].includes('stale.md'));

      // Introduce drift and confirm --check catches it.
      fs.writeFileSync(
        path.join(tempDir, 'entity.toml'),
        'id = "sample"\nversion = "0.1.0"\n',
        'utf8',
      );
      assert.equal(checkVersions(tempDir).mismatches.length, 1);
    } finally {
      fs.rmSync(tempDir, { recursive: true, force: true });
    }
  });
});
