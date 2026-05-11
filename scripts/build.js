const esbuild = require("esbuild");

async function build() {
  // Main app bundle
  await esbuild.build({
    entryPoints: ["app/static/js/app.js"],
    bundle: true,
    outfile: "app/static/js/bundle.js",
    format: "esm",
    minify: true,
    sourcemap: true,
    target: "es2020",
  });
  // Editor (submit page)
  await esbuild.build({
    entryPoints: ["app/static/editor.js"],
    bundle: true,
    outfile: "app/static/js/editor-bundle.js",
    format: "esm",
    minify: true,
    sourcemap: true,
    target: "es2020",
    external: ["https://esm.sh/*"],
  });
  console.log("Bundle complete");
}

build().catch(() => process.exit(1));
