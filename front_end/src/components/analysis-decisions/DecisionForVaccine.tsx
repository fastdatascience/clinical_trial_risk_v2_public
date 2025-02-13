import React from "react";
import { Vaccine } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForVaccine: React.FC<{ vaccine: Vaccine | undefined }> = ({
    vaccine,
}) => {
    if (!vaccine) return null;

    const heatmapGrid = normalizeDataForHeatmap(vaccine);

    return (
        <div className="flex flex-col w-full ">
            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Vaccine related terms by page number in
                    document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForVaccine;
