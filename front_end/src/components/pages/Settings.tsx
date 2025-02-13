import React from "react";
import { InnerSideBarLinkType } from "../../utils/types";
import { CustomTabs } from "../common/Tabs";
import { settingsItems } from "../../utils/constants";

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
    return (
        <div className="rounded-t-large bg-green_secondary">
            <CustomTabs
                orientation="vertical"
                value="My Profile"
                tabItems={settingsItems}
                data={innerSideBarLinks}
                tabListClassName="bg-green_secondary flex flex-col  w-full space-y-10 mt-10"
                tabPanelsClassName="font-poppins"
            />
        </div>
    );
};

export default Settings;
