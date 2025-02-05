import React from "react";
import { Simulation } from "../../utils/types";
import Heatmap from "../charts/Heatmap";
import { normalizeDataForHeatmap } from "../../utils/utils";

const DecisionForSimulation: React.FC<{
    simulation: Simulation | undefined;
}> = ({ simulation }) => {
    const heatmapGrid = normalizeDataForHeatmap(simulation!, 15);

    if (!simulation) return null;
    return (
        <div className="flex flex-col justify-center items-center mt-3 ">
            <p className=" text-center text-sm leading-6 font-normal  text-text_secondary">
                Which pages mentioned words related to simulation? The graph
                below shows a selection of simulation-related terms by page
                number. The protocol is{" "}
                <strong>{(simulation?.score * 100).toFixed(1)}%</strong> likely
                to involve simulation for sample size.
            </p>

            <div className="flex justify-center w-full items-center  flex-col gap-5 mt-10">
                <h3 className="text-base">
                    Graph of key SIMULATION related terms by page number in
                    document.
                </h3>
                <Heatmap width={700} height={500} data={heatmapGrid} />
            </div>
        </div>
    );
};

export default DecisionForSimulation;
