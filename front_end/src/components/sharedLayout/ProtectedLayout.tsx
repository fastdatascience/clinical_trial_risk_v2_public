import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import SideBar from "./SideBar";
import DashboardLayoutHeader from "./DashboardLayoutHeader";
import { useAuth } from "../../hooks/useAuth";
import { TOKEN_STORAGE_KEY } from "../../utils/network";
import { useAtom } from "jotai";
import { platformAtom } from "../../lib/atoms";

const ProtectedLayout: React.FC = () => {
    const { isAuthenticated } = useAuth();
    const [platform] = useAtom(platformAtom);

    if (isAuthenticated || !!localStorage.getItem(TOKEN_STORAGE_KEY)) {
        return (
            <div className="bg-green_secondary flex overflow-auto">
                <SideBar />
                <div className="md:pl-20 md:w-full h-screen">
                    <DashboardLayoutHeader />
                    <div className="bg-white rounded-large p-5 lg:mx-10 mx-5">
                        {<Outlet />}
                    </div>
                    {/* footer */}
                    {platform?.core_lib_version && platform?.server_version && (
                        <footer className="p-5 lg:mx-10  mx-5 flex justify-end items-end text-sm text-text_secondary/75">
                            <span className="mr-3">
                                Core Library v{platform.core_lib_version}{" "}
                            </span>
                            <span>Server v{platform.server_version}</span>
                        </footer>
                    )}
                </div>
            </div>
        );
    }
    return <Navigate to={"/login"} replace />;
};

export default ProtectedLayout;
