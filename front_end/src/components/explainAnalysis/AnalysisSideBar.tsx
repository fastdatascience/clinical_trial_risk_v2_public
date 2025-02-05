import React from "react";
import { useAtom } from "jotai";
import {
    SelectInput,
    CustomTextField,
    MultiSelectInput,
    CustomRangeSlider,
} from "../common";
import type { Option, ResultPrediction } from "../../utils/types";
import {
    historyRunResultAtom,
    metaDataAtom,
    processResultAtom,
    selectedParamAtom,
    selectFeatureAtom,
} from "../../lib/atoms";
import {
    processMetadataAndResult,
    renderObjectKeysWithValues,
} from "../../utils/utils";

const AnalysisSideBar: React.FC = () => {
    const [metadata] = useAtom(metaDataAtom);
    const [, setSelectedFeature] = useAtom(selectFeatureAtom);
    const [processResult, setProcessResult] = useAtom(processResultAtom);
    const [historyRunResult] = useAtom(historyRunResultAtom);
    const [selectedParam, setSelectedParam] = useAtom(selectedParamAtom);

    const getMergedMetadata = () => {
        if (historyRunResult) {
            const mergedMetadata = processMetadataAndResult(
                metadata,
                historyRunResult.result
            );
            return mergedMetadata;
        } else {
            const mergedMetadata = processMetadataAndResult(
                metadata,
                processResult
            );
            return mergedMetadata;
        }
    };

    const mergedMetadata = getMergedMetadata();

    const handleChange = (id: keyof ResultPrediction, value: string) => {
        setSelectedParam((prev) => ({
            ...prev,
            [id]: value,
        }));
    };

    const handlePredictionChange = (
        id: keyof ResultPrediction,
        event: React.FormEvent<HTMLInputElement>
    ) => {
        const element = event?.currentTarget as HTMLInputElement;
        const value = element.value;
        setProcessResult((prevResult) => ({
            ...prevResult,
            [id]: {
                ...((prevResult as Record<string, unknown>)[id] || {}),
                prediction: id === "drug" ? value : Number(value),
            },
        }));
    };

    const renderInput = (
        featureType: string,
        id: string,
        options: Option[],
        prediction: { [key: string]: number } | number | undefined,
        selectedParam: string | number | undefined
    ) => {
        switch (featureType) {
            case "numeric":
                if (typeof prediction === "object" && prediction !== null) {
                    return (
                        <CustomTextField
                            initialValue={renderObjectKeysWithValues(
                                prediction
                            )}
                            readonly={false}
                            type={
                                typeof prediction === "number"
                                    ? "number"
                                    : "text"
                            }
                            handleChange={(e) => handlePredictionChange(id, e)}
                        />
                    );
                }
                return (
                    <CustomTextField
                        initialValue={prediction}
                        readonly={false}
                        type={
                            typeof prediction === "number" ? "number" : "text"
                        }
                        handleChange={(e) => handlePredictionChange(id, e)}
                    />
                );
            case "multi_label":
                if (prediction !== null && Array.isArray(prediction)) {
                    return (
                        <MultiSelectInput
                            value={selectedParam ?? prediction ?? []}
                            placeholder="Select..."
                            options={options}
                            onChange={(value) => handleChange(id, value)}
                        />
                    );
                }
                break;
            case "text":
                if (typeof prediction === "number") {
                    return (
                        <CustomTextField
                            initialValue={prediction}
                            readonly={false}
                            type={"text"}
                            handleChange={(e) => handlePredictionChange(id, e)}
                        />
                    );
                }
                break;
            case "numeric_range":
                if (typeof prediction === "object" && prediction !== null) {
                    return (
                        <CustomRangeSlider
                            min={prediction.lower}
                            max={prediction.upper}
                        />
                    );
                }
                break;
            default:
                if (typeof prediction !== "object") {
                    return (
                        <SelectInput
                            value={selectedParam ?? prediction}
                            placeholder="Select..."
                            options={options}
                            onChange={(value) => handleChange(id, value)}
                        />
                    );
                }
        }
    };
    return (
        mergedMetadata?.length > 0 && (
            <div className="bg-green_secondary lg:w-1/4 w-full p-7 rounded-large">
                <div>
                    {mergedMetadata?.map(
                        ({ id, name, prediction, options, feature_type }) => (
                            <div className="mb-2" key={id}>
                                <div className="flex justify-between items-center text-sm  text-text_secondary text-start">
                                    <p>{name}</p>
                                    <button
                                        onClick={() => setSelectedFeature(id)}
                                        className="text-blue-400 text-xs cursor-pointer"
                                    >
                                        {"explain"}
                                    </button>
                                </div>
                                {renderInput(
                                    feature_type,
                                    id,
                                    options,
                                    prediction,
                                    selectedParam[id]
                                )}
                            </div>
                        )
                    )}
                </div>
            </div>
        )
    );
};

export default AnalysisSideBar;
