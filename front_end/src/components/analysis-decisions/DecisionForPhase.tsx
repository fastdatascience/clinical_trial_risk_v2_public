import React from "react";
import { HeatMapData, Phase } from "../../utils/types";
import { normalizeDataForHeatmap } from "../../utils/utils";
import Heatmap from "../charts/Heatmap";

const DecisionForPhase: React.FC<{ phase: Phase | undefined }> = ({
    phase,
}) => {
    if (!phase) return null;
    const heatmapGrid = normalizeDataForHeatmap(
        phase as unknown as HeatMapData<number[]>
    );
    return (
        <div className="flex flex-col justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Where was the phase mentioned in the document? The graph below
                shows possible phases and which pages they were mentioned on.
                The document is most likely to be{" "}
                <strong> Phase {phase?.prediction}</strong>. No terms relating
                to PHASE were found in the document.
            </p>

            <Heatmap data={heatmapGrid} />
        </div>
    );
};

export default DecisionForPhase;
