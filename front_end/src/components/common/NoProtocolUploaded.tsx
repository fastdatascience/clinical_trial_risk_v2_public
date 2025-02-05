import React from "react"
import logo from "../../assets/logo.svg"

const NoProtocolUploaded: React.FC = () => {
    return (
        <div className=" flex flex-col  md:h-96 justify-center items-center gap-6">
            <div className="flex justify-center items-center opacity-50 ">
                <img src={logo} alt="Fast Data Science" loading="lazy" className="object-contain" width={300} height={45} />
            </div>
            <p className="text-sm text-text_secondary break-words">Drag and Drop a PDF protocol into the box above</p>
        </div>
    )
}

export default NoProtocolUploaded