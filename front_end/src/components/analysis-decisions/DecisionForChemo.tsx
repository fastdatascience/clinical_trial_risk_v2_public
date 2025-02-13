import React from "react";
import { Chemo, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForChemo: React.FC<{ chemo: Chemo | undefined }> = ({
    chemo,
}) => {
    if (!chemo) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        chemo as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Prediction identified: <strong>{chemo?.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full  items-center flex-col gap-5 mt-10">
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForChemo;
