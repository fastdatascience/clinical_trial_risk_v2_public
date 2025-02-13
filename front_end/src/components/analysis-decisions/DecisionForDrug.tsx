import React from "react";
import { Drug, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForDrug: React.FC<{ drug: Drug | undefined }> = ({ drug }) => {
    if (!drug) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        drug as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full  mt-3">
            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Drug related terms by page number in document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForDrug;
