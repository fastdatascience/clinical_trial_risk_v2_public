import React from "react";
import { Child, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForChild: React.FC<{ child: Child | undefined }> = ({
    child,
}) => {
    if (!child) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        child as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Prediction identified: <strong>{child?.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full  items-center flex-col gap-5 mt-10">
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForChild;
