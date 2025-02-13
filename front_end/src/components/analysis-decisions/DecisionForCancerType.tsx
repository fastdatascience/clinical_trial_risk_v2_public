import React from "react";
import { CancerType } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForCancerType: React.FC<{
    cancer_type: CancerType | undefined;
}> = ({ cancer_type }) => {
    if (!cancer_type) return null;

    const heatmapGrid = normalizeDataForHeatmap(cancer_type, 5);

    return (
        <div className="flex flex-col w-full  mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Condition identified: <strong>{cancer_type?.prediction}</strong>{" "}
                {""}
                <span>Score:</span>{" "}
                <strong>{Number(cancer_type?.score).toFixed(1)}%</strong>
            </p>

            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForCancerType;
