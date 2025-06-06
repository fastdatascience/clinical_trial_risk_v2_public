import React from "react";
import { Biobank, HeatMapData } from "../../utils/types";
import { normalizeDataForHeatmap } from "../../utils/utils";
import Heatmap from "../charts/Heatmap";

const DecisionForCohortSize: React.FC<{
    cohort_size: Biobank | undefined;
}> = ({ cohort_size }) => {
    if (!cohort_size) return null;
    const heatmapGrid = normalizeDataForHeatmap(
        cohort_size as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex font-poppins flex-col    mt-3  space-y-5">
            <p className=" text-sm leading-6 text-start font-normal   text-text_secondary">
                Prediction: <strong>{cohort_size.prediction}</strong>.
            </p>

            <div className="flex flex-col w-full  gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Cohort Size related terms by page number in
                    document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForCohortSize;
