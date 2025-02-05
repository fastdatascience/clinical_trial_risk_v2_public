import {
    Dispatch,
    HTMLInputTypeAttribute,
    ReactNode,
    SetStateAction,
} from "react";
import { AxiosError, AxiosRequestHeaders, AxiosResponse } from "axios";

export interface SidebarLinkType {
    id: string;
    label: string;
    path: string;
    icon: ReactNode;
    tooltipText?: string;
    hasClick?: boolean;
}

export interface InnerSideBarLinkType {
    key: string;
    label: string;
    active: boolean;
}

export interface RepeatedSelectGroupType {
    key: string;
    label: string;
}

export interface RepeatedSwitchGroupType {
    key: string;
    label: string;
    description: string;
}

export interface IAuthLayoutProps {
    children: ReactNode;
}

export interface UserDetailsErrors {
    first_name?: string;
    last_name?: string;
    email?: string;
    password?: string;
    phone_number?: string;
    terms_and_privacy_accepted: boolean;
}

export interface UserType {
    first_name?: string;
    last_name?: string;
    email?: string;
    password: string;
    otp?: string | undefined;
    phone_number?: string;
    terms_and_privacy_accepted: boolean;
    subscribe_to_newsletter?: boolean;
}

// this for google user
export interface User {
    email: string;
    family_name: string;
    given_name: string;
    id: string;
    name: string;
    picture: string;
    verified_email: boolean;
}

export interface UpdatedUser {
    first_name: string;
    last_name: string;
}

export type UserAuthType = {
    payload: string | undefined;
    otp?: string;
    type: OtpSendTo;
};

export interface InputProps {
    inputType?: string;
    name?: string;
    type?: HTMLInputTypeAttribute;
    label?: string;
    error?: boolean;
    readonly?: boolean;
    initialValue: string | number | undefined;
    handleChange?: (e: React.FormEvent<HTMLInputElement>) => void;
    errorMessage?: string;
    min?: number;
    max?: number;
    onBlur?: React.FocusEventHandler<HTMLInputElement> | undefined;
}

export interface IModalProps {
    isOpen: boolean;
    isLoading?: boolean;
    setIsOpen: Dispatch<SetStateAction<boolean>>;
    onDelete?: () => Promise<void>;
}

export interface OtpInputProps {
    value: string;
    valueLength: number;
    onChange: (value: string) => void;
}

// Define a type for custom headers
export interface Headers extends AxiosRequestHeaders {
    "Cache-Control"?: string;
    Pragma?: string;
    "Content-Type"?: string;
    Accept?: string;
    "Access-Control-Allow-Origin"?: string;
}

export type AxiosHeaders = Partial<Headers>;

export enum OtpSendTo {
    EMAIL = "EMAIL",
    PHONE = "PHONE",
}

export interface ITrialCost {
    total_cost: number;
    total_cost_per_participant: number;
}
export interface IDocument {
    document_type: string;
    id: number;
    original_document_name: string;
    cdn_path: string;
    document_size: number;
    created_at: Date;
    cost: ITrialCost;
    trial_risk_score: "LOW" | "MEDIUM" | "HIGH";
}

export interface IHistoryRun {
    document: IDocument;
    result: Result;
    cost: ITrialCost;
    trial_cost_table: ITableRow[];
    trial_risk_table: ITableRow[];
    trial_risk_score: "LOW" | "MEDIUM" | "HIGH";
    trial_risk_score_numeric: number;
    weight_profile?: Weights; // keep it optional for now
}

export interface RunStatus {
    completion: number;
    user_resource_usage: string; // typeof user_resource_usage is DocumentRunStatus when parsed
    run_log: Array<string>;
    cost: ITrialCost;
    trial_cost_table: ITableRow[];
    trial_risk_table: ITableRow[];
    trial_risk_score: "LOW" | "MEDIUM" | "HIGH";
    trial_risk_score_numeric: number;
}

export interface IDocumentData {
    data: IDocument;
}

export interface IFileGridProps {
    documents: IDocument[];
    setDocuments: React.Dispatch<React.SetStateAction<IDocument[]>>;
}

export interface IFileItemProps {
    document: IDocument;
    setDocuments: React.Dispatch<React.SetStateAction<IDocument[]>>;
}

export interface IPaginationProps {
    currentPage: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
    onNextPage: () => void;
    onPreviousPage: () => void;
}

export type HeatmapProps = {
    width: number;
    height: number;
    data: { x: string; y: string; value: number }[];
};

export type HeatmapData = Pick<Condition, "pages"> &
    Partial<Pick<Condition, "annotations">>;

export interface HeatmapCell {
    x: string;
    y: string;
    value: number;
}

export type InteractionData = {
    xLabel: string;
    yLabel: string;
    xPos: number;
    yPos: number;
    value: number;
};

export type RendererProps = {
    width: number;
    height: number;
    data: { x: string; y: string; value: number }[];
    setHoveredCell: (hoveredCell: InteractionData | null) => void;
};

export interface DimensionObject {
    width: number;
    height: number;
    top: number;
    left: number;
    x: number;
    y: number;
    right: number;
    bottom: number;
}

export type UseDimensionsHook = [
    (node: HTMLElement) => void,
    {} | DimensionObject,
    HTMLElement
];

export interface UseDimensionsArgs {
    liveMeasure?: boolean;
}

export interface ServerResponseV1<T> {
    timestamp: number;
    data: T;
    error: null | string;
    errors: null | string[];
}

export interface UserProfileTree {
    user: User;
    user_roles?: UserRole[];
    user_subscription?: UserSubscription;
}

export interface User {
    last_login: Date;
    is_phone_number_verified: boolean;
    updated_at: Date;
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    phone_number: string;
    is_email_verified: boolean;
    profile_picture: string | null | undefined;
    created_at: Date;
}

export interface UserRole {
    id: number;
    name: string;
}

export interface UserSubscription {
    subscription_type_id: number;
    end_date: Date;
    created_at: Date;
    start_date: Date;
    id: number;
    user_id: number;
    subscription_type: SubscriptionType;
}

export interface SubscriptionType {
    price: number;
    id: number;
    name: string;
    description: string;
    duration: string;
    updated_at: Date;
    subscription_attribute: SubscriptionAttribute;
}

export interface SubscriptionAttribute {
    file_size: number;
    subscription_type_id: number;
    updated_at: Date;
    file_processing_limit: number;
}

export enum STATUS {
    QUEUED = "QUEUED",
    IN_PROGRESS = "IN_PROGRESS",
    COMPLETED = "COMPLETED",
    REQUIRES_ACTION = "REQUIRES_ACTION",
    EXPIRED = "EXPIRED",
    CANCELLING = "CANCELLING",
    FAILED = "FAILED",
}

export interface DocumentRunStatus {
    start_time: string;
    user_id: number;
    id: number;
    resource_id: number;
    result: Result;
    resource_type_id: number;
    end_time: string;
    status:
        | "QUEUED"
        | "IN_PROGRESS"
        | "COMPLETED"
        | "REQUIRES_ACTION"
        | "EXPIRED"
        | "CANCELLING"
        | "CANCELLED"
        | "FAILED";
}

export interface Result {
    sap?: Sap;
    drug?: CancerStage;
    phase?: Phase;
    biobank?: Biobank;
    country?: Country;
    duration?: Duration;
    condition?: Condition;
    num_sites?: NumSites;
    num_arms?: Sap;
    num_visits?: Biobank;
    simulation?: Simulation;
    cohort_size?: Biobank;
    sample_size?: SampleSize;
    cancer_stage?: CancerStage;
    effect_estimate?: EffectEstimate;
    num_interventions_total?: Biobank;
    num_interventions_per_visit?: Biobank;
}

export interface SelectInputProps {
    placeholder: string;
    options: Option[] | undefined;
    value?: string | number | string[];
    onChange: (value: string) => void;
}

export interface ResultPrediction {
    [key: string]: {
        prediction: number;
    };
}

export interface Biobank {
    prediction: number;
}

export interface CancerStage {}

export interface Condition {
    annotations: IAnnotation[];
    pages: { [key: string]: number[] };
    score: number;
    terms: { [key: string]: number };
    probas: number[];
    prediction: string;
}

export interface Country {
    pages: { [key: string]: number[] };
    context: { [key: string]: string };
    features: Features;
    prediction: string[];
}

export interface Features {
    jp: Array<Array<number | string>>;
    us: Array<Array<number | string>>;
}

export interface CountryPages {
    jp: number[];
    us: number[];
}

export interface Duration {
    candidates: Array<Array<number | string>>;
    prediction: string;
}

export interface EffectEstimate {
    pages: { [key: string]: number[] };
    score: number;
    context: { [key: string]: string };
    prediction: number;
    page_scores: number[];
}

export interface EffectEstimatePages {
    "10": number[];
    "80": number[];
    detect: number[];
    reduction: number[];
    "cohen's_d/h": { [key: string]: string }[];
    effect_size: { [key: string]: string }[];
    effect_estimate: { [key: string]: string }[];
    "relative_risk/rr": { [key: string]: string }[];
    "odds/hazard/risk_ratio": { [key: string]: string }[];
    "prevention_efficacy/effectiveness": { [key: string]: string }[];
}

export interface NumSites {
    candidates: { [key: string]: string }[];
    prediction: number;
    num_phone_numbers: number;
    num_mentions_multi_site: number;
    num_mentions_single_site: number;
}

export interface Phase {
    pages: { [key: string]: number[] };
    probas: CancerStage;
    context: CancerStage;
    prediction: number;
    probas_corrected: ProbasCorrected;
}

export interface ProbasCorrected {
    phase_0: number;
    phase_1: number;
    phase_2: number;
    phase_3: number;
    phase_4: number;
    "phase_0.5": number;
    "phase_1.5": number;
    "phase_2.5": number;
}

export interface SampleSize {
    pages: { [key: string]: number[] };
    proba: { [key: string]: number };
    score: number;
    comment: string;
    context: { [key: string]: string };
    is_per_arm: { [key: string]: string }[];
    prediction: number;
    is_low_confidence: number;
}

export interface Sap {
    pages: { [key: string]: number[] };
    score: number;
    prediction: number;
    page_scores: number[];
}

export interface Simulation {
    pages: { [key: string]: number[] };
    score: number;
    context: CancerStage;
    prediction: number;
    page_scores: number[];
}

export interface SimulationPages {
    power: number[];
    sample: number[];
    simulate: { [key: string]: string }[];
    scenarios: { [key: string]: string }[];
    sample_size: number[];
}

export interface IAnalysisProps {
    protocolResult: Result | undefined | null;
}

export interface IMetaData {
    modules: string[];
    metadata: Metadata[];
}

export interface Metadata {
    id: string;
    name: string;
    feature_type: string;
    options: Option[];
    prediction?: number;
    default_weights: IModuleWeight;
}

export interface Option {
    label: string;
    value: string | number;
}

export type AuthContextType = {
    isAuthenticated: boolean;
    setIsAuthenticated: (value: boolean) => void;
    logout: () => void;
};

export type AuthProviderProps = {
    children: ReactNode;
};

export type SetAtom<Args extends unknown[], Result> = (...args: Args) => Result;

export interface ITableRow {
    feature: string;
    description?: string;
    value: string | number;
    weight?: string | number;
    score?: string | number;
    formula?: string;
}

export interface IModuleWeight {
    cost: number;
    risk: number;
}

export interface IDefaultWeightProfile {
    contents: Content[];
    previous_page: null;
    next_page: null;
    has_previous: boolean;
    has_next: boolean;
    total: number;
    pages: number;
}

export interface Content {
    weights: Weights;
    updated_at: Date;
    created_at: Date;
    default: boolean;
    id: number;
    name: string;
}

// This is new type
export interface Weights {
    cost_risk_models: { [key: string]: CostRiskModel };
    sample_size_tertiles: SampleSizeTertile[];
    risk_thresholds: RiskThresholds;
}

export interface CostRiskModel {
    cost: number;
    risk: number;
}

export interface RiskThresholds {
    low: number;
    high: number;
}

export interface SampleSizeTertile {
    condition: ConditionType;
    phase: number | ConditionType;
    lower_tertile: number;
    upper_tertile: number;
}

export enum ConditionType {
    Empty = "*",
    TB = "TB",
    POL = "POL",
    NTD = "NTD",
    MAL = "MAL",
    HIV = "HIV",
    EDD = "EDD",
    COVID = "COVID",
}

export interface IWeightProfile {
    name: string;
    weights: Weights;
}

export interface IAnnotation {
    text: string;
    type: string;
    value: Value;
    page_no: number;
    subtype: string;
    end_char: number;
    start_char: number;
}

export interface Value {
    lower: number;
    upper: number;
}

export interface OAuthMessageData {
    type: string;
    data: {
        accessToken: string;
    };
}

export interface OAuthProps {
    googleOAuth2Url: string;
}

export interface IPdfImage {
    image: string;
    pageNumber: number;
}
[];

export interface IPlatformMetadata {
    core_lib_version: string;
    server_version: string;
}

export type ApiResponse = AxiosResponse | AxiosError;
