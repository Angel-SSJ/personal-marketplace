import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

function requireShape(data, key) {
  if (
    !data ||
    typeof data !== 'object' ||
    Array.isArray(data) ||
    data.schema_version !== 1 ||
    Object.keys(data).length !== 2 ||
    !Object.hasOwn(data, key) ||
    !Array.isArray(data[key])
  ) {
    throw new Error(`Invalid ${key} registry: expected schema_version and ${key} array only.`);
  }
  const values = data[key];
  if (
    values.some(
      (value) =>
        typeof value !== 'string' ||
        !value.trim() ||
        value !== value.trim() ||
        /\p{Cc}/u.test(value),
    ) ||
    new Set(values).size !== values.length
  ) {
    throw new Error(
      `Invalid ${key} registry: values must be unique nonblank exact strings without control characters.`,
    );
  }
  return values;
}

export function isLowercaseTag(value) {
  return (
    typeof value === 'string' &&
    value.length > 0 &&
    value === value.trim() &&
    !/[\p{Lu}\p{Lt}\p{Cc}]/u.test(value) &&
    /\p{Ll}/u.test(value) &&
    value === value.toLowerCase()
  );
}

export function validateVocabularyData(priorityData, tagData) {
  const priorities = requireShape(priorityData, 'priorities');
  const tags = requireShape(tagData, 'tags');
  if (priorities.length === 0) throw new Error('Priority registry cannot be empty.');
  if (!tags.every(isLowercaseTag))
    throw new Error('Tag registry contains a value that is not lowercase.');
  return { priorities: [...priorities], tags: [...tags] };
}

export async function readVocabulary(
  packageRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..'),
) {
  const [priorityText, tagText] = await Promise.all([
    readFile(resolve(packageRoot, 'assets/priorities.json'), 'utf8'),
    readFile(resolve(packageRoot, 'assets/tags.json'), 'utf8'),
  ]);
  return validateVocabularyData(JSON.parse(priorityText), JSON.parse(tagText));
}

export function priorityStatus(value, vocabulary) {
  if (value === undefined) return 'missing';
  return typeof value === 'string' && vocabulary.priorities.includes(value) ? 'allowed' : 'invalid';
}

export function tagStatus(value, vocabulary) {
  if (!isLowercaseTag(value)) return 'invalid_format';
  return vocabulary.tags.includes(value) ? 'allowed' : 'needs_approval';
}

async function cli() {
  const [mode, candidate, ...extra] = process.argv.slice(2);
  if (
    extra.length ||
    (mode && !['priority', 'tag'].includes(mode)) ||
    (mode && candidate === undefined)
  ) {
    throw new Error('Usage: node scripts/vocabulary.mjs [priority|tag <exact-value>]');
  }
  const data = await readVocabulary();
  if (!mode) {
    process.stdout.write(
      `${JSON.stringify({ valid: true, priorities: data.priorities, tags: data.tags })}\n`,
    );
    return;
  }
  const status = mode === 'priority' ? priorityStatus(candidate, data) : tagStatus(candidate, data);
  process.stdout.write(`${JSON.stringify({ type: mode, value: candidate, status })}\n`);
  if (status !== 'allowed') process.exitCode = 2;
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  cli().catch((error) => {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 1;
  });
}
