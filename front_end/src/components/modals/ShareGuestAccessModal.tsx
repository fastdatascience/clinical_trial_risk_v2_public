import React from "react";
import { IModalProps } from "../../utils/types";
import {
    Button,
    Dialog,
    DialogBody,
    DialogHeader,
    Typography,
} from "@material-tailwind/react";
import { TextInput } from "../common";
import { SHARABLE_ACCESS_LINK } from "../../utils/constants";
import { useCopyToClipboard } from "../../hooks/useCopyToClipboard";
import { FaCheck, FaCopy } from "react-icons/fa6";

const ShareGuestAccessModal: React.FC<IModalProps> = ({
    isOpen,
    setIsOpen,
}) => {
    const [copyToClipboard, { copied }] = useCopyToClipboard();
    return (
        <Dialog open={isOpen} handler={setIsOpen}>
            <DialogHeader className="flex flex-col justify-start items-start space-y-3">
                <Typography variant="h4">Share This Tool Instantly.</Typography>
                <Typography variant="paragraph" color="current">
                    Let others try Clinical Trials Risk Tool right away - no
                    sign-up needed!
                </Typography>
            </DialogHeader>
            <DialogBody>
                <div className="flex items-center space-x-2">
                    <div className=" flex justify-between  items-center w-full gap-3">
                        <div className="w-3/5">
                            <TextInput
                                initialValue={SHARABLE_ACCESS_LINK}
                                readonly
                                label="Copy link to share"
                            />
                        </div>
                        <div className="w-2/5">
                            <Button
                                size="md"
                                onClick={() => {
                                    copyToClipboard(SHARABLE_ACCESS_LINK);
                                }}
                                className="flex items-center gap-2 bg-text_primary"
                            >
                                {copied ? (
                                    <>
                                        <FaCheck className="h-4 w-4 text-white" />
                                        Copied
                                    </>
                                ) : (
                                    <>
                                        <FaCopy className="h-4 w-4 text-white" />
                                        Copy
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>

                <div className="mt-4 space-y-2  text-gray-900">
                    <p className="text-sm flex items-center">
                        <span className="text-green-500 mr-2">✓</span> Instant
                        access: No sign-up required
                    </p>
                    <p className="text-sm flex items-center">
                        <span className="text-green-500 mr-2">✓</span> Easy to
                        share: Just send the link
                    </p>
                    <p className="text-sm flex items-center">
                        <span className="text-green-500 mr-2">✓</span> Perfect
                        for quick demos or collaborations
                    </p>
                </div>
                <div className="mt-6 text-sm text-gray-900">
                    Anyone with this link can access the tool. Share
                    responsibly!
                </div>
            </DialogBody>
        </Dialog>
    );
};

export default ShareGuestAccessModal;
