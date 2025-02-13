import React from "react";
import { NumArms } from "../../utils/types";
import { normalizeDataForHeatmap } from "../../utils/utils";
import Heatmap from "../charts/Heatmap";

const DecisionForNumberOfArms: React.FC<{ num_arms: NumArms | undefined }> = ({
    num_arms,
}) => {
    if (!num_arms) return null;
    const heatmapGrid = normalizeDataForHeatmap(num_arms, 15);

    return (
        <div className="flex flex-col justify-center items-center mt-3 mb-3  w-full">
            <p className=" text-start text-sm leading-6 font-normal  text-text_secondary">
                Which pages contained terms relating to the number of arms? The
                trial appears to have <strong>{num_arms.prediction}</strong>{" "}
                arm(s).
            </p>

            <div className="flex w-full justify-center items-center">
                <Heatmap data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForNumberOfArms;
