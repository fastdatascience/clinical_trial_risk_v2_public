import React from "react";
import logo from "../../assets/logo.svg";
import { footerLinks, socialLinks } from "../../utils/constants";
import { Typography } from "@material-tailwind/react";

const Footer: React.FC = () => {
    return (
        <footer className="bg-text_primary w-full  mt-20">
            <div className="text-white p-16">
                {/* Logo */}
                <img src={logo} alt="Logo" className="h-10 w-auto" />
                {/* Footer links div */}
                <div className="mx-auto grid w-full grid-cols-1 gap-8 py-12 md:grid-cols-2 lg:grid-cols-5">
                    {footerLinks.map(({ title, links }, key) => (
                        <div key={key} className="w-full">
                            <Typography
                                variant="small"
                                color="white"
                                className="mb-4 font-semibold text-sm uppercase"
                            >
                                {title}
                            </Typography>
                            <ul className="space-y-1">
                                {links.map((link, key) => (
                                    <Typography
                                        key={key}
                                        as="li"
                                        color="white"
                                        className="font-normal text-base"
                                    >
                                        {/* Will be some link prolly later */}
                                        <p
                                            // href="#"
                                            className="inline-block py-1 pr-2 transition-transform hover:underline cursor-pointer"
                                        >
                                            {link}
                                        </p>
                                    </Typography>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
                {/* Social links div */}
                <div className=" flex justify-center items-center flex-wrap lg:gap-12 gap-6">
                    {socialLinks.map((item) => (
                        <a
                            href={item.url}
                            target="_blank"
                            key={item.id}
                            className="text-white cursor-pointer border-white/40 hover:border-white border p-3 rounded-full svg-xs"
                        >
                            <span className="sr-only">{item.id}</span>
                            {item.icon}
                        </a>
                    ))}
                </div>
                {/* Rights reserved links  */}
                <div className="text-center text-sm">
                    <p className="text-white text-xs mb-2 mt-16 leading-snug max-w-xl mx-auto text-center">
                        © 2023 Fast Data Science. © 2023 Fast Data Science Ltd,
                        provider of natural language processing, machine
                        learning and data science consulting services, London,
                        U.K Director: Thomas Wood
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
