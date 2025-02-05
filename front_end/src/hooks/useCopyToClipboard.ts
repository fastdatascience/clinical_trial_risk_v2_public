import { useState } from "react";

/**
 * Custom hook to copy text to the clipboard.
 * @returns [copyToClipboard, { success, error, copied }]
 */
export function useCopyToClipboard(): [
    (text: string) => Promise<void>,
    { success: boolean; error: string | null; copied: boolean }
] {
    const [status, setStatus] = useState<{
        success: boolean;
        error: string | null;
        copied: boolean;
    }>({
        success: false,
        error: null,
        copied: false,
    });

    const copyToClipboard = async (text: string): Promise<void> => {
        try {
            if (!navigator.clipboard) {
                throw new Error(
                    "Clipboard API is not supported by your browser."
                );
            }
            await navigator.clipboard.writeText(text);
            setStatus({ success: true, error: null, copied: true });

            setTimeout(() => {
                setStatus((prev) => ({ ...prev, copied: false }));
            }, 2000);
        } catch (error) {
            setStatus({
                success: false,
                error: (error as Error).message,
                copied: false,
            });
        }
    };

    return [copyToClipboard, status];
}
