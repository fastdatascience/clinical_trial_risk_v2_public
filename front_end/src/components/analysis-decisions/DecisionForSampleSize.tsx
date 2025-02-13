import React from "react";
import { SampleSize } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForSampleSize: React.FC<{
    sampleSize: SampleSize | undefined;
}> = ({ sampleSize }) => {
    if (!sampleSize) return null;
    const heatmapGrid = normalizeDataForHeatmap(sampleSize, 5);
    return (
        <div className="flex flex-col justify-center items-center mt-3">
            <p className=" text-start text-sm leading-6 font-normal  text-text_secondary">
                Which pages contained terms relating to the number of subjects?
                The sample size appears to be {sampleSize.prediction} with
                confidence{" "}
                <strong>{(sampleSize?.score * 100).toFixed(1)}%</strong>.
            </p>

            <Heatmap data={heatmapGrid} />

            <ul className="mt-5">
                {Object.keys(sampleSize.context).map((key) => (
                    <li
                        key={key}
                        className="whitespace-pre-wrap text-start font-poppins break-words text-sm text-text_secondary"
                    >
                        {sampleSize.context[key]}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default DecisionForSampleSize;
