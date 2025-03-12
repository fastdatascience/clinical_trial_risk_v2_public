import React from "react";
import { Biobank, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForControlNegative: React.FC<{
    control_negative: Biobank | undefined;
}> = ({ control_negative }) => {
    if (!control_negative) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        control_negative as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full  mt-3">
            <p className=" text-center text-sm leading-6 font-normal   text-text_secondary">
                Prediction: <strong>{control_negative.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Control Negative related terms by page number
                    in document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForControlNegative;
