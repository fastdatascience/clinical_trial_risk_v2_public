import React, { useEffect } from "react";
import { AxiosResponse } from "axios";
import { useSearchParams } from "react-router-dom";
import { useAtom } from "jotai";
import Analysis from "../explainAnalysis/Analysis";
import PDFViewer from "../pdf-viewer/PDFViewer";
import DocumentUpload from "../documentUpload/DocumentUpload";
import {
    historyRunResultAtom,
    metaDataAtom,
    moduleWeightAtom,
    pdfDocAtom,
    runLogs,
    showPdfViewer,
    weightProfilesAtom,
} from "../../lib/atoms";
import RunLogs from "../documentUpload/RunLogs";
import {
    getHistoryRunResult,
    getMetaData,
    getWeightProfiles,
} from "../../utils/services";

const Dashboard: React.FC = () => {
    const [searchParams] = useSearchParams();
    const docId = searchParams?.get("docId");
    const [isPdfViewerVisible, setShowPdfViewer] = useAtom(showPdfViewer);
    const [, setPdfDocAtom] = useAtom(pdfDocAtom);
    const [, setHistoryRunResult] = useAtom(historyRunResultAtom);

    const [, setMetaData] = useAtom(metaDataAtom);
    const [, setModuleWeight] = useAtom(moduleWeightAtom);
    const [, setWeightProfiles] = useAtom(weightProfilesAtom);
    const [runLog] = useAtom(runLogs);

    useEffect(() => {
        if (!docId) {
            return;
        }
        (async () => {
            try {
                (await getHistoryRunResult(
                    +docId,
                    setHistoryRunResult,
                    setPdfDocAtom
                )) as AxiosResponse;
                // TODO: improve this
                getMetaData(setMetaData);
                getWeightProfiles(setModuleWeight, setWeightProfiles);
                setShowPdfViewer(true);
            } catch (err) {
                console.log("Error occurred getting runs", err);
            }
        })();
    }, [docId]);

    return (
        <>
            {docId ? (
                isPdfViewerVisible && <PDFViewer />
            ) : isPdfViewerVisible ? (
                <PDFViewer />
            ) : (
                <DocumentUpload />
            )}
            {!!runLog.length && <RunLogs runLog={runLog} />}
            <Analysis />
        </>
    );
};

export default Dashboard;
