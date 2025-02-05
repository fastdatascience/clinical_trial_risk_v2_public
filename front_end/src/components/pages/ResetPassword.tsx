import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button, Card, Spinner, Typography } from "@material-tailwind/react";
import { PasswordInput } from "../common";
import { PASSWORD_REGEX } from "../../utils/constants";
import { recoverPassword } from "../../utils/services";
import { AxiosResponse } from "axios";

const ResetPassword: React.FC = () => {
    const [token, setToken] = useState<string | undefined>("");
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [isPasswordUpdated, setIsPasswordUpdated] = useState<boolean>(false);
    const [error, setError] = useState<boolean>();
    const [errorMessage, setErrorMessage] = useState<string>("");

    const [updatePassword, setUpdatePassword] = useState({
        newPassword: "",
        confirmPassword: "",
    });

    const { newPassword, confirmPassword } = updatePassword;
    const params = useParams();
    const navigate = useNavigate();

    useEffect(() => {
        const extractTokenFromUrl = () => {
            const token = params.token;
            setToken(token ?? "");
        };
        extractTokenFromUrl();
    }, [params]);

    const handleChange = (e: React.FormEvent<HTMLInputElement>) => {
        const { name, value } = e.target as HTMLInputElement;
        setUpdatePassword({
            ...updatePassword,
            [name]: value,
        });
    };

    const handleUpdatePassword = async () => {
        if (!token) return;
        try {
            setIsLoading(true);
            const res = (await recoverPassword({
                otp: token,
                password: newPassword,
            })) as AxiosResponse;

            if (res.status === 200) {
                setIsPasswordUpdated(true);
            }
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePasswordReset = () => {
        if (!token?.length) return;
        if (!newPassword || !confirmPassword) {
            setError(true);
            setErrorMessage("These fields are Required.");
        } else if (!PASSWORD_REGEX.test(newPassword)) {
            setError(true);
            setErrorMessage(
                "Use at least 8 characters, one uppercase, one lowercase, one number and one special character and max 20 characters."
            );
        } else if (newPassword !== confirmPassword) {
            setError(true);
            setErrorMessage("Passwords don't match.");
        } else {
            // Password is valid, proceed with password reset api call
            handleUpdatePassword();
        }
    };

    return (
        <Card className="bg-white p-7 my-10">
            <Typography variant="h3" className="text-text_primary text-center">
                {isPasswordUpdated ? "Password Updated!" : "Enter New Password"}
            </Typography>
            {isPasswordUpdated ? (
                <Typography
                    color="gray"
                    className="mt-1 text-center text-sm font-normal text-text_secondary"
                >
                    Your password has been updated successfully
                </Typography>
            ) : (
                <Typography
                    color="gray"
                    className="mt-1 text-center text-sm font-normal text-text_secondary"
                >
                    Your new password must be different <br /> from previously
                    used passwords
                </Typography>
            )}

            <div className="mt-5 mb-2 w-80 max-w-screen-lg sm:w-96">
                {!isPasswordUpdated && (
                    <div className="mb-4 flex flex-col gap-5">
                        <PasswordInput
                            name="newPassword"
                            label="New Password"
                            initialValue={newPassword}
                            handleChange={handleChange}
                            error={error}
                            errorMessage={errorMessage}
                        />
                        <PasswordInput
                            name="confirmPassword"
                            label="Password"
                            initialValue={confirmPassword}
                            handleChange={handleChange}
                            error={error}
                            errorMessage={errorMessage}
                        />
                    </div>
                )}

                {isPasswordUpdated ? (
                    <Button
                        className="mt-6 bg-green_primary rounded-full flex justify-center items-center "
                        fullWidth
                        onClick={() => navigate("/")}
                        disabled={!newPassword || !confirmPassword}
                    >
                        {isLoading ? (
                            <Spinner color="green" className="h-6 w-6" />
                        ) : (
                            "Back to Login"
                        )}
                    </Button>
                ) : (
                    <Button
                        className="mt-6 bg-green_primary rounded-full flex justify-center items-center "
                        fullWidth
                        onClick={handlePasswordReset}
                        disabled={!newPassword || !confirmPassword}
                    >
                        {isLoading ? (
                            <Spinner color="green" className="h-6 w-6" />
                        ) : (
                            "Update Password"
                        )}
                    </Button>
                )}
            </div>
        </Card>
    );
};

export default ResetPassword;
