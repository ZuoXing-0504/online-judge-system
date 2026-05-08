import assert from "node:assert/strict";

class MockClassList {
  constructor(element) {
    this.element = element;
    this.classes = new Set();
  }

  add(...classes) {
    for (const className of classes) {
      this.classes.add(className);
    }
    this.#sync();
  }

  remove(...classes) {
    for (const className of classes) {
      this.classes.delete(className);
    }
    this.#sync();
  }

  toggle(className, force) {
    if (force === undefined) {
      if (this.classes.has(className)) this.classes.delete(className);
      else this.classes.add(className);
    } else if (force) {
      this.classes.add(className);
    } else {
      this.classes.delete(className);
    }
    this.#sync();
  }

  #sync() {
    this.element.className = Array.from(this.classes).join(" ");
  }
}

class MockElement {
  constructor(id = "", tagName = "DIV") {
    this.id = id;
    this.tagName = tagName.toUpperCase();
    this.value = "";
    this.textContent = "";
    this.className = "";
    this.dataset = {};
    this.children = [];
    this.listeners = new Map();
    this.style = {};
    this.attributes = new Map();
    this.classList = new MockClassList(this);
    this.parentNode = null;
  }

  addEventListener(type, handler) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(handler);
  }

  click() {
    for (const handler of this.listeners.get("click") || []) {
      handler({
        currentTarget: this,
        target: this,
        preventDefault() {},
      });
    }
  }

  appendChild(child) {
    child.parentNode = this;
    this.children.push(child);
    return child;
  }

  replaceChildren(...children) {
    this.children = [];
    for (const child of children) {
      child.parentNode = this;
      this.children.push(child);
    }
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }

  getAttribute(name) {
    return this.attributes.get(name) ?? null;
  }

  focus() {
    this.focused = true;
  }

  querySelector() {
    return null;
  }

  querySelectorAll() {
    return [];
  }
}

const elements = new Map();

function registerElement(id, tagName = "DIV") {
  const element = new MockElement(id, tagName);
  elements.set(id, element);
  return element;
}

const body = new MockElement("body", "BODY");

globalThis.window = globalThis;
globalThis.location = {
  search: "?slug=demo-slug",
  protocol: "http:",
  host: "localhost:8000",
};
globalThis.document = {
  body,
  getElementById(id) {
    return elements.get(id) ?? null;
  },
  createElement(tagName) {
    return new MockElement("", tagName);
  },
  querySelector() {
    return null;
  },
  querySelectorAll() {
    return [];
  },
};
globalThis.fetch = async () => {
  throw new Error("fetch should not be called in frontend runtime smoke test");
};
globalThis.localStorage = {
  getItem() {
    return null;
  },
  setItem() {},
  removeItem() {},
};
Object.defineProperty(globalThis, "navigator", {
  value: { language: "en-US" },
  configurable: true,
});
globalThis.WebSocket = class MockWebSocket {};

const editorWrapper = registerElement("editor-wrapper", "DIV");
const editorTextarea = registerElement("code-editor", "TEXTAREA");
editorTextarea.value = 'print("Ready to judge")';
editorWrapper.appendChild(editorTextarea);

registerElement("manual-problem-slug", "INPUT");
registerElement("load-template", "BUTTON");
registerElement("submit-code", "BUTTON");
registerElement("editor-target", "SPAN");
registerElement("editor-hint", "SPAN");
registerElement("submit-feedback", "P");
registerElement("latest-submission-card", "DIV");

await import("../app/static/editor.js");
await new Promise((resolve) => setTimeout(resolve, 0));

assert.ok(globalThis.CodeEditor, "editor.js should expose window.CodeEditor immediately");
assert.equal(globalThis.CodeEditor._enhanced, false, "editor.js should keep textarea fallback when CDN upgrade fails");
assert.equal(globalThis.CodeEditor.getValue(), 'print("Ready to judge")');

const stateModule = await import("../app/static/js/state.js");
stateModule.state.language = "en";
stateModule.state.user = {
  id: "user-1",
  username: "demo",
  email: "demo@example.com",
  role: "user",
};

const submitModule = await import("../app/static/js/pages/submit.js");
submitModule.initSubmitPage();

const templateButton = document.getElementById("load-template");
templateButton.click();

const slugInput = document.getElementById("manual-problem-slug");
assert.equal(slugInput.value, "demo-slug", "submit page should hydrate slug from location.search");

const editorValue = globalThis.CodeEditor.getValue();
assert.match(editorValue, /def solve\(\) -> None:/);
assert.match(editorValue, /demo-slug/);

console.log("frontend runtime smoke test passed");
