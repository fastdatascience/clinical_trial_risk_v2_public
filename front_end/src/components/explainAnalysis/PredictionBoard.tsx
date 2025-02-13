import React from "react";
import { tabItems } from "../../utils/constants";
import { IAnalysisProps } from "../../utils/types";
import { NoProtocolUploaded } from "../common";
import { CustomTabs } from "../common/Tabs";

const PredictionBoard: React.FC<IAnalysisProps> = ({ protocolResult }) => {
    return (
        <div className="bg-green_secondary flex flex-col lg:items-stretch w-full rounded-large ">
            {protocolResult ? (
                <CustomTabs
                    value="Breakdown by page number"
                    tabItems={tabItems}
                    data={protocolResult}
                    tabListClassName="rounded-t-large bg-green_primary  flex md:flex-row flex-col  px-0 py-2 rounded-b-none overflow-hidden"
                />
            ) : (
                <NoProtocolUploaded />
            )}
        </div>
    );
};

export default PredictionBoard;
