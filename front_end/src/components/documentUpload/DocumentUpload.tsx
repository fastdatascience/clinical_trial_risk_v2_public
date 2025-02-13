import React, { useEffect, useState } from "react";
import { useAtom } from "jotai";
import styles from "../../utils/styles";
import Dropzone from "./Dropzone";
import {
    historyRunResultAtom,
    isDemoUserAtom,
    isFileProcessingAtom,
    isFileUploadingAtom,
    metaDataAtom,
    moduleWeightAtom,
    pdfDocAtom,
    showPdfViewer,
    weightProfilesAtom,
} from "../../lib/atoms";
import { Link } from "react-router-dom";
import SelectInput from "../common/SelectInput";
import {
    getMetaData,
    getPublicDocumentRunResult,
    getPublicDocuments,
    getWeightProfiles,
} from "../../utils/services";
import { ITemplateDocument } from "../../utils/types";
import { generateOptionsForTemplates } from "../../utils/utils";
import { AxiosResponse } from "axios";

const DocumentUpload: React.FC = () => {
    const [isDemoUser] = useAtom(isDemoUserAtom);
    const [isUploading] = useAtom(isFileUploadingAtom);
    const [isFileProcessing] = useAtom(isFileProcessingAtom);
    const [, setShowPdfViewer] = useAtom(showPdfViewer);
    const [, setPdfDocAtom] = useAtom(pdfDocAtom);
    const [, setHistoryRunResult] = useAtom(historyRunResultAtom);

    const [, setMetaData] = useAtom(metaDataAtom);
    const [, setModuleWeight] = useAtom(moduleWeightAtom);
    const [, setWeightProfiles] = useAtom(weightProfilesAtom);

    const [selectedTemplateId, setSelectedTemplateId] = useState<number>(0);
    const [errorText, setErrorText] = useState<string>("");
    const [templateDocuments, setTemplateDocuments] = useState<
        ITemplateDocument[]
    >([]);

    const getPublicTemplates = async () => {
        try {
            const response = await getPublicDocuments();
            const {
                data: { data },
            } = response;
            setTemplateDocuments(data);
        } catch (error) {
            console.log("Failed to fetch template protocols", error);
            setTemplateDocuments([]);
        }
    };

    useEffect(() => {
        getPublicTemplates();
    }, []);

    const options = generateOptionsForTemplates(templateDocuments);

    const startTemplateRunResults = async (template_id: number) => {
        setSelectedTemplateId(template_id);

        try {
            const response = (await getPublicDocumentRunResult(
                template_id
            )) as AxiosResponse;

            if (response.status !== 200) return;

            const {
                data: { data },
            } = response;

            if (data) {
                setHistoryRunResult(data);
                setPdfDocAtom(data?.document?.cdn_path);

                //    TODO: improve this
                getMetaData(setMetaData);
                getWeightProfiles(setModuleWeight, setWeightProfiles);
                setShowPdfViewer(true);
            }
        } catch (error) {
            setErrorText("Protocol not found. Please select another.");
            // set Error message and let them know to choose another doc
            console.error("Failed to get template run results", error);
        }
    };

    return (
        <div className="bg-green_secondary p-10 drop-shadow-md rounded-large">
            <div className={styles.headingContainer}>
                <h1 className={styles.heading}>
                    Upload your protocol in PDF format
                </h1>
                {isDemoUser && (
                    <p className="text-sm text-text_secondary/70">
                        You can upload up to{" "}
                        <strong className="text-text_secondary">3 files</strong>{" "}
                        as a Guest.{" "}
                        <span className="underline text-text_secondary">
                            <Link to={"/login"}> Log in or sign up</Link>
                        </span>{" "}
                        to unlock more!
                    </p>
                )}
            </div>

            <div className="flex flex-col items-center justify-center mt-3 gap-3">
                {/* for file upload */}
                <div className="w-full gap-3 flex md:flex-row flex-col  justify-between items-center">
                    <div
                        className={
                            "bg-white md:w-3/5 w-full rounded-large border-dashed border-2 border-Green  h-72 flex justify-center items-center"
                        }
                    >
                        <Dropzone />
                    </div>

                    {!isUploading && !isFileProcessing && (
                        <>
                            <div className=" text-text_secondary">OR</div>
                            <div className="md:w-2/5 w-full">
                                <SelectInput
                                    placeholder="Choose a protocol..."
                                    options={options}
                                    value={
                                        options.find(
                                            (option) =>
                                                option.value ===
                                                selectedTemplateId
                                        )?.label
                                    }
                                    onChange={(value) =>
                                        startTemplateRunResults(+value)
                                    }
                                />
                                {errorText && (
                                    <small className="text-red-700">
                                        {errorText}
                                    </small>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
};

export default DocumentUpload;
