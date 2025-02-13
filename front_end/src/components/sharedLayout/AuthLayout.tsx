import React from "react";

import { Footer, AuthLayoutHeader } from "../common";
import { Outlet } from "react-router-dom";
import EmailVerification from "../modals/EmailVerification";
import { openEmailVerificationAtom } from "../../lib/atoms";
import { useAtom } from "jotai";

const AuthLayout: React.FC = () => {
    const [openEmailVerification, setOpenEmailVerification] = useAtom<boolean>(
        openEmailVerificationAtom
    );

    return (
        <>
            <div className="bg-Gray flex flex-col items-center justify-center">
                <AuthLayoutHeader />
                <Outlet />
                <Footer />
            </div>

            <EmailVerification
                isOpen={openEmailVerification}
                setIsOpen={setOpenEmailVerification}
            />
        </>
    );
};

export default AuthLayout;
