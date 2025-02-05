import React, { useEffect, useState } from "react"
import { getSubscriptionPlans } from "../../utils/services";
import { AxiosResponse } from "axios";
import SubscriptionCard from "../Subscription/SubscriptionCard";
import { Spinner } from "@material-tailwind/react";
import { SubscriptionType } from "../../utils/types";
// import AuthLayout from "../sharedLayout/AuthLayout";

const SubscriptionPlans: React.FC = () => {
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [subscriptionPlans, setSubscriptionPlans] = useState<SubscriptionType[]>([]);

    const getAllSubscriptions = async () => {
        try {
            setIsLoading(true);
            const response = await getSubscriptionPlans() as AxiosResponse;
            if (response.status !== 200) {
                return;
            }
            const subscription_plans = response.data?.data;
            setSubscriptionPlans(subscription_plans)
            setIsLoading(false);
        } catch (error) {
            setIsLoading(false);
            console.error("An Error Occurred while fetching Subscription", error)
        }
    }

    useEffect(() => {
        getAllSubscriptions();
    }, [])

    return (
        <div className='flex justify-center items-center lg:h-screen md:h-screen  py-12'>
            <div className="w-full px-4 sm:px-6 lg:px-8">
                {isLoading ? (
                    <div className="flex justify-center items-center">
                        <Spinner color="green" className="h-12 w-12" />
                    </div>

                ) :
                    (
                        <div className="grid lg:grid-cols-4 md:grid-cols-2 grid-cols-1 -mx-4">
                            {subscriptionPlans.map((plan) => (
                                <SubscriptionCard key={plan.id} subscriptionPlan={plan} />
                            ))}
                        </div>
                    )
                }
            </div>
        </div>
    )
}

export default SubscriptionPlans
