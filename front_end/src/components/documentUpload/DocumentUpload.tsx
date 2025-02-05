import React from "react";
import { useAtom } from "jotai";
import styles from "../../utils/styles";
import Dropzone from "./Dropzone";
import { isDemoUserAtom } from "../../lib/atoms";
import { Link } from "react-router-dom";

const DocumentUpload: React.FC = () => {
    const [isDemoUser] = useAtom(isDemoUserAtom);

    {
        /* TODO: un-comment this when we have API's  */
    }
    // const [isUploading] = useAtom(isFileUploadingAtom);
    // const [isFileProcessing] = useAtom(isFileProcessingAtom);

    return (
        <div className="bg-green_secondary p-10 drop-shadow-md rounded-large">
            <div className={styles.headingContainer}>
                <h1 className={styles.heading}>
                    Upload your protocol in PDF format
                </h1>
                {isDemoUser && (
                    <p className="text-sm text-text_secondary/70">
                        You can upload up to{" "}
                        <strong className="text-text_secondary">3 files</strong>{" "}
                        as a Guest.{" "}
                        <span className="underline text-text_secondary">
                            <Link to={"/login"}> Log in or sign up</Link>
                        </span>{" "}
                        to unlock more!
                    </p>
                )}
            </div>

            <div className="flex flex-col items-center justify-center mt-3 gap-3">
                {/* for file upload */}
                <div className="w-full gap-3 flex md:flex-row flex-col  justify-between items-center">
                    <div
                        className={
                            "bg-white w-full rounded-large border-dashed border-2 border-Green  h-72 flex justify-center items-center"
                        }
                    >
                        <Dropzone />
                    </div>

                    {/* TODO: un-comment this when we have API's  */}
                    {/* {!isUploading && !isFileProcessing && (
                        <>
                            <div className=" text-text_secondary">OR</div>
                            <div className="md:w-2/5 w-full">
                                {/* Call api and pass file names as options, then send the selected id as query param 
                                <SelectInput
                                    placeholder="Choose a protocol..."
                                    options={[]}
                                    onChange={(value) =>
                                        console.log("value==>", value)
                                    }
                                />
                            </div>
                        </>
                    )} */}
                </div>
            </div>
        </div>
    );
};

export default DocumentUpload;
