import React from "react";
import { Consent, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForDesign: React.FC<{ design: Consent | undefined }> = ({
    design,
}) => {
    if (!design) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        design as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Prediction identified: <strong>{design?.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full  items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Design related terms by page number in
                    document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForDesign;
