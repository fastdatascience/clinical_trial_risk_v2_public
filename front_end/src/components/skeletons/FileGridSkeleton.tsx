const FileGridSkeleton = () => (
    <div className="mt-5 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 12 }).map((_, index) => (
            <div
                key={index}
                className="border mt-6 rounded-md hover:shadow-xl animate-pulse duration-500"
            >
                {/* Header */}
                <div className="h-8 bg-gray-300 rounded-t-md flex justify-end px-4 py-2"></div>

                {/* Body */}
                <div className="flex justify-center items-center py-6">
                    <div className="h-16 w-16 bg-gray-300 rounded-lg"></div>
                </div>

                {/* Footer */}
                <div className="p-4">
                    <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>{" "}
                    {/* Title */}
                    <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>{" "}
                    {/* File Size */}
                    {/* Cost Section */}
                    <div className="flex justify-between mb-2">
                        <div className="h-3 bg-gray-200 rounded w-2/5"></div>
                        <div className="h-3 bg-gray-200 rounded w-2/5"></div>
                    </div>
                    {/* Risk Section */}
                    <div className="h-3 bg-gray-200 rounded w-1/3 mb-2"></div>
                    {/* Created At */}
                    <div className="h-3 bg-gray-200 rounded w-1/2 mb-4"></div>
                    {/* Buttons */}
                    <div className="flex justify-between">
                        <div className="h-8 w-24 bg-gray-300 rounded"></div>
                        <div className="h-8 w-24 bg-gray-300 rounded"></div>
                    </div>
                </div>
            </div>
        ))}
    </div>
);

export default FileGridSkeleton;
