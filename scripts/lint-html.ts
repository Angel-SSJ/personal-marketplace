import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { HtmlValidate } from 'html-validate';

const IGNORED_DIRS = new Set([
  '.git',
  'node_modules',
  'dist',
  'coverage',
  '.scratch',
  'tmp',
  'temp',
]);

function findHtmlFiles(dir: string): string[] {
  if (!fs.existsSync(dir)) {
    return [];
  }
  const files: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (IGNORED_DIRS.has(entry.name)) {
      continue;
    }
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...findHtmlFiles(fullPath));
    } else if (entry.isFile() && entry.name.endsWith('.html')) {
      files.push(fullPath);
    }
  }
  return files;
}

export async function lintHtmlFiles(rootDir: string = process.cwd()): Promise<{
  checked: number;
  errors: string[];
}> {
  const htmlFiles = findHtmlFiles(rootDir);
  if (htmlFiles.length === 0) {
    return { checked: 0, errors: [] };
  }

  const configPath = path.join(rootDir, '.htmlvalidate.json');
  const config = fs.existsSync(configPath)
    ? JSON.parse(fs.readFileSync(configPath, 'utf8'))
    : { extends: ['html-validate:recommended'] };

  const validator = new HtmlValidate(config);
  const errors: string[] = [];

  for (const file of htmlFiles) {
    const report = await validator.validateFile(file);
    if (!report.valid) {
      const relative = path.relative(rootDir, file).replaceAll('\\', '/');
      for (const result of report.results) {
        for (const msg of result.messages) {
          errors.push(`${relative}:${msg.line}:${msg.column} [${msg.ruleId}] ${msg.message}`);
        }
      }
    }
  }

  return { checked: htmlFiles.length, errors };
}

function isMainModule(): boolean {
  const entry = process.argv[1];
  return Boolean(entry && import.meta.url === pathToFileURL(path.resolve(entry)).href);
}

if (isMainModule()) {
  const { checked, errors } = await lintHtmlFiles(process.cwd());
  if (checked === 0) {
    console.log('HTML lint skipped (no .html files found yet).');
    process.exit(0);
  }
  if (errors.length > 0) {
    for (const error of errors) {
      console.error(`ERROR: ${error}`);
    }
    console.error(
      `\nHTML validation failed (${errors.length} issue(s) across ${checked} file(s)).`,
    );
    process.exit(1);
  }
  console.log(`HTML validation passed (${checked} file(s) checked).`);
}
