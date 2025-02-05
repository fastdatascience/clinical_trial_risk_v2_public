import React, { useState } from "react";
import { InnerSideBarLinkType } from "../../utils/types";
import InnerSettings from "../settings/InnerSettings/InnerSettings";

const innerSideBarLinks: InnerSideBarLinkType[] = [
    {
        key: "My Profile",
        label: "My Profile",
        active: true,
    },
    {
        key: "Security",
        label: "Security",
        active: false,
    },
    {
        key: "Weight Profile",
        label: "Weight Profile",
        active: false,
    },
];

export interface SettingsPageProps {
    refresh: boolean;
    setRefresh: React.Dispatch<React.SetStateAction<boolean>>;
}

const Settings: React.FC = () => {
    const [reload, setReload] = useState(false);
    const [activeIndex, setActiveIndex] = useState(0);
    const handleLinkClick = (item: InnerSideBarLinkType) => {
        innerSideBarLinks.map((link, index) => {
            link === item ? (link.active = true) : (link.active = false);
            link === item && setActiveIndex(index);
        });
        setReload(!reload);
    };

    return (
        <div className="rounded-t-3xl bg-green_secondary ">
            <div className="bg-green_primary h-8 rounded-t-large" />

            <div className="flex md:flex-row  flex-col md:space-x-12">
                <div className="flex md:flex-col flex-row gap-5 mt-10">
                    {" "}
                    {/* Inner Sidebar  */}
                    {innerSideBarLinks.map((item) => {
                        return (
                            <InnerSideBarLink
                                key={item.key}
                                item={item}
                                onClick={handleLinkClick}
                            />
                        );
                    })}
                </div>
                <div className="flex flex-col w-full">
                    <InnerSettings activeIndex={activeIndex} />
                </div>
            </div>
        </div>
    );
};

export default Settings;

type InnerSidebarLinkProps = {
    item: InnerSideBarLinkType;
    onClick: (params: InnerSideBarLinkType) => void; //  turn off type checking
};
const InnerSideBarLink: React.FC<InnerSidebarLinkProps> = ({
    item,
    onClick,
}) => {
    return (
        <span
            className={`${
                item.active && "bg-green_primary text-white rounded-r-2xl"
            } flex justify-center items-center w-32 cursor-pointer`}
            onClick={() => onClick(item)}
        >
            <p className="font-poppins text-sm p-2">{item.label}</p>
        </span>
    );
};
