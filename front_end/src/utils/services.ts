import { FILES_PER_PAGE } from "./constants";
import {
    UserType,
    UserAuthType,
    IDocument,
    ServerResponseV1,
    DocumentRunStatus,
    RunStatus,
    SetAtom,
    IMetaData,
    Metadata,
    IDefaultWeightProfile,
    IWeightProfile,
    Content,
    Weights,
    IPlatformMetadata,
    IHistoryRun,
    ApiResponse,
    ITemplateDocument,
} from "./types";
import { API_V1, authHeader, network } from "./network";
import { fetchEventSource } from "@microsoft/fetch-event-source";
import { SetStateAction } from "jotai";
import { PDFDocumentProxy } from "pdfjs-dist";
import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

// ======> auth services <======
export const signup = async (payload: UserType): Promise<ApiResponse> => {
    const signupResponse = await network().post(
        `/${API_V1}/auth/signup`,
        payload
    );

    return signupResponse;
};

export const login = async (email: string, password: string) => {
    const loginResponse = await network().post(`/${API_V1}/auth/login`, {
        email,
        password,
    });
    return loginResponse;
};

export const loginSignupWithGoogle = async (
    code: string,
    codeVerifier: string
) => {
    try {
        const response = await network().post(`/${API_V1}/auth/google`, {
            code,
            code_verifier: codeVerifier,
        });
        return response;
    } catch (error) {
        return error;
    }
};

export const verifyEmail = async (authData: UserAuthType) => {
    const { payload, otp, type } = authData;

    const verifyEmailResponse = await network().post(`/${API_V1}/auth/verify`, {
        payload,
        otp,
        type,
    });
    return verifyEmailResponse;
};
export const resendOTP = async (authData: UserAuthType) => {
    const { payload, type } = authData;
    try {
        const resendOtpResponse = await network().post(
            `/${API_V1}/auth/resend/otp`,
            {
                payload,
                type,
            }
        );
        return resendOtpResponse;
    } catch (error) {
        return error;
    }
};

export const resetPassword = async (email: string): Promise<ApiResponse> => {
    const resetPasswordResponse = await network().post(
        `/${API_V1}/auth/password-reset/init`,
        {
            email,
        }
    );
    return resetPasswordResponse;
};

export const recoverPassword = async ({
    otp,
    password,
}: {
    otp: string;
    password: string;
}) => {
    try {
        const resp = await network().post(`/${API_V1}/auth/password-reset`, {
            otp,
            password,
        });
        return resp;
    } catch (error) {
        return error;
    }
};
// ======> auth services ended <======

// ======> PDF processing services  <======
export const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append("document", file);
    const response = await network().post<ServerResponseV1<IDocument>>(
        `/${API_V1}/documents`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );
    return response;
};

export const getRunStatus = async (
    documentId: number,
    setCurrentDocumentId: SetAtom<[SetStateAction<number | null>], void>,
    setDocumentRunResult: SetAtom<[SetStateAction<RunStatus | null>], void>,
    onProgress: (runStatus: DocumentRunStatus) => void,
    setRunLog: SetAtom<[SetStateAction<string[] | []>], void>,
    setUploadProgress: SetAtom<[SetStateAction<number>], void>
) => {
    const headers = authHeader() as Record<string, string>;

    if (Object.entries(headers).length < 1) {
        console.warn("Headers not set");
        return;
    }

    await fetchEventSource(
        `${
            import.meta.env.VITE_API_URL
        }/${API_V1}/documents/${documentId}/run-status`,
        {
            headers: { ...headers, "Accept-Encoding": "identity" },
            onmessage(ev) {
                const data = JSON.parse(ev.data) as RunStatus;
                // we can store the whole thing or seperate
                const {
                    completion,
                    user_resource_usage,
                    run_log,
                    trial_cost_table,
                    trial_risk_table,
                } = data;

                const parsedUserResourceUsage = JSON.parse(
                    user_resource_usage
                ) as DocumentRunStatus;

                const { resource_id } = parsedUserResourceUsage;

                // TODO: check if this causing too many re-renders
                if (resource_id) {
                    setCurrentDocumentId(resource_id);
                }
                if (
                    trial_cost_table &&
                    !!trial_cost_table?.length &&
                    trial_risk_table &&
                    !!trial_risk_table?.length
                ) {
                    // store the whole data globally
                    setDocumentRunResult(data);
                }

                // store run logs globally
                setRunLog(run_log);
                const integerProgress = Math.trunc(completion);

                setUploadProgress(integerProgress);
                onProgress({ ...parsedUserResourceUsage });
            },

            onclose() {
                console.log("Connection closed.");
                // set current doc id back to null as it's processed
                setCurrentDocumentId(null);
            },
        }
    );
};

export const getMetaData = async (
    setMetaData: SetAtom<[SetStateAction<Metadata[] | []>], void>
): Promise<void> => {
    const response = await network().get<ServerResponseV1<IMetaData>>(
        `/${API_V1}/metadata/engine`
    );
    if (response.status === 200) {
        const { metadata } = response.data.data || {};
        //    directly setting state here so it can be used in dashboard
        setMetaData(metadata);
    } else {
        throw new Error(`Unexpected status code: ${response.status}`);
    }
};

export const getHistoryRunResult = async (
    documentId: number,
    setHistoryRunResult: SetAtom<[SetStateAction<IHistoryRun | null>], void>,
    setPdfDocAtom: SetAtom<
        [SetStateAction<PDFDocumentProxy | string | null>],
        void
    >
) => {
    const headers = authHeader() as Record<string, string>;

    if (Object.entries(headers).length < 1) {
        console.warn("Headers not set");
        return;
    }

    try {
        const resp = await network().get<ServerResponseV1<IHistoryRun>>(
            `${
                import.meta.env.VITE_API_URL
            }/${API_V1}/documents/${documentId}/run`,
            { headers: { ...headers } }
        );

        if (resp.status !== 200) return;

        const {
            data: { data },
        } = resp;

        // store full history run data in one state
        if (data) {
            setHistoryRunResult(data);
        }
        setPdfDocAtom(data?.document?.cdn_path);
    } catch (error) {
        return error;
    }
};

export const exportPdfReport = async (document_id: string | number) => {
    const response = await network().get<BlobPart>(
        `/${API_V1}/documents/${document_id}/exports/pdf`,
        {
            responseType: "blob",
            headers: {
                Accept: "application/pdf",
            },
        }
    );
    return response;
};

// ======> PDF processing services ended <======

// ====> document CRUD services <======
export const getDocuments = async (currentPage: number) => {
    try {
        const response = await network().get(
            `/${API_V1}/documents?page_size=${FILES_PER_PAGE}&page=${currentPage}`
        );
        return response;
    } catch (error) {
        return error;
    }
};

export const getCdnUrlForDocument = async (document_id: string | number) => {
    const response = await network().get(
        `/${API_V1}/documents/cdn/${document_id}`
    );
    return response;
};

export const deleteDocument = async (docId: number) => {
    try {
        const response = await network().delete(
            `/${API_V1}/documents/${docId}`
        );
        return response;
    } catch (error) {
        return error;
    }
};

export const getPublicDocuments = async () => {
    const response = await network().get<ServerResponseV1<ITemplateDocument[]>>(
        `/${API_V1}/documents/p/templates`
    );
    return response;
};

export const getPublicDocumentRunResult = async (template_id: number) => {
    const headers = authHeader() as Record<string, string>;

    if (Object.entries(headers).length < 1) {
        console.warn("Headers not set");
        return;
    }

    const response = await network().get<ServerResponseV1<IHistoryRun>>(
        `${
            import.meta.env.VITE_API_URL
        }/${API_V1}/documents/p/templates/${template_id}`,
        { headers: { ...headers } }
    );

    return response;
};

// ====> document CRUD services ended <======

// ====> user services <======
export const getSubscriptionPlans = async () => {
    try {
        const response = await network().get(`/${API_V1}/subscriptions/plans`);
        return response;
    } catch (error) {
        return error;
    }
};

export const getUserSubscription = async () => {
    try {
        const response = await network().get(`/${API_V1}/users/subscriptions`);
        return response;
    } catch (error) {
        return error;
    }
};

export const updateUserSettings = async (payload: import("form-data")) => {
    try {
        const response = await network().post(`/${API_V1}/users`, payload, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        return response;
    } catch (error) {
        return error;
    }
};

export const getUserGoogleProfile = async (accessToken: string | null) => {
    try {
        const response = await axios.get(
            `https://www.googleapis.com/oauth2/v1/userinfo?access_token=${accessToken}`,
            {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    Accept: "application/json",
                },
            }
        );

        return response?.data;
    } catch (error) {
        console.error("Error fetching user info:", error);
        return null;
    }
};

export const deleteUserAccount = async () => {
    const response = await network().delete(`/${API_V1}/users`);
    return response;
};

// ====> user services ended <======

// ====> weight profile services <======
export const getAllDefaultWeightProfiles = async (
    setModuleWeights: SetAtom<[SetStateAction<Weights | undefined>], void>,
    setWeightProfiles: SetAtom<[SetStateAction<Content[] | undefined>], void>
): Promise<IDefaultWeightProfile> => {
    const response = await network().get<
        ServerResponseV1<IDefaultWeightProfile>
    >(`/${API_V1}/weight-profiles`);

    if (response?.status === 200) {
        const { data } = response?.data || {};
        setWeightProfiles(data?.contents);
        const weights = data?.contents?.reduce((acc, content) => {
            return {
                ...acc,
                ...content.weights,
            };
        }, {} as Weights);

        setModuleWeights(weights);
        return data;
    } else {
        throw new Error(`Unexpected status code: ${response.status}`);
    }
};

export const getUserWeightProfiles = async (
    setWeightProfiles: SetAtom<[SetStateAction<Content[] | undefined>], void>
): Promise<Content[]> => {
    const response = await network().get<
        ServerResponseV1<IDefaultWeightProfile>
    >(`/${API_V1}/weight-profiles/users`);

    if (response?.status === 200) {
        const { data } = response?.data || {};
        // // Storing this in global state
        setWeightProfiles(data.contents);
        return data?.contents;
    } else {
        throw new Error(`Unexpected status code: ${response.status}`);
    }
};

export const getWeightProfiles = async (
    setModuleWeights: SetAtom<[SetStateAction<Weights | undefined>], void>,
    setWeightProfiles: SetAtom<[SetStateAction<Content[] | undefined>], void>
): Promise<Content[] | undefined> => {
    const userWeights = await getUserWeightProfiles(setWeightProfiles);

    // if user configured weights exist return those else defaults
    if (userWeights?.length) {
        return userWeights;
    } else {
        const defaultWeights = await getAllDefaultWeightProfiles(
            setModuleWeights,
            setWeightProfiles
        );

        return defaultWeights?.contents;
    }
};

export const createUserWeightProfiles = async (
    weight_profile: IWeightProfile
): Promise<Content> => {
    const {
        name,
        weights: { cost_risk_models, risk_thresholds, sample_size_tertiles },
    } = weight_profile;
    const response = await network().post<ServerResponseV1<Content>>(
        `/${API_V1}/weight-profiles/users`,
        {
            name,
            cost_risk_models,
            risk_thresholds,
            sample_size_tertiles,
        }
    );

    if (response?.status === 201) {
        const { data } = response?.data || {};
        return data;
    } else {
        throw new Error(`Failed to create new profile: ${response.status}`);
    }
};

export const deleteUserWeightProfile = async (
    id: number | undefined,
    weights: AxiosRequestConfig<Weights> | undefined
): Promise<AxiosResponse<void>> => {
    const response = await network().delete(
        `/${API_V1}/weight-profiles/users/${id}`,
        weights
    );
    return response;
};

export const updateUserWeightProfile = async (
    id: number | undefined,
    weights: unknown
): Promise<IDefaultWeightProfile> => {
    const response = await network().patch<
        ServerResponseV1<IDefaultWeightProfile>
    >(`/${API_V1}/weight-profiles/users/${id}`, weights);

    if (response?.status === 200) {
        const { data } = response?.data || {};
        return data;
    } else {
        throw new Error(`Failed to update profile: ${response.status}`);
    }
};
// ====> weight profile services ended <======

// ====> Misc services <====
export const getPlatformMetadata = async (): Promise<
    IPlatformMetadata | undefined
> => {
    try {
        const response = await network().get<
            ServerResponseV1<IPlatformMetadata>
        >(`/${API_V1}/metadata/platform`);
        if (response.status === 200) return response?.data?.data;
    } catch (error) {
        console.error("Error fetching platform metadata:", error);
    }
};
// ====> Misc services ended <====
