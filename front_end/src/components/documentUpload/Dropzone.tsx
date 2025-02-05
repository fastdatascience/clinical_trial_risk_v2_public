import { useDropzone } from "react-dropzone";
import { AxiosResponse } from "axios";
import { useAtom } from "jotai";
import { PDFDocumentProxy } from "pdfjs-dist";

import {
    getMetaData,
    getRunStatus,
    getWeightProfiles,
    uploadFile,
} from "../../utils/services";
import CircularProgress from "../common/progress/CircularProgress";
import { DocumentRunStatus, IDocumentData, STATUS } from "../../utils/types";
import { Spinner } from "@material-tailwind/react";
import {
    runLogs,
    pdfDocAtom,
    metaDataAtom,
    showPdfViewer,
    userProfileAtom,
    moduleWeightAtom,
    weightProfilesAtom,
    uploadProgressAtom,
    isFileUploadingAtom,
    isFileProcessingAtom,
    documentRunResultAtom,
    processResultAtom,
    documentIdAtom,
    docInProgressIdAtom,
} from "../../lib/atoms";
import {
    getMaxFileSize,
    loadPDFDocument,
    megabytesToBytes,
} from "../../utils/utils";

let progressText: string = "Waiting to start...";

const Dropzone = () => {
    const [userProfile] = useAtom(userProfileAtom);
    const [, setProtocolResult] = useAtom(processResultAtom);
    const [, setMetaData] = useAtom(metaDataAtom);
    const [, setModuleWeight] = useAtom(moduleWeightAtom);
    const [, setWeightProfiles] = useAtom(weightProfilesAtom);
    const [, setPdfDocAtom] = useAtom(pdfDocAtom);
    const [, setDocumentId] = useAtom(documentIdAtom);
    const [, setDocInProgressId] = useAtom(docInProgressIdAtom);

    const [, setDocumentRunResult] = useAtom(documentRunResultAtom);

    const [isUploading, setIsUploading] = useAtom(isFileUploadingAtom);
    const [isFileProcessing, setIsFileProcessing] =
        useAtom(isFileProcessingAtom);
    const [, setShowPdfViewer] = useAtom(showPdfViewer);
    const [, setRunLogs] = useAtom(runLogs);

    const [uploadProgress, setUploadProgress] = useAtom(uploadProgressAtom);
    const { getRootProps, getInputProps, isDragActive, open, fileRejections } =
        useDropzone({
            accept: {
                "application/pdf": [],
                "application/vnd.ms-excel": [],
            },
            noClick: true,
            noKeyboard: true,
            onDrop: (files) => handleOnDrop(files),
            minSize: 0,
            maxSize: megabytesToBytes(getMaxFileSize(userProfile)),
        });

    const getAllWeightProfiles = async () => {
        try {
            await getWeightProfiles(setModuleWeight, setWeightProfiles);
        } catch (error) {
            console.error("Failed to get weight profiles,", error);
        }
    };

    const getDocsMetaDataWeights = async () => {
        try {
            await getMetaData(setMetaData);
            await getAllWeightProfiles();
        } catch (error) {
            console.error("Failed to get Meta data", error);
        }
    };

    const handleOnDrop = async (acceptedFiles: File[]) => {
        try {
            const file = acceptedFiles[0];
            const _PDF_DOC = (await loadPDFDocument(file)) as PDFDocumentProxy;
            setPdfDocAtom(_PDF_DOC);

            setIsUploading(true);

            const response = (await uploadFile(file)) as AxiosResponse;
            const { data, status } = response as AxiosResponse<IDocumentData>;

            if (status !== 200) {
                setIsUploading(false);
                return;
            }

            setIsUploading(false);
            setIsFileProcessing(true);
            // We can use this id to send in pdf export
            setDocumentId(data?.data?.id);

            // We have another state for currentResource that will be null on connection close
            getRunStatus(
                data?.data?.id,
                setDocInProgressId,
                setDocumentRunResult,
                handleRunStatusProgressUpdate,
                setRunLogs,
                setUploadProgress
            );
        } catch (error) {
            console.error("File upload or status check failed:", error);
        }
    };

    const handleRunStatusProgressUpdate = (runStatus: DocumentRunStatus) => {
        switch (runStatus.status) {
            case STATUS.QUEUED:
                progressText = "Waiting to start";
                break;
            case STATUS.IN_PROGRESS:
                progressText = "In progress...";
                break;
            default:
                progressText = "Completed";
                // need this to populate sidebar
                setProtocolResult(runStatus?.result);
                // Get meta data and weights here
                getDocsMetaDataWeights();
                setTimeout(() => {
                    setIsFileProcessing(false);
                    setShowPdfViewer(true);
                    setUploadProgress(0);
                }, 1000);
                break;
        }
    };

    const isFileTooLarge =
        fileRejections.length > 0 &&
        fileRejections[0]?.file?.size >
            megabytesToBytes(getMaxFileSize(userProfile));

    return (
        <>
            {!isUploading && !isFileProcessing && (
                <div {...getRootProps({ className: "dropzone" })}>
                    <input className="input-zone" {...getInputProps()} />
                    <div className="text-center">
                        {isDragActive ? (
                            <>
                                <h3 className="font-poppins">
                                    Release to drop the files here
                                </h3>
                                {isFileTooLarge && (
                                    <div className="text-danger mt-2">
                                        File is too large.
                                    </div>
                                )}
                            </>
                        ) : (
                            <>
                                <p className="text-text_secondary/50 text-sm font-semibold mt-2">
                                    Maximum file upload size is{" "}
                                    {getMaxFileSize(userProfile)} MBs
                                </p>
                                <div className="flex justify-center items-center mt-10 ">
                                    <button
                                        type="button"
                                        className="bg-gray-900 text-xs py-2 shadow-lg w-40  font-poppins text-white rounded-full cursor-pointer"
                                        onClick={open}
                                    >
                                        Select file
                                    </button>
                                </div>

                                {isFileTooLarge && (
                                    <div className="text-red-600 mt-5">
                                        File is too large.
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}

            {isFileProcessing && (
                <div className="flex flex-col gap-3">
                    <p className="text-xs text-center font-semibold text-text_secondary/50 break-words">
                        {progressText}
                    </p>
                    <CircularProgress
                        size={180}
                        progress={uploadProgress}
                        trackWidth={8}
                        trackColor={"#ebf9f3"}
                        indicatorWidth={8}
                        indicatorColor={"#57ca96"}
                    />
                </div>
            )}

            {isUploading && (
                <div className="flex flex-col justify-center items-center gap-5">
                    <p className="text-sm font-semibold text-text_secondary/50 break-words">
                        ⌛ Uploading your protocol. Please wait...
                    </p>
                    <Spinner color="green" className="h-10 w-10" />
                </div>
            )}
        </>
    );
};

export default Dropzone;
