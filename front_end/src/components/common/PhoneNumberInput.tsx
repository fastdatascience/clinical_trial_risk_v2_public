import "react-phone-number-input/style.css";
import PhoneInput from "react-phone-number-input";
import Typography from "@material-tailwind/react/components/Typography";

type PhoneInputProps = {
    initialValue: string | undefined;
    handleChange: (value?: string | undefined) => void;
    errorMessage?: string;
    onBlur?: React.FocusEventHandler<HTMLInputElement> | undefined;
};

const PhoneNumberInput = ({
    initialValue = "",
    handleChange,
    errorMessage,
    onBlur,
}: PhoneInputProps) => {
    return (
        <div className="w-full">
            <PhoneInput
                defaultCountry="US"
                placeholder="Enter phone number"
                value={initialValue}
                onChange={handleChange}
                onBlur={onBlur}
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

export default PhoneNumberInput;
