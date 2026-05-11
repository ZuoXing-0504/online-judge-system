const ta = document.getElementById("code-editor");
console.log("[editor] #code-editor found:", !!ta, "tag:", ta?.tagName);

if (!ta || ta.tagName !== "TEXTAREA") throw new Error("Missing #code-editor textarea");

// Chinese punctuation to English mapping for code editor
const PUNCT_MAP = {
  ",": ",", "，": ",", ".": ".", "。": ".", ";": ";", "；": ";",
  ":": ":", "：": ":", "!": "!", "！": "!", "?": "?", "？": "?",
  "(": "(", "（": "(", ")": ")", "）": ")",
  "[": "[", "【": "[", "]": "]", "】": "]",
  "{": "{", "｛": "{", "}": "}", "｝": "}",
  "'": "'", "'": "'", "'": "'", "\"": "\"", "\"": "\"", "\"": "\"",
  "<": "<", "《": "<", ">": ">", "》": ">",
  "=": "=", "＝": "=", "+": "+", "＋": "+", "-": "-", "－": "-",
  "*": "*", "＊": "*", "/": "/", "／": "/", "%": "%", "％": "%",
  " ": " ", " ": " ",
};
const PUNCT_RE = new RegExp("[" + Object.keys(PUNCT_MAP).join("") + "]", "g");

function normalizePunctuation(text) {
  return text.replace(PUNCT_RE, (ch) => PUNCT_MAP[ch] || ch);
}

ta.addEventListener("input", () => {
  const before = ta.value;
  const after = normalizePunctuation(before);
  if (after !== before) {
    const cursor = ta.selectionStart;
    ta.value = after;
    ta.selectionStart = ta.selectionEnd = cursor;
  }
});

window.CodeEditor = {
  getValue() { return normalizePunctuation(ta.value); },
  setValue(v) { ta.value = v; },
  focus() { ta.focus(); },
  _enhanced: false,
};
console.log("[editor] window.CodeEditor set (textarea fallback)");

(async function upgrade() {
  try {
    console.log("[editor] loading CodeMirror...");
    const [viewMod, langPy, langCpp, langJava, cmdMod, cmMod, stateMod] = await Promise.all([
      import("codemirror"),
      import("@codemirror/lang-python"),
      import("@codemirror/lang-cpp"),
      import("@codemirror/lang-java"),
      import("@codemirror/commands"),
      import("@codemirror/view"),
      import("@codemirror/state"),
    ]);
    const { EditorView, keymap } = viewMod;
    const { python } = langPy;
    const { cpp } = langCpp;
    const { java } = langJava;
    const { indentWithTab } = cmdMod;
    const historyKeymap = cmdMod.historyKeymap || [];
    const { basicSetup } = cmMod;
    const { Compartment } = stateMod;

    const langExtensions = { python: python(), cpp: cpp(), java: java() };
    const langCompartment = new Compartment();

    const parent = ta.parentNode;

    const view = new EditorView({
      doc: ta.value,
      extensions: [
        basicSetup,
        langCompartment.of(python()),
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

    ta.style.display = "none";

    window.CodeEditor = {
      getValue() { return normalizePunctuation(view.state.doc.toString()); },
      setValue(v) { view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: v } }); },
      focus() { view.focus(); },
      _enhanced: true,
      setLanguage(lang) {
        const ext = langExtensions[lang];
        if (ext) {
          view.dispatch({ effects: langCompartment.reconfigure(ext) });
          console.log("[editor] language switched to:", lang);
        }
      },
    };
    console.log("[editor] CodeMirror upgrade complete (Python/C++/Java)");
    parent.classList.add("cm-ready");
  } catch (e) {
    console.log("[editor] CDN upgrade failed, textarea stays:", e.message || e);
    ta.style.display = "";
  }
})();

if (typeof document !== "undefined" && document.addEventListener) {
document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("language-select-submit");
  if (sel) {
    sel.addEventListener("change", () => {
      if (window.CodeEditor && window.CodeEditor._enhanced) {
        window.CodeEditor.setLanguage(sel.value);
      }
    });
  }
});
}
