import React from "react";
import { Adjuvant, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForAdjuvant: React.FC<{ adjuvant: Adjuvant | undefined }> = ({
    adjuvant,
}) => {
    if (!adjuvant) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        adjuvant as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Prediction identified: <strong>{adjuvant?.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full  items-center flex-col gap-5 mt-10">
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForAdjuvant;
