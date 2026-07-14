import { useLayoutEffect } from "react";
import { translateSocietyText, useLanguageStore, words } from "../store/language";

const originals = new WeakMap<Node, string>();
const translatedValues = new Set(
  Object.values(words).flatMap((entry) => [entry.hi, entry.mr]),
);
const reverse = new Map<string, string>(
  Object.entries(words).flatMap(([english, entry]) => [
    [entry.hi, english],
    [entry.mr, english],
  ]),
);

function translateText(original: string, language: "en" | "hi" | "mr") {
  if (language === "en") return original;
  const exact = words[original]?.[language];
  if (exact) return exact;
  let result = original;
  for (const month of [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ])
    result = result.replaceAll(month, words[month][language]);
  const monthly = result.match(/^(\d+) monthly bills · (\d+) paid$/);
  if (monthly)
    return language === "hi"
      ? `${monthly[1]} मासिक बिल · ${monthly[2]} भुगतान किए`
      : `${monthly[1]} मासिक देयके · ${monthly[2]} भरलेली`;
  const due = result.match(/^(\d+) due$/);
  if (due) return language === "hi" ? `${due[1]} बकाया` : `${due[1]} थकीत`;
  const notices = result.match(
    /^(\d+) active notices are available\. Important updates are always shown above so they are hard to miss\.$/,
  );
  if (notices)
    return language === "hi"
      ? `${notices[1]} सक्रिय सूचनाएं उपलब्ध हैं। महत्वपूर्ण सूचना हमेशा ऊपर दिखाई जाती है।`
      : `${notices[1]} सक्रिय सूचना उपलब्ध आहेत. महत्त्वाची सूचना नेहमी वर दिसते.`;
  return translateSocietyText(result, language);
}

function applyTranslations(language: "en" | "hi" | "mr") {
  const root = document.body;
  if (!root) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let node: Node | null;
  while ((node = walker.nextNode())) {
    const current = node.textContent ?? "";
    const trimmed = current.trim();
    if (!trimmed) continue;
    if (language === "en" && reverse.has(trimmed)) {
      const english = reverse.get(trimmed)!;
      originals.set(node, english);
      node.textContent = current.replace(trimmed, english);
      continue;
    }
    if (!originals.has(node)) {
      originals.set(node, reverse.get(trimmed) ?? trimmed);
    } else {
      const stored = originals.get(node) ?? trimmed;
      const expected = translateText(stored, language);
      const looksLocalized = /[\u0900-\u097f]/.test(trimmed);
      if (
        trimmed !== expected &&
        !translatedValues.has(trimmed) &&
        !looksLocalized
      )
        originals.set(node, reverse.get(trimmed) ?? trimmed);
    }
    const original = originals.get(node) ?? reverse.get(trimmed) ?? trimmed;
    const replacement = translateText(original, language);
    if (trimmed !== replacement)
      node.textContent = current.replace(trimmed, replacement);
  }
  root
    .querySelectorAll<HTMLInputElement>(
      "input[placeholder], textarea[placeholder]",
    )
    .forEach((element) => {
      const stored = element.dataset.originalPlaceholder;
      const original =
        reverse.get(element.placeholder) ??
        (stored && element.placeholder === translateText(stored, language)
          ? stored
          : element.placeholder);
      element.dataset.originalPlaceholder = original;
      const translated = translateText(original, language);
      if (element.placeholder !== translated) element.placeholder = translated;
    });
  root
    .querySelectorAll<HTMLElement>("[aria-label], [title]")
    .forEach((element) => {
      if (element.hasAttribute("aria-label")) {
        const current = element.getAttribute("aria-label") ?? "";
        const stored = element.dataset.originalAriaLabel;
        const original =
          stored && current === translateText(stored, language)
            ? stored
            : current;
        element.dataset.originalAriaLabel = original;
        const translated = translateText(original, language);
        if (current !== translated)
          element.setAttribute("aria-label", translated);
      }
      if (element.hasAttribute("title")) {
        const current = element.getAttribute("title") ?? "";
        const stored = element.dataset.originalTitle;
        const original =
          stored && current === translateText(stored, language)
            ? stored
            : current;
        element.dataset.originalTitle = original;
        const translated = translateText(original, language);
        if (current !== translated) element.setAttribute("title", translated);
      }
    });
  document.documentElement.lang = language === "en" ? "en" : `${language}-IN`;
}

export function SiteTranslator() {
  const language = useLanguageStore((state) => state.language);
  useLayoutEffect(() => {
    applyTranslations(language);
    const root = document.body;
    const observer = new MutationObserver(() => applyTranslations(language));
    if (root)
      observer.observe(root, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ["aria-label", "title", "placeholder"],
      });
    return () => observer.disconnect();
  }, [language]);
  return null;
}
