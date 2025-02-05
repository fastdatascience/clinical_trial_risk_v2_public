import React from "react";
import styles from "../../utils/styles";

import AnalysisSideBar from "./AnalysisSideBar";
import PredictionBoard from "./PredictionBoard";
import { processResultAtom } from "../../lib/atoms";
import { useAtom } from "jotai";
const Analysis: React.FC = () => {
    const [protocolResult] = useAtom(processResultAtom);

    return (
        <>
            <div className={styles.headingContainer}>
                <h1 className={styles.heading}>Explanation of analysis</h1>
                <p className={styles.paragraph}>
                    Move the mouse over an item or click 'explain' for more
                    information
                </p>
            </div>

            <div className="mt-10 flex lg:flex-row flex-col gap-3 justify-between">
                {/* Sidebar */}
                <AnalysisSideBar />
                {/* Analysis Area */}
                <PredictionBoard protocolResult={protocolResult} />
            </div>
        </>
    );
};

export default Analysis;
