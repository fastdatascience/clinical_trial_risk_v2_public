import React from "react";
import { IconButton, Typography } from "@material-tailwind/react";
import { FaArrowRight, FaArrowLeftLong } from "react-icons/fa6";
import { IPaginationProps } from "../../utils/types";

const PaginationControls: React.FC<IPaginationProps> = (
    {
        currentPage,
        totalPages,
        hasNext,
        hasPrevious,
        onNextPage,
        onPreviousPage }
) => {
    return (
        <div className="flex py-5 justify-center items-center gap-8">
            <IconButton
                size="sm"
                variant="outlined"
                onClick={onPreviousPage}
                disabled={!hasPrevious}
            >
                <FaArrowLeftLong strokeWidth={2} className="h-4 w-4" />
            </IconButton>
            <Typography color="gray" className="font-normal">
                Page <strong className="text-gray-900">{currentPage}</strong> of{" "}
                <strong className="text-gray-900">{totalPages}</strong>
            </Typography>
            <IconButton
                size="sm"
                variant="outlined"
                onClick={onNextPage}
                disabled={!hasNext}
            >
                <FaArrowRight strokeWidth={2} className="h-4 w-4" />
            </IconButton>
        </div>
    );
}

export default PaginationControls