import React, { useState } from "react";
import { Button, Input, Typography } from "@material-tailwind/react";
import { InputProps } from "../../utils/types";
import { AiFillEye, AiFillEyeInvisible } from "react-icons/ai";

const PasswordInput: React.FC<InputProps> = ({
    name,
    label,
    error,
    initialValue,
    handleChange,
    errorMessage,
    onBlur,
}) => {
    const [showPassword, setShowPassword] = useState<boolean>(false);

    return (
        <div className="flex flex-col">
            <div className="relative flex w-full max-w-[24rem]">
                <Input
                    name={name}
                    error={error}
                    value={initialValue}
                    onChange={handleChange}
                    type={showPassword ? "text" : "password"}
                    size="lg"
                    color="teal"
                    label={label}
                    className="pr-20"
                    containerProps={{
                        className: "min-w-0",
                    }}
                    crossOrigin={undefined}
                    onBlur={onBlur}
                />
                <Button
                    size="sm"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="!absolute right-1 top-2 rounded bg-transparent shadow-none hover:shadow-none"
                >
                    {showPassword ? (
                        <AiFillEyeInvisible
                            size={16}
                            className="text-gray-500"
                        />
                    ) : (
                        <AiFillEye size={15} className="text-gray-500" />
                    )}
                </Button>
            </div>

            <Typography
                variant="small"
                color="gray"
                className="mt-2 flex items-center justify-start text-xs gap-1"
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

export default PasswordInput;
