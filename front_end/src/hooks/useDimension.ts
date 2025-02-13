import { useState, useEffect, useRef } from "react";

const useDimension = <T extends HTMLElement>() => {
    const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
    const ref = useRef<T>(null);

    useEffect(() => {
        const updateDimensions = () => {
            if (ref.current) {
                const { width, height } = ref.current.getBoundingClientRect();
                setDimensions({ width, height });
            }
        };

        // Initial dimensions update
        updateDimensions();

        // Update dimensions on window resize
        window.addEventListener("resize", updateDimensions);

        // Cleanup event listener on component unmount
        return () => window.removeEventListener("resize", updateDimensions);
    }, []);

    return { ref, dimensions };
};

export default useDimension;
