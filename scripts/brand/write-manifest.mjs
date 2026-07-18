import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "../..");
const brandRoot = path.join(root, "assets/brand");

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const absolute = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(absolute) : [absolute];
  });
}

const files = walk(brandRoot)
  .filter((file) => !file.endsWith("manifest.json") && !file.endsWith(".rendered"))
  .sort()
  .map((file) => ({
    path: path.relative(brandRoot, file),
    bytes: fs.statSync(file).size,
    sha256: crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex"),
  }));

fs.writeFileSync(
  path.join(brandRoot, "manifest.json"),
  `${JSON.stringify({ schemaVersion: 1, identity: "vibemaxxing", files }, null, 2)}\n`,
);

console.log(`Wrote manifest for ${files.length} brand files.`);
