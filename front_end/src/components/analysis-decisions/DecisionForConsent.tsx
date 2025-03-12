import React from "react";
import { Consent, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForConsent: React.FC<{ consent: Consent | undefined }> = ({
    consent,
}) => {
    if (!consent) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        consent as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full  mt-3">
            <p className=" text-center text-sm leading-6 font-normal   text-text_secondary">
                Prediction: <strong>{consent.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Consent related terms by page number in
                    document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForConsent;
