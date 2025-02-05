import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { loginSignupWithGoogle } from "../../utils/services";
import { AxiosResponse } from "axios";
import { API_V1, network } from "../../utils/network";
import { useAuth } from "../../hooks/useAuth";
import { useAtom } from "jotai";
import {
    userAccessTokenAtom,
    userProfileAtom,
    userRefreshTokenAtom,
} from "../../lib/atoms";
import { Button } from "@material-tailwind/react";

// Extract code from url
const GoogleCallback = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const token = searchParams.get("code");
    const { setIsAuthenticated } = useAuth();

    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [, setUserProfile] = useAtom(userProfileAtom);
    const [, setUserAccessToken] = useAtom(userAccessTokenAtom);
    const [, setUserRefreshToken] = useAtom(userRefreshTokenAtom);

    const encodedCode = token ? encodeURIComponent(token) : null;

    const getUserProfile = async () => {
        try {
            const userResponse = await network().get(`/${API_V1}/auth/user`);
            const data = userResponse.data;
            console.log("user data==>", data);
            setUserProfile(data);
            setIsAuthenticated(true);
            location.href = "/dashboard";
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        const handleLoginSignup = async () => {
            try {
                if (encodedCode) {
                    // after success do the same added in the commented out code handleLogin
                    const codeVerifier = localStorage.getItem(
                        "code_verifier"
                    ) as string;
                    setIsLoading(true);
                    const loginResponse = (await loginSignupWithGoogle(
                        encodedCode,
                        codeVerifier
                    )) as AxiosResponse;
                    if (
                        loginResponse?.status === 200 &&
                        loginResponse?.data?.data
                    ) {
                        // * Save user token
                        setUserAccessToken(
                            loginResponse?.data?.data?.access_token
                        );
                        setUserRefreshToken(
                            loginResponse?.data?.data?.refresh_token
                        );
                        await getUserProfile();
                    }
                }
            } catch (error) {
                console.error("Failed to login with google", error);
            } finally {
                setIsLoading(false);
            }
        };
        handleLoginSignup();
    }, [encodedCode]);

    if (isLoading) {
        return <div className="loading">Loading&#8230;</div>;
    }

    return (
        <div className="flex bg-Gray  flex-col h-screen justify-center items-center">
            <p className=" font-semibold text-lg text-text_primary">
                {" "}
                Something went Wrong! please try again
            </p>
            <Button
                className="mt-6 w-64 bg-green_primary  disabled:pointer-events-none rounded-full flex justify-center items-center "
                fullWidth
                onClick={() => navigate("/login")}
            >
                Log In
            </Button>
        </div>
    );
};

export default GoogleCallback;
