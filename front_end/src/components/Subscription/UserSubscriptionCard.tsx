import {
    Card,
    CardBody,
    CardFooter,
    Spinner,
    Typography,
} from "@material-tailwind/react";
import React, { useEffect, useState } from "react";
import { getUserSubscription } from "../../utils/services";
import { AxiosResponse } from "axios";
import { UserSubscription } from "../../utils/types";

const UserSubscriptionCard: React.FC = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [subscription, setSubscription] = useState<UserSubscription>();

    const getSubscription = async () => {
        try {
            setIsLoading(true);
            const response = (await getUserSubscription()) as AxiosResponse;
            if (response.status !== 200) {
                return;
            }
            const userSubscription = response.data?.data?.user_subscription;
            setSubscription(userSubscription);
            setIsLoading(false);
        } catch (error) {
            setIsLoading(false);
            console.error(
                "An Error Occurred while fetching Subscription",
                error
            );
        }
    };

    useEffect(() => {
        getSubscription();
    }, []);

    return (
        <>
            {isLoading ? (
                <Spinner color="green" className="h-6 w-6" />
            ) : (
                <Card className="mt-6 lg:w-96">
                    <CardBody>
                        <Typography>
                            {subscription?.subscription_type.description ?? ""}
                        </Typography>
                        <Typography
                            variant="h5"
                            color="blue-gray"
                            className="mb-2"
                        >
                            {subscription?.subscription_type.name ?? ""}
                        </Typography>
                        <Typography>
                            - File size{" "}
                            {
                                subscription?.subscription_type
                                    .subscription_attribute?.file_size
                            }{" "}
                            MBs
                        </Typography>
                    </CardBody>
                    <CardFooter className="pt-0 flex justify-end">
                        <Typography>
                            {subscription?.subscription_type.duration ?? ""}
                        </Typography>
                    </CardFooter>
                </Card>
            )}
        </>
    );
};

export default UserSubscriptionCard;
