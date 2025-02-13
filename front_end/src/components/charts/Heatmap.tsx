import React, { useState } from "react";
import { HeatmapProps, InteractionData } from "../../utils/types";
import { Renderer } from "./Renderer";
import { Tooltip } from "./Tooltip";
import useDimension from "../../hooks/useDimension";

const Heatmap: React.FC<HeatmapProps> = ({ data }) => {
    const { ref, dimensions } = useDimension<HTMLDivElement>();
    const [hoveredCell, setHoveredCell] = useState<InteractionData | null>(
        null
    );

    return (
        <div
            className="relative w-full  h-[60vh] min-h-[300px] border  rounded-lg shadow-md"
            ref={ref}
        >
            <Renderer
                width={dimensions.width}
                height={dimensions.height}
                data={data}
                setHoveredCell={setHoveredCell}
            />
            <Tooltip
                interactionData={hoveredCell}
                width={dimensions.width}
                height={dimensions.height}
            />
        </div>
    );
};

export default Heatmap;
