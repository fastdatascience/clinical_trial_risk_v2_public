import React from "react";
import { Listbox, Transition } from "@headlessui/react";
import { FaChevronDown } from "react-icons/fa";
import type { SelectInputProps } from "../../utils/types";

const SelectInput: React.FC<SelectInputProps> = ({
    placeholder,
    options,
    value,
    onChange,
}) => {
    const selectedOption = options?.find((option) => option.value === value);
    const displayValue = selectedOption ? selectedOption.label : value;

    return (
        <div className="w-full z-40">
            <Listbox value={value} onChange={onChange}>
                <div className="relative mt-1">
                    <Listbox.Button
                        className={
                            "relative w-full flex border border-blue-gray-200  cursor-pointer items-center rounded-large h-10 p-3 text-left bg-white sm:text-sm"
                        }
                    >
                        <span
                            className={`block truncate ${
                                displayValue ? "text-gray-800" : "text-gray-500"
                            }  font-normal`}
                        >
                            {displayValue ?? placeholder}
                        </span>
                        <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                            <FaChevronDown aria-hidden="true" />
                        </span>
                    </Listbox.Button>
                    <Transition
                        leave="transition ease-in duration-100"
                        leaveFrom="opacity-100"
                        leaveTo="opacity-0"
                    >
                        {!!options?.length && (
                            <Listbox.Options className="z-40 absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                                {options?.map(({ label, value }) => (
                                    <Listbox.Option
                                        key={value}
                                        className={({ active }) =>
                                            `relative cursor-default select-none py-2 text-left px-5  ${
                                                active
                                                    ? " bg-light-green-50  text-blue-600"
                                                    : "text-gray-900"
                                            }`
                                        }
                                        value={value}
                                    >
                                        <span
                                            className={
                                                "block truncate capitalize  font-normal"
                                            }
                                        >
                                            {label}
                                        </span>
                                    </Listbox.Option>
                                ))}
                            </Listbox.Options>
                        )}
                    </Transition>
                </div>
            </Listbox>
        </div>
    );
};

export default SelectInput;
