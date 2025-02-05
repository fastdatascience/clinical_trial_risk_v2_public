import React from "react";
import { SelectInput } from "../../common";
import {
    DecisionForCondition,
    DecisionForCountry,
    DecisionForEffectEstimate,
    DecisionForNumberOfArms,
    DecisionForPhase,
    DecisionForSampleSize,
    DecisionForSAP,
    DecisionForSimulation,
} from "../../analysis-decisions";
import { Result } from "../../../utils/types";
import { generateOptions } from "../../../utils/utils";
import { useAtom } from "jotai";
import { historyRunResultAtom, selectFeatureAtom } from "../../../lib/atoms";

const BreakDownByPageNumber: React.FC<Result> = (props) => {
    const [historyRunResult] = useAtom(historyRunResultAtom);
    const [selectedFeature, setSelectedFeature] = useAtom(selectFeatureAtom);

    const features = Object.keys(historyRunResult?.result ?? props ?? {});

    const options = generateOptions(features);

    const handleSelectChange = (value: string) => {
        setSelectedFeature(value);
    };

    const paramComponentMap: { [key: string]: React.ReactNode } = {
        condition: (
            <DecisionForCondition
                condition={
                    props?.condition ?? historyRunResult?.result?.condition
                }
            />
        ),
        country: (
            <DecisionForCountry
                country={props?.country ?? historyRunResult?.result?.country}
            />
        ),
        sap: (
            <DecisionForSAP sap={props?.sap ?? historyRunResult?.result?.sap} />
        ),
        phase: (
            <DecisionForPhase
                phase={props?.phase ?? historyRunResult?.result?.phase}
            />
        ),
        effect_estimate: (
            <DecisionForEffectEstimate
                estimate={
                    props?.effect_estimate ??
                    historyRunResult?.result?.effect_estimate
                }
            />
        ),
        simulation: (
            <DecisionForSimulation
                simulation={
                    props?.simulation ?? historyRunResult?.result?.simulation
                }
            />
        ),
        sample_size: (
            <DecisionForSampleSize
                sampleSize={
                    props?.sample_size ?? historyRunResult?.result?.sample_size
                }
            />
        ),
        num_arms: (
            <DecisionForNumberOfArms
                num_arms={props?.num_arms ?? historyRunResult?.result?.num_arms}
            />
        ),
    };

    const renderComponentBasedOnParam = () => {
        return paramComponentMap[selectedFeature] || null;
    };

    return (
        <div className="flex flex-col gap-3 justify-between  items-start flex-wrap">
            <p className="text-sm text-text_secondary">
                Display explanation of AI decision for:
            </p>

            <SelectInput
                placeholder="Select..."
                options={options}
                value={selectedFeature}
                onChange={(value) => handleSelectChange(value)}
            />
            {renderComponentBasedOnParam()}
        </div>
    );
};

export default BreakDownByPageNumber;
