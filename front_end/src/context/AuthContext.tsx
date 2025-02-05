import { useEffect, useState, createContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContextType, AuthProviderProps } from "../utils/types";
import {
    DEMO_USER,
    REFRESH_TOKEN_STORAGE_KEY,
    TOKEN_STORAGE_KEY,
    USER_STORAGE_KEY,
} from "../utils/network";
import {
    documentIdAtom,
    historyRunResultAtom,
    metaDataAtom,
    runLogs,
    showPdfViewer,
} from "../lib/atoms";
import { useAtom } from "jotai";

export const AuthContext = createContext<AuthContextType>({
    isAuthenticated: false,
    setIsAuthenticated: () => {},
    logout: () => {},
});

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const navigate = useNavigate();
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [, setPdfViewer] = useAtom(showPdfViewer);
    const [, setHistoryRunResult] = useAtom(historyRunResultAtom);
    const [, setMetaData] = useAtom(metaDataAtom);
    const [, setRunLogs] = useAtom(runLogs);
    const [, setDocumentId] = useAtom(documentIdAtom);

    const isUserLoggedIn = () => {
        const token = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (token) {
            setIsAuthenticated(true);
        }
    };

    useEffect(() => {
        isUserLoggedIn();
    }, []);

    const clearStates = () => {
        setPdfViewer(false);
        setMetaData([]);
        setRunLogs([]);
        setHistoryRunResult(null);
        setDocumentId(0);
    };

    const logout = () => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        localStorage.removeItem(USER_STORAGE_KEY);
        localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
        localStorage.removeItem(DEMO_USER);
        setIsAuthenticated(false);
        clearStates();
        navigate("/login", { replace: true });
    };

    const authContextValue = {
        isAuthenticated,
        setIsAuthenticated,
        logout,
    };

    return (
        <AuthContext.Provider value={authContextValue}>
            {children}
        </AuthContext.Provider>
    );
};
