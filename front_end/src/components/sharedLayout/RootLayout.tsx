import React, { useEffect, useState } from "react";
import { useOutlet } from "react-router-dom";
import { AuthProvider } from "../../context/AuthContext";
import { network, API_V1 } from "../../utils/network";
import { useAtom } from "jotai";
import { platformAtom, userProfileAtom } from "../../lib/atoms";
import { ServerResponseV1, UserProfileTree } from "../../utils/types";
import { getPlatformMetadata } from "../../utils/services";

const styles: { [key: string]: React.CSSProperties } = {
    topLoadingBar: {
        position: "fixed",
        top: 0,
        left: 0,
        width: "100%",
        height: "10px",
        backgroundColor: "#eee",
        zIndex: 999,
    },
    glowContainer: {
        width: "100%",
        height: "100%",
        overflow: "hidden",
        borderRadius: "5px",
    },
    glowLine: {
        position: "absolute",
        top: 0,
        left: "-100%",
        width: "100%",
        height: "100%",
        backgroundImage:
            "linear-gradient(to right, transparent, #57ca96 50%, transparent)",
        animation: "glow 1s linear infinite",
    },
};

const keyframes = `
@keyframes glow {
    0% {
        left: -100%;
    }
    100% {
        left: 100%;
    }
}`;

export const LoadingBar = () => (
    <>
        <style>{keyframes}</style>
        <div style={styles.topLoadingBar}>
            <div style={styles.glowContainer}>
                <div style={styles.glowLine}></div>
            </div>
        </div>
    </>
);

const RootLayout: React.FC = () => {
    const outlet = useOutlet();

    const [, setUserProfile] = useAtom(userProfileAtom);
    const [loading, setLoading] = useState(true);

    const [, setPlatform] = useAtom(platformAtom);

    const fetchPlatformMetadata = async () => {
        try {
            const data = await getPlatformMetadata();
            if (data) {
                setPlatform({
                    core_lib_version: data?.core_lib_version,
                    server_version: data?.server_version,
                });
            }
        } catch (err) {
            console.error("Error fetching platform metadata:", err);
        }
    };

    useEffect(() => {
        const getUserProfile = async () => {
            try {
                const userResponse = await network().get<
                    ServerResponseV1<UserProfileTree>
                >(`/${API_V1}/auth/user`);
                const data = userResponse.data;
                setUserProfile(data.data);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchPlatformMetadata();

        getUserProfile();
    }, [setUserProfile, setPlatform]);

    if (loading) {
        return <LoadingBar />;
    }

    return <AuthProvider>{outlet}</AuthProvider>;
};

export default RootLayout;
