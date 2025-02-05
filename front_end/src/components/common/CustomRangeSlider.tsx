import Slider from "@material-tailwind/react/components/Slider";

// TODO: add handle change and here
const CustomRangeSlider = ({ min, max }: { min: number; max: number }) => {
    return (
        <div className="w-full relative mb-8">
            <Slider
                defaultValue={max}
                min={min}
                max={max}
                size="sm"
                className="text-green_primary my-2"
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
