const Security: React.FC = () => {
    return (
        <div className="flex flex-col p-5 flex-wrap space-y-10 w-full">
            <h3 className="font-poppins text-2xl font-semibold">Password</h3>
            <div className="flex flex-col space-y-4 flex-wrap">
                <h3 className="font-poppins text-sm font-semibold">
                    Current Password
                </h3>
                <input
                    type="password"
                    className="outline-none border-none rounded-md h-7 bg-white p-3"
                    disabled
                    placeholder="**********"
                />
                <div className="bg-Midnight_Blue cursor-pointer rounded-full flex flex-wrap justify-center lg:w-[18rem] md:w-[12rem] sm:w-[8rem]">
                    <h3 className="text-white font-poppins pt-1 pb-1">
                        Security Pin
                    </h3>
                </div>
                <h3 className="font-poppins text-xs">
                    Security Pin will be sent to your phone number
                </h3>
            </div>
            <hr />
            <div className="flex flex-col space-y-4">
                <h3 className="font-poppins text-sm font-semibold">
                    Security Pin
                </h3>
                <input
                    type="password"
                    className="outline-none border-none rounded-md h-7 bg-white p-3"
                    placeholder=""
                />
                <div className="bg-emerald-400 cursor-pointer rounded-full flex flex-wrap justify-center items-center lg:w-[18rem] md:w-[12rem] sm:w-[8rem]">
                    <h3 className="text-white font-poppins pt-1 pb-1">
                        Unlock Password
                    </h3>
                </div>
            </div>
            <hr />
            <div className="flex flex-col space-y-4 text-gray-400">
                <h3 className="font-poppins font-semibold text-sm">
                    New password
                </h3>
                <input
                    type="password"
                    className="outline-none border-none rounded-md h-7 p-3 bg-white"
                    disabled
                    placeholder=""
                />
                <h3 className="font-poppins font-semibold text-sm">
                    Re-enter new password
                </h3>
                <input
                    type="password"
                    className="outline-none border-none rounded-md h-7 p-3 bg-white"
                    disabled
                    placeholder=""
                />
                <div className="bg-gray-400 rounded-full flex flex-wrap justify-center items-center lg:w-[18rem] md:w-[12rem] sm:w-[8rem]">
                    <h3 className="text-white font-poppins pt-1 pb-1">
                        Update Password
                    </h3>
                </div>
            </div>
        </div>
    );
};

export default Security;
