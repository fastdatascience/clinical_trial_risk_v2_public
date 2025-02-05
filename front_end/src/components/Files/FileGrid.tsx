import React from "react"
import FileItem from "./FileItem"
import { IFileGridProps } from "../../utils/types"

const FileGrid: React.FC<IFileGridProps> = ({ documents, setDocuments }) => {
    return (
        <div className="mt-5 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((document) => (
                <FileItem key={document.id} document={document} setDocuments={setDocuments} />
            ))}
        </div>
    )
}

export default FileGrid
