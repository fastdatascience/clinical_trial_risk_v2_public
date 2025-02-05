import React, { useEffect, useState } from "react";
import {
    Button,
    Dialog,
    DialogHeader,
    DialogBody,
    IconButton,
} from "@material-tailwind/react";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import { IPdfImage } from "../../utils/types";

export function EnlargeViewModal({
    open,
    setOpen,
    selectedImage = 0,
    imageSrc,
}: Readonly<{
    open: boolean;
    setOpen: React.Dispatch<React.SetStateAction<boolean>>;
    selectedImage: number;
    imageSrc: IPdfImage[] | [];
}>) {
    const [currentImage, setCurrentImage] = useState<number>(selectedImage);

    const handleOpen = () => setOpen((cur) => !cur);

    const handleNext = () => {
        if (currentImage < imageSrc.length - 1) {
            setCurrentImage((prevIndex) => prevIndex + 1);
        }
    };

    const handlePrev = () => {
        if (currentImage > 0) {
            setCurrentImage((prevIndex) => prevIndex - 1);
        }
    };

    useEffect(() => {
        if (open) {
            setCurrentImage(selectedImage);

            // Define the keyboard handler
            const handleKeyDown = (event: KeyboardEvent) => {
                if (event.key === "ArrowRight") {
                    handleNext();
                } else if (event.key === "ArrowLeft") {
                    handlePrev();
                }
            };

            window.addEventListener("keydown", handleKeyDown);

            return () => {
                window.removeEventListener("keydown", handleKeyDown);
            };
        }
    }, [open, selectedImage]);

    return (
        <Dialog size="xl" open={open} handler={handleOpen}>
            <DialogHeader className="justify-end">
                <div className="flex items-center gap-2">
                    <Button color="teal" size="sm" onClick={handleOpen}>
                        Close
                    </Button>
                </div>
            </DialogHeader>

            {/* instead of  imgSrc this should accept array */}
            <DialogBody className="md:h-[48rem] flex  justify-between items-center  bg-gray-300  rounded-lg overflow-y-scroll">
                <IconButton
                    size={"lg"}
                    color="white"
                    title="Left"
                    onClick={handlePrev}
                    disabled={currentImage === 0}
                >
                    <FaArrowLeft />
                </IconButton>

                {imageSrc.length > 0 && (
                    <img
                        alt="pdf"
                        className="h-full rounded-lg border border-green_primary object-contain object-center"
                        src={imageSrc[currentImage]?.image}
                    />
                )}

                <IconButton
                    size={"lg"}
                    color="white"
                    title="Left"
                    onClick={handleNext}
                    disabled={currentImage === imageSrc.length - 1}
                >
                    <FaArrowRight />
                </IconButton>
            </DialogBody>
        </Dialog>
    );
}
