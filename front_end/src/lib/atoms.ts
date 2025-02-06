import { atom } from "jotai";
import {
    Content,
    IHistoryRun,
    IPlatformMetadata,
    ITableRow,
    Metadata,
    Result,
    RunStatus,
    User,
    UserProfileTree,
    UserType,
    Weights,
} from "../utils/types";
import { atomWithStorage } from "jotai/utils";
import { PDFDocumentProxy } from "pdfjs-dist";

const userAtom = atom<UserType>({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    phone_number: "",
    terms_and_privacy_accepted: false,
});

// Passing these directly instead of importing from constants because order of execution was causing accessing before initialized issue
const userProfileAtom = atomWithStorage<UserProfileTree | null>("user", null);
const userAuthProfileAtom = atomWithStorage<User | null>("user", null);
const userAccessTokenAtom = atomWithStorage<string | null>(
    "access_token",
    null
);
const isDemoUserAtom = atomWithStorage<boolean>("demo_user", false);
const userRefreshTokenAtom = atomWithStorage("refresh_token", null);
const processResultAtom = atom<Result | object>({});
const trialCostTableAtom = atom<ITableRow[] | []>([]);
const metaDataAtom = atom<Metadata[] | []>([]);
const moduleWeightAtom = atom<Weights | object>({});
const weightProfilesAtom = atom<Content[] | undefined>([]);
const runLogs = atom<Array<string> | []>([]);
const selectedParamAtom = atom<{ [key: string]: string }>({});
const pdfDocAtom = atom<PDFDocumentProxy | string | null>(null);
const selectFeatureAtom = atom<string>("condition");
const showPdfViewer = atom<boolean>(false);
const isFileUploadingAtom = atom<boolean>(false);
const isFileProcessingAtom = atom<boolean>(false);
const filteredWeightProfilesAtom = atom<Content[] | undefined>([]);
const platformAtom = atom<IPlatformMetadata | undefined>(undefined);
const historyRunResultAtom = atom<IHistoryRun | null>(null);
const documentRunResultAtom = atom<RunStatus | null>(null);
const uploadProgressAtom = atom<number>(0);
const documentIdAtom = atom<number>(0);
const docInProgressIdAtom = atom<number | null>(null);

export {
    runLogs,
    userAtom,
    pdfDocAtom,
    metaDataAtom,
    platformAtom,
    showPdfViewer,
    documentIdAtom,
    isDemoUserAtom,
    userProfileAtom,
    moduleWeightAtom,
    selectFeatureAtom,
    processResultAtom,
    selectedParamAtom,
    trialCostTableAtom,
    weightProfilesAtom,
    uploadProgressAtom,
    docInProgressIdAtom,
    userAccessTokenAtom,
    userAuthProfileAtom,
    isFileUploadingAtom,
    isFileProcessingAtom,
    userRefreshTokenAtom,
    historyRunResultAtom,
    documentRunResultAtom,
    filteredWeightProfilesAtom,
};
