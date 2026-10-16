#!/usr/bin/env node
import { chmodSync, copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { homedir, platform } from "node:os";
import { dirname, join } from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const pluginRoot = process.env.CURSOR_PLUGIN_ROOT || process.env.PLUGIN_ROOT || join(scriptDir, "..");
const configPath = join(homedir(), ".config", "vs100-knowledge-mcp.env");
const exampleConfigPath = join(pluginRoot, "mcp-servers", "vs100-knowledge-mcp.env.example");

function ensureConfigFile() {
  if (existsSync(configPath)) {
    return;
  }
  if (!existsSync(exampleConfigPath)) {
    console.error(`VS100 Knowledge MCP config template not found: ${exampleConfigPath}`);
    process.exit(1);
  }

  mkdirSync(dirname(configPath), { recursive: true });
  copyFileSync(exampleConfigPath, configPath);
  try {
    chmodSync(configPath, 0o600);
  } catch {
    // Windows may not support chmod; ignore.
  }
  console.error(`Created ${configPath}`);
}

function loadConfig() {
  if (!existsSync(configPath)) {
    return;
  }

  for (const line of readFileSync(configPath, "utf8").split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (match && !Object.hasOwn(process.env, match[1])) {
      process.env[match[1]] = match[2].replace(/^['"]|['"]$/g, "");
    }
  }
}

ensureConfigFile();
loadConfig();

function rid() {
  if (platform() === "win32") {
    return "win-x64";
  }
  if (platform() === "darwin") {
    return process.arch === "arm64" ? "osx-arm64" : "osx-x64";
  }
  return "linux-x64";
}

function binaryName() {
  return platform() === "win32" ? "vs100-knowledge-mcp.exe" : "vs100-knowledge-mcp";
}

const binary = join(pluginRoot, "bin", rid(), binaryName());

if (!existsSync(binary)) {
  console.error("VS100 Knowledge MCP binary is missing from this plugin build.");
  console.error(`Expected bundled binary: ${binary}`);
  console.error("Maintainers must bundle prebuilt binaries for linux-x64, osx-arm64, osx-x64, and win-x64.");
  process.exit(1);
}

const child = spawn(binary, [], { env: process.env, stdio: "inherit", shell: platform() === "win32" });
child.on("error", (error) => {
  console.error(`VS100 Knowledge MCP failed to start: ${error.message}`);
  process.exit(1);
});
child.on("exit", (code) => process.exit(code === null ? 1 : code));
