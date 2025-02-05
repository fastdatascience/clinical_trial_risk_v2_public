import React, { useRef, useState } from "react";
import logo from "../../assets/logo.svg";
import { Link } from "react-router-dom";
import { GrClose } from "react-icons/gr";
import { HiMenuAlt1 } from "react-icons/hi";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "@material-tailwind/react";
import { useOnClickOutside } from "../../hooks/useOnClickOutside";
import { authButtonsLinks, navLinks } from "../../utils/constants";

const AuthLayoutHeader: React.FC = () => {
    const ref = useRef(null);
     const buttonRef = useRef<HTMLButtonElement>(null);
    const [toggle, setToggle] = useState<boolean>(false);
    const { isAuthenticated, logout } = useAuth();

    useOnClickOutside(ref, () => setToggle(false), buttonRef);

    return (
        <header className="bg-white w-full border-b border-slate-100 sticky top-0 z-10 ">
            <div className="px-6 lg:px-8">
                <nav className="mx-auto max-w-7xl py-4 lg:py-5">
                    <div className="flex items-center justify-between lg:justify-start lg:space-x-10">
                        <div className="flex justify-start lg:w-0 lg:flex-1">
                            <Link to={"/"}>
                                <span className="sr-only">
                                    Fast Data Science
                                </span>
                                <img
                                    src={logo}
                                    alt="Fast Data Science"
                                    className="h-9 w-auto"
                                    width={"156"}
                                    height={"36"}
                                />
                            </Link>
                        </div>
                        {/* Hamburger */}
                        <button
                            ref={buttonRef}
                            onClick={() => setToggle((prev) => !prev)}
                            className="flex items-center lg:hidden gap-2 cursor-pointer"
                        >
                            {toggle ? (
                                <GrClose
                                    size={25}
                                    className="text-text_primary"
                                />
                            ) : (
                                <HiMenuAlt1
                                    size={32}
                                    className="text-text_primary"
                                />
                            )}
                        </button>

                        {/* Web Menu */}
                        <nav className="hidden lg:flex lg:space-x-2">
                            <ul className="font-medium flex flex-col p-4 md:p-0 mt-4 border border-gray-100 rounded-lg bg-gray-50 md:flex-row md:space-x-8 rtl:space-x-reverse md:mt-0 md:border-0 md:bg-white dark:bg-gray-800 md:dark:bg-gray-900 dark:border-gray-700">
                                {navLinks.map((navItem) => (
                                    <li key={navItem.id}>
                                        <Link
                                            to={navItem.path}
                                            className="block tracking-wide text-text_primary font-medium transform-none items-center text-base hover:bg-slate-100 px-4 py-2.5 rounded-full focus:outline-none"
                                        >
                                            {navItem.title}
                                        </Link>
                                    </li>
                                ))}

                                {isAuthenticated ? (
                                    <li className="flex gap-3">
                                        <Button
                                            onClick={logout}
                                            className={
                                                "block cursor-pointer w-full lg:w-auto text-center tracking-wide px-6 py-2 transition whitespace-nowrap border text-text_primary bg-transparent border-text_primary hover:opacity-90 rounded-full font-semibold"
                                            }
                                        >
                                            Logout
                                        </Button>
                                        <Link
                                            to={"/dashboard"}
                                            className={
                                                "block w-full lg:w-auto text-center tracking-wide px-6 py-2 transition whitespace-nowrap border text-white bg-green_primary  border-green_primary\"}  hover:opacity-90 rounded-full font-semibold"
                                            }
                                        >
                                            Dashboard
                                        </Link>
                                    </li>
                                ) : (
                                    authButtonsLinks.map((authLink) => (
                                        <li key={authLink.id}>
                                            <Link
                                                to={authLink.path}
                                                className={`block w-full lg:w-auto text-center tracking-wide px-6 py-2 transition whitespace-nowrap border ${
                                                    authLink.title === "Login"
                                                        ? "text-text_primary border-text_primary"
                                                        : "text-white bg-green_primary  border-green_primary"
                                                }  hover:opacity-90 rounded-full font-semibold`}
                                            >
                                                {authLink.title}
                                            </Link>
                                        </li>
                                    ))
                                )}
                            </ul>
                        </nav>
                    </div>
                </nav>
            </div>

            {/* Mobile Menu */}
            <div
                ref={ref}
                className={`${
                    toggle ? "block z-10 zoomIn " : "hidden"
                } absolute w-full mt-0.25 lg:hidden border-y border-gray-200 `}
            >
                <ul className="font-medium flex flex-col p-4 md:p-0 border border-gray-100 rounded-lg bg-gray-50 gap-2">
                    {navLinks.map((navItem) => (
                        <li key={navItem.id}>
                            <Link
                                to={navItem.path}
                                className="block tracking-wide text-text_primary font-medium transform-none items-center text-base hover:bg-light_gray_bg duration-150 px-4 py-2.5  focus:outline-none"
                            >
                                {navItem.title}
                            </Link>
                        </li>
                    ))}

                    {isAuthenticated ? (
                        <li>
                            <Button
                                onClick={logout}
                                className={
                                    "block w-full mx-3 my-2 bg-inherit lg:w-auto text-center tracking-wide px-6 py-2 transition whitespace-nowrap border cursor-pointer text-text_primary border-text_primary hover:opacity-90 rounded-full font-semibold"
                                }
                            >
                                Logout
                            </Button>
                            <Link
                                to={"/dashboard"}
                                className={
                                    "block w-full mx-3 my-2 lg:w-auto text-center tracking-wide px-6 py-2 transition whitespace-nowrap border text-white bg-green_primary  border-green_primary  hover:opacity-90 rounded-full font-semibold"
                                }
                            >
                                Dashboard
                            </Link>
                        </li>
                    ) : (
                        authButtonsLinks.map((authLink) => (
                            <li key={authLink.id}>
                                <Link
                                    to={authLink.path}
                                    className={`block w-full mx-3 my-2 lg:w-auto text-center tracking-wide px-6 py-2 transition whitespace-nowrap border ${
                                        authLink.title === "Login"
                                            ? "text-text_primary border-text_primary"
                                            : "text-white bg-green_primary  border-green_primary"
                                    }  hover:opacity-90 rounded-full font-semibold`}
                                >
                                    {authLink.title}
                                </Link>
                            </li>
                        ))
                    )}
                </ul>
            </div>
        </header>
    );
};

export default AuthLayoutHeader;
