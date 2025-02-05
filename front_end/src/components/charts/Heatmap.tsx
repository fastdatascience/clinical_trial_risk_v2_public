import React, { useState } from "react";
import { HeatmapProps, InteractionData } from "../../utils/types";
import { Renderer } from "./Renderer";
import { Tooltip } from "./Tooltip";

const Heatmap: React.FC<HeatmapProps> = ({ width, height, data }) => {
    const [hoveredCell, setHoveredCell] = useState<InteractionData | null>(
        null
    );

    return (
        <div className="relative">
            <Renderer
                width={width}
                height={height}
                data={data}
                setHoveredCell={setHoveredCell}
            />
            <Tooltip
                interactionData={hoveredCell}
                width={width}
                height={height}
            />
        </div>
    );
};

export default Heatmap;
