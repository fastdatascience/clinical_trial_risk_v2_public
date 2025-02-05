import React from "react";
import { Input, Typography } from "@material-tailwind/react";
import { InputProps } from "../../utils/types";

const TextInput: React.FC<InputProps> = ({
    inputType,
    label,
    name,
    error,
    initialValue,
    handleChange,
    errorMessage,
    onBlur,
}) => {
    return (
        <div className="w-full">
            <Input
                type={inputType}
                label={label}
                name={name}
                value={initialValue}
                error={error}
                onChange={handleChange}
                size="lg"
                color="teal"
                crossOrigin={undefined}
                onBlur={onBlur}
                className="truncate"
            />
            <Typography
                variant="small"
                color="gray"
                className="mt-1 flex text-xs"
            >
                {errorMessage && (
                    <p className="text-[10px] text-red-500 mx-1">
                        {errorMessage}
                    </p>
                )}
            </Typography>
        </div>
    );
};

export default TextInput;
