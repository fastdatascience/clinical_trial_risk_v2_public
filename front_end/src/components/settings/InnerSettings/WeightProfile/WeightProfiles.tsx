import { useAtom } from "jotai";
import { useEffect, useState } from "react";
import {
    filteredWeightProfilesAtom,
    moduleWeightAtom,
    weightProfilesAtom,
} from "../../../../lib/atoms";
import { Option, Weights } from "../../../../utils/types";
import { getWeightProfiles } from "../../../../utils/services";
import { generateDropdownOptions } from "../../../../utils/utils";
import { Card, Spinner } from "@material-tailwind/react";
import { SelectInput } from "../../../common";
import { weightTabItems } from "../../../../utils/constants";
import { CustomTabs } from "../../../common/Tabs";

const WeightProfiles: React.FC = () => {
    const [, setModuleWeight] = useAtom(moduleWeightAtom);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [options, setOptions] = useState<Option[]>([]);
    const [selectedProfile, setSelectedProfile] = useState<string>("");
    const [weightProfiles, setWeightProfiles] = useAtom(weightProfilesAtom);

    const [, setFilteredWeightProfiles] = useAtom(filteredWeightProfilesAtom);

    const fetchUserWeightProfiles = async () => {
        try {
            setIsLoading(true);
            const weights = await getWeightProfiles(
                setModuleWeight,
                setWeightProfiles
            );
            const weight_profile_options = generateDropdownOptions(weights!);
            if (weight_profile_options) {
                setOptions(weight_profile_options);
            }
        } catch (err) {
            console.log("Error occurred getting weight profiles", err);
        } finally {
            setIsLoading(false);
        }
    };

    // fetch data every time profile is selected.
    useEffect(() => {
        fetchUserWeightProfiles();
    }, [selectedProfile]);

    const handleSelectWeightProfile = (profile: string) => {
        setSelectedProfile(profile);
        const filteredWightProfiles = weightProfiles?.filter(
            (_profile) => _profile.name === profile
        );

        if (filteredWightProfiles && filteredWightProfiles.length > 0) {
            setFilteredWeightProfiles(filteredWightProfiles);
        }

        const weights = filteredWightProfiles?.reduce((acc, weights) => {
            return {
                ...acc,
                ...weights.weights,
            };
        }, {} as Weights);

        setModuleWeight(weights);
    };

    const onSelectProfile = (profile: string) => {
        setSelectedProfile(profile);
        handleSelectWeightProfile(profile);
    };

    return (
        <div className="flex flex-col space-y-8 p-5">
            <div className="flex flex-col gap-y-1">
                <h3 className="text-2xl font-poppins font-semibold flex flex-wrap">
                    Configure Weight Profile
                </h3>
                <p className=" text-sm text-text_secondary">
                    You can adjust the weights. Dashboard tell you when a set of
                    weights is applicable
                </p>
            </div>

            {/* 3 Tabs here and each tab will have it's own component */}
            {isLoading && !!weightProfiles?.length ? (
                <div className="flex justify-center items-center">
                    <Spinner color="green" className="h-20 w-20" />
                </div>
            ) : (
                <Card className="h-full w-full overflow-scroll">
                    <header className="rounded-none flex justify-end bg-blue-gray-50/50 border-b border-blue-gray-100  space-y-6 p-5">
                        <div className="w-full md:w-96">
                            <SelectInput
                                value={
                                    selectedProfile || weightProfiles?.[0]?.name
                                }
                                placeholder="Choose weight profile..."
                                options={options}
                                onChange={(value) => onSelectProfile(value)}
                            />
                        </div>
                    </header>
                    <CustomTabs
                        value="Cost Risk Models"
                        tabItems={weightTabItems}
                        data={weightProfiles}
                        tabListClassName="bg-green_primary rounded-none"
                    />
                </Card>
            )}
        </div>
    );
};

export default WeightProfiles;
