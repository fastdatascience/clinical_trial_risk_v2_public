import {
    Button,
    Card,
    CardBody,
    CardFooter,
    CardHeader,
    Spinner,
    Typography,
} from "@material-tailwind/react";
import React, { useState } from "react";
import { FaArrowRight, FaRegFileLines } from "react-icons/fa6";
import { IFileItemProps } from "../../utils/types";
import { bytesToHuman, formatCurrency } from "../../utils/utils";
import { ImBin } from "react-icons/im";
import { deleteDocument, getCdnUrlForDocument } from "../../utils/services";
import { AxiosResponse } from "axios";
import FileDeleteModal from "../modals/FileDeleteModal";
import { createSearchParams, Link } from "react-router-dom";
import { useAtom } from "jotai";
import { docInProgressIdAtom } from "../../lib/atoms";

const FileItem: React.FC<IFileItemProps> = ({ document, setDocuments }) => {
    const [documentInProgress] = useAtom(docInProgressIdAtom);
    const [showModal, setShowModal] = useState<boolean>(false);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isOpenCdn, setIsOpenCdn] = useState<boolean>(false);

    const handleFileDelete = async (docId: number) => {
        try {
            setIsLoading(true);
            const resp = (await deleteDocument(docId)) as AxiosResponse;
            if (resp.status === 204) {
                setDocuments((prevDocuments) =>
                    prevDocuments.filter((doc) => doc.id !== docId)
                );
                setIsLoading(false);
            }
            return;
        } catch (error) {
            setIsLoading(false);
            console.error("An Error Occurred while deleting document", error);
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

    return (
        <>
            <Card className="mt-6 border hover:shadow-xl cursor-pointer duration-500 ">
                <CardHeader
                    shadow={false}
                    floated={false}
                    className="flex text-red-600 justify-end  items-center rounded-none"
                >
                    <ImBin
                        size={20}
                        onClick={() => setShowModal((prev) => !prev)}
                    />
                </CardHeader>
                <CardBody className="flex justify-center items-center">
                    <Typography className=" text-green_primary bg-green_secondary p-2 rounded-lg">
                        <FaRegFileLines size={50} />
                    </Typography>
                </CardBody>
                <CardFooter className="pt-0">
                    <Typography variant="h6" color="blue-gray">
                        {document?.original_document_name}
                    </Typography>
                    <Typography variant="small" color="gray" className="mb-2">
                        File Size: {bytesToHuman(document?.document_size)}
                    </Typography>

                    {/* Show "Processing..." */}
                    {/* This will be fixed when we have eventStream */}
                    {documentInProgress === document.id ? (
                        <Typography
                            variant="small"
                            color="gray"
                            className="font-semibold flex text-gray-500 items-center h-full"
                        >
                            Processing...
                        </Typography>
                    ) : (
                        <>
                            <div className="flex justify-between items-center mb-2">
                                <Typography
                                    variant="small"
                                    color="gray"
                                    className=" font-normal flex text-start"
                                >
                                    Total Cost Per participant:{" "}
                                    {formatCurrency(
                                        document?.cost
                                            ?.total_cost_per_participant
                                    )}
                                </Typography>
                                <Typography
                                    variant="small"
                                    color="gray"
                                    className="font-semibold flex text-end"
                                >
                                    Total Cost:{" "}
                                    {formatCurrency(document?.cost.total_cost)}
                                </Typography>
                            </div>
                            {document?.trial_risk_score && (
                                <Typography
                                    variant="small"
                                    color="gray"
                                    className="mb-2 font-semibold"
                                >
                                    Risk:{" "}
                                    <span
                                        className={`${
                                            document?.trial_risk_score === "LOW"
                                                ? "text-green-700"
                                                : document?.trial_risk_score ===
                                                  "HIGH"
                                                ? "text-red-600"
                                                : "text-orange-600"
                                        }`}
                                    >
                                        {document?.trial_risk_score}
                                    </span>
                                </Typography>
                            )}

                            <Typography
                                variant="small"
                                color="gray"
                                className="mb-2"
                            >
                                Created at:{" "}
                                {new Date(document?.created_at).toLocaleString(
                                    "en-US",
                                    {
                                        year: "numeric",
                                        month: "long",
                                        day: "numeric",
                                    }
                                )}
                            </Typography>

                            <div className="flex justify-between">
                                <Button
                                    disabled={isOpenCdn}
                                    size="sm"
                                    variant="text"
                                    className=" items-center inline-flex gap-2"
                                    onClick={() => getCDNUrl(document.id)}
                                >
                                    {isOpenCdn && (
                                        <Spinner
                                            color="green"
                                            className="h-5 w-5"
                                        />
                                    )}
                                    View file
                                </Button>
                                <Link
                                    to={{
                                        pathname: "/dashboard",
                                        search: `?${createSearchParams({
                                            docId: `${document.id}`,
                                        })}`,
                                    }}
                                    target="_blank"
                                    className="inline-block"
                                >
                                    <Button
                                        size="sm"
                                        variant="text"
                                        className="flex items-center gap-2"
                                    >
                                        View Runs
                                        <FaArrowRight />
                                    </Button>
                                </Link>
                            </div>
                        </>
                    )}
                </CardFooter>
            </Card>

            <FileDeleteModal
                isOpen={showModal}
                isLoading={isLoading}
                setIsOpen={setShowModal}
                onDelete={() => handleFileDelete(document.id)}
            />
        </>
    );
};

export default FileItem;
