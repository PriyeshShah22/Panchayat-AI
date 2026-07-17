import { translateDynamicSocietyText, useLanguageStore } from "../store/language";

export function useLocalizedTexts(texts: string[]) {
  const language = useLanguageStore((state) => state.language);
  return texts.map((text) => translateDynamicSocietyText(text, language));
}

export function LocalizedText({ children }: { children: string }) {
  const language = useLanguageStore((state) => state.language);
  return <>{translateDynamicSocietyText(children, language)}</>;
}
