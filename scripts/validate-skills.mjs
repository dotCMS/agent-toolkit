#!/usr/bin/env node
// Every directory under skills/ must hold a SKILL.md whose `name` equals the
// directory name, with a non-empty `description`. `npx skills add` SKIPS a skill
// that fails either check — printing a warning and exiting 0 — so without this a
// broken skill ships as a silent no-op.
//
// Also checks that every skill listed in .claude-plugin/marketplace.json exists.

import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import process from 'node:process';

const SKILLS_DIR = 'skills';
const issues = [];

function frontmatter(source) {
  const match = source.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return null;
  const fields = {};
  let key = null;
  for (const line of match[1].split(/\r?\n/)) {
    const start = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (start) {
      key = start[1];
      fields[key] = start[2].trim();
    } else if (key && line.trim()) {
      fields[key] = `${fields[key]} ${line.trim()}`.trim();
    }
  }
  return fields;
}

const entries = await readdir(SKILLS_DIR, { withFileTypes: true });
const dirs = entries.filter((entry) => entry.isDirectory()).map((entry) => entry.name);

if (dirs.length === 0) issues.push(`${SKILLS_DIR}/ contains no skill directories`);

for (const dir of dirs) {
  const path = join(SKILLS_DIR, dir, 'SKILL.md');
  let source;
  try {
    source = await readFile(path, 'utf8');
  } catch {
    issues.push(`${dir}/ has no SKILL.md`);
    continue;
  }

  const fields = frontmatter(source);
  if (!fields) {
    issues.push(`${path} has no YAML frontmatter block`);
    continue;
  }
  if (!fields.name) issues.push(`${path} is missing \`name\``);
  else if (fields.name !== dir) {
    issues.push(`${path} declares name "${fields.name}" but lives in ${dir}/ — they must match`);
  }
  if (!fields.description) issues.push(`${path} is missing \`description\``);
}

const marketplace = JSON.parse(await readFile('.claude-plugin/marketplace.json', 'utf8'));
for (const plugin of marketplace.plugins ?? []) {
  for (const skill of plugin.skills ?? []) {
    const name = skill.replace(/^\.\/skills\//, '');
    if (!dirs.includes(name)) {
      issues.push(`.claude-plugin/marketplace.json lists "${skill}", which does not exist`);
    }
  }
  for (const dir of dirs) {
    if (!(plugin.skills ?? []).includes(`./skills/${dir}`)) {
      issues.push(`skills/${dir} is not listed in .claude-plugin/marketplace.json`);
    }
  }
}

if (issues.length > 0) {
  console.error('Skill validation failed:');
  for (const issue of issues) console.error(`  - ${issue}`);
  process.exit(1);
}

console.log(`${dirs.length} skills are valid: ${dirs.join(', ')}`);
