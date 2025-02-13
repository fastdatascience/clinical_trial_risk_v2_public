import React from "react";
import { useAtom } from "jotai";
import { Result } from "../../../utils/types";
import { CalculationTable } from "../../tables";

import {
    documentRunResultAtom,
    historyRunResultAtom,
    moduleWeightAtom,
} from "../../../lib/atoms";
import { NoProtocolUploaded } from "../../common";
import {
    transformDataForTable,
    updateFeatureDescriptions,
} from "../../../utils/utils";

const TABLE_HEAD = ["Feature", "Description", "Value", "Weight", "Score"];

const CostCalculation: React.FC<Result> = () => {
    const [weightProfile] = useAtom(moduleWeightAtom);
    const [historyRunResult] = useAtom(historyRunResultAtom);
    const [documentRunResult] = useAtom(documentRunResultAtom);

    const TABLE_ROWS =
        (historyRunResult?.trial_cost_table?.length ?? 0) > 0
            ? historyRunResult?.trial_cost_table || []
            : documentRunResult?.trial_cost_table || [];

    const tableRows = updateFeatureDescriptions(TABLE_ROWS);

    const tableData = transformDataForTable("cost", tableRows, weightProfile!);

    return (
        <div className="flex flex-col mt-3">
            {tableData.length > 0 ? (
                <CalculationTable
                    isCostTable={true}
                    title="Clinical trial cost calculation"
                    columns={TABLE_HEAD}
                    data={tableData}
                    originalDocumentName={historyRunResult?.document?.original_document_name}
                    condition={historyRunResult?.result?.condition?.prediction}
                />
            ) : (
                <NoProtocolUploaded />
            )}
        </div>
    );
};

export default CostCalculation;
