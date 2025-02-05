import { useState, useEffect } from "react";
import avatar from "../../../../assets/avatar.jpeg";
import FormData from "form-data";
import { useUploady, useBatchStartListener } from "@rpldy/uploady";

import { Button, Spinner, Typography } from "@material-tailwind/react";
import { useAtom } from "jotai";

import { AxiosResponse } from "axios";
import {
    deleteUserAccount,
    updateUserSettings,
} from "../../../../utils/services";
import { userAuthProfileAtom, userProfileAtom } from "../../../../lib/atoms";
import { UpdatedUser, User } from "../../../../utils/types";
import { USER_STORAGE_KEY } from "../../../../utils/network";
import EventEmitter from "../../../../utils/EventEmitter";
import UserSubscriptionCard from "../../../Subscription/UserSubscriptionCard";
import DeleteAccountModal from "../../../modals/DeleteAccountModal";
import { useAuth } from "../../../../hooks/useAuth";

const MyAccount: React.FC = () => {
    const { logout } = useAuth();
    const [userAuthAcount] = useAtom(userAuthProfileAtom);
    const [userProfile] = useAtom(userProfileAtom);
    const [user, setUser] = useState<User>();
    const [displaySave, setDisplaySave] = useState<boolean>(false);
    const [updatedUser, setUpdatedUser] = useState<UpdatedUser>({
        first_name: "",
        last_name: "",
    });

    const uploady = useUploady();
    const [userUpdatedImage, setUserUpdatedImage] = useState<boolean>(false);
    const [selectedImage, setSelectedImage] = useState<string>();
    const [selectedFile, setSelectedFile] = useState<Blob>();
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [showDeleteModal, setShowDeleteModal] = useState<boolean>(false);
    const [isDeleting, setIsDeleting] = useState<boolean>(false);

    const userInfo = userAuthAcount || userProfile?.user;

    useBatchStartListener((batch) => {
        const file = batch.items[0].file as unknown as Blob; // Get the selected file
        if (file) {
            setSelectedFile(file);
            setDisplaySave(true);
            const imageUrl = URL.createObjectURL(file);
            setSelectedImage(imageUrl);
        }
        setUserUpdatedImage(!userUpdatedImage);
    });

    useEffect(() => {
        getUser();
    }, []);

    const getUser = () => {
        if (userInfo) {
            setUser(userInfo);
            setUpdatedUser({
                first_name: userInfo?.given_name
                    ? userInfo?.given_name
                    : userInfo?.first_name,
                last_name: userInfo?.family_name
                    ? userInfo?.family_name
                    : userInfo?.last_name,
            });
        }
    };

    const updateUser = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.name === "first_name") {
            if (e.target.value === user?.first_name) {
                !userUpdatedImage && setDisplaySave(false);
            } else {
                setDisplaySave(true);
            }
        } else {
            if (e.target.value === user?.last_name) {
                !userUpdatedImage && setDisplaySave(false);
            } else {
                setDisplaySave(true);
            }
        }
        setUpdatedUser({
            ...updatedUser,
            [e.target.name]: e.target.value,
        });
    };

    const saveChanges = async () => {
        const payload = new FormData();
        const obj: { [key: string]: string } = {};

        if (user?.first_name !== updatedUser.first_name) {
            obj["first_name"] = updatedUser.first_name;
        }

        if (user?.last_name !== updatedUser.last_name) {
            obj["last_name"] = updatedUser.last_name;
        }

        if (userUpdatedImage === true) {
            payload.append("profile_picture", selectedFile);
        }

        payload.append("user", JSON.stringify(obj));

        try {
            setIsLoading(true);
            const response = (await updateUserSettings(
                payload
            )) as AxiosResponse;
            const objectToUpdate = localStorage.getItem(USER_STORAGE_KEY);
            if (objectToUpdate) {
                const parsedObj = JSON.parse(objectToUpdate);
                parsedObj.user = response.data.data.user;
                localStorage.setItem(
                    USER_STORAGE_KEY,
                    JSON.stringify(parsedObj)
                );
                setIsLoading(false);
                EventEmitter.emit("NewLog", {
                    text: "Reload",
                });
            }
        } catch (err) {
            console.error("An Error Occurred While Saving Changes", err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteUserAccount = async () => {
        try {
            setIsDeleting(true);
            const response = await deleteUserAccount();
            if (response.status === 204) {
                logout();
            }
            return;
        } catch (error) {
            console.error("An Error Occurred while deleting account", error);
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <>
            <div className="p-10 flex flex-col flex-wrap space-y-6 w-full">
                <div>
                    <h3 className="font-poppins text-2xl font-semibold">
                        Account
                    </h3>
                </div>
                <div className="flex justify-between items-center flex-wrap">
                    {/* Profile picture */}
                    <div className="flex items-center space-x-3">
                        <button
                            className="cursor-pointer overflow-hidden rounded-full h-20 w-20"
                            onClick={() => uploady.showFileUpload()}
                        >
                            {userInfo?.picture ? (
                                <img
                                    src={userInfo?.picture || avatar}
                                    className="object-cover h-full w-full"
                                    alt={"User"}
                                />
                            ) : (
                                <img
                                    src={
                                        userUpdatedImage
                                            ? selectedImage
                                            : userProfile?.user?.profile_picture
                                            ? `https://d1zouhzy7fucw3.cloudfront.net/images/${userProfile?.user?.profile_picture}`
                                            : avatar
                                    }
                                    className="object-cover h-full w-full"
                                    alt={"User"}
                                />
                            )}
                        </button>
                        <div>
                            <h3 className="font-poppins text-base font-semibold">
                                {userInfo?.name ??
                                    userProfile?.user?.first_name +
                                        " " +
                                        userProfile?.user?.last_name}
                            </h3>
                        </div>
                    </div>
                    <div>
                        <Button
                            className="rounded-full bg-green_primary"
                            onClick={() => uploady.showFileUpload()}
                        >
                            <h3 className="text-white font-poppins cursor-pointer capitalize">
                                Upload Your Avatar
                            </h3>
                        </Button>
                    </div>
                </div>

                <div className="flex flex-col space-y-5">
                    <h3 className="font-poppins text-2xl font-semibold">
                        General
                    </h3>
                    <div className="flex flex-col space-y-5 flex-wrap">
                        <h3 className="text-sm font-poppins font-semibold">
                            Email
                        </h3>
                        <input
                            type="email"
                            name="email"
                            value={`${
                                userInfo?.email ?? userProfile?.user?.email
                            }`}
                            className="rounded-lg p-1 outline-none"
                            readOnly
                        />
                        <h3 className="font-poppins inline text-sm">
                            {"Please"}
                            <h3 className="text-emerald-400 inline">
                                {"contact the administrator"}
                            </h3>
                            {"to change your email"}
                        </h3>
                    </div>
                    <div className="flex flex-col space-y-5 flex-wrap">
                        <h3 className="text-sm font-poppins font-semibold">
                            First Name
                        </h3>
                        <input
                            type="text"
                            name="first_name"
                            value={`${
                                userInfo?.given_name
                                    ? userInfo?.given_name
                                    : userProfile?.user?.first_name
                            }`}
                            className="rounded-lg p-1 outline-none"
                            onChange={(e) => updateUser(e)}
                        />
                    </div>
                    <div className="flex flex-col space-y-5 flex-wrap">
                        <h3 className="text-sm font-poppins font-semibold">
                            Last Name
                        </h3>
                        <input
                            type="text"
                            name="last_name"
                            value={`${
                                userInfo?.family_name
                                    ? userInfo?.family_name
                                    : userProfile?.user?.last_name
                            }`}
                            className="rounded-lg p-1 outline-none"
                            onChange={(e) => updateUser(e)}
                        />
                    </div>
                    <div className="flex flex-col space-y-5 flex-wrap">
                        <h3 className="text-sm font-poppins font-semibold">
                            Phone Number
                        </h3>
                        <input
                            type="tel"
                            name="phone_number"
                            value={`${
                                userInfo?.phone_number ??
                                userProfile?.user?.phone_number ??
                                "No phone number added"
                            }`}
                            placeholder="Phone number"
                            className="rounded-lg p-1 outline-none"
                            readOnly
                        />
                    </div>
                    {displaySave && (
                        <Button
                            className="bg-[#57ca96] p-2 flex justify-center items-center rounded-lg cursor-pointer"
                            onClick={saveChanges}
                        >
                            <h3 className="text-sm text-center text-white font-poppins">
                                {isLoading ? (
                                    <Spinner color="light-green" />
                                ) : (
                                    "Save Changes"
                                )}
                            </h3>
                        </Button>
                    )}
                </div>
                <hr />
                <div className="flex flex-col space-y-5">
                    <div className="flex justify-between font-poppins">
                        <h3 className="text-2xl font-semibold">Subscription</h3>
                    </div>

                    <UserSubscriptionCard />
                </div>

                <hr />
                <div className="flex flex-col space-y-5">
                    <div className="flex flex-col  justify-between font-poppins">
                        <h3 className="text-2xl font-semibold">
                            Account Deletion
                        </h3>
                        <p className=" text-red-700 font-bold mt-3">Warning!</p>
                        <Typography variant="paragraph" color="gray">
                            Deleting your account will permanently delete all
                            your run results and documents. This action can't be
                            undone.
                        </Typography>
                    </div>
                    <div>
                        <Button
                            variant="outlined"
                            className="border-red-700 text-red-700"
                            onClick={() => setShowDeleteModal((prev) => !prev)}
                        >
                            Delete My account
                        </Button>
                    </div>
                </div>
            </div>

            <DeleteAccountModal
                isOpen={showDeleteModal}
                isLoading={isDeleting}
                setIsOpen={setShowDeleteModal}
                onDelete={handleDeleteUserAccount}
            />
        </>
    );
};

export default MyAccount;
