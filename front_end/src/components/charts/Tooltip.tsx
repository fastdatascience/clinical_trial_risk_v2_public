import { InteractionData } from "../../utils/types";

type TooltipProps = {
    interactionData: InteractionData | null;
    width: number;
    height: number;
};

export const Tooltip = ({ interactionData, width, height }: TooltipProps) => {
    if (!interactionData) {
        return null;
    }

    return (
        // Wrapper div: a rect on top of the viz area
        <div
            style={{
                width,
                height,
                position: "absolute",
                top: 0,
                left: 0,
                pointerEvents: "none",
            }}
        >
            {/* The actual box with dark background */}
            <div
                className={"bg-black text-white"}
                style={{
                    position: "absolute",
                    left: interactionData.xPos,
                    top: interactionData.yPos,
                }}
            >
                <TooltipRow label={"page"} value={interactionData.xLabel} />
                <TooltipRow
                    label={"condition"}
                    value={interactionData.yLabel}
                />
                <TooltipRow
                    label={"occurrences"}
                    value={String(interactionData.value)}
                />
            </div>
        </div>
    );
};

type TooltipRowProps = {
    label: string;
    value: string;
};

const TooltipRow = ({ label, value }: TooltipRowProps) => (
    <div>
        <b>{label}</b>
        <span>: </span>
        <span>{value}</span>
    </div>
);
