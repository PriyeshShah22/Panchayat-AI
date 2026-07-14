let activeUtterance: SpeechSynthesisUtterance | null = null;
let requestNumber = 0;

interface SpeechCallbacks {
  onEnd?: () => void;
  onError?: (message: string) => void;
}

function availableVoices(): Promise<SpeechSynthesisVoice[]> {
  const immediate = window.speechSynthesis.getVoices();
  if (immediate.length) return Promise.resolve(immediate);
  return new Promise((resolve) => {
    const timer = window.setTimeout(
      () => resolve(window.speechSynthesis.getVoices()),
      800,
    );
    window.speechSynthesis.addEventListener(
      "voiceschanged",
      () => {
        window.clearTimeout(timer);
        resolve(window.speechSynthesis.getVoices());
      },
      { once: true },
    );
  });
}

export function stopLocalizedSpeech() {
  requestNumber += 1;
  window.speechSynthesis?.cancel();
  activeUtterance = null;
}

export async function playLocalizedSpeech(
  text: string,
  language: "en" | "hi" | "mr",
  callbacks: SpeechCallbacks = {},
) {
  stopLocalizedSpeech();
  const currentRequest = requestNumber;
  const languageCode = `${language}-IN`;
  if (!("speechSynthesis" in window))
    throw new Error("Read aloud is unavailable in this browser.");

  const voices = await availableVoices();
  if (currentRequest !== requestNumber) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = languageCode;
  const exactVoice = voices.find((voice) =>
    voice.lang.toLowerCase().startsWith(language),
  );
  const devanagariFallback =
    language === "mr"
      ? voices.find((voice) => voice.lang.toLowerCase().startsWith("hi"))
      : undefined;
  const voice = exactVoice || devanagariFallback;
  if (voice) {
    utterance.voice = voice;
    // A Hindi fallback remains understandable for Marathi Devanagari text.
    utterance.lang = voice.lang;
  }
  utterance.onend = () => {
    if (currentRequest !== requestNumber) return;
    if (activeUtterance === utterance) activeUtterance = null;
    callbacks.onEnd?.();
  };
  utterance.onerror = () => {
    // speechSynthesis reports an intentional cancel/interrupt as an error.
    // Stop and new-recording actions increment the request number, so ignore
    // that stale event while preserving genuine playback failures.
    if (currentRequest !== requestNumber) return;
    if (activeUtterance === utterance) activeUtterance = null;
    callbacks.onError?.(
      language === "mr"
        ? "Marathi read-aloud needs a Marathi or Hindi voice installed on this device."
        : "Read-aloud failed. Please tap the speaker and try again.",
    );
  };
  activeUtterance = utterance;
  speechSynthesis.speak(utterance);
}
