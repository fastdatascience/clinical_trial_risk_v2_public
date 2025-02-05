import React from "react";
import { EffectEstimate } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForEffectEstimate: React.FC<{
    estimate: EffectEstimate | undefined;
}> = ({ estimate }) => {
    const heatmapGrid = normalizeDataForHeatmap(estimate!, 20);

    if (!estimate) return null;

    return (
        <div className="flex flex-col justify-center items-center mt-3">
            <p className=" text-start text-sm leading-6 font-normal  text-text_secondary">
                Where was an effect estimate found in the document? The graph
                below shows some candidate effect estimates and a selection of
                key terms by page number, overlaid with page-level probabilities
                (in pink - click the legend to hide). The protocol is{" "}
                {(estimate?.score * 100).toFixed(1)}% likely to contain an
                effect estimate. No terms relating to EFFECT ESTIMATE were found
                in the document.
            </p>

            <Heatmap width={700} height={500} data={heatmapGrid} />
            <div className="flex flex-col  mt-8">
                <h3 className="text-text_secondary text-start font-semibold text-base">
                    Possible mentions of EFFECT ESTIMATE in the document
                </h3>

                <ul className="mt-5">
                    {Object.keys(estimate.context).map((key) => (
                        <li
                            key={key}
                            className="whitespace-pre-wrap text-start list-disc font-poppins break-words text-sm text-text_secondary"
                        >
                            {estimate.context[key]}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default DecisionForEffectEstimate;
