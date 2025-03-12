import React from "react";
import { DocumentType, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForDocumentType: React.FC<{
    document_type: DocumentType | undefined;
}> = ({ document_type }) => {
    if (!document_type) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        document_type as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full  mt-3">
            <p className=" text-center text-sm leading-6 font-normal   text-text_secondary">
                Prediction: <strong>{document_type.prediction}</strong>.
            </p>

            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key Biobank related terms by page number in
                    document.
                </h3>

                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForDocumentType;
