import React from "react";
import { FaChevronDown } from "react-icons/fa";
import { FaCheck } from "react-icons/fa6";

function RunLogs({ runLog }: { runLog: [] | string[] }) {
  const [isOpen, setIsOpen] = React.useState<boolean>(false);
  return (
    <div className="mt-5 flex flex-col">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className={`flex bg-green_secondary cursor-pointer  focus:outline-green_primary  focus:outline-1 hover:bg-green_primary/20  duration-100 px-3 py-1 ${
          isOpen ? "rounded-t-lg" : "rounded-lg"
        }  items-center justify-between text-text_primary font-semibold  w-full`}
      >
        Run Logs.
        <FaChevronDown />
      </button>

      <ul
        className={`${
          isOpen ? "h-60 p-3 border rounded-b-xl " : "h-0"
        } overflow-y-scroll  transition-all duration-100  custom-scrollbar w-full  gap-y-4 text-left flex flex-col-reverse  text-text_primary`}
      >
        {runLog?.map((log, idx) => (
          <li
            key={idx}
            className="flex items-center space-x-3 rtl:space-x-reverse "
          >
            <FaCheck color="#57ca96" />
            <span className="text-sm">{log}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RunLogs;
