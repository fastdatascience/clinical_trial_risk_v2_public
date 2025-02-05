import axios, {
    AxiosError,
    AxiosRequestHeaders,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";
import { AxiosHeaders } from "./types";

export const API_V1 = "api/v1";
export const TOKEN_STORAGE_KEY = "access_token";
export const REFRESH_TOKEN_STORAGE_KEY = "refresh_token";
export const USER_STORAGE_KEY = "user";
export const DEMO_USER = "demo_user";

export const apiConfig = {
    returnRejectedPromiseOnError: true,
    timeout: 30000,
    baseURL: import.meta.env.VITE_API_URL,
    headers: {
        common: {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            Pragma: "no-cache",
            "Content-Type": "application/json",
            Accept: "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    } as AxiosHeaders,
};

/**
 * Return the auth spec header Bearer + Token
 * Check the local storage for the user object and get the token and return the object
 *
 * @returns {object} { Authorization: "Bearer " + user.token }
 */
function authHeader(): object {
    const accessToken = localStorage.getItem(TOKEN_STORAGE_KEY);

    if (accessToken) {
        return { Authorization: `Bearer ${JSON.parse(accessToken)}` };
    } else {
        return {};
    }
}

export const getUserToken = () => {
    let userToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (userToken) {
        try {
            userToken = JSON.parse(userToken);
            return userToken;
        } catch (error) {
            console.error("Error parsing token as JSON:", error);
        }
    } else {
        console.error("Token not found in localStorage.");
    }
};

async function refreshAccessToken() {
    const refreshToken = localStorage.getItem(TOKEN_STORAGE_KEY);

    if (refreshToken) {
        try {
            const response = await axios.post(
                `${import.meta.env.VITE_API_URL}/${API_V1}/auth/refresh-token`,
                {
                    refresh_token: JSON.parse(refreshToken),
                }
            );

            const { access_token } = response.data.data;
            localStorage.setItem(
                TOKEN_STORAGE_KEY,
                JSON.stringify(access_token)
            );
            return access_token;
        } catch (error) {
            console.error("Error refreshing token:", error);
            localStorage.removeItem(TOKEN_STORAGE_KEY);
            localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
            localStorage.removeItem(USER_STORAGE_KEY);
            window.location.reload();
        }
    } else {
        console.error("Refresh token not found in localStorage");
    }
}

function globalAuthInterceptor(request: InternalAxiosRequestConfig) {
    if (Object.keys(authHeader()).length !== 0) {
        request.headers = {
            ...request.headers,
            ...authHeader(),
        } as AxiosRequestHeaders;
    }
    return request;
}

function globalSuccessHandler(response: AxiosResponse) {
    return response;
}

async function globalErrorHandler(error: AxiosError) {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
        _retry?: boolean;
    };

    if (
        error?.response?.status === 401 &&
        originalRequest &&
        !originalRequest._retry
    ) {
        originalRequest._retry = true;
        const newAccessToken = await refreshAccessToken();
        if (newAccessToken) {
            axios.defaults.headers.common[
                "Authorization"
            ] = `Bearer ${newAccessToken}`;
            originalRequest.headers[
                "Authorization"
            ] = `Bearer ${newAccessToken}`;
            return axios(originalRequest);
        }
    }

    return Promise.reject(error);
}

function network() {
    const axiosInstance = axios.create(apiConfig);
    axiosInstance.interceptors.request.use((request) =>
        globalAuthInterceptor(request)
    );
    axiosInstance.interceptors.response.use(
        globalSuccessHandler,
        globalErrorHandler
    );
    return axiosInstance;
}

export { network, authHeader };
