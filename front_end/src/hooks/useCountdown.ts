import { useState, useEffect } from "react";

export default function useCountdown(initialValue: number, interval = 1000) {
  const [timer, setTimer] = useState<number>(initialValue);

  useEffect(() => {
    const countdown = setInterval(() => {
      setTimer((prevTimer) => (prevTimer > 0 ? prevTimer - 1 : 0));
    }, interval);

    return () => clearInterval(countdown);
  }, [initialValue, interval]);

  const resetTimer = (newValue: number) => {
    setTimer(newValue);
  };

  return [timer, resetTimer];
}
