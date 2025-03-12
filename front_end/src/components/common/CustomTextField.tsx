import React from "react";
import { Input } from "@material-tailwind/react";
import { InputProps } from "../../utils/types";
import { classNames } from "../../utils/utils.ts";

const CustomTextField: React.FC<InputProps> = ({
    initialValue = "",
    type = "text",
    readonly = true,
    handleChange,
    min,
    max,
    disabled = false,
}) => {
    return (
        <div className="w-full">
            <Input
                size="md"
                color="teal"
                value={initialValue}
                className={classNames(
                    disabled ? "text-gray-500" : "",
                    "rounded-full bg-white !border !border-blue-gray-200 focus:outline-1 mt-1"
                )}
                crossOrigin={undefined}
                readOnly={readonly}
                type={type}
                onChange={handleChange}
                min={min}
                max={max}
                disabled={disabled}
                labelProps={{
                    className: "hidden",
                }}
            />
        </div>
    );
};

export default CustomTextField;
