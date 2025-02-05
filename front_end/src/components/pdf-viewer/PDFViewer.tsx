import React, { useEffect, useState } from "react";
import * as pdfjsLib from "pdfjs-dist";
import { Button, Spinner } from "@material-tailwind/react";
import { RxExternalLink } from "react-icons/rx";
import { RenderParameters } from "pdfjs-dist/types/src/display/api";
import PdfImagesSkeleton from "../skeletons/PdfImagesSkeleton";
import { useAtom } from "jotai";
import {
    documentIdAtom,
    historyRunResultAtom,
    metaDataAtom,
    pdfDocAtom,
    runLogs,
    showPdfViewer,
} from "../../lib/atoms";
import { useSearchParams } from "react-router-dom";
import { EnlargeViewModal } from "../modals/EnlargeViewModal";
import { IPdfImage } from "../../utils/types";
import { FaRegFilePdf } from "react-icons/fa6";
import { exportPdfReport, getCdnUrlForDocument } from "../../utils/services";

const PDFViewer: React.FC = () => {
    const [searchParams] = useSearchParams();
    const historyDocId = searchParams?.get("docId");
    const [, setHistoryRunResult] = useAtom(historyRunResultAtom);
    const [, setPdfViewer] = useAtom(showPdfViewer);
    const [pdfDoc] = useAtom(pdfDocAtom);
    const [, setMetaData] = useAtom(metaDataAtom);
    const [, setRunLogs] = useAtom(runLogs);
    const [documentId, setDocumentId] = useAtom(documentIdAtom);
    const [pdfImages, setPdfImages] = useState<IPdfImage[]>([]);
    const [selectedImage, setSelectedImage] = useState<number>(0);
    const [openZoomedView, setOpenZoomedView] = useState<boolean>(false);
    const [pageRendering, setPageRendering] = useState<boolean>(false);
    const [isExporting, setIsExporting] = useState<boolean>(false);
    const [isOpenCdn, setIsOpenCdn] = useState<boolean>(false);

    async function renderPdf(pdfDoc: string | pdfjsLib.PDFDocumentProxy) {
        setPageRendering(true);
        const imagesList = [];
        const canvas = document.createElement("canvas");

        let pdf;

        if (typeof pdfDoc === "string") {
            // If pdfDoc is a URL string, load the PDF from the URL
            const loadingTask = pdfjsLib?.getDocument(pdfDoc);
            pdf = await loadingTask.promise;
        } else {
            // If pdfDoc is a PDF document object, use it directly
            pdf = pdfDoc;
        }
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const viewport = page.getViewport({ scale: 1 });
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            const render_context = {
                canvasContext: canvas.getContext("2d"),
                viewport: viewport,
            };
            await page?.render(render_context as RenderParameters).promise;
            const img = canvas.toDataURL("image/png");
            imagesList.push({ image: img, pageNumber: page?.pageNumber });
        }

        setPdfImages(imagesList);
        setPageRendering(false);
    }

    const exportPdf = async (document_id: string | number | null) => {
        if (!document_id) return;
        try {
            // start loading
            setIsExporting((prev) => !prev);
            const response = await exportPdfReport(document_id);
            if (response.status === 200) {
                // Create a Blob from raw PDF
                const blob = new Blob([response.data], {
                    type: "application/pdf",
                });

                // Create a URL for the Blob
                const url = URL.createObjectURL(blob);

                // Create a temporary link element
                const link = document.createElement("a");
                link.href = url;
                link.download = `report-${document_id}.pdf`;
                document.body.appendChild(link);

                // Trigger the download
                link.click();

                // Cleanup
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }
        } catch (error) {
            console.error("Failed to export PDF:", error);
        } finally {
            // stop loading
            setIsExporting((prev) => !prev);
        }
    };

    const getCDNUrl = async (document_id: string | number) => {
        try {
            // start loading
            setIsOpenCdn((prev) => !prev);
            const response = await getCdnUrlForDocument(document_id);
            if (response.status !== 200) return;
            const {
                data: { data },
            } = response;

            if (data.cdn_path) {
                window.open(data.cdn_path, "_blank");
            }
        } catch (error) {
            console.error("Failed to get CND url for doc:", document_id, error);
        } finally {
            // stop loading
            setIsOpenCdn((prev) => !prev);
        }
    };

    useEffect(() => {
        if (pdfDoc) {
            renderPdf(pdfDoc);
        }
    }, [pdfDoc]);

    const clearStates = () => {
        setPdfViewer(false);
        setPdfImages([]);
        setMetaData([]);
        setRunLogs([]);
        setHistoryRunResult(null);
        setDocumentId(0);
    };

    return (
        <>
            <section className="flex flex-col ">
                {/* (Not allowing adding new doc when viewing history) */}
                {!historyDocId && (
                    <div className="flex  justify-end items-center">
                        <Button
                            onClick={() => clearStates()}
                            className="bg-green_primary px-16 py-3 rounded-full"
                        >
                            Add new document
                        </Button>
                    </div>
                )}

                {/* Scrollable div for pdfs */}
                <div className="flex justify-between  w-full mt-3 shadow-md rounded-3xl bg-green_secondary ">
                    {pageRendering ? (
                        <PdfImagesSkeleton />
                    ) : (
                        <div className="space-y-3 overflow-x-hidden p-5">
                            <div className="flex md:flex-row  flex-col gap-2 items-start">
                                <Button
                                    disabled={isExporting}
                                    size="sm"
                                    variant="filled"
                                    onClick={() => {
                                        historyDocId
                                            ? exportPdf(historyDocId)
                                            : exportPdf(documentId);
                                    }}
                                    className="bg-text_primary flex items-center gap-x-2 justify-center"
                                >
                                    {isExporting ? (
                                        <Spinner
                                            color="green"
                                            className="h-5 w-5"
                                        />
                                    ) : (
                                        <FaRegFilePdf size={20} />
                                    )}
                                    <span>Export Report as PDF</span>
                                </Button>
                                {/* Only showing view PDF for history  */}
                                {typeof pdfDoc === "string" && (
                                    <Button
                                        disabled={isOpenCdn}
                                        variant="filled"
                                        size="sm"
                                        className="bg-text_primary flex items-center gap-x-2 justify-center"
                                        onClick={() => getCDNUrl(historyDocId!)}
                                    >
                                        {isOpenCdn ? (
                                            <Spinner
                                                color="green"
                                                className="h-5 w-5"
                                            />
                                        ) : (
                                            <RxExternalLink size={20} />
                                        )}
                                        <span>View PDF</span>
                                    </Button>
                                )}
                            </div>
                            <div className="flex p-3 gap-5 border border-green_primary/25 shadow-md rounded-xl  w-full  overflow-x-scroll custom-scrollbar [&>div]:flex-shrink-0 ">
                                {pdfImages.map(({ image, pageNumber }) => (
                                    <div
                                        key={pageNumber}
                                        className="flex flex-col items-center justify-center"
                                    >
                                        <button
                                            onClick={() => {
                                                setSelectedImage(pageNumber);
                                                setOpenZoomedView(
                                                    (prev) => !prev
                                                );
                                            }}
                                        >
                                            <img
                                                id="image-generated"
                                                src={image}
                                                alt="pdfImage"
                                                className="w-64 object-contain rounded-md  shadow-md"
                                            />
                                        </button>
                                        {/* Page number below the image */}
                                        <div className="mt-2 text-sm  text-gray-700">
                                            Page {pageNumber}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </section>
            {/* Modal for large view */}
            <EnlargeViewModal
                open={openZoomedView}
                setOpen={() => setOpenZoomedView((prev) => !prev)}
                selectedImage={
                    selectedImage > 0 ? selectedImage - 1 : selectedImage
                }
                imageSrc={pdfImages}
            />
        </>
    );
};

export default PDFViewer;
