import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useAtom } from "jotai";
import { CustomRangeSlider, CustomTextField, MultiSelectInput, SelectInput } from "../common";
import type { Metadata, Option, ResultPrediction } from "../../utils/types";
import {
    historyRunResultAtom,
    metaDataAtom,
    processResultAtom,
    selectedParamAtom,
    selectFeatureAtom,
} from "../../lib/atoms";
import {
    capitalizeFirstLetter,
    classNames,
    processMetadataAndResult,
    renderObjectKeysWithValues,
    textFormatter,
} from "../../utils/utils";
import { Disclosure } from "@headlessui/react";
import { FaChevronDown } from "react-icons/fa";


const AnalysisSideBar: React.FC = () => {
    const [metadata] = useAtom(metaDataAtom);
    const [processResult] = useAtom(processResultAtom);
    const [historyRunResult] = useAtom(historyRunResultAtom);
    const [selectedConditionPrediction, setSelectedConditionPrediction] = useState<string | null>(null);
    const defaultFieldGroupId = "default";

    const mergedMetadata = useMemo(() => {
        if (historyRunResult) {
            return processMetadataAndResult(
                metadata,
                historyRunResult.result
            );
        } else {
            return processMetadataAndResult(
                metadata,
                processResult
            );
        }
    }, [historyRunResult, metadata, processResult]);

    // Set state with the initial condition prediction
    useEffect(() => {
        const condition = mergedMetadata.find((metadata) => metadata.id === "condition");
        if (condition?.prediction && typeof condition.prediction === "string") {
            setSelectedConditionPrediction(condition.prediction);
        }
    }, [mergedMetadata]);

    // Divide metadata by required_condition, fields without required_condition are grouped together (default fields)
    const metadataMap = useMemo(() => {
        const map: Map<string, Metadata[]> = new Map();
        
        if (mergedMetadata.length < 1) return map;
        
        mergedMetadata.forEach((data) => {
            if (data.required_condition) {
                if (!map.get(data.required_condition)) map.set(data.required_condition, []);
                map.set(data.required_condition, [...(map.get(data.required_condition) ?? []), data]);

            } else {
                if (!map.get(defaultFieldGroupId)) map.set(defaultFieldGroupId, []);
                map.set(defaultFieldGroupId, [...(map.get(defaultFieldGroupId) ?? []), data]);
            }
        });

        return new Map([...map].sort((a, b) => {
            if (a[0] === defaultFieldGroupId || b[0] === defaultFieldGroupId) return 1;
            return 0;
        }));
    }, [mergedMetadata]);
    
    // Create list with field groups
    const fieldGroups = useMemo(()=> {
        const tmpFieldGroups: React.ReactNode[] = [];
        
        for (const [metaDataGroupId, metadata] of metadataMap) {
            tmpFieldGroups.push(
                <FieldGroup
                    groupId={metaDataGroupId}
                    metadata={metadata}
                    isDefault={metaDataGroupId === defaultFieldGroupId}
                    selectedConditionPrediction={selectedConditionPrediction}
                    setSelectedConditionPrediction={setSelectedConditionPrediction}
                />
            );
        }
        
        return tmpFieldGroups
    }, [metadataMap, selectedConditionPrediction]);
    
    if (fieldGroups.length < 1) return null;

    return (
        <div className="bg-green_secondary w-full lg:flex-[1_0_25%] p-7 rounded-large flex flex-col gap-y-4">
            {fieldGroups.map((fieldGroup, index) => (
                <React.Fragment key={`field-group-${index}`}>
                    <>
                        {/* Field group */}
                        {fieldGroup}
                        
                        {/* Divider */}
                        {index + 1 < fieldGroups.length && <div className="h-[1px] bg-blue-gray-100"></div>}
                    </>
                </React.Fragment>
            ))}
        </div>
    );
};

/**
 * This component is used to display fields grouped together.
 * If isDefault === false, then the group will be displayed in a collapsed section.
 * E.g. the field group that contains fields related to cancer.
 */
const FieldGroup = ({groupId, metadata, isDefault, selectedConditionPrediction, setSelectedConditionPrediction}: {
    groupId: string;
    metadata: Metadata[];
    isDefault: boolean;
    selectedConditionPrediction: string | null;
    setSelectedConditionPrediction: React.Dispatch<React.SetStateAction<string | null>>
}) => {
    const [, setSelectedFeature] = useAtom(selectFeatureAtom);
    const [selectedParam, setSelectedParam] = useAtom(selectedParamAtom);
    const [, setProcessResult] = useAtom(processResultAtom);
    const groupName = capitalizeFirstLetter(groupId);

    /**
     * Handle field change.
     */
    const handleChange = (id: keyof ResultPrediction, value: string) => {
        // Update state with new selected condition prediction
        if (id === "condition") setSelectedConditionPrediction(value)

        setSelectedParam((prev) => ({
            ...prev,
            [id]: value,
        }));
    };

    /**
     * Handle field prediction change.
     */
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

    /**
     * Check if requiredCondition (when not null) matches the current selected condition.
     * If it does not, then the field should be disabled.
     */
    const checkIfFieldShouldBeDisabled = useCallback((requiredCondition: string | null) => {
        let disabled = false;
        
        if (requiredCondition && selectedConditionPrediction) {
            if (requiredCondition.toLowerCase() !== selectedConditionPrediction.toLowerCase()) {
                disabled = true;
            }
        }

        return disabled;
    }, [selectedConditionPrediction]);

    /**
     * Render an input field.
     */
    const renderInput = (
        featureType: string,
        id: string,
        name: string,
        options: Option[],
        prediction: { [key: string]: number } | number | string | undefined,
        selectedParam: string | number | undefined,
        disabled: boolean,
    ) => {
        switch (featureType) {
            case "numeric":
                if (typeof prediction === "object" && prediction !== null) {
                    return (
                        <CustomTextField
                            initialValue={renderObjectKeysWithValues(
                                prediction
                            )}
                            disabled={disabled}
                            readonly={false}
                            type="text"
                            handleChange={(e) => handlePredictionChange(id, e)}
                        />
                    );
                }
                
                return (
                    <CustomTextField
                        initialValue={prediction}
                        readonly={false}
                        disabled={disabled}
                        type={
                            typeof prediction === "number" ? "number" : "text"
                        }
                        handleChange={(e) => handlePredictionChange(id, e)}
                    />
                );
            case "multiple_numeric":
                if (typeof prediction === "object" && prediction !== null) {
                    const fields = [];
                    for (const [key, value] of Object.entries(prediction)) {
                        fields.push(
                            <>
                                <span className="flex justify-between items-center text-sm text-text_secondary">
                                    {name} - {textFormatter(key, {clearUnderscores: true, capitalizeFirstLetter: true})}
                                </span>
                               <CustomTextField
                                   initialValue={value}
                                   disabled={disabled}
                                   readonly={false}
                                   type="number"
                                   handleChange={(e) => handlePredictionChange(id, e)}
                               />
                            </>
                        );
                    }
                    
                    return (
                        <div className="flex mt-2 flex-col gap-y-2">
                            {fields.map((field, index) => (
                                <React.Fragment key={`field-${id}-${index}`}>
                                        {field}
                                </React.Fragment>
                            ))}
                        </div>
                    )
                }
                
                return (
                    <CustomTextField
                        initialValue={prediction}
                        readonly={false}
                        disabled={disabled}
                        type={
                            typeof prediction === "number" ? "number" : "text"
                        }
                        handleChange={(e) => handlePredictionChange(id, e)}
                    />
                );
            case "multi_label":
                return (
                    <MultiSelectInput
                        value={selectedParam ?? (Array.isArray(prediction) ? prediction : []) ?? []}
                        placeholder="Select..."
                        options={options}
                        disabled={disabled}
                        onChange={(value) => handleChange(id, value)}
                    />
                );
            case "text":
                // Display an array of values as one text in text input field
                if (Array.isArray(prediction)) {
                    const value = prediction.length > 0 ? prediction.join(", ") : "";
                    
                    return (
                        <CustomTextField
                            initialValue={value}
                            readonly={false}
                            type={"text"}
                            disabled={disabled}
                            handleChange={(e) => handlePredictionChange(id, e)}
                        />
                    );
                }
                
                // Display string/number in text input field
                else if (typeof prediction === "string" || typeof prediction === "number") {
                    return (
                        <CustomTextField
                            initialValue={prediction}
                            readonly={false}
                            type={"text"}
                            disabled={disabled}
                            handleChange={(e) => handlePredictionChange(id, e)}
                        />
                    );
                }
                
                break;
            case "numeric_range":
                if (typeof prediction === "object" && prediction !== null) {
                    return (
                        <CustomRangeSlider
                            disabled={disabled}
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
                            disabled={disabled}
                            onChange={(value) => handleChange(id, value)}
                        />
                    );
                }
        }
    };

    const fieldsRendered = metadata.length > 0 ? (
        <div>
            {metadata?.map(
                ({id, name, prediction, options, feature_type, required_condition}) => {
                    const disabled = checkIfFieldShouldBeDisabled(required_condition)

                    return <div className="mb-2" key={id}>
                        <div
                            className="flex justify-between items-start text-sm text-text_secondary text-start">
                            <p>{name}</p>
                            <button
                                onClick={() => !disabled && setSelectedFeature(id)}
                                className={classNames(
                                    disabled ? "text-blue-gray-200 !cursor-not-allowed" : "text-blue-400 ",
                                    "text-xs cursor-pointer"
                                )}
                            >
                                explain
                            </button>
                        </div>
                        {renderInput(
                            feature_type,
                            id,
                            name,
                            options,
                            prediction,
                            selectedParam[id],
                            disabled,
                        )}
                    </div>
                })
            }
        </div>
    ) : null;
    
    if (!fieldsRendered) return null;

    // Return the rendered fields
    if (isDefault) {
        return fieldsRendered;
    }
    
    // Non default groups will return the rendered fields in a collapsable section, will be displayed when
    // selectedConditionPrediction is available.
    else {
        if (!selectedConditionPrediction) return null;
        
        // The field group from the selected condition initially should be open by default
        const defaultOpen = selectedConditionPrediction.toLowerCase() === groupId.toLowerCase();
        
        return (
            <Disclosure as="div" defaultOpen={defaultOpen}>
                {({open}) => (
                    <>
                        <Disclosure.Button className="group flex w-full items-center justify-between mb-3">
                            <span className="font-bold">
                                {groupName}
                            </span>
                            <span>
                                 <FaChevronDown aria-hidden="true" className={classNames(
                                     open ? "rotate-180" : ""
                                 )}/>
                            </span>
                        </Disclosure.Button>
                        <Disclosure.Panel className="mt-2 text-sm/5">
                            {fieldsRendered}
                        </Disclosure.Panel>
                    </>
                )}
            </Disclosure>
        );
    }
};

export default AnalysisSideBar;
