import React from "react";
import { Age, HeatMapData } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForAge: React.FC<{ age: Age | undefined }> = ({ age }) => {
    if (!age) return null;

    const heatmapGrid = normalizeDataForHeatmap(
        age as unknown as HeatMapData<number[]>
    );

    return (
        <div className="flex flex-col w-full  mt-3">
            <p className=" text-center text-sm leading-6 font-normal   text-text_secondary">
                Minimum Age: <strong>{age.prediction.lower}</strong>. Maximum
                Age: <strong>{age.prediction.upper}</strong>.
            </p>

            <div className="flex justify-center w-full   items-center flex-col gap-5 mt-10">
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForAge;
