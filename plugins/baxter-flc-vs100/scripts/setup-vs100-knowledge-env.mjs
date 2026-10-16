#!/usr/bin/env node
/**
 * Copy the non-secret VS100 Knowledge MCP config template on first use.
 */
import { chmodSync, copyFileSync, existsSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = join(scriptDir, "..");
const example = join(pluginRoot, "mcp-servers", "vs100-knowledge-mcp.env.example");
const target = join(homedir(), ".config", "vs100-knowledge-mcp.env");

if (existsSync(target)) {
  console.log(`Already exists: ${target}`);
  process.exit(0);
}

if (!existsSync(example)) {
  console.error(`Example file not found: ${example}`);
  process.exit(1);
}

mkdirSync(dirname(target), { recursive: true });
copyFileSync(example, target);
try {
  chmodSync(target, 0o600);
} catch {
  // Windows may not support chmod; ignore.
}
console.log(`Created ${target}`);