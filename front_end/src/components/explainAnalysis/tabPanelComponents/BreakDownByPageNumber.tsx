import React from "react";
import { SelectInput } from "../../common";
import {
    DecisionForAge,
    DecisionForSAP,
    DecisionForPhase,
    DecisionForBioBank,
    DecisionForCountry,
    DecisionForAdjuvant,
    DecisionForCondition,
    DecisionForSimulation,
    DecisionForSampleSize,
    DecisionForNumberOfArms,
    DecisionForEffectEstimate,
    DecisionForCancerType,
    DecisionForCancerStage,
    DecisionForChemo,
    DecisionForChild,
    DecisionForDrug,
    DecisionForCohortSize,
    DecisionForVaccine,
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

    // TODO: This will grow alot refactor this to make it scalable
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
        adjuvant: (
            <DecisionForAdjuvant
                adjuvant={props?.adjuvant ?? historyRunResult?.result?.adjuvant}
            />
        ),
        age: (
            <DecisionForAge age={props?.age ?? historyRunResult?.result?.age} />
        ),
        biobank: (
            <DecisionForBioBank
                biobank={props?.biobank ?? historyRunResult?.result?.biobank}
            />
        ),
        cancer_stage: (
            <DecisionForCancerStage
                cancer_stage={
                    props?.cancer_stage ??
                    historyRunResult?.result?.cancer_stage
                }
            />
        ),
        cancer_type: (
            <DecisionForCancerType
                cancer_type={
                    props?.cancer_type ?? historyRunResult?.result?.cancer_type
                }
            />
        ),
        chemo: (
            <DecisionForChemo
                chemo={props?.chemo ?? historyRunResult?.result?.chemo}
            />
        ),
        cohort_size: (
            <DecisionForCohortSize
                cohort_size={
                    props?.cohort_size ?? historyRunResult?.result?.cohort_size
                }
            />
        ),
        child: (
            <DecisionForChild
                child={props?.child ?? historyRunResult?.result?.child}
            />
        ),
        drug: (
            <DecisionForDrug
                drug={props?.drug ?? historyRunResult?.result?.drug}
            />
        ),
        vaccine: (
            <DecisionForVaccine
                vaccine={props?.vaccine ?? historyRunResult?.result?.vaccine}
            />
        ),
    };

    const renderComponentBasedOnParam = () => {
        return paramComponentMap[selectedFeature] || null;
    };

    console.log("result===>", historyRunResult?.result);

    return (
        <div className="flex flex-col gap-3 justify-between font-poppins space-y-5 mt-5  items-start flex-wrap">
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
