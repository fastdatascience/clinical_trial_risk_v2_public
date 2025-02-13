import { Dialog, Transition } from "@headlessui/react";
import React, { Fragment, useState } from "react";
import { useAtom } from "jotai";
import { IModalProps, OtpSendTo } from "../../utils/types";
import { Button, Spinner } from "@material-tailwind/react";
import Countdown from "../common/Countdown";
import OtpInput from "../common/OTPInput";
import { userAtom } from "../../lib/atoms";
import { resendOTP, verifyEmail } from "../../utils/services";
import { useNavigate } from "react-router-dom";
import { AxiosError, AxiosResponse } from "axios";

const EmailVerification: React.FC<IModalProps> = ({ isOpen, setIsOpen }) => {
    const navigate = useNavigate();
    const [user] = useAtom(userAtom);
    const [isLoading, setIsLoading] = useState(false);
    const [otp, setOtp] = useState<string>("");
    const [errorText, setErrorText] = useState<string>("");
    const { email } = user;

    const onChange = (value: string) => {
        setOtp(value);
    };

    const closeModal = () => {
        setIsOpen(false);
    };

    const openModal = () => {
        setIsOpen(true);
    };

    const handleEmailVerification = async () => {
        const data = {
            payload: email,
            otp,
            type: OtpSendTo.EMAIL,
        };
        try {
            setIsLoading(true);
            const res = (await verifyEmail(data)) as AxiosResponse;
            if (res?.status === 200) {
                if (res?.data?.data?.is_email_verified) {
                    setIsLoading(false);
                    navigate("/login");
                    closeModal();
                }
            }
        } catch (error) {
            if (error instanceof AxiosError) {
                console.error("Error verifying OTP", error);
                setErrorText(error.response?.data?.error);
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleResendOTP = async () => {
        const data = {
            payload: email,
            type: OtpSendTo.EMAIL,
        };
        try {
            (await resendOTP(data)) as AxiosResponse;
        } catch (error) {
            console.error(error);
        }
    };
    const maskedEmail = email?.replace(/^(.{2})[^@]+/, "$1***");

    return (
        <Transition appear show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-10" onClose={openModal}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-black bg-opacity-25" />
                </Transition.Child>
                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 scale-95"
                            enterTo="opacity-100 scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 scale-100"
                            leaveTo="opacity-0 scale-95"
                        >
                            <Dialog.Panel className="w-full max-w-md transform overflow-hidden bg-white border shadow-2xl rounded-lg transition-all">
                                <div className="flex flex-col">
                                    <div className="flex justify-between items-start px-5">
                                        <div className="text-left my-5">
                                            <h3 className="font-semibold text-2xl text-text_primary mb-1 ">
                                                Please check your E-Mail
                                            </h3>
                                            <h3 className="font-normal text-sm text-text_secondary">
                                                we have sent 6 digit code to{" "}
                                                {maskedEmail}
                                            </h3>
                                        </div>
                                    </div>

                                    {/* Modal Body */}
                                    <div className="flex flex-col justify-between items-start py-3 px-3 gap-6">
                                        <Countdown />
                                        <h3 className="font-semibold text-3xl text-BLACK flex flex-wrap">
                                            Enter the 6 Digit Code
                                        </h3>
                                        <div className="flex flex-col space-y-2 w-full justify-between">
                                            <div className="flex w-full justify-between">
                                                <OtpInput
                                                    isError={!!errorText}
                                                    value={otp}
                                                    valueLength={6}
                                                    onChange={onChange}
                                                />
                                            </div>
                                            {errorText && (
                                                <small className="text-red-500">
                                                    {errorText}
                                                </small>
                                            )}
                                        </div>

                                        <Button
                                            disabled={isLoading}
                                            className="mt-6 bg-green_primary rounded-full flex justify-center items-center py-4 font-semibold"
                                            fullWidth
                                            onClick={handleEmailVerification}
                                        >
                                            {isLoading ? (
                                                <Spinner
                                                    color="green"
                                                    className="h-6 w-6"
                                                />
                                            ) : (
                                                "Submit"
                                            )}
                                        </Button>
                                        <div className="w-full flex flex-col items-center">
                                            <div className="text-sm ">
                                                <p className="text-text_secondary">
                                                    You didnt get a code?{" "}
                                                    <span
                                                        role="button"
                                                        className="text-green_primary cursor-pointer font-semibold"
                                                        onClick={
                                                            handleResendOTP
                                                        }
                                                    >
                                                        {" "}
                                                        Resend code{" "}
                                                    </span>
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
};

export default EmailVerification;
