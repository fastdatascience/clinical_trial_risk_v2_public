import { Card, Button, Typography, Spinner } from "@material-tailwind/react";
import { useState } from "react";
import { TextInput } from "../common";
import { resetPassword } from "../../utils/services";
import { AxiosResponse } from "axios";
import { EMAIL_REGEX } from "../../utils/constants";

const ForgotPassword: React.FC = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [emailSent, setEmailSent] = useState<boolean>(false);
    const [loginInfo, setLoginInfo] = useState({
        email: "",
    });
    const [error, setError] = useState<boolean>();
    const [errorMessage, setErrorMessage] = useState<string>("");
    const { email } = loginInfo;

    const handleChange = (e: React.FormEvent<HTMLInputElement>) => {
        const { name, value } = e.target as HTMLInputElement;
        setLoginInfo({
            ...loginInfo,
            [name]: value,
        });
    };

    /* I guess for security purpose this API returns 
       success for the emails that doesn't exist, but 
       email is not sent to those emails. But on F.E 
       it will show success 
    */
    const sendResetPasswordEmail = async () => {
        if (!EMAIL_REGEX.test(email)) {
            setError(true);
            setErrorMessage("Email must be a valid email");
            return;
        }
        try {
            setIsLoading(true);
            const response = (await resetPassword(email)) as AxiosResponse;
            if (response?.status === 200) {
                setEmailSent(true);
            }
        } catch (error) {
            console.error("Failed to send email", error);
            setError(true);
            setErrorMessage("Something went wrong, Please try again!");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {emailSent ? (
                <Card className="bg-white p-7 my-10">
                    <Typography
                        color="gray"
                        className="mt-1 text-center text-lg font-medium text-text_secondary"
                    >
                        An email has been sent to your inbox. <br /> Please
                        click the link once you receive it
                    </Typography>
                </Card>
            ) : (
                <Card className="bg-white p-7 my-10">
                    <Typography
                        variant="h3"
                        className="text-text_primary text-center"
                    >
                        Email Address
                    </Typography>
                    <Typography
                        color="gray"
                        className="mt-1 text-center text-sm font-normal text-text_secondary"
                    >
                        Please enter the email address associated with your
                        account.
                    </Typography>

                    <div className="mt-5 mb-2 w-80 max-w-screen-lg sm:w-96">
                        <div className="mb-4 flex flex-col gap-5">
                            <TextInput
                                name={"email"}
                                inputType={"email"}
                                label="Email"
                                initialValue={email}
                                handleChange={handleChange}
                                error={error}
                                errorMessage={errorMessage}
                                onBlur={() => {
                                    setError(false);
                                    setErrorMessage("");
                                }}
                            />
                        </div>

                        <Button
                            disabled={!email || isLoading}
                            className="mt-6 w-full bg-green_primary rounded-full flex justify-center items-center "
                            onClick={sendResetPasswordEmail}
                        >
                            {isLoading ? (
                                <Spinner color="green" className="h-6 w-6" />
                            ) : (
                                "Recover Password"
                            )}
                        </Button>
                    </div>
                </Card>
            )}
        </>
    );
};

export default ForgotPassword;
