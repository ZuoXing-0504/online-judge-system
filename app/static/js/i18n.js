export const DEFAULT_LANGUAGE = "zh-CN";
export const SUPPORTED_LANGUAGES = [
  { code: "zh-CN", label: "简体中文" },
  { code: "en", label: "English" },
  { code: "es", label: "Español" },
  { code: "fr", label: "Français" },
  { code: "de", label: "Deutsch" },
  { code: "ja", label: "日本語" },
  { code: "ko", label: "한국어" },
  { code: "pt-BR", label: "Português" },
  { code: "ru", label: "Русский" },
  { code: "ar", label: "العربية" },
  { code: "hi", label: "हिन्दी" },
];

export const LANGUAGE_ALIASES = {
  zh: "zh-CN", "zh-hans": "zh-CN", en: "en", es: "es", fr: "fr",
  de: "de", ja: "ja", ko: "ko", pt: "pt-BR", ru: "ru", ar: "ar", hi: "hi",
};

export const RTL_LANGUAGES = new Set(["ar"]);

export const DEMO_PROBLEM_TRANSLATIONS = {
  "zh-CN": {
    "sum-two-numbers": {
      title: "两数求和",
      description: "从标准输入读取两个整数 a 和 b，输出它们的和。两个整数都在 64 位有符号整数范围内。",
      input_description: "一行，包含两个以空格分隔的整数 a 和 b。",
      output_description: "输出一个整数 a + b。",
    },
    "word-counter": {
      title: "单词计数",
      description: "读取全部输入文本，统计其中单词的数量。单词定义为由非空白字符组成的最长连续片段。",
      input_description: "一行或多行文本。",
      output_description: "输出单词总数。",
    },
    "distinct-sort": {
      title: "去重排序",
      description: "给定 n 个整数，去除重复值后按升序排序，并在一行中用空格输出。",
      input_description: "第一行包含整数 n。第二行包含 n 个整数。",
      output_description: "按升序输出去重后的整数，数字之间用空格分隔。",
    },
    "balanced-brackets": {
      title: "括号是否平衡",
      description: "给定一个仅由 (), [] 和 {} 组成的字符串，判断括号是否平衡。若平衡输出 YES，否则输出 NO。",
      input_description: "一行括号字符串。",
      output_description: "输出 YES 或 NO。",
    },
    "climbing-stairs-mod": {
      title: "爬楼梯取模",
      description: "你站在第 0 级台阶，要到达第 n 级。每次可以向上走 1 级或 2 级。求不同走法的数量，并对 1000000007 取模。",
      input_description: "一个整数 n。",
      output_description: "输出走法总数对 1000000007 取模后的结果。",
    },
  },
};

import { translations } from "./translations.js";

export function resolveLanguage(value) {
  if (!value) return DEFAULT_LANGUAGE;
  if (value === "zh-CN" || value === "en") return value;
  const normalized = value.toLowerCase();
  if (LANGUAGE_ALIASES[normalized]) return LANGUAGE_ALIASES[normalized];
  const base = normalized.split("-")[0];
  if (LANGUAGE_ALIASES[base]) return LANGUAGE_ALIASES[base];
  return DEFAULT_LANGUAGE;
}

export function detectLanguage() {
  const candidates = Array.isArray(navigator.languages) && navigator.languages.length
    ? navigator.languages : [navigator.language || DEFAULT_LANGUAGE];
  for (const c of candidates) {
    const resolved = resolveLanguage(c);
    if (resolved) return resolved;
  }
  return DEFAULT_LANGUAGE;
}

function lookup(locale, key) {
  return key.split(".").reduce((v, p) => (v && v[p] !== undefined ? v[p] : null), translations[locale]);
}

export function t(key, vars = {}) {
  const current = lookup(resolveLanguage(state.language), key);
  const fallback = lookup("en", key);
  const template = current || fallback || key;
  return template.replace(/\{(\w+)\}/g, (_, token) => (token in vars ? String(vars[token]) : `{${token}}`));
}

import { state } from "./state.js";
