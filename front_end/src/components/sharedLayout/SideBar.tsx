import React, { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { RiLogoutBoxFill } from "react-icons/ri";
import { Button, Tooltip } from "@material-tailwind/react";

import { dashboardSidebarLinks } from "../../utils/constants";
import { SidebarLinkType } from "../../utils/types";
import logo from "../../assets/logo.svg";
import logoIcon from "../../assets/logo-icon.png";
import avatar from "../../assets/avatar.jpeg";
import { useAuth } from "../../hooks/useAuth";
import { useAtom } from "jotai";
import { isDemoUserAtom, userProfileAtom } from "../../lib/atoms";
import { FaArrowLeft } from "react-icons/fa";
import ShareGuestAccessModal from "../modals/ShareGuestAccessModal";
import { getProfilePictureUrl } from "../../utils/utils";

const SideBar: React.FC = () => {
    // this user from google (remove this for now)
    // const [user] = useAtom(userAuthProfileAtom);

    // this user from email
    const [userProfile] = useAtom(userProfileAtom);
    const [open, setOpen] = useState<boolean>(false);
    const { logout, setIsAuthenticated } = useAuth();

    const toggleSidebar = () => {
        setOpen((prev) => !prev);
    };

    if (!userProfile) return;
    return (
        <>
            {/* Responsive Floating button */}
            <button
                className="fixed z-50 md:hidden  top-5 right-5 bg-green_primary w-10 h-10 rounded-full drop-shadow-lg flex justify-center items-center text-white text-4xl hover:bg-teal-800   duration-300"
                onClick={toggleSidebar}
            >
                <span className="text-white">
                    {open ? (
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="16"
                            height="16"
                            fill="currentColor"
                            className="bi bi-x-lg"
                            viewBox="0 0 16 16"
                        >
                            <path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8z" />
                        </svg>
                    ) : (
                        <svg
                            className="w-6 h-6"
                            aria-hidden="true"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                clipRule="evenodd"
                                fillRule="evenodd"
                                d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"
                            ></path>
                        </svg>
                    )}
                </span>
            </button>
            {/* Sidebar */}
            <aside
                className={`${
                    open
                        ? " w-44 p-5 drop-shadow-lg slideInLeft"
                        : " w-24 md:opacity-100 opacity-0"
                }  duration-300 bg-green_primary font-poppins  text-white h-full flex flex-col justify-around items-center fixed z-50`}
            >
                <button
                    onClick={toggleSidebar}
                    className="bg-white  md:flex items-center justify-center hidden cursor-pointer absolute border-2 border-light_yellow -right-3 top-9 rounded-full w-8 h-8"
                >
                    <span
                        title={open ? "collapse" : "expand"}
                        className={`text-text_primary ${!open && "rotate-180"}`}
                    >
                        <FaArrowLeft />
                    </span>
                </button>

                {/* full logo */}
                <div className={`${open ? "block" : "hidden"}`}>
                    <div className="flex items-center justify-center">
                        <img
                            src={logo}
                            alt="Fast Data Science Logo"
                            className="object-contain w-auto h-9 contrast-200"
                        />
                    </div>
                </div>

                {/* icon only logo */}
                <div
                    className={`${
                        open
                            ? "hidden"
                            : "flex items-center w-12 justify-center "
                    }`}
                >
                    <img
                        src={logoIcon}
                        alt="Fast Data Science Logo"
                        className="object-contain w-auto contrast-200"
                    />
                </div>
                <div className=" flex flex-col gap-16 items-center">
                    {/* profile */}
                    {userProfile.user && (
                        <div className="flex items flex-col items-center justify-center">
                            <div className="rounded-full overflow-hidden w-16 h-16 mb-1">
                                <img
                                    src={getProfilePictureUrl(
                                        userProfile.user.profile_picture,
                                        avatar
                                    )}
                                    className="object-cover h-full w-full"
                                    alt={
                                        userProfile?.user?.first_name ??
                                        "Profile Picture"
                                    }
                                />
                            </div>
                            <p
                                className={`${
                                    open
                                        ? "leading-relaxed text-sm"
                                        : "font-thin text-center text-sm"
                                }`}
                            >
                                {userProfile?.user?.first_name +
                                    " " +
                                    userProfile?.user?.last_name}
                            </p>
                        </div>
                    )}

                    <div className="flex flex-col justify-center items-center gap-3">
                        {dashboardSidebarLinks.map((item) => (
                            <SideBarLink
                                key={item.id}
                                item={item}
                                open={open}
                            />
                        ))}
                    </div>
                </div>
                <div
                    className={`flex flex-col ${open && "w-40"} justify-center`}
                >
                    <Button
                        size="md"
                        className={`bg-green_secondary font-semibold text-green_primary ${
                            open ? "rounded-full" : "rounded-xl"
                        }`}
                        onClick={() => {
                            logout();
                            setIsAuthenticated(false);
                        }}
                    >
                        {open ? "Log out" : <RiLogoutBoxFill size={20} />}
                    </Button>
                </div>
            </aside>
        </>
    );
};

type SidebarLinkProps = {
    item: SidebarLinkType;
    open: boolean;
};

const SideBarLink: React.FC<SidebarLinkProps> = ({ item, open }) => {
    const { pathname } = useLocation();
    const [isDemoUser] = useAtom(isDemoUserAtom);
    const [openShareModal, setOpenShareModal] = useState<boolean>(false);

    const isRestricted =
        isDemoUser && (item.path === "/history" || item.path === "/settings");
    return isRestricted ? (
        <Tooltip content={item.tooltipText}>
            <div
                className={`flex items-center justify-between cursor-help
       gap-2 p-2
       ${open ? "w-40 rounded-full" : "w-fit"} rounded-xl font-thin`}
            >
                <div
                    className={`flex ${
                        open ? "flex-row" : "flex-col"
                    } gap-2 items-center justify-between`}
                >
                    <span className={"text-text_secondary/75 text-3xl"}>
                        {item.icon}
                    </span>
                    <p
                        className={`${
                            open ? "text-base" : "text-[10px] "
                        } text-text_secondary/75`}
                    >
                        {item.label}
                    </p>
                </div>
            </div>
        </Tooltip>
    ) : (
        <>
            <NavLink
                to={item.path}
                onClick={
                    item.hasClick
                        ? () => setOpenShareModal((prev) => !prev)
                        : undefined
                }
                className={({ isActive }) =>
                    `flex items-center justify-between
       gap-2 p-2
       ${
           isActive
               ? "bg-active_accent text-black"
               : "hover:bg-active_accent hover:text-black"
       }
       ${open ? "w-40 rounded-full" : "w-fit"} rounded-xl font-thin`
                }
            >
                <div
                    className={`flex ${
                        open ? "flex-row" : "flex-col"
                    } gap-2 items-center justify-between`}
                >
                    <span
                        className={`${
                            pathname === item.path && "text-green_primary"
                        } text-3xl`}
                    >
                        {item.icon}
                    </span>
                    <p className={`${open ? " text-sm" : "text-[10px]"}`}>
                        {item.label}
                    </p>
                </div>
            </NavLink>
            <ShareGuestAccessModal
                isOpen={openShareModal}
                setIsOpen={setOpenShareModal}
            />
        </>
    );
};

export default SideBar;
