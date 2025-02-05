import React from "react";
import { Input } from "@material-tailwind/react";
import { InputProps } from "../../utils/types";

const CustomTextField: React.FC<InputProps> = ({
    initialValue = "",
    type = "text",
    readonly = true,
    handleChange,
    min,
    max,
}) => {
    return (
        <div className="w-full">
            <Input
                size="md"
                color="teal"
                value={initialValue}
                className="rounded-full bg-white border-none"
                crossOrigin={undefined}
                readOnly={readonly}
                type={type}
                onChange={handleChange}
                min={min}
                max={max}
            />
        </div>
    );
};

export default CustomTextField;
