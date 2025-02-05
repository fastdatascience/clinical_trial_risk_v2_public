import React from "react";
import { tabItems } from "../../utils/constants";
import { IAnalysisProps } from "../../utils/types";
import { NoProtocolUploaded, Tabs } from "../common";

const PredictionBoard: React.FC<IAnalysisProps> = ({ protocolResult }) => {
    return (
        <div className="bg-green_secondary flex flex-col lg:items-stretch w-full rounded-large ">
            {protocolResult ? (
                <Tabs
                    tabItems={tabItems}
                    data={protocolResult}
                    tabListClassName="bg-green_primary font-thin p-5 rounded-t-large text-white md:text-sm text-base"
                />
            ) : (
                <NoProtocolUploaded />
            )}
        </div>
    );
};

export default PredictionBoard;
