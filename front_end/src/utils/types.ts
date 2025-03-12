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
    disabled?: boolean;
}

export interface IModalProps {
    isOpen: boolean;
    isLoading?: boolean;
    setIsOpen: Dispatch<SetStateAction<boolean>>;
    onDelete?: () => Promise<void>;
}

export interface OtpInputProps {
    isError?: boolean;
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

export interface ITemplateDocument
    extends Omit<IDocument, "cost" | "trial_risk_score" | "cdn_path"> {
    system_assigned_name: string;
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
    data: { x: string; y: string; value: number }[];
};

export type HeatMapData<T> = {
    pages: { [key: string]: T };
};

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
    age?: Age;
    ner?: Ner;
    sap?: Sap;
    drug?: Drug;
    ppie?: Biobank;
    chemo?: Chemo;
    child?: Child;
    phase?: Phase;
    design?: Consent;
    gender?: Gender;
    biobank?: Biobank;
    consent?: Consent;
    country?: Country;
    healthy?: Healthy;
    interim?: Biobank;
    placebo?: Biobank;
    recency?: Recency;
    regimen?: Regimen;
    vaccine?: Vaccine;
    adjuvant?: Adjuvant;
    duration?: Duration;
    hospital?: Hospital;
    num_arms?: NumArms;
    condition?: Condition;
    num_sites?: NumSites;
    radiation?: Radiation;
    num_visits?: Num;
    prevalence?: Biobank;
    simulation?: Simulation;
    cancer_type?: CancerType;
    cohort_size?: Biobank;
    sample_size?: SampleSize;
    cancer_stage?: CancerStage;
    document_type?: DocumentType;
    num_endpoints?: NumEndpoints;
    randomisation?: Consent;
    model_informed?: Biobank;
    overnight_stay?: Biobank;
    platform_trial?: Consent;
    effect_estimate?: EffectEstimate;
    human_challenge?: Biobank;
    master_protocol?: Consent;
    control_negative?: Biobank;
    regimen_duration?: RegimenDuration;
    intervention_type?: InterventionType;
    num_interventions_total?: Num;
    num_interventions_per_visit?: Num;
}

export interface Adjuvant {
    pages: AdjuvantPages;
    prediction: PredictionEnum;
    annotations: Annotation[];
}

export interface Annotation {
    text: string;
    type: PredictionEnum;
    page_no: number;
    subtype?: string;
    end_char: number;
    start_char: number;
    value?: ValueClass | string;
}

export enum PredictionEnum {
    Adjuvant = "adjuvant",
    Age = "age",
    CancerStage = "cancer_stage",
    CancerType = "cancer_type",
    Child = "child",
    Condition = "condition",
    Drug = "drug",
    Duration = "duration",
    Exclusion = "exclusion",
    Gender = "gender",
    Healthy = "healthy",
    Hospital = "hospital",
    Inclusion = "inclusion",
    InterventionType = "intervention_type",
    NumArms = "num_arms",
    NumPrimaryEndpoints = "num_primary_endpoints",
    NumSites = "num_sites",
    Prevalence = "prevalence",
    Radiation = "radiation",
    Regimen = "regimen",
    SampleSize = "sample_size",
    Vaccine = "vaccine",
}

export interface ValueClass {
    lower?: number;
    upper?: number;
    name?: string;
    mesh_id?: string;
    synonyms?: string[];
    is_brand?: number;
    drugbank_id?: string;
    nhs_url?: string;
    nhs_api_url?: string;
    medline_plus_id?: string;
    text?: string;
    unit?: string;
    years?: number;
    numeric?: number;
    sample_size?: string;
}

export interface AdjuvantPages {
    adjuvant: number[];
}

export interface Age {
    pages: AgePages;
    candidates: Array<Array<number[] | number | string>>;
    prediction: AgePrediction;
    annotations: Annotation[];
    candidates_with_scores: Array<Array<number[] | number | string>>;
}

export interface AgePages {
    "3_years": number[];
    "75_years": number[];
    "18-75_years": number[];
    "75_years_old": number[];
    "18-75_years_old": number[];
}

export interface AgePrediction {
    lower: number;
    upper: number;
}

export interface Biobank {
    pages: ContextClass;
    prediction: number;
    annotations: unknown[];
    candidates?: unknown[];
    probas?: number[];
}

export interface ContextClass {}

export interface CancerStage {
    pages: CancerStagePages;
    candidates: Array<Array<number | string>>;
    prediction: string[];
    annotations: Annotation[];
    candidates_with_scores: number[];
}

export interface CancerStagePages {
    metastasis: number[];
}

export interface CancerType {
    pages: { [key: string]: number[] };
    score: number;
    terms: { [key: string]: number };
    probas: number[];
    prediction: string;
    annotations: Annotation[];
}

export interface Chemo {
    pages: ChemoPages;
    proba: number;
    prediction: number;
    annotations: Annotation[];
}

export interface ChemoPages {
    cycles: number[];
    chemotherapy: number[];
}

export interface Child {
    pages: ChildPages;
    proba: number[];
    prediction: number;
    annotations: Annotation[];
}

export interface ChildPages {
    child?: number[];
    female: number[];
    criteria: number[];
    exclusion: number[];
    inclusion: number[];
    eligibility: number[];
}

export interface Consent {
    pages: ContextClass;
    candidates?: unknown[];
    prediction: string;
    annotations: unknown[];
}

export interface Country {
    logs: string[];
    pages: ContextClass;
    context: ContextClass;
    features: ContextClass;
    prediction: string[];
    annotations: unknown[];
}

export interface DocumentType {
    candidates: Candidates;
    prediction: string;
}

export interface Candidates {
    icf: number;
}

export interface Drug {
    pages: DrugPages;
    counts: Counts;
    scores: Array<Array<number | string>>;
    prediction: unknown[];
    annotations: Annotation[];
}

export interface Counts {
    digoxin: number;
    anticonvulsants: number;
    alanine_transaminase: number;
    alkaline_phosphatase: number;
    "anti-arrhythmia_agents": number;
    aspartate_aminotransferases: number;
}

export interface DrugPages {
    "": number[];
    alanine: number[];
    alkaline: number[];
    aspartate: number[];
    antiepileptic: number[];
    antiarrhythmic: number[];
}

export interface Duration {
    pages: DurationPages;
    score: number;
    candidates: Array<Array<number | string>>;
    prediction: number;
    annotations: Annotation[];
    is_low_confidence: number;
}

export interface DurationPages {
    "12_months": number[];
    "24_months": number[];
}

export interface EffectEstimate {
    logs: string[];
    pages: EffectEstimatePages;
    score: number;
    context: { [key: string]: string };
    prediction: number;
    annotations: unknown[];
    page_scores: number[];
}

export interface EffectEstimatePages {
    "12": number[];
    "24": number[];
    "50": number[];
    detect: unknown[];
    reduction: unknown[];
    "cohen's_d/h": unknown[];
    effect_size: unknown[];
    effect_estimate: unknown[];
    "relative_risk/rr": unknown[];
    "odds/hazard/risk_ratio": unknown[];
    "prevention_efficacy/effectiveness": unknown[];
}

export interface Gender {
    pages: ChildPages;
    proba: number[];
    prediction: number;
    annotations: Annotation[];
    explanation: string;
}

export interface Healthy {
    pages: HealthyPages;
    proba: number[];
    prediction: number;
    annotations: Annotation[];
}

export interface HealthyPages {
    health: number[];
    disease: number[];
    history: number[];
    illness: number[];
    criteria: number[];
    condition: number[];
    exclusion: number[];
    inclusion: number[];
    conditions: number[];
    eligibility: number[];
}

export interface Hospital {
    pages: HospitalPages;
    prediction: number;
    annotations: Annotation[];
}

export interface HospitalPages {
    hospital: number[];
}

export interface InterventionType {
    pages: { [key: string]: number[] };
    score: number;
    terms: { [key: string]: number };
    probas: number[];
    prediction: PredictionEnum;
    annotations: Annotation[];
}

export interface Ner {
    pages: ContextClass;
    prediction: Array<string[]>;
    annotations: Annotation[];
}

export interface NumArms {
    logs: string[];
    pages: { [key: string]: number[] };
    context: Context;
    prediction: number;
    annotations: Annotation[];
}

export interface Context {
    two_group: string;
    two_groups: string;
}

export interface NumEndpoints {
    pages: NumEndpointsPages;
    proba: number;
    prediction: number;
    annotations: Annotation[];
}

export interface NumEndpointsPages {
    measure: number[];
    outcome: number[];
    primary: number[];
    efficacy: number[];
    exploratory: number[];
}

export interface Num {
    pages: NumInterventionsPerVisitPages;
    prediction: number;
}

export interface NumInterventionsPerVisitPages {
    schedule_of_events: number[];
}

export interface NumSites {
    pages: ContextClass;
    candidates: unknown[];
    prediction: number;
    annotations: Annotation[];
    num_phone_numbers: number;
    num_mentions_multi_site: number;
    num_mentions_single_site: number;
}

export interface Phase {
    logs: string[];
    pages: ContextClass;
    probas: ContextClass;
    context: ContextClass;
    prediction: number;
    annotations: unknown[];
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

export interface Radiation {
    pages: RadiationPages;
    proba: number;
    prediction: number;
    annotations: Annotation[];
}

export interface RadiationPages {
    radiotherapy: number[];
}

export interface Recency {
    pages: RecencyPages;
    prediction: number;
    annotations: Annotation[];
}

export interface RecencyPages {
    "31_october": number[];
    october_2019: number[];
    "31_october_2019": number[];
}

export interface Regimen {
    pages: RegimenPages;
    contexts: unknown[];
    candidates: CandidateClass[];
    prediction: RegimenPrediction;
    annotations: Annotation[];
}

export interface CandidateClass {
    end_idx: number;
    page_no: number;
    frequency: string;
    start_idx: number;
    dosage_number: number;
    distance_to_drug: number;
    distance_to_regimen: number;
}

export interface RegimenPages {
    every_three_months: number[];
}

export interface RegimenPrediction {
    doses_per_day: number;
    days_between_doses: number;
    multiple_doses_per_day: number;
}

export interface RegimenDuration {
    pages: RegimenDurationPages;
    contexts: unknown[];
    candidates: unknown[];
    prediction: RegimenDurationPrediction;
    annotations: unknown[];
}

export interface RegimenDurationPages {
    cr: number[];
    death: number[];
    response: number[];
    metastasis: number[];
    complete_response: number[];
}

export interface RegimenDurationPrediction {
    until_progression: number;
}

export interface SampleSize {
    logs: string[];
    pages: { [key: string]: number[] };
    proba: Proba;
    score: number;
    comment: string;
    context: { [key: string]: string };
    is_per_arm: unknown[];
    prediction: number;
    annotations: Annotation[];
    is_low_confidence: number;
}

export interface Proba {
    "9": number;
}

export interface Sap {
    logs: string[];
    pages: { [key: string]: number[] };
    score: number;
    prediction: number;
    page_scores: number[];
}

export interface Simulation {
    pages: PurplePages;
    score: number;
    context: ContextClass;
    prediction: number;
    annotations: unknown[];
    page_scores: number[];
}

export interface PurplePages {
    power: unknown[];
    sample: number[];
    simulate: unknown[];
    scenarios: unknown[];
    sample_size: number[];
}

export interface Vaccine {
    pages: { [key: string]: number[] };
    score: number;
    terms: { [key: string]: number };
    probas: number[];
    prediction: number;
    annotations: Annotation[];
}

export interface SelectInputProps {
    placeholder: string;
    options: Option[] | undefined;
    value?: string | number | string[];
    disabled?: boolean;
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
    annotations: Annotation[];
    pages: { [key: string]: number[] };
    score: number;
    terms: { [key: string]: number };
    probas: number[];
    prediction: string;
}

export interface Features {
    jp: Array<Array<number | string>>;
    us: Array<Array<number | string>>;
}

export interface CountryPages {
    jp: number[];
    us: number[];
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

export interface Sap {
    pages: { [key: string]: number[] };
    score: number;
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
    prediction?: number | string;
    required_condition: string | null;
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

export interface ISheetJsTableCell {
    t: string;
    v: string | number | undefined;
    f?: string;
}

export interface ITableRowWithCellObj {
    feature: ISheetJsTableCell;
    description?: ISheetJsTableCell;
    value: ISheetJsTableCell;
    weight?: ISheetJsTableCell;
    score?: ISheetJsTableCell;
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

export interface NestedCostRiskModel {
    [key: string]: CostRiskModel | NestedCostRiskModel;
}

export interface Weights {
    cost_risk_models: Record<string, CostRiskModel | NestedCostRiskModel>;
    tertiles?: TertilesClass;
    risk_thresholds?: RiskThresholds;
}

export interface TertilesClass {
    recency_tertiles: Tertile[];
    duration_tertiles: Tertile[];
    num_sites_tertiles: Tertile[];
    num_visits_tertiles: Tertile[];
    sample_size_tertiles: Tertile[];
}
export interface CostRiskModel {
    cost?: number;
    risk?: number;
}

export interface RiskThresholds {
    low: number;
    high: number;
}

export interface Tertile {
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
