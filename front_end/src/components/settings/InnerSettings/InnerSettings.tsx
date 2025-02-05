import MyAccount from "./MyAccount/MyAccount";
import Security from "./Security/Security";
import WeightProfile from "./WeightProfile/WeightProfiles";

interface InnerSettingsProps {
    activeIndex: number;
}

const InnerSettings: React.FC<InnerSettingsProps> = ({ activeIndex }) => {
    return (
        <>
            {activeIndex === 0 && <MyAccount />}
            {activeIndex === 1 && <Security />}
            {activeIndex === 2 && <WeightProfile />}
        </>
    );
};

export default InnerSettings;
