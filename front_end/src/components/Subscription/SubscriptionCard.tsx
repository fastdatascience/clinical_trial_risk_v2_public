import React from "react";
import { useNavigateParams } from "../../hooks/useNavigateParams";
import { objectToQueryString } from "../../utils/utils";
import { SubscriptionType } from "../../utils/types";

interface ISubscriptionCardProps {
    subscriptionPlan: SubscriptionType;
}

const SubscriptionCard: React.FC<ISubscriptionCardProps> = ({ subscriptionPlan }) => {
    const { id, name, price, description, duration, subscription_attribute } = subscriptionPlan;

    const selectedSubs = {
        id,
        name,
        price,
        description,
        duration
    };
    const navigate = useNavigateParams();

    const navigateHandler = () => {
        const queryParam = objectToQueryString(selectedSubs);
        navigate("/register", { queryParam });
    };

    return (
        <div className="col-span-1 px-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-lg border-t-4 border-green_primary transition duration-300 ease-in-out transform hover:scale-105 cursor-pointer hover:shadow-sm">
                <p className="uppercase text-sm font-medium text-gray-500">
                    {name === "FREE" ? "Starter" : name}
                </p>
                {name === "FREE" ? (
                    <p className="mt-4 text-3xl text-gray-800 font-semibold">
                        {name}
                    </p>
                ) :
                    (
                        <div className="mt-4">
                            <span className="text-4xl font-bold text-gray-800">${price}</span>
                            <span className="text-gray-600">/month</span>
                        </div>
                    )
                }
                <p className="mt-4 capitalize font-medium text-gray-700">
                    {`Upload ${description}`}
                </p>
                <ul className="mt-6 space-y-2 flex flex-col">
                    <li className="inline-flex items-center text-gray-600">
                        <svg className="w-4 h-4 mr-2 fill-current text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                            <path d="M256 0C114.6 0 0 114.6 0 256s114.6 256 256 256s256-114.6 256-256S397.4 0 256 0zM371.8 211.8l-128 128C238.3 345.3 231.2 348 224 348s-14.34-2.719-19.81-8.188l-64-64c-10.91-10.94-10.91-28.69 0-39.63c10.94-10.94 28.69-10.94 39.63 0L224 280.4l108.2-108.2c10.94-10.94 28.69-10.94 39.63 0C382.7 183.1 382.7 200.9 371.8 211.8z"></path>
                        </svg>

                        {subscription_attribute?.file_processing_limit === 1 ? `${subscription_attribute.file_processing_limit} Document per day` : `${subscription_attribute?.file_processing_limit} Documents per day`}
                    </li>
                    <li className="inline-flex items-center text-gray-600">
                        <svg className="w-4 h-4 mr-2 fill-current text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
                            <path d="M256 0C114.6 0 0 114.6 0 256s114.6 256 256 256s256-114.6 256-256S397.4 0 256 0zM371.8 211.8l-128 128C238.3 345.3 231.2 348 224 348s-14.34-2.719-19.81-8.188l-64-64c-10.91-10.94-10.91-28.69 0-39.63c10.94-10.94 28.69-10.94 39.63 0L224 280.4l108.2-108.2c10.94-10.94 28.69-10.94 39.63 0C382.7 183.1 382.7 200.9 371.8 211.8z"></path>
                        </svg>
                        File size <span className="font-semibold mx-1">{subscription_attribute?.file_size}MB</span>
                    </li>
                </ul>
                <div className="mt-8">
                    <button onClick={navigateHandler} className="block w-full rounded-full bg-green_primary hover:bg-green_primary/90 text-white font-semibold text-center py-2 transition duration-300 ">Get Started</button>
                </div>
            </div>
        </div>
    );
};

export default SubscriptionCard;
