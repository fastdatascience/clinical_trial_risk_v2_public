const PdfImagesSkeleton = () => {
    return (
        <div className="w-full h-80  flex overflow-x-auto p-5 space-x-5">
            {Array(5)
                .fill(0)
                .map((_, index) => (
                    <div
                        key={index}
                        className="max-w-sm p-4 border rounded-xl  bg-white  border-gray-300 shadow animate-pulse md:p-6"
                    >
                        <div className="h-2.5 bg-gray-300 rounded-full  w-48 mb-4"></div>
                        <div className="h-2 bg-gray-300 rounded-full  mb-2.5"></div>
                        <div className="h-2 bg-gray-300 rounded-full  mb-2.5"></div>

                        <div className="flex items-center mt-4 mb-4">
                            <div>
                                <div className="h-2.5 bg-gray-300 rounded-full  w-32 mb-2"></div>
                                <div className="w-48 h-2 bg-gray-300 rounded-full "></div>
                            </div>
                        </div>
                        <div className="h-2.5 bg-gray-300 rounded-full  w-48 mb-4"></div>
                        <div className="h-2 bg-gray-300 rounded-full  mb-2.5"></div>
                        <div className="h-2 bg-gray-300 rounded-full  mb-2.5"></div>

                        <div className="flex items-center mt-4 mb-4">
                            <div>
                                <div className="h-2.5 bg-gray-300 rounded-full  w-32 mb-2"></div>
                                <div className="w-48 h-2 bg-gray-300 rounded-full "></div>
                            </div>
                        </div>
                        <span className="sr-only">Loading...</span>
                    </div>
                ))}
        </div>
    );
};

export default PdfImagesSkeleton;
