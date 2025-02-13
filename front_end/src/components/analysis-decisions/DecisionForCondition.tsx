import React from "react";
import { Condition } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForCondition: React.FC<{ condition: Condition | undefined }> = ({
    condition,
}) => {
    if (!condition) return null;

    const heatmapGrid = normalizeDataForHeatmap(condition);

    return (
        <div className="flex flex-col w-full justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Condition identified: <strong>{condition?.prediction}</strong>.
                Confidence:{" "}
                <strong>{(condition?.score * 100).toFixed(1)}%</strong>
                The heat map below shows you key terms related to the condition
                and which pages they occurred on throughout the document.
            </p>

            <div className="flex justify-center w-full  items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key CONDITION related terms by page number in
                    document.
                </h3>
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForCondition;
