import React from "react";
import { useAtom } from "jotai";
import { Result } from "../../../utils/types";
import { CalculationTable } from "../../tables";

import {
    documentRunResultAtom,
    historyRunResultAtom,
} from "../../../lib/atoms";
import { NoProtocolUploaded } from "../../common";
import { updateFeatureDescriptions } from "../../../utils/utils";

const TABLE_HEAD = ["Feature", "Description", "Value", "Weight", "Score"];

const CostCalculation: React.FC<Result> = () => {
    const [historyRunResult] = useAtom(historyRunResultAtom);
    const [documentRunResult] = useAtom(documentRunResultAtom);

    const TABLE_ROWS =
        (historyRunResult?.trial_cost_table?.length ?? 0) > 0
            ? historyRunResult?.trial_cost_table || []
            : documentRunResult?.trial_cost_table || [];

    const tableData = updateFeatureDescriptions(TABLE_ROWS);

    return (
        <div className="flex flex-col mt-3">
            {tableData.length > 0 ? (
                <CalculationTable
                    isCostTable
                    title="Clinical trial cost calculation"
                    columns={TABLE_HEAD}
                    data={tableData}
                />
            ) : (
                <NoProtocolUploaded />
            )}
        </div>
    );
};

export default CostCalculation;
