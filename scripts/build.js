import esbuild from "esbuild";

async function build() {
  // App bundle with code splitting (uses entryNames to avoid overwriting source)
  await esbuild.build({
    entryPoints: ["app/static/js/app.js"],
    bundle: true,
    splitting: true,
    outdir: "app/static/js",
    format: "esm",
    minify: true,
    sourcemap: true,
    target: "es2020",
    entryNames: "bundle",
    chunkNames: "chunks/[name]-[hash]",
  });

  // Editor bundle with local CodeMirror
  await esbuild.build({
    entryPoints: ["app/static/editor.js"],
    bundle: true,
    outfile: "app/static/js/editor-bundle.js",
    format: "esm",
    minify: true,
    sourcemap: true,
    target: "es2020",
  });

  // CSS minify
  await esbuild.build({
    entryPoints: ["app/static/styles.css"],
    bundle: true,
    minify: true,
    outfile: "app/static/styles.min.css",
  });

  console.log("Build complete");
}

build().catch(() => process.exit(1));
