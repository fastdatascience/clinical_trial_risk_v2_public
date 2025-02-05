// TODO: Refactor this component (remove redundancy, make it smaller)
import {
    Typography,
    Button,
    CardBody,
    CardFooter,
    Spinner,
    IconButton,
    Tooltip,
    Input,
} from "@material-tailwind/react";

import { Content, SetAtom, Weights } from "../../utils/types";
import { SetStateAction, useState } from "react";
import WeightProfileDeleteModal from "../modals/WeightProfileDeleteModal";
import { FaCheck } from "react-icons/fa6";
import {
    createUserWeightProfiles,
    updateUserWeightProfile,
} from "../../utils/services";

type WeightType = keyof Weights;

export function WeightConfigureTable({
    isLoading,
    isFiltered,
    columns,
    data,
    setWeightProfiles,
    setFilteredWeightProfiles,
    onDelete,
    weightKey,
}: Readonly<{
    isLoading: boolean;
    isFiltered: boolean;
    columns: string[];
    data: Content[] | undefined;
    setWeightProfiles: SetAtom<[SetStateAction<Content[] | undefined>], void>;
    setFilteredWeightProfiles: React.Dispatch<
        React.SetStateAction<Content[] | undefined>
    >;
    onDelete: () => Promise<void>;
    weightKey: WeightType;
}>) {
    const [showModal, setShowModal] = useState<boolean>(false);
    const [isUpdating, setIsUpdating] = useState<Record<string, boolean>>({});

    // TODO: add condition here
    const handleUpdateWeightProfile = async (
        name: string,
        feature: string,
        weights: Weights
    ) => {
        const { cost_risk_models, risk_thresholds, sample_size_tertiles } =
            weights;

        const updatedCostRiskModels = {
            ...cost_risk_models,
            [feature]: {
                ...cost_risk_models[feature],
                cost: cost_risk_models[feature]?.cost,
                risk: cost_risk_models[feature]?.risk,
            },
        };

        const updated_profile = {
            name,
            weights: {
                cost_risk_models: updatedCostRiskModels,
                risk_thresholds,
                sample_size_tertiles,
            },
        };

        try {
            setIsUpdating((prev) => ({ ...prev, [feature]: true }));
            await updateUserWeightProfile(data?.[0]?.id, updated_profile);
        } catch (error) {
            console.error("Failed to update weight profile", error);
        } finally {
            setIsUpdating((prev) => ({
                ...prev,
                [feature]: false,
            }));
        }
    };

    // handle change for all 3 weight profile types
    const handleCRMWeightChange = (
        profileIndex: number,
        feature: string,
        weightType: "cost" | "risk" | "name",
        value: number | string
    ) => {
        if (isFiltered) {
            setFilteredWeightProfiles((prevProfiles) => {
                if (!prevProfiles?.length) return prevProfiles;
                const updatedProfiles = [...prevProfiles];
                const profile = updatedProfiles[profileIndex];

                if (weightType === "name" && typeof value === "string") {
                    profile.name = value;
                }

                if (
                    weightType !== "name" &&
                    profile?.weights?.cost_risk_models[feature]
                ) {
                    if (typeof value === "number") {
                        profile.weights.cost_risk_models[feature][weightType] =
                            value;
                    }
                }

                return updatedProfiles;
            });
        } else {
            setWeightProfiles((prevProfiles) => {
                if (!prevProfiles?.length) return prevProfiles;

                const updatedProfiles = [...prevProfiles];

                const profile = updatedProfiles[profileIndex];

                if (weightType === "name" && typeof value === "string") {
                    profile.name = value;
                }

                if (
                    weightType !== "name" &&
                    profile?.weights.cost_risk_models[feature]
                ) {
                    if (typeof value === "number") {
                        profile.weights.cost_risk_models[feature][weightType] =
                            value;
                    }
                }

                return updatedProfiles;
            });
        }
    };

    const handleRiskThresholdChange = (
        profileIndex: number,
        thresholdType: "low" | "high",
        value: number
    ) => {
        if (isFiltered) {
            setFilteredWeightProfiles((prevProfiles) => {
                if (!prevProfiles?.length) return prevProfiles;

                const updatedProfiles = [...prevProfiles];
                const profile = updatedProfiles[profileIndex];

                if (profile?.weights?.risk_thresholds) {
                    profile.weights.risk_thresholds[thresholdType] = value;
                }

                return updatedProfiles;
            });
        } else {
            setWeightProfiles((prevProfiles) => {
                if (!prevProfiles?.length) return prevProfiles;

                const updatedProfiles = [...prevProfiles];
                const profile = updatedProfiles[profileIndex];

                if (profile?.weights?.risk_thresholds) {
                    profile.weights.risk_thresholds[thresholdType] = value;
                }

                return updatedProfiles;
            });
        }
    };

    // TODO: the update function will be different for this one
    const handleSSTChange = (
        profileIndex: number,
        sstIndex: number,
        sstType: "condition" | "phase" | "lower_tertile" | "upper_tertile",
        value: null | string
    ) => {
        const updateProfiles = (profiles: Content[]) => {
            if (!profiles?.length) return profiles;

            const updatedProfiles = [...profiles];
            const profile = updatedProfiles[profileIndex];

            if (
                profile?.weights?.sample_size_tertiles &&
                profile.weights.sample_size_tertiles[sstIndex]
            ) {
                const updatedTertile = {
                    ...profile.weights.sample_size_tertiles[sstIndex],
                    [sstType]: value && parseFloat(value),
                };

                // Replace the updated sst in the sample_size_tertiles array
                profile.weights.sample_size_tertiles = [
                    ...profile.weights.sample_size_tertiles.slice(0, sstIndex),
                    updatedTertile,
                    ...profile.weights.sample_size_tertiles.slice(sstIndex + 1),
                ];
            }

            return updatedProfiles;
        };

        if (isFiltered) {
            setFilteredWeightProfiles(
                (prevProfiles) => prevProfiles && updateProfiles(prevProfiles)
            );
        } else {
            setWeightProfiles(
                (prevProfiles) => prevProfiles && updateProfiles(prevProfiles)
            );
        }
    };

    // TODO: update the payload based on new updated API
    const onSave = async () => {
        const updatedWeights = data?.map((profile) => ({
            name: profile?.name,
            weights: profile?.weights,
        }));

        if (!updatedWeights) return;

        try {
            setIsUpdating((prev) => ({ ...prev, saving: true }));
            const newWeightProfile = await createUserWeightProfiles(
                updatedWeights[0]
            );
            if (newWeightProfile && isFiltered) {
                setFilteredWeightProfiles((prevProfiles) => {
                    if (!prevProfiles?.length) return prevProfiles;
                    const updatedProfiles = [...prevProfiles];
                    const profile = updatedProfiles.find(
                        (p) => p.id === newWeightProfile?.id
                    );
                    if (profile) {
                        profile.name = newWeightProfile.name;
                        profile.weights = newWeightProfile.weights;
                    }
                    return updatedProfiles;
                });
            } else {
                setWeightProfiles((prevProfiles) => {
                    if (!prevProfiles?.length) return prevProfiles;
                    const updatedProfiles = [...prevProfiles];
                    const profile = updatedProfiles.find(
                        (p) => p.id === newWeightProfile?.id
                    );
                    if (profile) {
                        profile.name = newWeightProfile.name;
                        profile.weights = newWeightProfile.weights;
                    }
                    return updatedProfiles;
                });
            }
        } catch (error) {
            console.error("Failed to save weight profile.", error);
        } finally {
            setIsUpdating((prev) => ({ ...prev, saving: false }));
        }
    };

    // Rows for different weight types
    const renderCRMRows = (
        weights: Weights,
        profileIndex: number,
        name: string,
        handleWeightChange: (
            profileIndex: number,
            feature: string,
            weightType: "cost" | "risk" | "name",
            value: number | string
        ) => void,
        handleUpdateWeightProfile: (
            name: string,
            feature: string,
            weights: Weights
        ) => Promise<void>,
        isUpdating: Record<string, boolean>,
        isDefault: boolean
    ) => {
        const { cost_risk_models } = weights;
        return Object.keys(cost_risk_models)?.map((feature, index) => {
            const { cost, risk } = cost_risk_models[feature];
            const isLast = index === Object.keys(cost_risk_models).length - 1;
            const rowClass = isLast
                ? "p-4"
                : "p-4 border-b border-blue-gray-50";

            return (
                <tr key={`feature-${feature}-${index}`}>
                    <td className={rowClass}>
                        <Typography
                            variant="small"
                            color="blue-gray"
                            className="font-normal"
                        >
                            {feature}
                        </Typography>
                    </td>
                    <td className={rowClass}>
                        <input
                            type="number"
                            value={cost}
                            min={0}
                            onChange={(e) =>
                                handleWeightChange(
                                    profileIndex,
                                    feature,
                                    "cost",
                                    parseFloat(e.target.value)
                                )
                            }
                            className="border rounded p-1"
                        />
                    </td>
                    <td className={rowClass}>
                        <input
                            type="number"
                            value={risk}
                            min={0}
                            onChange={(e) =>
                                handleWeightChange(
                                    profileIndex,
                                    feature,
                                    "risk",
                                    parseFloat(e.target.value)
                                )
                            }
                            className="border rounded p-1"
                        />
                    </td>
                    {!isDefault && (
                        <td className="p-4">
                            <Tooltip content="Save Sample size">
                                {isUpdating[`feature-${feature}-${index}`] ? (
                                    <Spinner className="h-5 w-5 text-text_secondary" />
                                ) : (
                                    <IconButton
                                        variant="text"
                                        size="sm"
                                        onClick={() =>
                                            handleUpdateWeightProfile(
                                                name,
                                                feature,
                                                weights
                                            )
                                        }
                                    >
                                        <FaCheck className="h-4 w-4 text-green_primary" />
                                    </IconButton>
                                )}
                            </Tooltip>
                        </td>
                    )}
                </tr>
            );
        });
    };

    const renderRTRows = (
        weights: Weights,
        profileIndex: number,
        name: string,
        handleRiskThresholdChange: (
            profileIndex: number,
            thresholdType: "low" | "high",
            value: number
        ) => void,
        handleUpdateWeightProfile: (
            name: string,
            feature: string,
            weights: Weights
        ) => Promise<void>,
        isUpdating: Record<string, boolean>,
        isDefault: boolean
    ) => {
        const { risk_thresholds } = weights;
        const { low, high } = risk_thresholds;
        const rowClass = "p-4 border-b border-blue-gray-50";

        return (
            <tr>
                <td className={rowClass}>
                    <input
                        type="number"
                        value={low}
                        min={0}
                        onChange={(e) =>
                            handleRiskThresholdChange(
                                profileIndex,
                                "low",
                                parseFloat(e.target.value)
                            )
                        }
                        className="border rounded p-1"
                    />
                </td>
                <td className={rowClass}>
                    <input
                        type="number"
                        value={high}
                        min={0}
                        onChange={(e) =>
                            handleRiskThresholdChange(
                                profileIndex,
                                "high",
                                parseFloat(e.target.value)
                            )
                        }
                        className="border rounded p-1"
                    />
                </td>
                {!isDefault && (
                    <td className="p-4">
                        <Tooltip content="Save risk threshold">
                            {isUpdating["risk"] ? (
                                <Spinner className="h-5 w-5 text-text_secondary" />
                            ) : (
                                <IconButton
                                    variant="text"
                                    size="sm"
                                    onClick={() =>
                                        handleUpdateWeightProfile(
                                            name,
                                            "risk",
                                            weights
                                        )
                                    }
                                >
                                    <FaCheck className="h-4 w-4 text-green_primary" />
                                </IconButton>
                            )}
                        </Tooltip>
                    </td>
                )}
            </tr>
        );
    };

    const renderSSTRows = (
        weights: Weights,
        profileIndex: number,
        name: string,
        handleSSTChange: (
            profileIndex: number,
            sstIndex: number,
            sstType: "condition" | "phase" | "lower_tertile" | "upper_tertile",
            value: null | string
        ) => void,
        handleUpdateWeightProfile: (
            name: string,
            feature: string,
            weights: Weights
        ) => Promise<void>,
        isUpdating: Record<string, boolean>,
        isDefault: boolean
    ) => {
        const { sample_size_tertiles } = weights;
        return sample_size_tertiles?.map((sst, index) => {
            const isLast = index === sample_size_tertiles?.length - 1;
            const rowClass = isLast
                ? "p-4"
                : "p-4 border-b border-blue-gray-50";

            return (
                <tr key={`sst-${sst.condition}-${index}`}>
                    <td className={rowClass}>
                        <Typography
                            variant="small"
                            color="blue-gray"
                            className="font-normal"
                        >
                            {sst.condition}
                        </Typography>
                    </td>

                    <td className={rowClass}>
                        <input
                            type="number"
                            value={sst.phase}
                            min={0}
                            onChange={(e) =>
                                handleSSTChange(
                                    profileIndex,
                                    index,
                                    "phase",
                                    e.target.value
                                )
                            }
                            className="border rounded p-1"
                        />
                    </td>
                    <td className={rowClass}>
                        <input
                            type="number"
                            value={sst.lower_tertile}
                            min={0}
                            onChange={(e) =>
                                handleSSTChange(
                                    profileIndex,
                                    index,
                                    "lower_tertile",
                                    e.target.value
                                )
                            }
                            className="border rounded p-1"
                        />
                    </td>
                    <td className={rowClass}>
                        <input
                            type="number"
                            value={sst.upper_tertile}
                            min={0}
                            onChange={(e) =>
                                handleSSTChange(
                                    profileIndex,
                                    index,
                                    "upper_tertile",
                                    e.target.value
                                )
                            }
                            className="border rounded p-1"
                        />
                    </td>
                    {!isDefault && (
                        <td className="p-4">
                            <Tooltip content="Save Sample size">
                                {isUpdating[sst.condition] ? (
                                    <Spinner className="h-5 w-5 text-text_secondary" />
                                ) : (
                                    <IconButton
                                        variant="text"
                                        size="sm"
                                        onClick={() =>
                                            // this will be diffterent
                                            handleUpdateWeightProfile(
                                                name,
                                                sst.condition,
                                                weights
                                            )
                                        }
                                    >
                                        <FaCheck className="h-4 w-4 text-green_primary" />
                                    </IconButton>
                                )}
                            </Tooltip>
                        </td>
                    )}
                </tr>
            );
        });
    };

    return (
        <>
            <CardBody className="overflow-scroll px-0 p-0">
                <table className="w-full min-w-max table-auto text-left">
                    <thead>
                        <tr>
                            {columns.map((head) => (
                                <th
                                    key={head}
                                    className="border-b border-blue-gray-100 bg-blue-gray-50/50 p-4"
                                >
                                    <Typography
                                        variant="small"
                                        color="blue-gray"
                                        className="font-semibold leading-none opacity-70"
                                    >
                                        {head}
                                    </Typography>
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data?.[0] &&
                            data?.map(({ name, weights }, profileIndex) => (
                                <>
                                    <tr key={`profile-${profileIndex}`}>
                                        <td
                                            colSpan={columns.length}
                                            className="p-4 border-b  bg-gray-50 font-bold "
                                        >
                                            <div className="w-full md:w-96">
                                                <Input
                                                    label={
                                                        "Weight Profile Name"
                                                    }
                                                    color="teal"
                                                    crossOrigin={undefined}
                                                    value={name}
                                                    onChange={(e) =>
                                                        handleCRMWeightChange(
                                                            profileIndex,
                                                            "",
                                                            "name",
                                                            e.target.value
                                                        )
                                                    }
                                                />
                                            </div>
                                        </td>
                                    </tr>
                                    {/* TODO(refactor): remove redundant code from here */}
                                    {weightKey === "cost_risk_models"
                                        ? renderCRMRows(
                                              weights,
                                              profileIndex,
                                              name,
                                              handleCRMWeightChange,
                                              handleUpdateWeightProfile,
                                              isUpdating,
                                              data?.[0]?.default
                                          )
                                        : weightKey === "risk_thresholds"
                                        ? renderRTRows(
                                              weights,
                                              profileIndex,
                                              name,
                                              handleRiskThresholdChange,
                                              handleUpdateWeightProfile,
                                              isUpdating,
                                              data?.[0]?.default
                                          )
                                        : renderSSTRows(
                                              weights,
                                              profileIndex,
                                              name,
                                              handleSSTChange,
                                              handleUpdateWeightProfile,
                                              isUpdating,
                                              data?.[0]?.default
                                          )}
                                </>
                            ))}
                    </tbody>
                </table>
            </CardBody>
            <CardFooter className="flex md:flex-row flex-col items-center justify-between border-t border-blue-gray-50 p-4">
                <div className=" flex md:flex-row flex-col    items-center gap-2 md:w-fit w-full">
                    <Button
                        onClick={onSave}
                        variant="filled"
                        className="flex justify-center hover:bg-text_primary/90    bg-text_primary items-center md:w-fit w-full  "
                    >
                        {isUpdating["saving"] ? (
                            <Spinner className="h-5 w-5" />
                        ) : (
                            "Create Weight Profile"
                        )}
                    </Button>

                    <Button
                        disabled={data?.[0]?.default}
                        onClick={() => setShowModal((prev) => !prev)}
                        variant="filled"
                        className="flex hover:bg-red-600/90 justify-center  bg-red-600 items-center  md:w-fit w-full "
                    >
                        Delete Weight Profile
                    </Button>
                </div>
            </CardFooter>

            <WeightProfileDeleteModal
                isOpen={showModal}
                isLoading={isLoading}
                setIsOpen={setShowModal}
                onDelete={onDelete}
            />
        </>
    );
}
