import React from "react";
import { CancerStage, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForCancerStage: React.FC<{
    cancer_stage: CancerStage | undefined;
}> = ({ cancer_stage }) => {
    if (!cancer_stage) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        cancer_stage as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Prediction: <strong>{cancer_stage?.prediction}</strong>.
                Confidence:{" "}
            </p>

            <div className="flex justify-center w-full  items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Cancer Stage related terms by page number in
                    document.
                </h3>
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForCancerStage;
