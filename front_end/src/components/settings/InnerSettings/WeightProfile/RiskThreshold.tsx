import { useAtom } from "jotai";
import {
    filteredWeightProfilesAtom,
    moduleWeightAtom,
    weightProfilesAtom,
} from "../../../../lib/atoms";
import { useState } from "react";
import {
    deleteUserWeightProfile,
    getWeightProfiles,
} from "../../../../utils/services";
import { WeightConfigureTable } from "../../../tables";

const TABLE_HEAD = ["Low", "High", ""];

const RiskThreshold = () => {
    const [, setModuleWeight] = useAtom(moduleWeightAtom);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [weightProfiles, setWeightProfiles] = useAtom(weightProfilesAtom);

    const [filteredWeightProfiles, setFilteredWeightProfiles] = useAtom(
        filteredWeightProfilesAtom
    );

    const fetchUserWeightProfiles = async () => {
        try {
            setIsLoading(true);
            await getWeightProfiles(setModuleWeight, setWeightProfiles);
        } catch (err) {
            console.log("Error occurred getting weight profiles", err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async () => {
        try {
            setIsLoading(true);

            //    if filtered array is empty just delete the first profile because we know theres's only one
            if (filteredWeightProfiles?.length === 0) {
                const deleted = await deleteUserWeightProfile(
                    weightProfiles?.[0]?.id,
                    weightProfiles?.[0].weights.cost_risk_models // TODO: need to fix this as well
                );
                if (deleted.status === 204) {
                    await fetchUserWeightProfiles();
                }
            } else {
                const deleted = await deleteUserWeightProfile(
                    filteredWeightProfiles?.[0]?.id,
                    filteredWeightProfiles?.[0].weights?.cost_risk_models
                );
                if (deleted.status === 204) {
                    await fetchUserWeightProfiles();
                }
            }
        } catch (error) {
            console.error("Failed to delete weight profile.", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div>
            {/* weight configure table here */}
            <WeightConfigureTable
                isLoading={isLoading}
                isFiltered={!!filteredWeightProfiles?.length}
                columns={TABLE_HEAD}
                data={
                    filteredWeightProfiles && filteredWeightProfiles.length > 0
                        ? filteredWeightProfiles
                        : weightProfiles && weightProfiles.length > 0
                        ? [weightProfiles[0]]
                        : []
                }
                setWeightProfiles={setWeightProfiles}
                setFilteredWeightProfiles={setFilteredWeightProfiles}
                onDelete={handleDelete}
                weightKey="risk_thresholds"
            />
        </div>
    );
};

export default RiskThreshold;
