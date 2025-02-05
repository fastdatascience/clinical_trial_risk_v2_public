import React from "react"
import { IModalProps } from "../../utils/types"
import { Button, Dialog, DialogBody, DialogFooter, DialogHeader, Spinner } from "@material-tailwind/react";
import { IoMdClose } from "react-icons/io";
const FileDeleteModal: React.FC<IModalProps> = ({ isOpen, setIsOpen, isLoading, onDelete }) => {
    const closeModal = () => {
        setIsOpen(false);
    };

    const openModal = () => {
        setIsOpen(true);
    };


    return (
        <Dialog open={isOpen} handler={openModal} size="xs">
            <DialogHeader className="flex justify-between">
                Are you sure?
                <IoMdClose color="gray" className="cursor-pointer rounded-md duration-150s hover:bg-gray-300" onClick={closeModal} />
            </DialogHeader>
            <DialogBody>
                Are you sure you want to delete this file?
            </DialogBody>
            <DialogFooter>
                <Button
                    variant="outlined"
                    color="red"
                    onClick={onDelete}
                    className="mr-1 focus:outline-none focus:ring-0"
                >
                    <span>
                        {isLoading ? (<Spinner color="red" className="h-5 w-5" />) : "Yes"}
                    </span>
                </Button>
                <Button variant="gradient" color="green" className=" focus:outline-none focus:ring-0" onClick={closeModal}>
                    <span>No</span>
                </Button>
            </DialogFooter>
        </Dialog>
    );
}

export default FileDeleteModal
