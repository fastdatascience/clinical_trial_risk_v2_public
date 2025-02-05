import "./CircularProgress.css";
import { CircularProgressProps } from "./ProgressProps";
import React, { useEffect, useRef, useState } from "react";

const CircularProgress: React.FC<CircularProgressProps> = ({
    size,
    progress,
    trackWidth,
    trackColor,
    indicatorWidth,
    indicatorColor,
}) => {
    const [offset, setOffset] = useState(0);
    const circleRef = useRef<SVGCircleElement>(null);

    const center = size / 2,
        radius =
            center -
            (trackWidth > indicatorWidth ? trackWidth : indicatorWidth),
        dashArray = 2 * Math.PI * radius,
        dashOffset = dashArray * ((100 - progress) / 100);

    useEffect(() => {
        const progressOffset = dashArray * ((100 - progress) / 100);
        setOffset(progressOffset);
        if (circleRef.current !== null) {
            circleRef.current.setAttribute(
                "style",
                "transition: stroke-dashoffset 850ms ease-in-out"
            );
        }
    }, [setOffset, progress, dashArray, offset]);

    return (
        <>
            <div
                className="svg-pi-wrapper"
                style={{ width: size, height: size }}
            >
                <svg className="svg-pi" style={{ width: size, height: size }}>
                    <circle
                        className="svg-pi-track"
                        cx={center}
                        cy={center}
                        fill="transparent"
                        r={radius}
                        stroke={trackColor}
                        strokeWidth={trackWidth}
                    />
                    <circle
                        className={"svg-pi-indicator"}
                        cx={center}
                        cy={center}
                        fill="transparent"
                        ref={circleRef}
                        r={radius}
                        stroke={indicatorColor}
                        strokeWidth={indicatorWidth}
                        strokeDasharray={dashArray}
                        strokeDashoffset={dashOffset}
                        strokeLinecap={"round"}
                    />
                </svg>

                <svg
                    className="svg-pi-label"
                    style={{
                        width: "100%",
                        height: "90%",
                        alignItems: "center",
                    }}
                >
                    <text
                        x={`${center}`}
                        y={`${center}`}
                        className="svg-circle-text"
                    >
                        {progress}%
                    </text>
                </svg>
            </div>
        </>
    );
};

export default CircularProgress;
