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
const WeightProfileDeleteModal: React.FC<IModalProps> = ({
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
                Are you sure?
                <IoMdClose
                    color="gray"
                    className="cursor-pointer rounded-md duration-150s hover:bg-gray-300"
                    onClick={closeModal}
                />
            </DialogHeader>
            <DialogBody className="font-normal">
                Are you sure you want to delete this weight profile? This action
                cannot be undone.
            </DialogBody>
            <DialogFooter>
                <Button
                    disabled={isLoading}
                    variant="outlined"
                    color="red"
                    onClick={() => {
                        if (onDelete) {
                            onDelete();
                            closeModal();
                        }
                    }}
                    className="mr-1 focus:outline-none focus:ring-0"
                >
                    <span>
                        {isLoading ? (
                            <Spinner color="red" className="h-5 w-5" />
                        ) : (
                            "Yes"
                        )}
                    </span>
                </Button>
                <Button
                    disabled={isLoading}
                    variant="gradient"
                    color="green"
                    className=" focus:outline-none focus:ring-0"
                    onClick={closeModal}
                >
                    <span>No</span>
                </Button>
            </DialogFooter>
        </Dialog>
    );
};

export default WeightProfileDeleteModal;
