import React, { useEffect, useState } from "react";
import FileGrid from "../Files/FileGrid";
import FileGridSkeleton from "../skeletons/FileGridSkeleton";
import PaginationControls from "../Files/PaginationControls";
import { getDocuments } from "../../utils/services";
import { AxiosResponse } from "axios";
import { IDocument } from "../../utils/types";
import { Typography } from "@material-tailwind/react";

const FileHistory: React.FC = () => {
    const [loading, setLoading] = useState<boolean>(false);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [totalPages, setTotalPages] = useState<number>(1);
    const [documents, setDocuments] = useState<IDocument[]>([]);

    const fetchDocs = async () => {
        try {
            setLoading(true);
            const data = (await getDocuments(currentPage)) as AxiosResponse;
            if (data.status !== 200) {
                return;
            }
            setDocuments(data?.data?.data?.contents || []);
            setTotalPages(data?.data?.data?.pages || 1);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching documents:", error);
        }
    };

    useEffect(() => {
        fetchDocs();
        // Fetch documents on page change, and when no docs
    }, [currentPage, documents.length === 0]);

    return (
        <>
            <h3 className="font-poppins text-xl font-bold text-text_primary">
                Files
            </h3>

            {loading ? (
                <FileGridSkeleton />
            ) : (
                <>
                    {documents.length ? (
                        <FileGrid
                            documents={documents}
                            setDocuments={setDocuments}
                        />
                    ) : (
                        <div className="text-center">
                            <Typography
                                variant="h5"
                                className="font-semibold text-Extra_Light_Gray"
                            >
                                No Files Uploaded
                            </Typography>
                        </div>
                    )}

                    <PaginationControls
                        currentPage={currentPage}
                        totalPages={totalPages}
                        hasNext={currentPage < totalPages}
                        hasPrevious={currentPage > 1}
                        onNextPage={() =>
                            setCurrentPage((prevPage) => prevPage + 1)
                        }
                        onPreviousPage={() =>
                            setCurrentPage((prevPage) => prevPage - 1)
                        }
                    />
                </>
            )}
        </>
    );
};

export default FileHistory;
