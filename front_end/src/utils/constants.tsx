import { MdDashboard } from "react-icons/md";
import { VscHistory } from "react-icons/vsc";
import { IoIosShareAlt, IoMdSettings } from "react-icons/io";
import {
    FaFacebookF,
    FaGithub,
    FaGoogle,
    FaInstagram,
    FaLinkedinIn,
    FaMastodon,
    FaYelp,
    FaYoutube,
} from "react-icons/fa";
import { type SidebarLinkType } from "./types";
import {
    BreakDownByPageNumber,
    RiskCalculation,
    CostCalculation,
} from "../components/explainAnalysis/tabPanelComponents";
import CostRiskModelProfile from "../components/settings/InnerSettings/WeightProfile/CostRiskModelProfile";
import SampleSizeTertile from "../components/settings/InnerSettings/WeightProfile/SampleSizeTertile";
import RiskThreshold from "../components/settings/InnerSettings/WeightProfile/RiskThreshold";
import { FaThreads } from "react-icons/fa6";

// constants
export const FILES_PER_PAGE = 9;
export const SHARABLE_ACCESS_LINK =
    "https://clinical.fastdatascience.com/login?guest=true";

// REGEX
export const RE_DIGIT = /^\d+$/;
export const NAME_REGEX = /^[A-Za-z\s]*$/;
// eslint-disable-next-line no-useless-escape
export const EMAIL_REGEX = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/;
export const PASSWORD_REGEX =
    // eslint-disable-next-line no-useless-escape
    /^(?=.*[A-Z])(?=.*d)(?=.*[@#$%^&+=!]).{8,20}$/;

export const dashboardSidebarLinks: SidebarLinkType[] = [
    {
        id: "share",
        label: "Share this tool",
        path: "",
        icon: <IoIosShareAlt />,
        hasClick: true,
    },
    {
        id: "dashboard",
        label: "Dashboard",
        path: "/dashboard",
        icon: <MdDashboard />,
    },
    {
        id: "history",
        label: "History",
        path: "/history",
        icon: <VscHistory />,
        tooltipText: "Create an account to unlock history",
    },
    {
        id: "settings",
        label: "Settings",
        path: "/settings",
        icon: <IoMdSettings />,
        tooltipText: "Create an account to unlock settings",
    },
];

export interface PropsType
    extends React.ComponentProps<typeof BreakDownByPageNumber> {}

export const tabItems: TabItem<PropsType>[] = [
    {
        id: 1,
        label: "Breakdown by page number",
        renderTabPanelComponent: (props: PropsType) => (
            <BreakDownByPageNumber {...props} />
        ),
    },
    {
        id: 2,
        label: "Cost calculation spreadsheet",
        renderTabPanelComponent: (props) => <CostCalculation {...props} />,
    },
    {
        id: 3,
        label: "Risk calculation spreadsheet",
        renderTabPanelComponent: (props) => <RiskCalculation {...props} />,
    },
];

export const weightTabItems: TabItem<unknown>[] = [
    {
        id: 1,
        label: "Cost Risk Models",
        renderTabPanelComponent: () => <CostRiskModelProfile />,
    },
    {
        id: 2,
        label: "Risk Thresholds",
        renderTabPanelComponent: () => <RiskThreshold />,
    },
    {
        id: 3,
        label: "Sample Size Tertiles",
        renderTabPanelComponent: () => <SampleSizeTertile />,
    },
];

export interface TabItem<T> {
    id: number;
    label: string;
    renderTabPanelComponent: (props: T) => JSX.Element;
}

export const labelData = [
    { label: "Trial is for condition", parameter: "condition" },
    { label: "Trial phase", parameter: "phase" },
    {
        label: "Has the statistical analysis plan been completed?",
        parameter: "sap",
    },
    {
        label: "Has the Effect estimate been disclosed?",
        parameter: "effect_estimate",
    },
    { label: "Number of subjects", parameter: "sample_size" },
];

export const labelData2 = [
    "Number of arms",
    "Countries of investigation",
    "Trial uses simulation for sample size?",
];

export const navLinks = [
    {
        id: "home",
        title: "Home",
        path: "/",
    },
    {
        id: "about",
        title: "About",
        path: "/",
    },
    {
        id: "pricing",
        title: "Pricing",
        path: "/pricing",
    },
    {
        id: "terms_and_condition",
        title: "Terms & Conditions",
        path: "/",
    },
];

export const authButtonsLinks = [
    {
        id: "login",
        title: "Login",
        path: "/login",
    },
    {
        id: "signup",
        title: "Sign Up",
        path: "/register",
    },
];

export const lorem_ipsum_xs: string = "Lorem ipsum";
export const lorem_ipsum_sm: string = "Lorem ipsum dolor sit amet";
export const lorem_ipsum_md: string =
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam";
export const lorem_ipsum_lg: string =
    "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor";

// Dummy footer data
export const footerLinks = [
    {
        title: "SERVICES",
        links: [
            "AI for healthcare",
            "AI in pharma",
            "AI in public sector procurement",
            "AI technical due diligence",
        ],
    },
    {
        title: "SKILLS",
        links: [
            "Natural Language Processing",
            "Cloud Machine Learning Consulting",
            "Predictive Analytics Consulting",
            "Conversion Optimisation",
        ],
    },
    {
        title: "CASE STUDIES",
        links: [
            "Drug named entity recognition Python library",
            "Open Source Tools for Natural Language Processing",
            "Pharma - PubMed authorship analysis",
            "Tesco - Customer basket weights",
        ],
    },
    {
        title: "DEMOS",
        links: [
            "Clinical Trial Risk Tool",
            "NLP Survey Dashboard for What Women Want",
            "Author prediction demo",
            "Insolvency bot",
        ],
    },
    {
        title: "ABOUT",
        links: [
            "Team",
            "Blog",
            "Resources",
            "Contact",
            "Company info",
            "Privacy policy",
            "Publications and patents",
        ],
    },
];

// dummy footer social links
export const socialLinks = [
    {
        id: "facebook",
        icon: <FaFacebookF />,
        url: "https://www.linkedin.com/company/fastdatascience/",
    },
    {
        id: "github",
        icon: <FaGithub />,
        url: "https://github.com/fastdatascience",
    },
    {
        id: "linkedIn",
        icon: <FaLinkedinIn />,
        url: "https://www.linkedin.com/company/fastdatascience/",
    },
    {
        id: "youtube",
        icon: <FaYoutube />,
        url: "https://www.youtube.com/channel/UCLPrDH7SoRT55F6i50xMg5g",
    },
    {
        id: "googleMaps",
        icon: <FaGoogle />,
        url: "https://www.google.com/maps/place/Fast+Data+Science/@47.73855,12.5088275,4z/data=!3m1!4b1!4m6!3m5!1s0x4876070922ec9795:0xf247a90fd16c2791!8m2!3d47.73855!4d12.5088275!16s%2Fg%2F11h2hn38hf?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D",
    },
    {
        id: "instagram",
        icon: <FaInstagram />,
        url: "https://www.instagram.com/fastdatascience",
    },
    {
        id: "thread",
        icon: <FaThreads />,
        url: "https://www.threads.net/@fastdatascience",
    },
    {
        id: "yelp",
        icon: <FaYelp />,
        url: "https://www.yelp.com/biz/fast-data-science-london",
    },
    {
        id: "mastodon",
        icon: <FaMastodon />,
        url: "https://mastodon.social/@fastdatascience",
    },
];

export interface FormErrors {
    [fieldName: string]: string;
}

// hardocded formulas for Risk table for now
export const hardcodedFormulas = [
    { id: "num_arms", formula: "=B7*C7" },
    { id: "phase", formula: "=B8*C8" },
    { id: "sap", formula: "=B9*C9" },
    { id: "effect_estimate", formula: "=B10*C10" },
    { id: "phase", formula: "=B11*C11" },
    { id: "simulation", formula: "=B13*C13" },
];

export const formulaLookup = new Map(
    hardcodedFormulas.map((item) => [item.id, item.formula])
);
