import React, { useState, useMemo, useCallback, useEffect } from "react";
import { IoSearchOutline } from "react-icons/io5";
import {
    Button,
    Card,
    CardBody,
    Input,
    Typography,
} from "@material-tailwind/react";
import { IModuleWeight, ITableRow } from "../../utils/types";
import ExcelExport from "./ExcelExport";
import { formatCurrency, generateDropdownOptions } from "../../utils/utils";
import { SelectInput } from "../common";
import { useAtom } from "jotai";
import {
    historyRunResultAtom,
    moduleWeightAtom,
    weightProfilesAtom,
} from "../../lib/atoms";
import { FaPlus } from "react-icons/fa6";
import { useNavigate } from "react-router-dom";

const CalculationTable = ({
    isCostTable,
    title,
    columns,
    data,
}: {
    isCostTable: boolean;
    title: string;
    columns: string[];
    data: ITableRow[];
}) => {
    const [weightProfiles] = useAtom(weightProfilesAtom);
    const [, setModuleWeight] = useAtom(moduleWeightAtom);
    const [historyRunResult] = useAtom(historyRunResultAtom);

    const navigate = useNavigate();

    const [tableData, setTableData] = useState<ITableRow[]>(data);
    const [filteredData, setFilteredData] = useState<ITableRow[]>(data);

    const [searchQuery, setSearchQuery] = useState<string>("");
    const [selectedProfile, setSelectedProfile] = useState<string>("");
    const [sampleSize, setSampleSize] = useState<number>(1);

    const weight_profile_options = generateDropdownOptions(weightProfiles);

    useEffect(() => {
        setTableData(data);
        setFilteredData(data);

        const sampleSizeRow = data.find((row) => row.feature === "sample_size");

        if (sampleSizeRow) {
            setSampleSize(Number(sampleSizeRow?.value) ?? 1);
        }
    }, [data]);

    /* 
    this function handle weight change and calculates score 
      - weights are user configurable 
      - (value * weight) = score 
    */
    const handleWeightChange = useCallback(
        (index: number, newWeight: number) => {
            setFilteredData((prevData) => {
                const updatedData = [...prevData];
                const numericValue = isNaN(Number(updatedData[index].value))
                    ? 0
                    : updatedData[index].value;
                updatedData[index] = {
                    ...updatedData[index],
                    weight: newWeight,
                    score: Number(numericValue) * Number(newWeight),
                };
                return updatedData;
            });
        },
        []
    );

    // Sum of scores = total cost per participants
    const totalCostPerParticipant = useMemo(
        () =>
            filteredData.reduce(
                (acc, row) => Number(acc) + Number(row.score),
                0
            ),
        [filteredData]
    );

    // total cost per participants * sample size we get total costs
    const totalCostOfTrial = useMemo(
        () => totalCostPerParticipant * sampleSize,
        [totalCostPerParticipant, sampleSize]
    );

    // Determining the Risk level based on score
    const riskLevel = useMemo(() => {
        if (totalCostPerParticipant >= 50 && totalCostPerParticipant <= 100) {
            return <span className=" text-green-700">Low</span>;
        } else if (
            totalCostPerParticipant >= 0 &&
            totalCostPerParticipant < 40
        ) {
            return <span className=" text-red-600">High</span>;
        } else {
            return <span className="text-orange-600">Medium</span>;
        }
    }, [totalCostPerParticipant]);

    const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearchQuery(event.target.value);

        const filteredData = searchQuery
            ? tableData?.filter((row) =>
                  row.feature
                      .toLowerCase()
                      .includes(event.target?.value?.toLowerCase())
              )
            : tableData;

        // Update table data with filtered data
        setFilteredData(filteredData);
    };

    const handleSelectWeightProfile = (profile: string) => {
        setSelectedProfile(profile);
        const filteredWightProfiles = weightProfiles?.filter(
            (_profile) => _profile.name === profile
        );

        const weights = filteredWightProfiles?.reduce((acc, weights) => {
            return {
                ...acc,
                ...weights.weights.cost_risk_models,
            };
        }, {} as IModuleWeight);

        setModuleWeight(weights || {});
    };

    return (
        <Card className="h-full w-full overflow-scroll ">
            <header className="rounded-none space-y-6 p-5">
                {/* Main Heading */}
                <div className="flex flex-col justify-between gap-8 md:flex-row md:items-center">
                    <Typography variant="h4" className="text-text_secondary">
                        {title}
                    </Typography>
                    <ExcelExport
                        data={filteredData}
                        fileName={"cost_calculation"}
                    />
                </div>

                {/* Inputs for Search and Filter */}
                <div className="w-full flex md:flex-row flex-col gap-4 items-center justify-between ">
                    <div className="md:w-96 w-full">
                        <Input
                            label={
                                isCostTable
                                    ? "Search Feature..."
                                    : "Search Parameter..."
                            }
                            color="teal"
                            icon={<IoSearchOutline className="h-5 w-5" />}
                            crossOrigin={undefined}
                            value={searchQuery}
                            onChange={handleSearchChange}
                        />
                    </div>

                    <div className="md:w-64 md:flex md:justify-end md:items-center w-full ">
                        {weightProfiles?.[0]?.default ? (
                            <Button
                                size="sm"
                                variant="outlined"
                                onClick={() => navigate("/settings")}
                                className="flex border border-text_primary text-text_primary  items-center gap-3 justify-center "
                            >
                                <FaPlus size={16} />
                                Add Weight Profile
                            </Button>
                        ) : (
                            <SelectInput
                                value={selectedProfile}
                                placeholder="Select weight profile..."
                                options={weight_profile_options}
                                onChange={(value) =>
                                    handleSelectWeightProfile(value)
                                }
                            />
                        )}
                    </div>
                </div>

                {/* Sub Headings */}
                <div className="flex  justify-between items-center">
                    {isCostTable ? (
                        <div className="flex justify-between  w-full items-center ">
                            <Typography
                                variant="h5"
                                className=" text-text_primary font-semibold text-start "
                            >
                                Total Cost of Trial:{" "}
                                {historyRunResult
                                    ? formatCurrency(
                                          historyRunResult?.cost?.total_cost
                                      )
                                    : formatCurrency(totalCostOfTrial)}
                            </Typography>
                            <Typography
                                variant="h5"
                                className=" text-text_primary font-semibold text-start "
                            >
                                Total Cost per Participant:
                                {historyRunResult
                                    ? formatCurrency(
                                          historyRunResult?.cost
                                              ?.total_cost_per_participant
                                      )
                                    : formatCurrency(totalCostPerParticipant)}
                            </Typography>
                        </div>
                    ) : (
                        <div className="flex justify-between w-full items-center ">
                            <Typography
                                variant="h6"
                                className="text-text_primary font-semibold text-start "
                            >
                                Risk Level:{" "}
                                <span
                                    className={`${
                                        historyRunResult?.trial_risk_score ===
                                        "LOW"
                                            ? "text-green-700"
                                            : historyRunResult?.trial_risk_score ===
                                              "HIGH"
                                            ? "text-red-600"
                                            : "text-orange-600"
                                    }`}
                                >
                                    {historyRunResult
                                        ? historyRunResult?.trial_risk_score
                                        : riskLevel}
                                </span>
                            </Typography>
                            <Typography
                                variant="h6"
                                className="text-text_secondary font-normal text-start "
                            >
                                <span className="font-semibold">
                                    Total Score:{" "}
                                    {historyRunResult
                                        ? historyRunResult.trial_risk_score_numeric
                                        : Math.trunc(totalCostPerParticipant)}
                                </span>{" "}
                                (50-100=low risk, 0-40=high risk)
                            </Typography>
                        </div>
                    )}
                </div>
            </header>

            <CardBody>
                <table className="w-full min-w-max table-auto text-left">
                    <thead>
                        <tr>
                            {columns.map((head) => (
                                <th
                                    key={head}
                                    className="border-b border-blue-gray-100 bg-green_secondary rounded-t-lg p-4"
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
                        {filteredData?.map((row, index) => {
                            const isLast = index === filteredData?.length - 1;
                            const classes = isLast
                                ? "p-4"
                                : "p-4 border-b border-blue-gray-50";
                            return (
                                <TableRow
                                    key={`${row.feature}-${index}`}
                                    row={row}
                                    index={index}
                                    onWeightChange={handleWeightChange}
                                    classes={classes}
                                />
                            );
                        })}
                    </tbody>
                </table>
            </CardBody>
        </Card>
    );
};

const TableRow = React.memo(
    ({
        row,
        index,
        onWeightChange,
        classes,
    }: {
        row: ITableRow;
        index: number;
        onWeightChange: (index: number, newWeight: number) => void;
        classes: string;
    }) => {
        const { feature, description, value, weight, score, formula } = row;

        return (
            <tr key={feature}>
                <td className={classes}>
                    <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                    >
                        {feature}
                    </Typography>
                </td>
                {description && (
                    <td className={`${classes} md:w-24 w-fit`}>
                        <Typography
                            variant="small"
                            color="blue-gray"
                            className="font-normal break-words"
                        >
                            {description}
                        </Typography>
                    </td>
                )}
                <td className={`${classes} md:w-20 w-fit`}>
                    <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                    >
                        {value}
                    </Typography>
                </td>
                <td className={classes}>
                    <input
                        type="number"
                        value={weight}
                        min={0}
                        onChange={(e) =>
                            onWeightChange(index, parseFloat(e.target.value))
                        }
                        className="border rounded p-1"
                    />
                </td>
                <td className={classes}>
                    <Typography
                        variant="small"
                        color="blue-gray"
                        className="font-normal"
                    >
                        {score}
                    </Typography>
                </td>
                {formula && (
                    <td className={`${classes} md:w-24 w-fit`}>
                        <Typography
                            variant="small"
                            color="blue-gray"
                            className="font-normal"
                        >
                            {formula}
                        </Typography>
                    </td>
                )}
            </tr>
        );
    }
);

export default CalculationTable;
