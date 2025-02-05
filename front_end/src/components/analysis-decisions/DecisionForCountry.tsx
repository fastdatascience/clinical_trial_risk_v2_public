import React from "react";
import { Country } from "../../utils/types";
import { normalizeDataForHeatmap } from "../../utils/utils";
import Heatmap from "../charts/Heatmap";

const DecisionForCountry: React.FC<{ country: Country | undefined }> = ({
    country,
}) => {
    const heatmapGrid = normalizeDataForHeatmap(country!);

    if (!country) return null;

    return (
        <div className="flex flex-col justify-center items-start mt-3">
            <p className=" text-start text-sm leading-6 font-normal  text-text_secondary">
                {" "}
                Which countries were mentioned on which pages in the document?
                Estimated trial countries:{" "}
                <strong>{Object.keys(country?.context).join(",")}</strong>. The
                AI looked at the countries which were mentioned more often and
                earlier on in the document than other countries. The graph below
                shows the candidate countries as a heat map throughout the pages
                of the document.
            </p>

            <div className="flex w-full justify-center items-center">
                <Heatmap width={700} height={500} data={heatmapGrid} />
            </div>

            <div className="flex flex-col  mt-8">
                <h3 className="text-text_secondary text-start font-semibold text-base">
                    Possible mentions of COUNTRY in the document
                </h3>
                <div className="mt-5">
                    <p className="text-start text-text_secondary mb-3">
                        {Object.keys(country?.context).join(",")}
                    </p>
                    <p className=" text-start  font-poppins break-words ">
                        {Object.entries(country.context).map(([key, value]) => (
                            <pre
                                key={key}
                                className=" text-sm whitespace-normal text-text_secondary"
                            >
                                <span className=" font-bold text-blue-gray-900 capitalize">
                                    {key}
                                </span>
                                :{value}
                            </pre>
                        ))}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default DecisionForCountry;
