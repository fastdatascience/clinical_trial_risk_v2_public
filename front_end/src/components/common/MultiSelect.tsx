import { Listbox, Transition } from "@headlessui/react";
import { SelectInputProps } from "../../utils/types";
import { FaChevronDown } from "react-icons/fa";
import { IoMdCheckmark } from "react-icons/io";
import { classNames } from "../../utils/utils.ts";

const MultiSelectInput = ({
    placeholder,
    options,
    value,
    disabled = false,
    onChange,
}: SelectInputProps) => {
    return (
        <div className="w-full z-40">
            <Listbox value={value} onChange={onChange} multiple disabled={disabled}>
                <div className="relative mt-1">
                    <Listbox.Button
                        className={classNames(
                            disabled ? "bg-blue-gray-50 cursor-not-allowed" : "cursor-pointer bg-white border border-blue-gray-200",
                            "relative w-full flex flex-wrap gap-1 items-center rounded-large p-3 text-left  sm:text-sm"
                        )}
                    >
                        {Array.isArray(value) && value?.length > 0 ? (
                            value.map((val) => (
                                <span
                                    key={val}
                                    className={classNames(
                                        disabled ? "text-gray-500 border-gray-500" : "text-blue-600 border-blue-400 bg-blue-50",
                                        "border text-xs px-1 rounded"
                                        )}
                                >
                                    {val}
                                </span>
                            ))
                        ) : (
                            <span className="text-gray-500">{placeholder}</span>
                        )}

                        <span className={classNames(
                            disabled ? "text-gray-300" : "",
                            "pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2"
                        )}
                        >
                            <FaChevronDown aria-hidden="true" />
                        </span>
                    </Listbox.Button>
                    <Transition
                        leave="transition ease-in duration-100"
                        leaveFrom="opacity-100"
                        leaveTo="opacity-0"
                    >
                        <Listbox.Options className="z-50 absolute  w-full bg-white rounded-md p-1  text-sm shadow-lg  mt-1 max-h-60 overflow-auto ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                            {options?.map(({ label, value }) => (
                                <Listbox.Option
                                    key={value}
                                    value={value}
                                    className={({ active }) =>
                                        `relative cursor-default select-none py-2 text-left px-5 ${
                                            active
                                                ? "bg-light-green-50 text-blue-600"
                                                : "text-gray-900"
                                        }`
                                    }
                                >
                                    {({ selected }) => (
                                        <>
                                            <span
                                                className={`block text-sm truncate ${
                                                    selected
                                                        ? "font-semibold"
                                                        : "font-normal text-gray-900"
                                                }`}
                                            >
                                                {label}
                                            </span>
                                            {selected && (
                                                <span className="absolute inset-y-0 left-0 flex  items-center pr-3">
                                                    <IoMdCheckmark aria-hidden="true" />
                                                </span>
                                            )}
                                        </>
                                    )}
                                </Listbox.Option>
                            ))}
                        </Listbox.Options>
                    </Transition>
                </div>
            </Listbox>
        </div>
    );
};

export default MultiSelectInput;
