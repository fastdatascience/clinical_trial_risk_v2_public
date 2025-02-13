import React from "react";
import { Sap } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForSAP: React.FC<{ sap: Sap | undefined }> = ({ sap }) => {
    if (!sap) return null;
    const heatmapGrid = normalizeDataForHeatmap(sap);

    return (
        <div className="flex flex-col justify-center items-center mt-3">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Which pages contained highly statistical content and were likely
                to be part of the SAP? Graph of a selection of key statistical
                terms by page number.
            </p>

            <div className="flex justify-between  w-full items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key SAP related terms by page number in document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForSAP;
