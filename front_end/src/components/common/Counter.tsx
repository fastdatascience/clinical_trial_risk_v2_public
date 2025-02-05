import React, { useState } from "react";
import { FaPlus, FaMinus } from "react-icons/fa";

const Counter: React.FC = () => {
    const [count, setCount] = useState(0);

    const increaseCount = () => {
        setCount(prevCount => prevCount + 1);
    };

    const decreaseCount = () => {
        if (count > 1) {
            setCount(prevCount => prevCount - 1);
        }
    };

    return (
        <div className="flex gap-3 items-center">
            <button onClick={increaseCount} className="ml-2 focus:outline-none">
                <FaPlus size={10} />
            </button>

            <p className="bg-white  w-12 py-2 text-center rounded-large text-xs">
                {count}
            </p>
            <button onClick={decreaseCount} className="mr-2 focus:outline-none">
                <FaMinus size={10} />
            </button>
        </div>

    );
};

export default Counter;
