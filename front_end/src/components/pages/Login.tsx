import { Card, Button, Typography, Spinner } from "@material-tailwind/react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { PasswordInput, TextInput } from "../common";
import { login } from "../../utils/services";
import { AxiosError } from "axios";
import { useAtom } from "jotai";
import {
    isDemoUserAtom,
    openEmailVerificationAtom,
    userAccessTokenAtom,
    userAtom,
    userProfileAtom,
    userRefreshTokenAtom,
} from "../../lib/atoms";
import { API_V1, network } from "../../utils/network";

import { useAuth } from "../../hooks/useAuth";
import GoogleAuthButton from "../common/GoogleAuthButton";
import {
    constructUrl,
    generateGoogleCodeVerifierAndChallenge,
} from "../../utils/utils";

const Login: React.FC = () => {
    const { setIsAuthenticated } = useAuth();

    const navigate = useNavigate();
    const [, setIsDemoUser] = useAtom(isDemoUserAtom);
    const [, setUserProfile] = useAtom(userProfileAtom);
    const [, setUserAccessToken] = useAtom(userAccessTokenAtom);
    const [, setUserRefreshToken] = useAtom(userRefreshTokenAtom);
    const [, setOpenEmailVerification] = useAtom<boolean>(
        openEmailVerificationAtom
    );

    const [isLoading, setIsLoading] = useState<{
        as_guest: boolean;
        as_user: boolean;
    }>({
        as_guest: false,
        as_user: false,
    });

    const [user, setUser] = useAtom(userAtom);

    const [error, setError] = useState<boolean>();
    const [errorMessage, setErrorMessage] = useState<string>("");
    const { email, password } = user;

    const handleChange = (e: React.FormEvent<HTMLInputElement>) => {
        const { name, value } = e.target as HTMLInputElement;
        setUser({
            ...user,
            [name]: value,
        });
    };

    const getUserProfile = async () => {
        try {
            const userResponse = await network().get(`/${API_V1}/auth/user`);
            const data = userResponse.data;
            setUserProfile(data);
            setIsAuthenticated(true);
            location.href = "dashboard";
        } catch (error) {
            console.error(error);
        }
    };

    const handleGoogleLogin = async () => {
        const { codeVerifier, codeChallenge } =
            await generateGoogleCodeVerifierAndChallenge();
        localStorage.setItem("code_verifier", codeVerifier);

        const params = new URLSearchParams({
            client_id: import.meta.env.VITE_SECRET_GOOGLE_REDIRECT_URL,
            redirect_uri: constructUrl("/sign-up/callback"),
            response_type: "code",
            scope: "openid email profile",
            code_challenge: codeChallenge,
            code_challenge_method: "S256",
        });

        // redirects to consent screen
        window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
    };

    const loginAsUser = async () => {
        if (!email || !password) return;
        try {
            setIsLoading((prev) => ({ ...prev, as_user: true }));
            const loginResponse = await login(email, password);

            if (loginResponse?.status === 200) {
                if (loginResponse?.data?.data) {
                    setIsLoading((prev) => ({ ...prev, as_user: false }));
                    setError(false);
                    setErrorMessage("");

                    // * Save user token
                    setUserAccessToken(loginResponse?.data?.data?.access_token);
                    setUserRefreshToken(
                        loginResponse?.data?.data?.refresh_token
                    );
                    await getUserProfile();
                }
            } else {
                setIsLoading((prev) => ({ ...prev, as_user: false }));
                setError(true);
                setErrorMessage("Invalid Credentials");
            }
        } catch (error) {
            console.error("Failed to login", error);
            if (error instanceof AxiosError) {
                setErrorMessage(error.response?.data?.error);
                if (error.response?.status === 401) {
                    setOpenEmailVerification(true);
                }
            }
        } finally {
            setIsLoading((prev) => ({ ...prev, as_user: false }));
        }
    };

    const loginAsGuest = async () => {
        try {
            setIsLoading((prev) => ({ ...prev, as_guest: true }));

            const loginResponse = await login("demo@fastdatascience.com", "");

            if (loginResponse?.status === 200) {
                if (loginResponse?.data?.data) {
                    const {
                        data: { access_token, demo_user, user },
                    } = loginResponse.data;
                    setIsLoading((prev) => ({ ...prev, as_guest: false }));
                    setError(false);
                    setErrorMessage("");

                    // * Save user token
                    setUserAccessToken(access_token);

                    if (demo_user) {
                        setIsDemoUser(demo_user);
                        setUserProfile({ user: user });
                        setIsAuthenticated(true);
                        navigate("/dashboard", { replace: true });
                    }
                }
            } else {
                setIsLoading((prev) => ({ ...prev, as_guest: false }));
                setError(true);
                setErrorMessage("Invalid Credentials");
            }
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading((prev) => ({ ...prev, as_guest: false }));
        }
    };

    // Automatically login as guest if query parameter `guest=true` exists
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        if (params.get("guest") === "true") {
            loginAsGuest();
        }
    }, []);

    return (
        <Card className="bg-white p-7 my-10">
            <Typography variant="h3" className="text-text_primary text-center">
                Log In
            </Typography>
            <Typography
                color="gray"
                className="mt-1 text-center text-sm font-normal text-text_secondary"
            >
                Welcome back! Please enter your details.
            </Typography>
            <div className="mt-5 mb-2 w-80 max-w-screen-lg sm:w-96">
                <form
                    onSubmit={(e) => {
                        e.preventDefault();
                        loginAsUser();
                    }}
                    className="mb-4 flex flex-col gap-5"
                >
                    <TextInput
                        name="email"
                        inputType={"email"}
                        label="Email"
                        initialValue={email}
                        handleChange={handleChange}
                        error={error}
                        errorMessage={errorMessage}
                        onBlur={() => setErrorMessage("")}
                    />
                    <PasswordInput
                        name="password"
                        label="Password"
                        initialValue={password}
                        handleChange={handleChange}
                        error={error}
                        errorMessage={errorMessage}
                        onBlur={() => setErrorMessage("")}
                    />

                    <div className="text-right mt-0  inline-flex justify-end">
                        <Link
                            to={"/forgot-password"}
                            className="text-green_primary"
                        >
                            <Typography
                                variant="small"
                                className="font-semibold text-sm"
                            >
                                Forgot Password?{" "}
                            </Typography>
                        </Link>
                    </div>
                    <Button
                        type="submit"
                        className="mt-6 bg-green_primary  disabled:pointer-events-none rounded-full flex justify-center items-center "
                        fullWidth
                        disabled={!email || !password || isLoading.as_user}
                    >
                        {isLoading.as_user ? (
                            <Spinner color="green" className="h-6 w-6" />
                        ) : (
                            "Log In"
                        )}
                    </Button>
                </form>

                <Button
                    variant="outlined"
                    className="mt-6  border-text_primary text-text_primary  disabled:pointer-events-none rounded-full flex justify-center items-center "
                    fullWidth
                    onClick={loginAsGuest}
                    disabled={isLoading.as_guest}
                >
                    {isLoading.as_guest ? (
                        <Spinner color="green" className="h-6 w-6" />
                    ) : (
                        "Continue as Guest"
                    )}
                </Button>
                <Typography color="gray" className="mt-4 text-center text-sm">
                    Don't have an account?{" "}
                    <Link
                        to={"/register"}
                        className="font-semibold  text-green_primary cursor-pointer"
                    >
                        Sign Up
                    </Link>
                </Typography>
            </div>
            <div className="my-4 flex items-center gap-2">
                <span className="h-[1px] w-1/2 bg-blue-gray-100" />
                <Typography variant="small" color="blue-gray">
                    Or
                </Typography>
                <span className="h-[1px] w-1/2 bg-blue-gray-100" />
            </div>
            <GoogleAuthButton
                btnText={"Sign in with Google"}
                handleGoogleAuth={handleGoogleLogin}
            />
        </Card>
    );
};

export default Login;
