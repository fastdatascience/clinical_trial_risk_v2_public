import {
    Card,
    Button,
    Typography,
    Spinner,
    CardBody,
    CardFooter,
    Checkbox,
} from "@material-tailwind/react";
import jsonp from "jsonp";
import { useEffect, useState } from "react";
import {
    userAccessTokenAtom,
    userAtom,
    userAuthProfileAtom,
} from "../../lib/atoms";
import { useAtom } from "jotai";
import { Link, useSearchParams } from "react-router-dom";

import { getUserGoogleProfile, signup } from "../../utils/services";
import { EMAIL_REGEX, FormErrors } from "../../utils/constants";

import { TextInput, PasswordInput, PhoneNumberInput } from "../common/index";
import EmailVerification from "../modals/EmailVerification";
import { validateFormData } from "../../utils/utils";
import GoogleAuthButton from "../common/GoogleAuthButton";
import { useAuth } from "../../hooks/useAuth";
import { TokenResponse, useGoogleLogin } from "@react-oauth/google";
import { AxiosError } from "axios";

const SignUp: React.FC = () => {
    const [auth, setAuth] = useState<TokenResponse | null>(null);

    const { setIsAuthenticated } = useAuth();
    const [, setUserAccessToken] = useAtom(userAccessTokenAtom);
    const [, setGoogleUser] = useAtom(userAuthProfileAtom);

    const loginWithGoogle = useGoogleLogin({
        onSuccess: (codeResponse) => setAuth(codeResponse),
        onError: (error) => console.log("Login Failed:", error),
    });
    const [isLoading, setIsLoading] = useState<boolean>(false);

    const [openEmailVerification, setOpenEmailVerification] =
        useState<boolean>(false);
    const [errors, setErrors] = useState<FormErrors | undefined>({});
    const [user, setUser] = useAtom(userAtom);
    const [searchParams] = useSearchParams();
    const currentParam = Object.fromEntries([...searchParams]);

    const {
        first_name,
        last_name,
        email,
        password,
        phone_number,
        terms_and_privacy_accepted,
        subscribe_to_newsletter,
    } = user;

    const handleSubscribeToMailChimp = async () => {
        const tags = 14571148;
        jsonp(
            `${
                import.meta.env.VITE_MAILCHIMP_URL
            }&EMAIL=${email}&tags=${tags}&gdpr[63078]=Y&b_acc84a3f93f62dda11aa38a8b_8995bdc735`,
            // Not sure why this "c" is for
            { param: "c" },
            (_, data) => {
                const { result } = data;
                if (result !== "success") return;
            }
        );
    };

    const handleSignUp = async () => {
        // Client-side validations
        const clientValidationErrors = validateFormData({
            first_name,
            last_name,
            email,
            password,
            phone_number,
            terms_and_privacy_accepted,
        });
        setErrors((prevErrors) => {
            return { ...prevErrors, ...clientValidationErrors };
        });

        // If client side errors, do not proceed with api call
        if (Object.keys(clientValidationErrors).length > 0) {
            return;
        }
        try {
            setIsLoading(true);
            if (subscribe_to_newsletter) {
                handleSubscribeToMailChimp();
            }
            // Api call
            await signup(user);
            setOpenEmailVerification(true);
        } catch (error) {
            // Server-side validations
            let serverValidationErrors = {};
            // Formatted errors from Server-side
            if (error instanceof AxiosError) {
                const { response, status } = error;
                const serverErrors = response?.data?.errors || [];

                // Because 400 is only for email already exist
                if (status === 400) {
                    setErrors({ ...errors, emailError: response?.data?.error });
                }
                // Because 500 shows up for incorrect formate and SMTP error
                if (status === 500) {
                    if (response?.data?.error?.includes("Password")) {
                        setErrors({
                            ...errors,
                            passwordError: response?.data?.error,
                        });
                    }
                    setErrors({
                        ...errors,
                        emailError:
                            "Failed to send OTP. Please check if the address is correct or active.",
                    });
                }
                if (serverErrors?.length)
                    // if array of errors exist then return formatted error messages
                    serverValidationErrors = validateFormData({}, serverErrors);
                setErrors((prevErrors) => {
                    return { ...prevErrors, ...serverValidationErrors };
                });
            }
        } finally {
            setIsLoading(false);
        }
    };

    const handleChange = (e: React.FormEvent<HTMLInputElement>) => {
        const { name, type, checked, value } = e.target as HTMLInputElement;
        setUser({
            ...user,
            [name]: type === "checkbox" ? checked : value,
        });
    };

    useEffect(() => {
        const initializeUser = async () => {
            if (auth && auth?.access_token) {
                setUserAccessToken(auth.access_token);

                const userInfo = await getUserGoogleProfile(auth.access_token);

                if (userInfo) {
                    setGoogleUser(userInfo);
                    setIsAuthenticated(true);
                    window.location.href = "dashboard";
                } else {
                    console.log("Failed to fetch user information.");
                }
            } else {
                console.log("Empty user");
            }
        };

        initializeUser();
    }, [auth]);

    return (
        <>
            <>
                {Object.keys(currentParam).length !== 0 ? (
                    // TODO: refactor this code to be modular
                    <div className="flex lg:flex-row flex-col my-10">
                        <div className="lg:bg-gradient-to-l from-[#0c4a6e] to-[#065984]  lg:shadow-md rounded-l-lg lg:flex lg:justify-center lg:items-center p-5 ">
                            <Card className="mt-6 lg:w-96 border-t-4 border-green_primary">
                                <CardBody>
                                    <Typography>
                                        {currentParam?.description}
                                    </Typography>
                                    <Typography
                                        variant="h5"
                                        color="blue-gray"
                                        className="mb-2"
                                    >
                                        {currentParam?.name}
                                    </Typography>
                                </CardBody>
                                <CardFooter className="pt-0 flex justify-end">
                                    <Typography>
                                        {currentParam?.duration}
                                    </Typography>
                                </CardFooter>
                            </Card>
                        </div>
                        <div>
                            <Card className="bg-white p-5">
                                <Typography
                                    variant="h3"
                                    className="text-text_primary text-center"
                                >
                                    Sign Up
                                </Typography>
                                <Typography
                                    variant="h6"
                                    color="gray"
                                    className="mt-1 text-center font-normal text-text_secondary"
                                >
                                    Please enter your details.
                                </Typography>
                                <div className="mt-5 mb-2 w-80 max-w-screen-lg sm:w-96">
                                    <div className="flex flex-col gap-6">
                                        <TextInput
                                            name={"first_name"}
                                            inputType={"text"}
                                            label={"First Name"}
                                            initialValue={first_name}
                                            handleChange={handleChange}
                                            errorMessage={
                                                errors?.first_nameError
                                            }
                                        />
                                        <TextInput
                                            name={"last_name"}
                                            inputType={"text"}
                                            label={"Last Name"}
                                            initialValue={last_name}
                                            handleChange={handleChange}
                                            errorMessage={
                                                errors?.last_nameError
                                            }
                                        />

                                        <TextInput
                                            name={"phoneNumber"}
                                            inputType={"tel"}
                                            label={"Phone Number"}
                                            initialValue={phone_number}
                                            handleChange={handleChange}
                                            errorMessage={
                                                errors?.phone_numberError
                                            }
                                        />

                                        <TextInput
                                            name={"email"}
                                            inputType={"email"}
                                            label="Email"
                                            initialValue={email}
                                            handleChange={handleChange}
                                            errorMessage={
                                                errors?.emailError ??
                                                errors?.apiError
                                            }
                                        />
                                        <PasswordInput
                                            name="password"
                                            label="Password"
                                            initialValue={password}
                                            handleChange={handleChange}
                                            errorMessage={errors?.passwordError}
                                        />
                                    </div>
                                    <Button
                                        className="mt-6 bg-green_primary rounded-full flex justify-center items-center py-4 font-semibold"
                                        fullWidth
                                        onClick={handleSignUp}
                                    >
                                        {isLoading ? (
                                            <Spinner
                                                color="green"
                                                className="h-6 w-6"
                                            />
                                        ) : (
                                            "Register"
                                        )}
                                    </Button>
                                    <Typography
                                        color="gray"
                                        className="mt-4 text-sm text-center font-normal text-text_secondary"
                                    >
                                        Already have an account?{" "}
                                        <span className="font-medium text-green_primary text-sm">
                                            <Link to={"/login"}>Sign In</Link>
                                        </span>
                                    </Typography>
                                </div>
                            </Card>
                        </div>
                    </div>
                ) : (
                    <Card className="bg-white p-5 my-10 ">
                        <Typography
                            variant="h3"
                            className="text-text_primary text-center"
                        >
                            Sign Up
                        </Typography>
                        <Typography
                            variant="h6"
                            color="gray"
                            className="mt-1 text-center font-normal text-text_secondary"
                        >
                            Please enter your details.
                        </Typography>
                        <div className="mt-5 mb-2 w-80 max-w-screen-lg sm:w-96">
                            <div className="flex flex-col gap-6">
                                <TextInput
                                    name={"first_name"}
                                    inputType={"text"}
                                    label={"First Name"}
                                    initialValue={first_name}
                                    handleChange={handleChange}
                                    errorMessage={errors?.first_nameError}
                                    onBlur={() =>
                                        setErrors({
                                            ...errors,
                                            first_nameError: "",
                                        })
                                    }
                                />
                                <TextInput
                                    name={"last_name"}
                                    inputType={"text"}
                                    label={"Last Name"}
                                    initialValue={last_name}
                                    handleChange={handleChange}
                                    errorMessage={errors?.last_nameError}
                                    onBlur={() =>
                                        setErrors({
                                            ...errors,
                                            last_nameError: "",
                                        })
                                    }
                                />

                                <PhoneNumberInput
                                    initialValue={phone_number}
                                    handleChange={(value) =>
                                        setUser({
                                            ...user,
                                            phone_number: value,
                                        })
                                    }
                                    errorMessage={errors?.phone_numberError}
                                    onBlur={() =>
                                        setErrors({
                                            ...errors,
                                            phone_numberError: "",
                                        })
                                    }
                                />

                                <TextInput
                                    name={"email"}
                                    inputType={"email"}
                                    label="Email"
                                    initialValue={email}
                                    handleChange={handleChange}
                                    errorMessage={errors?.emailError}
                                    onBlur={() =>
                                        setErrors({
                                            ...errors,
                                            emailError: "",
                                        })
                                    }
                                />
                                <PasswordInput
                                    name="password"
                                    label="Password"
                                    initialValue={password}
                                    handleChange={handleChange}
                                    errorMessage={errors?.passwordError}
                                    onBlur={() =>
                                        setErrors({
                                            ...errors,
                                            passwordError: "",
                                        })
                                    }
                                />

                                <Checkbox
                                    required
                                    crossOrigin={undefined}
                                    color="green"
                                    name="terms_and_privacy_accepted"
                                    checked={terms_and_privacy_accepted}
                                    onChange={handleChange}
                                    label={
                                        <>
                                            <Typography
                                                variant="small"
                                                color="gray"
                                                className="flex items-center font-normal "
                                            >
                                                I agree with the&nbsp;
                                                <a
                                                    href="https://fastdatascience.com/clinical-trial-risk-tool-terms-of-use/"
                                                    target="_blank"
                                                    className="font-medium text-[#38A385] underline transition-colors hover:text-text_primary"
                                                >
                                                    Terms of Use
                                                </a>
                                                &nbsp;and
                                                <a
                                                    href="https://fastdatascience.com/clinical-trial-risk-tool-privacy-policy/"
                                                    target="_blank"
                                                    className="font-medium  ml-1 underline   text-[#38A385]  transition-colors hover:text-text_primary"
                                                >
                                                    Privacy Policy
                                                </a>
                                            </Typography>
                                            {errors?.terms_and_privacy_acceptedError && (
                                                <Typography
                                                    variant="small"
                                                    color="red"
                                                    className="text-[10px]"
                                                >
                                                    You must accept the terms
                                                    and privacy policy.
                                                </Typography>
                                            )}
                                        </>
                                    }
                                    containerProps={{
                                        className: "-ml-2.5",
                                    }}
                                />
                            </div>

                            <Checkbox
                                // only enabled when email is valid
                                disabled={!email || !EMAIL_REGEX.test(email)}
                                crossOrigin={undefined}
                                color="green"
                                name="subscribe_to_newsletter"
                                checked={subscribe_to_newsletter}
                                onChange={handleChange}
                                label={
                                    <Typography
                                        variant="small"
                                        color="gray"
                                        className="flex items-center font-normal "
                                    >
                                        I would like to subscribe to newsletter
                                    </Typography>
                                }
                                containerProps={{
                                    className: "-ml-2.5",
                                }}
                            />

                            <Typography
                                variant="small"
                                color="black"
                                className="text-[10px]"
                            >
                                We use Mailchimp as our marketing platform. By
                                clicking above to subscribe you acknowledge that
                                your information will be transferred to
                                Mailchimp for processing.{" "}
                                <a
                                    href="https://mailchimp.com/legal/"
                                    target="_blank"
                                    className="underline text-blue-600 font-medium"
                                >
                                    Learn More
                                </a>{" "}
                                about Mailchimp's privacy practices.
                            </Typography>

                            <Button
                                className="mt-6 bg-green_primary rounded-full flex justify-center items-center py-4 font-semibold"
                                fullWidth
                                onClick={handleSignUp}
                            >
                                {isLoading ? (
                                    <Spinner
                                        color="green"
                                        className="h-6 w-6"
                                    />
                                ) : (
                                    "Register"
                                )}
                            </Button>
                            <Typography
                                color="gray"
                                className="mt-4 text-sm text-center font-normal text-text_secondary"
                            >
                                Already have an account?{" "}
                                <Link
                                    to={"/login"}
                                    className="font-semibold text-green_primary text-sm"
                                >
                                    Sign In
                                </Link>
                            </Typography>

                            <div className="my-4 flex items-center gap-2">
                                <span className="h-[1px] w-1/2 bg-blue-gray-100" />
                                <Typography variant="small" color="blue-gray">
                                    Or
                                </Typography>
                                <span className="h-[1px] w-1/2 bg-blue-gray-100" />
                            </div>
                            <GoogleAuthButton
                                btnText={"Sign up with Google"}
                                handleGoogleAuth={loginWithGoogle}
                            />
                        </div>
                    </Card>
                )}
            </>
            <EmailVerification
                isOpen={openEmailVerification}
                setIsOpen={setOpenEmailVerification}
            />
        </>
    );
};

export default SignUp;
