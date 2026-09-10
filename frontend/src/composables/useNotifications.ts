import { ref } from 'vue';

export interface DueWordItem {
  word: string;
  [key: string]: unknown;
}

export function useNotifications() {
  const isSupported = typeof window !== 'undefined' && 'Notification' in window;
  const permission = ref<NotificationPermission>(isSupported ? Notification.permission : 'denied');

  const requestPermission = async (): Promise<boolean> => {
    if (!isSupported) return false;
    try {
      const result = await Notification.requestPermission();
      permission.value = result;
      return result === 'granted';
    } catch {
      return false;
    }
  };

  const sendNotification = async (title: string, options: NotificationOptions = {}) => {
    if (!isSupported || permission.value !== 'granted') return;

    const defaultOptions: NotificationOptions = {
      icon: '/favicon.svg',
      badge: '/favicon.svg',
      tag: 'vocab-study-reminder',
      ...options,
    };

    if ('serviceWorker' in navigator) {
      try {
        const registration = await navigator.serviceWorker.ready;
        await registration.showNotification(title, defaultOptions);
        return;
      } catch {
        // Fallback to standard window Notification
      }
    }

    new Notification(title, defaultOptions);
  };

  // Smart reminder: Triggers only when words are due and once per day max
  const checkAndNotifyDueWords = async (dueWords: DueWordItem[]) => {
    if (!dueWords || dueWords.length === 0 || permission.value !== 'granted') return;

    const todayStr = new Date().toISOString().slice(0, 10);
    const lastNotified = localStorage.getItem('vocab_last_notification_date');

    if (lastNotified === todayStr) return;

    const count = dueWords.length;
    const sampleWord = dueWords[0].word;

    const title = count === 1
      ? `📚 1 word ready for review!`
      : `📚 ${count} words ready for review!`;

    const body = `Keep your streak sharp. Do you still remember "${sampleWord}"? Take 2 minutes to review.`;

    await sendNotification(title, {
      body,
      data: { url: '/' },
    });

    localStorage.setItem('vocab_last_notification_date', todayStr);
  };

  const sendTestNotification = async () => {
    if (permission.value !== 'granted') {
      const granted = await requestPermission();
      if (!granted) return;
    }

    await sendNotification("🎉 Smart reminders enabled!", {
      body: "We'll gently remind you only when your flashcards are due for review.",
    });
  };

  return {
    isSupported,
    permission,
    requestPermission,
    sendNotification,
    checkAndNotifyDueWords,
    sendTestNotification,
  };
}