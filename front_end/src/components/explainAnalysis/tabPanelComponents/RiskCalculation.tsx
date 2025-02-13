import React from "react";
import { ITableRow, Result } from "../../../utils/types";
import { useAtom } from "jotai";
import {
    documentRunResultAtom,
    historyRunResultAtom,
    moduleWeightAtom,
} from "../../../lib/atoms";

import { CalculationTable } from "../../tables";
import { NoProtocolUploaded } from "../../common";
import { transformDataForTable } from "../../../utils/utils";

const TABLE_HEAD = ["Parameter", "Value", "Weight", "Score"];

const removeDescription = (data: ITableRow[]) => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    return data.map(({ description, ...rest }) => rest);
};
const RiskCalculation: React.FC<Result> = () => {
    const [weightProfile] = useAtom(moduleWeightAtom);
    const [historyRunResult] = useAtom(historyRunResultAtom);
    const [documentRunResult] = useAtom(documentRunResultAtom);

    const TABLE_ROWS = removeDescription(
        (historyRunResult?.trial_risk_table?.length ?? 0) > 0
            ? historyRunResult?.trial_risk_table || []
            : documentRunResult?.trial_risk_table || []
    );

    const tableData = transformDataForTable("risk", TABLE_ROWS, weightProfile!);

    return (
        <div className="flex flex-col justify-center items-center mt-3 font-poppins">
            <p className=" text-start text-sm leading-6 font-normal  text-text_secondary">
                The table below shows how the risk of this protocol was
                calculated. Protocols are scored according to a simple linear
                formula between 0 and 100, where 100 would be a perfect low-risk
                protocol and 0 would be a high-risk protocol. Each parameter
                extracted in the table on the left is entered into a spreadsheet
                and contributes to the scoring with an associated weight. For
                example, by far the strongest indicator that a protocol is
                low-risk is the presence of a statistical analysis plan. You can
                change the weights in the dropdowns on the left, or you can
                download the risk calculations as a spreadsheet and experiment
                with the parameters in Excel.
            </p>

            {/*  Table with Download to Excel functionality */}
            <div className="flex flex-col mt-3 w-full">
                {tableData.length > 0 ? (
                    <CalculationTable
                        isCostTable={false}
                        title="Clinical trial Risk calculation"
                        columns={TABLE_HEAD}
                        data={tableData}
                        originalDocumentName={historyRunResult?.document?.original_document_name}
                        condition={historyRunResult?.result?.condition?.prediction}
                    />
                ) : (
                    <NoProtocolUploaded />
                )}
            </div>
        </div>
    );
};

export default RiskCalculation;
