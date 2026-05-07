const ta = document.getElementById("code-editor");
console.log("[editor] #code-editor found:", !!ta, "tag:", ta?.tagName);

if (!ta || ta.tagName !== "TEXTAREA") throw new Error("Missing #code-editor textarea");

window.CodeEditor = {
  getValue() { console.log("[editor] getValue =>", ta.value.slice(0, 40)); return ta.value; },
  setValue(v) { console.log("[editor] setValue len:", v.length, "preview:", v.slice(0, 60)); ta.value = v; },
  focus() { ta.focus(); },
  _enhanced: false,
};
console.log("[editor] window.CodeEditor set (textarea fallback)");

// Try CodeMirror upgrade in the background.
(async function upgrade() {
  try {
    console.log("[editor] fetching CodeMirror from CDN...");
    const base = "https://esm.sh";
    const [viewMod, langPy, cmdMod, cmMod] = await Promise.all([
      import(`${base}/@codemirror/view@6`),
      import(`${base}/@codemirror/lang-python@6`),
      import(`${base}/@codemirror/commands@6`),
      import(`${base}/codemirror@6`),
    ]);
    const { EditorView, keymap } = viewMod;
    const { python } = langPy;
    const { indentWithTab } = cmdMod;
    const historyKeymap = cmdMod.historyKeymap || cmdMod.defaultKeymap?.filter(k => k?.key?.startsWith("Mod-")) || [];
    const { basicSetup } = cmMod;
    console.log("[editor] CodeMirror loaded, upgrading...");

    const parent = ta.parentNode;

    const view = new EditorView({
      doc: ta.value,
      extensions: [
        basicSetup,
        python(),
        keymap.of([indentWithTab, ...(Array.isArray(historyKeymap) ? historyKeymap : [])]),
        EditorView.theme({
          ".cm-scroller": {
            fontFamily: '"Cascadia Code","Consolas","Lucida Console",monospace',
            fontSize: "0.95rem", lineHeight: "1.7",
          },
          ".cm-content": { padding: "16px" },
          ".cm-gutters": {
            borderRight: "1px solid var(--border)",
            background: "var(--bg-alt)", color: "var(--muted)",
          },
        }),
      ],
      parent: parent,
    });

    // Only hide textarea AFTER EditorView is successfully created.
    ta.style.display = "none";

    window.CodeEditor = {
      getValue() { return view.state.doc.toString(); },
      setValue(v) { view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: v } }); },
      focus() { view.focus(); },
      _enhanced: true,
    };
    console.log("[editor] CodeMirror upgrade complete");
    parent.classList.add("cm-ready");
  } catch (e) {
    console.log("[editor] CDN upgrade failed, textarea stays:", e.message || e);
    ta.style.display = ""; // ensure visible
  }
})();
