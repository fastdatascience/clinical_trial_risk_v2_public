import Slider from "@material-tailwind/react/components/Slider";
import { classNames } from "../../utils/utils.ts";

// TODO: add handle change and here
const CustomRangeSlider = ({ min, max, disabled = false }: { min: number; max: number, disabled?: boolean }) => {
    return (
        <div className={classNames(
            disabled ? "cursor-not-allowed" : "",
            "w-full relative mb-8"
        )}
        >
            <Slider
                defaultValue={disabled ? 0 : max}
                min={disabled ? 0 : min}
                max={disabled ? 0 : max}
                size="sm"
                thumbClassName={disabled ? "!cursor-not-allowed" : ""}
                barClassName={disabled ? "!cursor-not-allowed" : ""}
                trackClassName={disabled ? "!cursor-not-allowed" : ""}
                className={classNames(
                    disabled ? "text-gray-500" : "text-green_primary",
                    "my-2"
                )}
            />
            <span className="text-xs text-text_secondary  absolute start-0 -bottom-5">
                Min: ({min})
            </span>

            <span className="text-xs text-text_secondary  absolute end-0 -bottom-5">
                Max: ({max})
            </span>
        </div>
    );
};

export default CustomRangeSlider;
