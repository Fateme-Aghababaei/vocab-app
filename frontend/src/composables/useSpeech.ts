import { ref } from 'vue';

export function useSpeech() {
  const isSpeaking = ref(false);

  const speak = (text: string, lang = 'en-US') => {
    if (!('speechSynthesis' in window)) {
      console.warn('مرورگر شما از Web Speech API پشتیبانی نمی‌کند.');
      return;
    }

    // متوقف کردن صدای قبلی برای تداخل نداشتن صداها
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.9; // سرعت ملایم و شمرده برای یادگیری دقیق لهجه

    utterance.onstart = () => {
      isSpeaking.value = true;
    };

    utterance.onend = () => {
      isSpeaking.value = false;
    };

    utterance.onerror = () => {
      isSpeaking.value = false;
    };

    window.speechSynthesis.speak(utterance);
  };

  const stop = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      isSpeaking.value = false;
    }
  };

  return {
    speak,
    stop,
    isSpeaking,
  };
}