import React, { useMemo } from "react";
import { RE_DIGIT } from "../../utils/constants";
import { OtpInputProps } from "../../utils/types";


const OtpInput: React.FC<OtpInputProps> = ({ value, valueLength, onChange }) => {
    const valueItems = useMemo(() => {
        const valueArray = value.split("");
        const items = [];

        for (let i = 0; i < valueLength; i++) {
            const char = valueArray[i];

            if (RE_DIGIT.test(char)) {
                items.push(char);
            } else {
                items.push("");
            }
        }

        return items;
    }, [value, valueLength]);

    const focusToNextInput = (target: HTMLInputElement) => {
        const nextElementSibling = target.nextElementSibling as HTMLInputElement;

        if (nextElementSibling) {
            nextElementSibling.focus();
        }
    };

    const focusToPrevInput = (target: HTMLInputElement) => {
        const previousElementSibling = target.previousElementSibling as HTMLInputElement;

        if (previousElementSibling) {
            previousElementSibling.focus();
        }
    };

    const inputOnKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        const { key } = e;
        const target = e.target as HTMLInputElement;

        if (key === "ArrowRight" || key === "ArrowDown") {
            e.preventDefault();
            return focusToNextInput(target);
        }

        if (key === "ArrowLeft" || key === "ArrowUp") {
            e.preventDefault();
            return focusToPrevInput(target);
        }

        const targetValue = target.value;

        // keep the selection range position
        // if the same digit was typed
        target.setSelectionRange(0, targetValue.length);

        if (e.key !== "Backspace" || targetValue !== "") {
            return;
        }

        focusToPrevInput(target);
    };

    const inputOnFocus = (e: React.FocusEvent<HTMLInputElement>) => {
        const { target } = e;

        // keep focusing back until previous input
        // element has value
        const prevInputEl = target.previousElementSibling as HTMLInputElement;

        if (prevInputEl && prevInputEl.value === "") {
            return prevInputEl.focus();
        }

        target.setSelectionRange(0, target.value.length);
    };

    const inputOnChange = (e: React.ChangeEvent<HTMLInputElement>, idx: number) => {
        const target = e.target;
        let targetValue = target.value.trim();
        const isTargetValueDigit = RE_DIGIT.test(targetValue);

        if (!isTargetValueDigit && targetValue !== "") {
            return;
        }
        const nextInputEl = target.nextElementSibling as HTMLInputElement;

        if (!isTargetValueDigit && nextInputEl && nextInputEl.value !== "") {
            return;
        }

        targetValue = isTargetValueDigit ? targetValue : " ";

        const targetValueLength = targetValue.length;

        if (targetValueLength === 1) {
            const newValue =
                value.substring(0, idx) + targetValue + value.substring(idx + 1);

            onChange(newValue);

            if (!isTargetValueDigit) {
                return;
            }

            focusToNextInput(target);
        } else if (targetValueLength === valueLength) {
            onChange(targetValue);

            target.blur();
        }
    };
    return (
        <>
            {valueItems.map((digit, idx) => (
                <input
                    key={idx}
                    type="text"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    pattern="\d{1}"
                    maxLength={valueLength}
                    style={{ backgroundColor: "#E0ECF8" }}
                    className="flex w-12 h-12  border-none rounded-md text-center text-2xl font-bold leading-none focus:outline-green_primary"
                    value={digit}
                    onChange={(e) => inputOnChange(e, idx)}
                    onKeyDown={inputOnKeyDown}
                    onFocus={inputOnFocus}
                />
            ))}
        </>
    );
};

export default OtpInput;