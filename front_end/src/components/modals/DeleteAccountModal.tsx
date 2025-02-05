import React from "react";
import { IModalProps } from "../../utils/types";
import {
    Button,
    Dialog,
    DialogBody,
    DialogFooter,
    DialogHeader,
    Spinner,
} from "@material-tailwind/react";
import { IoMdClose } from "react-icons/io";
const DeleteAccountModal: React.FC<IModalProps> = ({
    isOpen,
    setIsOpen,
    isLoading,
    onDelete,
}) => {
    const closeModal = () => {
        setIsOpen(false);
    };

    const openModal = () => {
        setIsOpen(true);
    };

    return (
        <Dialog open={isOpen} handler={openModal} size="md">
            <DialogHeader className="flex justify-between">
                Delete Account
                <IoMdClose
                    color="gray"
                    className="cursor-pointer rounded-md duration-150s hover:bg-gray-300"
                    onClick={closeModal}
                />
            </DialogHeader>
            <DialogBody divider className="font-normal space-y-4">
                Deleting your account will permanently remove:
                <ul className="list-disc pl-6 pt-2 space-y-1">
                    <li>
                        All clinical trial data associated with your account
                    </li>
                    <li>Your custom cost and risk configurations</li>
                    <li>Any uploaded documents</li>
                </ul>
                <p>
                    This action is irreversible. If you proceed, you will lose
                    access to all your data and configurations.
                </p>
            </DialogBody>
            <DialogFooter className="flex gap-3">
                <Button
                    disabled={isLoading}
                    variant="outlined"
                    color="teal"
                    className="focus:outline-none focus:ring-0 "
                    onClick={closeModal}
                >
                    <span>Cancel</span>
                </Button>

                <Button
                    disabled={isLoading}
                    variant="filled"
                    onClick={() => {
                        if (onDelete) {
                            onDelete();
                            closeModal();
                        }
                    }}
                    className=" focus:outline-none focus:ring-0 bg-red-700"
                >
                    <span>
                        {isLoading ? (
                            <Spinner color="red" className="h-5 w-5" />
                        ) : (
                            "Delete"
                        )}
                    </span>
                </Button>
            </DialogFooter>
        </Dialog>
    );
};

export default DeleteAccountModal;
