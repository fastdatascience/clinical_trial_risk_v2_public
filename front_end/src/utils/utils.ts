import { getDocument, GlobalWorkerOptions } from "pdfjs-dist";

import { EMAIL_REGEX, formulaLookup } from "./constants";
import {
    HeatmapCell,
    HeatmapData,
    Content,
    Metadata,
    Option,
    Result,
    UserProfileTree,
    ITableRow,
} from "./types";

GlobalWorkerOptions.workerSrc = "./pdf.worker.min.mjs";

export const MARGIN = { top: 10, right: 50, bottom: 30, left: 50 };

export function snakeCaseToNormal(input: string): string {
    return input
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}

export interface UserDetailsErrors {
    first_name?: string;
    last_name?: string;
    email?: string;
    password?: string;
    phone_number?: string;
    terms_and_privacy_accepted?: boolean;
}

export interface FormErrors {
    [key: string]: string;
}

export const validateFormData = (
    inputs: UserDetailsErrors,
    serverErrors: string[] = []
): FormErrors => {
    const errors: FormErrors = {};

    // Client-side validation
    for (const [fieldName, value] of Object.entries(inputs)) {
        const formattedFieldName = snakeCaseToNormal(fieldName);

        if (!value) {
            errors[
                `${fieldName}Error`
            ] = `${formattedFieldName} should not be empty`;
        } else if (fieldName === "first_name" && value?.length < 3) {
            errors[
                `${fieldName}Error`
            ] = `${formattedFieldName} must be longer than or equal to 3 characters`;
        } else if (fieldName === "email" && !EMAIL_REGEX.test(value)) {
            errors[
                `${fieldName}Error`
            ] = `${formattedFieldName} must be a valid email`;
        } else if (fieldName === "phone_number" && value.length < 10) {
            errors[
                `${fieldName}Error`
            ] = `${formattedFieldName} must be a valid phone number`;
        }
    }

    if (!inputs.terms_and_privacy_accepted) {
        errors["terms_and_privacy_acceptedError"] =
            "You must accept the terms and privacy policy.";
    }

    // Server-side validation
    if (serverErrors.length > 0) {
        serverErrors.forEach((error) => {
            const fieldMatch = error.split(":")[0]?.split(".")[1]; // Extract field name from "body.field_name"
            const errorMessage = error.split(":")[1]?.trim(); // Extract the error message

            if (fieldMatch && errorMessage) {
                errors[`${fieldMatch}Error`] = errorMessage;
            }
        });
    }
    return errors;
};

export const bytesToHuman = (bytes: number) => {
    const units = ["B", "Kb", "Mb"];
    let i = 0;

    for (i; bytes > 1024; i++) {
        bytes /= 1024;
    }
    return parseFloat(bytes.toFixed(0)) + " " + units[i];
};

export const objectToQueryString = (obj: {
    [key: string | number]: string | number;
}) => {
    const keys = Object.keys(obj);
    const keyValuePairs = keys.map((key) => {
        return encodeURIComponent(key) + "=" + encodeURIComponent(obj[key]);
    });
    return keyValuePairs.join("&");
};

export const getInitialValue = (
    label: string,
    protocolResult?: Result | null
) => {
    switch (label) {
        case "Trial is for condition":
            return protocolResult?.condition?.prediction;
        case "Trial phase":
            return protocolResult?.phase?.prediction;
        case "Has the statistical analysis plan been completed?":
            return protocolResult?.sap?.prediction === 0
                ? "No"
                : protocolResult?.sap?.prediction === 1
                ? "Yes"
                : "";
        case "Has the Effect estimate been disclosed?":
            return protocolResult?.effect_estimate?.prediction === 0
                ? "No"
                : protocolResult?.effect_estimate?.prediction === 1
                ? "Yes"
                : "";
        case "Number of subjects":
            return protocolResult?.sample_size?.prediction;
        case "Number of arms":
            return protocolResult?.sample_size?.prediction;
        case "Countries of investigation":
            return protocolResult?.country?.prediction[0]; // can be multiple fix this
        case "Trial uses simulation for sample size?":
            return protocolResult?.simulation?.prediction === 0
                ? "No"
                : protocolResult?.simulation?.prediction === 1
                ? "Yes"
                : "";
        default:
            return ""; // Default value for other labels
    }
};

export const loadPDFDocument = (file: File) => {
    return new Promise((resolve, reject) => {
        try {
            const uri = URL.createObjectURL(file);
            getDocument({ url: uri })
                .promise.then((_PDF_DOC) => {
                    resolve(_PDF_DOC);
                })
                .catch((error) => {
                    console.error("Failed to load PDF document:", error);
                    reject(error);
                });
        } catch (error) {
            console.error("Failed to load PDF document:", error);
            reject(error);
        }
    });
};

export function megabytesToBytes(mb: number) {
    const BYTES_IN_ONE_MB = 1048576;
    return mb * BYTES_IN_ONE_MB;
}

export const getMaxFileSize = (userProfile: UserProfileTree | null) => {
    const subscriptionAttributes =
        userProfile?.user_subscription?.subscription_type
            ?.subscription_attribute;

    return subscriptionAttributes?.file_size ?? 500; // Default to 500MB if not specified
};

export const createFormulasArray = (
    metadata: Metadata[]
): { id: string; formula: string }[] => {
    return metadata.map((meta) => ({
        id: meta.id,
        formula: formulaLookup.get(meta.id) ?? "_", // Use formula from lookup map or default to "_"
    }));
};

export const removeDuplicates = (metadata: Metadata[]) => {
    const uniqueMetaData = metadata?.filter(
        (item, index, self) =>
            index === self.findIndex((meta) => meta.id === item.id)
    );

    return uniqueMetaData;
};

export const processMetadataAndResult = (
    metadataArray: Metadata[],
    resultObject: Result | object
) => {
    if (!metadataArray || !resultObject) {
        console.error("Metadata or result is missing");
        return [];
    }

    const uniqueMetaData = removeDuplicates(metadataArray);

    return uniqueMetaData?.map((metadata) => {
        const key = metadata.id;
        const result = resultObject as Result;

        if (!(key in result)) {
            console.error(`'${key}' not found in resultObject`);
            return metadata;
        }
        const data = result[key as keyof Result] as Metadata;

        if (data?.prediction !== null) {
            return { ...metadata, prediction: data.prediction };
        } else {
            return metadata;
        }
    });
};

export const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
    }).format(value);
};

// TODO: make it reusable
export const generateDropdownOptions = (
    data: Content[] | undefined
): Option[] | undefined => {
    return data?.map((content) => ({
        label: content.name,
        value: content.name,
    }));
};

// Using this for now
export const generateOptions = (data: string[]): Option[] => {
    return data?.map((content) => ({
        label: content,
        value: content,
    }));
};

// this util function will utilise pages, annotations and normalize the data for heatmap
export function normalizeDataForHeatmap(
    data: HeatmapData,
    rangeSize: number = 10
): HeatmapCell[] {
    if (!data?.pages) {
        return [];
    }

    const { pages } = data;

    const heatmapCells: HeatmapCell[] = [];

    // First, Iterate over the keys in the pages object (Y-axis labels)
    Object.keys(pages).forEach((label) => {
        const pageArray = pages[label];
        const pageCountMap: { [range: string]: number } = {};

        // Count the occurrences of each page number
        pageArray?.forEach((pageIndex) => {
            const pageNo = pageIndex + 1;
            const rangeStart =
                Math.floor((pageNo - 1) / rangeSize) * rangeSize + 1; // Calculate range start
            const rangeEnd = rangeStart + rangeSize - 1; // Calculate range end
            const xLabel = `${rangeStart}-${rangeEnd}`;
            pageCountMap[xLabel] = (pageCountMap[xLabel] || 0) + 1;

            // Create heatmap entry for each page and label combination
            heatmapCells.push({
                x: xLabel,
                y: label,
                value: pageCountMap[xLabel],
            });
        });
    });

    return heatmapCells;
}

function base64URLEncode(str: ArrayBuffer): string {
    return btoa(String.fromCharCode(...new Uint8Array(str)))
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

export async function generateGoogleCodeVerifierAndChallenge() {
    const codeVerifier = base64URLEncode(
        crypto.getRandomValues(new Uint8Array(32))
    );
    const encoder = new TextEncoder();
    const data = encoder.encode(codeVerifier);
    const digest = await crypto.subtle.digest("SHA-256", data);
    const codeChallenge = base64URLEncode(digest);
    return { codeVerifier, codeChallenge };
}

export function constructUrl(path: string) {
    const protocol = window.location.protocol;

    const hostname = window.location.host;

    const normalizedPath = path.startsWith("/") ? path : `/${path}`;

    return `${protocol}//${hostname}${normalizedPath}`;
}

/**
 * - Replaces the description for `feature` values "age=lower" and "age=upper" with "Lower" and "Upper" respectively.
 * - Keeps the rest of the properties same.
 *
 * @param trialCostTable - An array of table row objects (ITableRow[]) to transform.
 * @returns A new array of table rows with updated descriptions for specific features.
 */

export function updateFeatureDescriptions(
    trialCostTable: ITableRow[]
): ITableRow[] {
    return trialCostTable?.map((entry) => {
        let transformedDescription = entry.description;

        if (entry.feature === "age=lower") {
            transformedDescription = "Lower";
        } else if (entry.feature === "age=upper") {
            transformedDescription = "Upper";
        }

        return {
            ...entry,
            description: transformedDescription,
        };
    });
}

// helper for now
export const renderObjectKeysWithValues = (
    obj: { [key: string]: number } | undefined
): string => {
    if (!obj) return "";
    return Object.entries(obj)
        .map(([key, value]) => `${key}: ${value}`)
        .join(", ");
};

export const getProfilePictureUrl = (
    profilePicture: string | null | undefined,
    defaultAvatar: string
) => {
    if (!profilePicture) {
        return defaultAvatar;
    }

    if (profilePicture.startsWith("http")) {
        return profilePicture;
    }

    return `https://d1zouhzy7fucw3.cloudfront.net/images/${profilePicture}`;
};
