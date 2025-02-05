import React from "react";
import useCountdown from "../../hooks/useCountdown";

const Countdown: React.FC = () => {
    const [timer] = useCountdown(120);

    const minutes = Math.floor(timer as number / 60);
    const seconds = timer as number % 60;

    return (
        <div
            className={`w-full h-[45px] px-4 inline-flex justify-center items-center gap-2 rounded-large border-none text-white font-semibold bg-green_primary outline-none focus:ring-0 transition-all text-base"
      }`}
        >
            {minutes.toString().padStart(2, "0")}:
            {seconds.toString().padStart(2, "0")}
        </div>
    );
};

export default Countdown;