import React from "react";
import styles from "../../utils/styles";

const DashboardLayoutHeader: React.FC = () => {
    return (
        <div className="flex flex-wrap justify-between items-center p-10 text-Midnight_Blue font-poppins">
            <div className={`${styles.headingContainer}`}>
                <h1 className="text-3xl font-semibold">
                    Clinical Trial Risk Tool by Fast Data Science
                </h1>
                <p className={styles.paragraph}>
                    The Clinical Trial Risk Tool can analyse your clinical trial
                    protocols and estimate the cost in dollars, or the risk of
                    the trial ending uninformatively. Upload a Clinical Trial
                    Protocol in PDF format, and the Clinical Trial Risk Tool
                    will generate a risk assessment of the trial. You can find
                    example protocols by searching on{" "}
                    <a
                        href="https://youtu.be/wgLCAJUA1oI"
                        target="_blank"
                        className="text-blue-400 font-semibold underline"
                    >
                        ClinicalTrials.gov
                    </a>
                    .The tool supports protocols and other types of document
                    such as clinical development plans (CDPs) and the DAC
                    assessment tool.
                </p>
            </div>
        </div>
    );
};

export default DashboardLayoutHeader;
