--
-- PostgreSQL database dump
--

-- Dumped from database version 13.9 (Ubuntu 13.9-1.pgdg20.04+1)
-- Dumped by pg_dump version 16.1

-- Started on 2023-11-19 22:55:23 +04

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4257 (class 1262 OID 4009973)
-- Name: kjezmrcz; Type: DATABASE; Schema: -; Owner: kjezmrcz
--

CREATE DATABASE kjezmrcz WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE kjezmrcz OWNER TO kjezmrcz;

\connect kjezmrcz

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 25 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 4259 (class 0 OID 0)
-- Dependencies: 25
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 1482 (class 1247 OID 4199471)
-- Name: subscriptionduration; Type: TYPE; Schema: public; Owner: kjezmrcz
--

CREATE TYPE public.subscriptionduration AS ENUM (
    'MONTHLY',
    'YEARLY'
);


ALTER TYPE public.subscriptionduration OWNER TO kjezmrcz;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 240 (class 1259 OID 4349744)
-- Name: Currency; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."Currency" (
    id bigint NOT NULL,
    code character varying NOT NULL
);


ALTER TABLE public."Currency" OWNER TO kjezmrcz;

--
-- TOC entry 251 (class 1259 OID 4757329)
-- Name: Document; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."Document" (
    id bigint NOT NULL,
    original_document_name text NOT NULL,
    system_assigned_name text NOT NULL,
    document_type character varying(20) DEFAULT 'application/pdf'::character varying NOT NULL,
    document_size integer DEFAULT 0 NOT NULL,
    created_at information_schema.time_stamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id bigint NOT NULL
);


ALTER TABLE public."Document" OWNER TO kjezmrcz;

--
-- TOC entry 4261 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN "Document".original_document_name; Type: COMMENT; Schema: public; Owner: kjezmrcz
--

COMMENT ON COLUMN public."Document".original_document_name IS 'Original document name';


--
-- TOC entry 4262 (class 0 OID 0)
-- Dependencies: 251
-- Name: COLUMN "Document".document_size; Type: COMMENT; Schema: public; Owner: kjezmrcz
--

COMMENT ON COLUMN public."Document".document_size IS 'File size in MB';


--
-- TOC entry 250 (class 1259 OID 4757327)
-- Name: Document_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."Document_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Document_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4263 (class 0 OID 0)
-- Dependencies: 250
-- Name: Document_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."Document_id_seq" OWNED BY public."Document".id;


--
-- TOC entry 252 (class 1259 OID 4757345)
-- Name: Document_user_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."Document_user_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Document_user_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4264 (class 0 OID 0)
-- Dependencies: 252
-- Name: Document_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."Document_user_id_seq" OWNED BY public."Document".user_id;


--
-- TOC entry 243 (class 1259 OID 4350484)
-- Name: ResourceType; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."ResourceType" (
    id bigint NOT NULL,
    name character varying NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."ResourceType" OWNER TO kjezmrcz;

--
-- TOC entry 229 (class 1259 OID 4192189)
-- Name: Role; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."Role" (
    id bigint NOT NULL,
    name character varying(100) NOT NULL
);


ALTER TABLE public."Role" OWNER TO kjezmrcz;

--
-- TOC entry 228 (class 1259 OID 4192185)
-- Name: Role_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."Role_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Role_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4265 (class 0 OID 0)
-- Dependencies: 228
-- Name: Role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."Role_id_seq" OWNED BY public."Role".id;


--
-- TOC entry 249 (class 1259 OID 4392691)
-- Name: SubscriptionAttribute; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."SubscriptionAttribute" (
    subscription_type_id bigint NOT NULL,
    file_processing_limit integer DEFAULT 0 NOT NULL,
    file_size integer DEFAULT 0 NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."SubscriptionAttribute" OWNER TO kjezmrcz;

--
-- TOC entry 4266 (class 0 OID 0)
-- Dependencies: 249
-- Name: COLUMN "SubscriptionAttribute".file_size; Type: COMMENT; Schema: public; Owner: kjezmrcz
--

COMMENT ON COLUMN public."SubscriptionAttribute".file_size IS 'File size in mega bytes MB';


--
-- TOC entry 234 (class 1259 OID 4199416)
-- Name: SubscriptionType; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."SubscriptionType" (
    id bigint NOT NULL,
    name character varying NOT NULL,
    price numeric(10,2) DEFAULT 0 NOT NULL,
    description text,
    duration public.subscriptionduration DEFAULT 'MONTHLY'::public.subscriptionduration NOT NULL,
    currency_id bigint NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."SubscriptionType" OWNER TO kjezmrcz;

--
-- TOC entry 241 (class 1259 OID 4349754)
-- Name: SubscriptionType_currency_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."SubscriptionType_currency_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."SubscriptionType_currency_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4267 (class 0 OID 0)
-- Dependencies: 241
-- Name: SubscriptionType_currency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."SubscriptionType_currency_id_seq" OWNED BY public."SubscriptionType".currency_id;


--
-- TOC entry 227 (class 1259 OID 4012220)
-- Name: User; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."User" (
    id bigint NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(255) NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    phone_number character varying(15),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_login timestamp without time zone,
    is_email_verified boolean DEFAULT false,
    email_otp character varying,
    phone_number_otp character varying,
    is_phone_number_verified boolean DEFAULT false,
    profile_picture text,
    user_resource_identifier text DEFAULT public.uuid_generate_v4() NOT NULL
);


ALTER TABLE public."User" OWNER TO kjezmrcz;

--
-- TOC entry 4268 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN "User".profile_picture; Type: COMMENT; Schema: public; Owner: kjezmrcz
--

COMMENT ON COLUMN public."User".profile_picture IS 'Picture resource uri';


--
-- TOC entry 4269 (class 0 OID 0)
-- Dependencies: 227
-- Name: COLUMN "User".user_resource_identifier; Type: COMMENT; Schema: public; Owner: kjezmrcz
--

COMMENT ON COLUMN public."User".user_resource_identifier IS 'UUID used for managing AWS resources';


--
-- TOC entry 245 (class 1259 OID 4350498)
-- Name: UserResourceUsage; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."UserResourceUsage" (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    resource_type_id bigint NOT NULL,
    start_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_time timestamp without time zone
);


ALTER TABLE public."UserResourceUsage" OWNER TO kjezmrcz;

--
-- TOC entry 4270 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN "UserResourceUsage".end_time; Type: COMMENT; Schema: public; Owner: kjezmrcz
--

COMMENT ON COLUMN public."UserResourceUsage".end_time IS 'Null marks that this resource is still under use';


--
-- TOC entry 247 (class 1259 OID 4350518)
-- Name: UserResourceUsage_resource_type_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."UserResourceUsage_resource_type_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."UserResourceUsage_resource_type_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4271 (class 0 OID 0)
-- Dependencies: 247
-- Name: UserResourceUsage_resource_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."UserResourceUsage_resource_type_id_seq" OWNED BY public."UserResourceUsage".resource_type_id;


--
-- TOC entry 246 (class 1259 OID 4350506)
-- Name: UserResourceUsage_user_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."UserResourceUsage_user_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."UserResourceUsage_user_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4272 (class 0 OID 0)
-- Dependencies: 246
-- Name: UserResourceUsage_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."UserResourceUsage_user_id_seq" OWNED BY public."UserResourceUsage".user_id;


--
-- TOC entry 232 (class 1259 OID 4192247)
-- Name: UserRole; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."UserRole" (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);


ALTER TABLE public."UserRole" OWNER TO kjezmrcz;

--
-- TOC entry 238 (class 1259 OID 4199447)
-- Name: UserSubscription; Type: TABLE; Schema: public; Owner: kjezmrcz
--

CREATE TABLE public."UserSubscription" (
    id bigint NOT NULL,
    user_id bigint NOT NULL,
    subscription_type_id bigint NOT NULL,
    start_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_date timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public."UserSubscription" OWNER TO kjezmrcz;

--
-- TOC entry 226 (class 1259 OID 4012218)
-- Name: User_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public."User_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."User_id_seq" OWNER TO kjezmrcz;

--
-- TOC entry 4273 (class 0 OID 0)
-- Dependencies: 226
-- Name: User_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public."User_id_seq" OWNED BY public."User".id;


--
-- TOC entry 239 (class 1259 OID 4349742)
-- Name: currecny_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.currecny_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.currecny_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4274 (class 0 OID 0)
-- Dependencies: 239
-- Name: currecny_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.currecny_id_seq OWNED BY public."Currency".id;


--
-- TOC entry 242 (class 1259 OID 4350482)
-- Name: resourcetype_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.resourcetype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resourcetype_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4275 (class 0 OID 0)
-- Dependencies: 242
-- Name: resourcetype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.resourcetype_id_seq OWNED BY public."ResourceType".id;


--
-- TOC entry 248 (class 1259 OID 4392689)
-- Name: subscriptionattribute_subscription_type_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.subscriptionattribute_subscription_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptionattribute_subscription_type_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4276 (class 0 OID 0)
-- Dependencies: 248
-- Name: subscriptionattribute_subscription_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.subscriptionattribute_subscription_type_id_seq OWNED BY public."SubscriptionAttribute".subscription_type_id;


--
-- TOC entry 233 (class 1259 OID 4199414)
-- Name: subscriptiontype_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.subscriptiontype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptiontype_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4277 (class 0 OID 0)
-- Dependencies: 233
-- Name: subscriptiontype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.subscriptiontype_id_seq OWNED BY public."SubscriptionType".id;


--
-- TOC entry 244 (class 1259 OID 4350496)
-- Name: userresourceusage_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.userresourceusage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userresourceusage_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4278 (class 0 OID 0)
-- Dependencies: 244
-- Name: userresourceusage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.userresourceusage_id_seq OWNED BY public."UserResourceUsage".id;


--
-- TOC entry 231 (class 1259 OID 4192245)
-- Name: userrole_role_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.userrole_role_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userrole_role_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4279 (class 0 OID 0)
-- Dependencies: 231
-- Name: userrole_role_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.userrole_role_id_seq OWNED BY public."UserRole".role_id;


--
-- TOC entry 230 (class 1259 OID 4192243)
-- Name: userrole_user_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.userrole_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userrole_user_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4280 (class 0 OID 0)
-- Dependencies: 230
-- Name: userrole_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.userrole_user_id_seq OWNED BY public."UserRole".user_id;


--
-- TOC entry 235 (class 1259 OID 4199441)
-- Name: usersubscription_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.usersubscription_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usersubscription_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4281 (class 0 OID 0)
-- Dependencies: 235
-- Name: usersubscription_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.usersubscription_id_seq OWNED BY public."UserSubscription".id;


--
-- TOC entry 237 (class 1259 OID 4199445)
-- Name: usersubscription_subscription_type_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.usersubscription_subscription_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usersubscription_subscription_type_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4282 (class 0 OID 0)
-- Dependencies: 237
-- Name: usersubscription_subscription_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.usersubscription_subscription_type_id_seq OWNED BY public."UserSubscription".subscription_type_id;


--
-- TOC entry 236 (class 1259 OID 4199443)
-- Name: usersubscription_user_id_seq; Type: SEQUENCE; Schema: public; Owner: kjezmrcz
--

CREATE SEQUENCE public.usersubscription_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.usersubscription_user_id_seq OWNER TO kjezmrcz;

--
-- TOC entry 4283 (class 0 OID 0)
-- Dependencies: 236
-- Name: usersubscription_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: kjezmrcz
--

ALTER SEQUENCE public.usersubscription_user_id_seq OWNED BY public."UserSubscription".user_id;


--
-- TOC entry 4044 (class 2604 OID 4349747)
-- Name: Currency id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Currency" ALTER COLUMN id SET DEFAULT nextval('public.currecny_id_seq'::regclass);


--
-- TOC entry 4055 (class 2604 OID 4757332)
-- Name: Document id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Document" ALTER COLUMN id SET DEFAULT nextval('public."Document_id_seq"'::regclass);


--
-- TOC entry 4059 (class 2604 OID 4757347)
-- Name: Document user_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Document" ALTER COLUMN user_id SET DEFAULT nextval('public."Document_user_id_seq"'::regclass);


--
-- TOC entry 4045 (class 2604 OID 4350487)
-- Name: ResourceType id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."ResourceType" ALTER COLUMN id SET DEFAULT nextval('public.resourcetype_id_seq'::regclass);


--
-- TOC entry 4031 (class 2604 OID 4192192)
-- Name: Role id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Role" ALTER COLUMN id SET DEFAULT nextval('public."Role_id_seq"'::regclass);


--
-- TOC entry 4051 (class 2604 OID 4392694)
-- Name: SubscriptionAttribute subscription_type_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionAttribute" ALTER COLUMN subscription_type_id SET DEFAULT nextval('public.subscriptionattribute_subscription_type_id_seq'::regclass);


--
-- TOC entry 4034 (class 2604 OID 4199419)
-- Name: SubscriptionType id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionType" ALTER COLUMN id SET DEFAULT nextval('public.subscriptiontype_id_seq'::regclass);


--
-- TOC entry 4037 (class 2604 OID 4349756)
-- Name: SubscriptionType currency_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionType" ALTER COLUMN currency_id SET DEFAULT nextval('public."SubscriptionType_currency_id_seq"'::regclass);


--
-- TOC entry 4025 (class 2604 OID 4012223)
-- Name: User id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."User" ALTER COLUMN id SET DEFAULT nextval('public."User_id_seq"'::regclass);


--
-- TOC entry 4047 (class 2604 OID 4350501)
-- Name: UserResourceUsage id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserResourceUsage" ALTER COLUMN id SET DEFAULT nextval('public.userresourceusage_id_seq'::regclass);


--
-- TOC entry 4048 (class 2604 OID 4350508)
-- Name: UserResourceUsage user_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserResourceUsage" ALTER COLUMN user_id SET DEFAULT nextval('public."UserResourceUsage_user_id_seq"'::regclass);


--
-- TOC entry 4049 (class 2604 OID 4350520)
-- Name: UserResourceUsage resource_type_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserResourceUsage" ALTER COLUMN resource_type_id SET DEFAULT nextval('public."UserResourceUsage_resource_type_id_seq"'::regclass);


--
-- TOC entry 4032 (class 2604 OID 4192250)
-- Name: UserRole user_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserRole" ALTER COLUMN user_id SET DEFAULT nextval('public.userrole_user_id_seq'::regclass);


--
-- TOC entry 4033 (class 2604 OID 4192251)
-- Name: UserRole role_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserRole" ALTER COLUMN role_id SET DEFAULT nextval('public.userrole_role_id_seq'::regclass);


--
-- TOC entry 4039 (class 2604 OID 4199450)
-- Name: UserSubscription id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserSubscription" ALTER COLUMN id SET DEFAULT nextval('public.usersubscription_id_seq'::regclass);


--
-- TOC entry 4040 (class 2604 OID 4199451)
-- Name: UserSubscription user_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserSubscription" ALTER COLUMN user_id SET DEFAULT nextval('public.usersubscription_user_id_seq'::regclass);


--
-- TOC entry 4041 (class 2604 OID 4199452)
-- Name: UserSubscription subscription_type_id; Type: DEFAULT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserSubscription" ALTER COLUMN subscription_type_id SET DEFAULT nextval('public.usersubscription_subscription_type_id_seq'::regclass);


--
-- TOC entry 4239 (class 0 OID 4349744)
-- Dependencies: 240
-- Data for Name: Currency; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."Currency" (id, code) FROM stdin;
1	USD
2	GBP
3	EURO
\.


--
-- TOC entry 4250 (class 0 OID 4757329)
-- Dependencies: 251
-- Data for Name: Document; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."Document" (id, original_document_name, system_assigned_name, document_type, document_size, created_at, user_id) FROM stdin;
1	HZQ20231108008.pdf	63fca219-2d4a-4108-a9bb-847078afd087_HZQ20231108008.pdf	application/pdf	0	2023-11-19 18:50:39.25+00	71
\.


--
-- TOC entry 4242 (class 0 OID 4350484)
-- Dependencies: 243
-- Data for Name: ResourceType; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."ResourceType" (id, name, updated_at) FROM stdin;
\.


--
-- TOC entry 4228 (class 0 OID 4192189)
-- Dependencies: 229
-- Data for Name: Role; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."Role" (id, name) FROM stdin;
1	PLATFORM_SUPER_ADMIN
2	ADMIN
3	USER
4	GUEST
5	EDITOR
\.


--
-- TOC entry 4248 (class 0 OID 4392691)
-- Dependencies: 249
-- Data for Name: SubscriptionAttribute; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."SubscriptionAttribute" (subscription_type_id, file_processing_limit, file_size, updated_at) FROM stdin;
1	3	20	2023-10-19 02:59:04.803623
3	100	100	2023-10-19 02:59:49.250256
4	1	10	2023-10-19 03:00:00.880559
2	10	10	2023-10-19 02:59:49.115853
\.


--
-- TOC entry 4233 (class 0 OID 4199416)
-- Dependencies: 234
-- Data for Name: SubscriptionType; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."SubscriptionType" (id, name, price, description, duration, currency_id, updated_at) FROM stdin;
2	STANDARD	45.00	10 documents per day	MONTHLY	1	2023-10-13 01:40:33.657011
1	BASIC	20.00	3 documents per day	MONTHLY	1	2023-10-13 01:40:33.657011
3	PRO	60.00	Unlimited	MONTHLY	1	2023-10-13 02:19:29.909678
4	FREE	0.00	1 documet per day	MONTHLY	1	2023-10-13 02:19:29.909678
\.


--
-- TOC entry 4226 (class 0 OID 4012220)
-- Dependencies: 227
-- Data for Name: User; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."User" (id, email, password, first_name, last_name, phone_number, created_at, updated_at, last_login, is_email_verified, email_otp, phone_number_otp, is_phone_number_verified, profile_picture, user_resource_identifier) FROM stdin;
57	shirley.arsema@my2ducks.com	$2b$12$dp2ntkB7jVM5jUiitp/2ueVf.8Sy7VE6VHb5F5/s3RfWzVjeCD2z6	Maite	Cooke	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	b4395ca2-4cc4-4d7e-9d61-26ff6a91c866
25	haltayurzu@gufum.com	$2b$12$98dH0VqGpsb2jB4ff5NOP.jwvH5RXB4eJghVts2LCOzXPVS.J6kFi	Abdullah	W.	jsdjsd	2023-10-01 16:14:59.302928	2023-10-01 16:14:59.302942	\N	t	\N	\N	f	\N	f3597d95-95d6-4d8f-82d4-b90ca09d995e
26	nuspesorku@gufum.com	$2b$12$.p8Gek/Skxjvr3oy0oofNeJ6j8Rjog1c1rMtdlpumRRW0DunwUOQa	Abdullah	W.	jsdjsd	2023-10-02 11:03:57.568164	2023-10-02 11:03:57.568186	\N	t	\N	\N	f	\N	3839fe50-4428-47c8-b786-7131a263f0f6
27	abcq@gufum.com	$2b$12$sRyp.sO4VTrBp0GZC7rHdujexvPcJFneRV5/d6C501Brsr5.qH2mC	johnq	doeq	03344567899	2023-10-03 22:38:17.650299	2023-10-03 22:38:17.65032	\N	f	552709	\N	f	\N	e43c608c-8855-4e71-8c96-9e97975ec30b
28	gekinuqa@mailinatr.com	$2b$12$H21m0LlIAgKjDwevStZD0e8zVyRXfZ2yQhT5dIe3YSmjYM3uSleYu	Murph	Pachec	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	604095	\N	f	\N	bf037421-93a9-4b9b-8a1b-23b5438a0de3
29	gekinuqa@mailinatr.co	$2b$12$TbLv054xDTY3gF5YIK8iHOlXruQET5/ZdhlVDM.CZ8rFWA/3wmouq	Murphww	Pachecd	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	921997	\N	f	\N	24b48abf-c90d-48d8-915b-503f0fceb93e
30	jujyvax@mailinator.com	$2b$12$pmI5lT.ZeRtre4VtGTRejeiY/s9oiQw1sWhs./NGbIpmLC47gI8J2	Darryl	Maxwell	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	119120	\N	f	\N	67972d15-ea29-4aff-b3ab-27b82e8d4565
31	hoxiviwi@mailinator.com	$2b$12$j7g3wlW8YcdOXhR0g0Dwnem5oIwA39ZsfIv3dO01sEzCPQhhNOMRO	Quemby	Butler	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	675198	\N	f	\N	687df5d6-9f3c-4695-9e55-34a37fd9f723
32	shloimy.chanze@my2ducks.com	$2b$12$BcwmznZJKML6U1nnYFRyd.kjamOkZ9GwO18kWf1AiiznHdlVrJyEi	Quemby	Butler	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	229059	\N	f	\N	fd6a07e6-3c2a-4ba6-8d93-f578e66d72b8
33	chrisangel.kimari@my2ducks.com	$2b$12$5YcMyprDocr0tPTw4f9QDuYOk7yGLYK9jzDKBvKnKB/5.DzwgItTW	Chester	Zimmerman	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	322975	\N	f	\N	f42ce4c2-2f99-4968-989a-f8913fcf8b0f
34	jojo@my2ducks.com	$2b$12$wgNPlw9xcVBZ3I0U6QQ4YuVuHf9kSvIHGYi2lMre6ZNAdhHK7vsla	Ruth	Hayes	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	882689	\N	f	\N	4de1d8b0-78b5-4c8c-a685-f5e1769c78de
35	zyere.cyree@my2ducks.com	$2b$12$Clm62LdCaOwGt2ytaVktgO9jgrAxUa66jL6GIShn.zvu8V5QH76Aq	MacKenzie	Kidd	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	345592	\N	f	\N	307c81f3-bf4a-40c3-913e-3ec4c466ffcd
36	bob@my2ducks.com	$2b$12$/4Ubfi3kR7ggIMGAAk1CxeSQByToWo3e0aYx6vSVCQ7T9V3AFBIMq	Aline	Dickerson	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	574477	\N	f	\N	6e0b48fa-2d9c-4ba6-8adf-09ae4b503d85
37	laraine.teigen@my2ducks.com	$2b$12$K4FMLaPbdUS9OVe0F9fmgelMwHpMay0ZSeHWJogZrWowvUaiSj63W	Oren	Love	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	296088	\N	f	\N	5f56226c-2690-4b52-a21a-22bb41b9a9cd
38	tanish.misael@my2ducks.com	$2b$12$gdZNvo3Y1EisuVgnvODRQe8HqoNET.NF5KILcrp1hgs8b3eCtcPD6	Rowan	Delgado	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	921652	\N	f	\N	bd9011cc-d401-419a-9d27-e2c8037f2a7a
39	aki.wayne@my2ducks.com	$2b$12$tZ1Q1O0WIlM6N7fsGiIzJeEGdcOkkfFLFsSWa7Cqi3L7N1c13r8au	Kitra	Oneil	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	187485	\N	f	\N	d9953b0b-06d6-484b-9236-e100b885c712
40	cashus.sherwin@my2ducks.com	$2b$12$lRx7SMnwegqnuoWDViqg.uuUwLz4v/NFNn/tStVxiOKSaa6dLsEMG	Dillon	Paul	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	336950	\N	f	\N	a4c6c9b9-d04f-4ca9-a90f-063218552f0a
41	finnly.kristabella@my2ducks.com	$2b$12$tJufhTp6bCh7ez7Z16RwJOwsKkPfKtNXB/jNPh2AlkqCmlJ/Rdtq2	Driscoll	Fuller	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	347493	\N	f	\N	e3e48200-4a62-4227-afb3-de5fa42554f5
42	bebe@my2ducks.com	$2b$12$i4fKiGgiepIHwALU0YB/qO8TtkRogcU/qpz0MzC0nuKDyNj8hyW46	Jorden	Perez	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	661510	\N	f	\N	192b9199-fb16-43ab-ba9d-d1081bab1ebb
43	bobo@my2ducks.com	$2b$12$Rv7AZ.cFJMhvisQGplue8umf1Ae8SuTQ57H8l9OqkT5MsHXw3APUW	Cain	Reilly	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	413757	\N	f	\N	fc2d587d-4eb1-4b68-bd74-4d7880ef3389
44	hudsen.maxi@my2ducks.com	$2b$12$FnNBga/.9ukCDSTQxDR4AOyUIHLqFx3TbaxJYaqZIDX.xMmZ/8VF6	Chantale	Robinson	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	975836	\N	f	\N	a70683e3-f647-4089-b330-3d0bcdf95415
45	ror@my2ducks.com	$2b$12$mxwdChd7fsqXph2AJD0AbuDaeNdPZBEbulCpP/uXzgWiFjXRBkpm6	Chantale	Robinson	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	179571	\N	f	\N	75dce856-d339-401b-8b07-1b5cf8642043
46	qoq@my2ducks.com	$2b$12$3rr9v84Nqj8nDvPJ8.8yU.hrb0OLE4WbqHIkjIlca6RL95JELn41K	Noelle	Stafford	\N	2023-10-05 11:07:27.524844	2023-10-05 11:07:27.52487	\N	f	230714	\N	f	\N	4fd053c9-7b02-4851-aedb-44b23a241af5
47	sutter.asad@my2ducks.com	$2b$12$AGpsQkdz./.elI4FgkJCGOz71rKRkCaYrsWbLSOmfBMo/c8KU5Ozi	Sylvia	Jordan	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	654460	\N	f	\N	91ab07c1-e71a-4e25-8122-746b0b3d0af0
48	xyjyqyg@mailinator.com	$2b$12$Wu5UHoqYEBfK7XGRavhTWu0c.4aSHFHxvXbBUBG4lRBOVXjUyOl2O	Hoyt	Pace	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	464202	\N	f	\N	90bfb4f6-c328-4ed5-8b1b-7c3c683b79c8
49	kayvon.talen@my2ducks.com	$2b$12$m8ol/MPgUFc4Q5zpnCscW.JUpsizJJCLU9YubozMzLoZadLgC76kS	Castor	Walls	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	878965	\N	f	\N	fff061ea-c25b-4597-a125-244b3a9dd81e
50	eponine.judie@my2ducks.com	$2b$12$VZvlsq8jDLCs/6QSDgmB/O0c7vmtwKu9UXKaIpQvQ6ljojuB.yOhK	Aurelia	Davis	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	932896	\N	f	\N	5509e612-0b2c-441e-aff9-872b2f76ed40
51	boblo@my2ducks.com	$2b$12$3jgKljQ9ZWKyB8B/MTd7CO7HdbZsKY58iipXoz62iEsvQu/KJZSQm	Rhonda	Walls	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	395174	\N	f	\N	3e70de93-8a35-48d4-98bc-2de2728618dc
52	vovo@my2ducks.com	$2b$12$y81Zg7ztJuRf8UzPHnqiSO3Tq8rMKCHa1W0aHbPn5/.bi1y7uDCcu	Yolanda	Edwards	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	753296	\N	f	\N	033325b5-4550-476c-afc9-e95d9909cade
53	bobolof@my2ducks.com	$2b$12$lwOkYXPz1IbXO1QzZm5CCOEDo02sWBey5aw0AKqQbusWGPQyM5XCC	Noble	Hogan	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	660213	\N	f	\N	7a79efcc-861c-4c4f-b9b5-64c1d1f46716
54	wwww@my2ducks.com	$2b$12$1Vs6rZ.sUbZlCg1s/Ec9d.zy80.jKtgoUVyk5JnxlDEwDmlBJJBIy	Lengh	Chambers	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	ca938ecf-0175-4320-85c1-3ed7e97a2605
55	qqq@my2ducks.com	$2b$12$fopE0dMD64IQ9ned/oMr6.vBgWWU3AwFZNOC9A9nLiaAbTnaP5qbW	George	Dorsey	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	79d0007d-a59d-40b4-8224-f419f30255e9
56	rrrr@my2ducks.com	$2b$12$eWw6asVK5gWAubh1jHuJy.KhTMzF6hSMV73ewlbOFLQO4PF72azIa	Ianjljl	Rivera	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	5d671e41-b14e-4db4-a5a7-0ef9c7161815
58	jama.aria@my2ducks.com	$2b$12$/ePK3dWdTUoYsWCXFe3U9OPTECE54m1vjIqs1smLeFbkt/CnXt42q	August	Dawson	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	f	253926	\N	f	\N	6ab4eefd-fc46-498f-a890-552788e1039f
61	melvyn.ciro@my2ducks.com	$2b$12$M/.AjxgYdHxkN851lIcbqOEWAVUl013OExfO4rVYlEeqIC9zCRXB2	Keelie	Rosario	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	dab138b1-8eab-485e-89b7-f633acf20dfe
59	miquel.landyn@my2ducks.com	$2b$12$.MNJ28E3i5WVvUF4X6DzA.ZwC9B0AZ68c/wRwxHgHrP26UVqwfm3m	Jordan	Moore	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	8f865b0c-cdf6-4a15-b46b-17db019a50c5
60	omarr.nico@my2ducks.com	$2b$12$BqN161bnUPNQiIO1mm05e.vcLpPlGBw20yfl9pUNJu0sLN8d.6h8u	Teegan	Aguilar	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	fdcaf8eb-00f0-4090-9540-917d175d6fcf
62	shruthi.kamorra@my2ducks.com	$2b$12$eHKm521Ahvaxk9jpMvV0g.vZldVKxQzA50wQyueFNECgDsbX8hnfq	Evangeline	Oneal	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	db2f9466-6422-485e-949c-596b10c348b3
63	sylvio.decklin@my2ducks.com	$2b$12$a9hS/SZ6qyoHbn8F.22J5embfB3wrF9tG9vcAMX4Tib3hKx1fKXwi	Dahlia	Simon	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	45783629-55e4-44ef-b2b5-9925ea70cf1e
64	kanae.kamiya@my2ducks.com	$2b$12$mizJh2t/L5u4pfqF1rPNxednfwN8JsG2K2d2VqbiIVgK7J4UrAp5i	Shelley	Oneill	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	20aae979-d008-4e2d-84ec-9236d1da0d1f
65	sssss@my2ducks.com	$2b$12$Hci.GtCWBx3ma6A7B2O23e4Tg0y.oj4qNp0PMAoSWEE9Q9lvSjVrC	Todd	Dillon	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	56493f56-573a-4dde-a756-7332076b651c
66	chinmayi.skila@my2ducks.com	$2b$12$16g.hfCVZaPrfG7xeV2kQOalFQ6ohBYLK2SO6x7m.O6mkBZmwDibO	Hudfd	Padilla	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	f1768555-3118-49c6-8a48-64d6bab43bb2
67	adil.jabdiel@my2ducks.com	$2b$12$S/PLO8otUoUQllQ7UH6hveer2EofXVfp3/kH8cX44HrTOVC3xhKJa	Hedwig	Francis	\N	2023-10-09 12:12:19.969503	2023-10-09 12:12:19.969523	\N	t	\N	\N	f	\N	34688af9-701d-4c84-aeff-e9e85c9e0be1
69	vumlamurda@gufum.com	$2b$12$bd1DkDfzt47sAYIqfv.BCuVizOX7uXTsaeI0WuG6sHiW4HsfD15xG	Abdullah	W.	jsdjsd	2023-10-12 16:10:40.446226	2023-10-12 16:10:40.446242	\N	t	\N	\N	f	\N	8de9d17c-cc09-42ec-ac97-036d8a09dcde
70	catrikikki@gufum.com	$2b$12$qI0Zp5x2u0ZUTgirPafpeeeWvuT4xC.F.aELX7sSCUKx7nQkzKy4K	Abdullah	W.	jsdjsd	2023-10-12 23:25:46.45119	2023-10-12 23:25:46.451203	\N	f	125087	\N	f	\N	2eded61f-71bc-410d-8019-3b7b0b3a64f7
72	timothy.chanson@my2ducks.com	$2b$12$LccrEdALckvRh7Y3J.wkbuOwHqMZ/u7m.3/HiabAIm4nboWWzrd/y	Iansfsdf	Parsons	\N	2023-10-12 16:22:38.541651	2023-10-12 16:22:38.541671	\N	t	\N	\N	f	\N	b9d1387a-35d9-4fd0-877b-e12b334ea920
95	aerial.keyonna@meshfor.com	$2b$12$1z0KCQw08MrSc9zbWAv4GeYEEiEdSmD0mMMKU47iyood77GCY.Zny	Malik	Preston	\N	2023-11-09 00:08:55.606658	2023-11-10 10:54:24.518021	\N	t	e981afb3dabe473d9fa36ceaffe19f2a4a1a227baa96453dbd6fd9cf5fa1e502	\N	f	false	a9b60171-1806-4886-aa4b-dd9976d83130
89	pafep28893@newnime.com	$2b$12$Px9ygD3phxhzA2Y0mQdtf.9TyxGwz.ak6eXWFVxoX7X8Jx7dBPtf2	kailum	fender	090078601	2023-11-09 00:08:55.606658	2023-11-10 08:30:35.286136	\N	t	7f4a76ed9e0041698bb1148e1f400e50986a854d06cd4f6eaf9fa6f211008886	\N	f	false	24724a97-331c-4636-9557-25bc6fd89443
83	gurkuzilme@gufums.com	$2b$12$Uhs39G/FUOc5OcBL7IAux.6iLX.bf31AXPse9IY2/vWsrZ/ZOhGW2	Abdullah	W.	jsdjsd	2023-11-08 22:50:28.881025	2023-11-08 22:50:28.881041	\N	f	518619	\N	f	false	35ce7c91-de99-44c8-a820-28047c2fe8d6
90	belinda.kayan@meshfor.com	$2b$12$zL3vyeu/Na7Oevh1EP9c1eUIftlKUBoeuJfq0TNZAuAA9IMJgU66i	Lillian	Strong	\N	2023-11-09 00:08:55.606658	2023-11-10 08:40:55.010519	\N	t	\N	\N	f	false	65fe2bc8-0789-4e50-a0c6-c0b6db00c17d
91	kieran.marquese@meshfor.com	$2b$12$VtZe5154aBZlejO.OSkgbOImGDR2hfQ8KsvsK0EZL3ynceoJ1SXQu	Rhiannon	Dean	\N	2023-11-09 00:08:55.606658	2023-11-10 09:03:38.425545	\N	t	11697918fb504aff8959b2ea66d96e6aade2199443a240089dcc52cc93a0c57d	\N	f	false	9c602ce2-e047-4599-9812-a8b92c838006
73	shaheerfluid@gmail.com	$2b$12$Nx64u3urZkFY7O.ct9EEqeahQVegt0SdY1WOpOl20abxgRI09U2fm	John	User	+96656781239	2023-10-12 16:22:38.541651	2023-10-12 16:22:38.541671	\N	t	\N	\N	f	68cc3102-8246-4bdc-9363-85de39201867_home.png	c8d4e3c8-2c2c-4efe-8bec-41665ebcb76b
74	wuvebeqy@hexi.pics	$2b$12$2fhwTAn7ytwqeZ7BNl3TMeN/fkOeehrFofoWbHgnDVFw5PO3lm4NW	John	Doee	234235253	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	f	360714	\N	f	false	871887ef-fce6-4b2d-bd6f-3d0a7e9e0034
82	gurkuzilme@gufum.com	$2b$12$9ruPa6siV4LKKJaOrwHYVuGzPtzt0Q1wkspdb9NksYuEw9i29w0Qu	Abdullah	W.	jsdjsd	2023-11-08 22:33:03.475682	2023-11-09 14:32:47.206206	\N	t	a9b2c59a63a24544970305f720d4f1d3c7b051f3eab94f2ebfe20ab23b3dcc90	\N	f	false	5f32e43b-0284-4d72-9450-5e0ff3a304f1
84	gurkuzilme@gufssumss.com	$2b$12$blVDOOgIdy1sfAA4sKxxWeFd3.3YfgyDTEScc1oPfbqNAXtEuQWQ.	Abdullah	W.	jsdjsd	2023-11-09 00:08:55.606658	2023-11-09 00:08:55.606678	\N	f	775765	\N	f	false	d0f200ec-528a-490a-baa5-5d36deb80bf8
85	dordesepso@gufum.com	$2b$12$LQa/2F33h8zqMFs1Fo3tJ.EeEp0L0512aKisVGybRg4I1crUPMF/e	Test	Test	02929292929	2023-11-09 00:08:55.606658	2023-11-09 00:08:55.606678	\N	f	497988	\N	f	false	3e6e9a00-c622-4b22-8010-1e1f379b46d3
86	tirdolipse@gufum.com	$2b$12$h2lX2dxnjWIWiI5YUwLIo.m8Ibyb900ezPLzpNx3cUXFiNIo3QU62	Test	Test	090078601	2023-11-09 00:08:55.606658	2023-11-09 14:37:58.740668	\N	t	\N	\N	f	false	beb8bc88-851c-48c5-a2c0-5c19641c33d5
75	cipiqiwu@hexi.pics	$2b$12$aCUjOHRthaPcOpec/AX8GO0V9v7JP32N4KMyManN1wYRhy.cBhTEO	Lorem	Ipsum	12390184	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	f	964470	\N	f	false	6ab5b2df-d355-44bf-9f51-09f548f488f4
71	kakkaheste@gufum.com	$2b$12$4OP3W.oUvIeXN6Qpd3fgIOaqdvsKEmOxSTsiU8piZ.LDL9bXga4EO	Abdullah	Waqar	jsdjsd	2023-10-12 23:28:14.476408	2023-10-12 23:28:14.476421	\N	t	\N	\N	f	37b93465-124b-429f-a625-a33d6fb19f58_rick-and-morty-adult-swim-cartoon-rick-sanchez-wallpaper-4167485795.png	01df7f5c-618a-40f4-8c50-f16170a43b50
76	qasypequ@tutuapp.bid	$2b$12$NcRjp3HKQAnBOEh2DHouteUBAbVCgQsPLxuyvcaS85DAHSEk59bh2	Test	User	3190582395	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	f	249652	\N	f	false	f449eab0-7e13-42b7-aad4-ade36e965c3e
77	weduboko@socam.me	$2b$12$vzpyRfZb80Y2tFjfwrmd6OQWi/OCovEkORN94MS7UnOAlvljJTb.W	Test	User	01294823	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	f	307430	\N	f	false	62151530-de00-4e86-8fed-18e496a32db4
78	nuxezube@tutuapp.bid	$2b$12$zMbL2IwP6iCYVzT5lptRGOS3FOCBkWfBVIJVxOaNNbjb1PAIK.cAe	Test	User5	1204831	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	f	841585	\N	f	false	a0f891af-c5e1-41cb-a75e-a0f234deabff
79	sacimege@tutuapp.bid	$2b$12$03sraevbUduawDtrui.SDOo57DJtxfpqrk/1YNmwgSrjX9vD.3fI6	Test	Userrr	324235124	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	f	689757	\N	f	false	7c303323-b3a4-435c-9b35-2fc8da0c0e09
80	hanson.stacey@meshfor.com	$2b$12$X1egwabCbLfnq4kWUw/z5eafEfDSGY9TC66/9/0fVR6Qb0xLLcixC	Rhiannon	Hampton	\N	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	t	\N	\N	f	false	e37f420b-ceef-4510-a993-246b80175fe2
87	woodthom@gmail.com	$2b$12$sqlfKiluP7kLU1i6q2k1euZa1EZm8x6SbxAwsdjbZQ7BA.lZPi67i	Thomas	Wood	07906331524	2023-11-09 00:08:55.606658	2023-11-09 15:31:29.043282	\N	t	\N	\N	f	false	d155b6e8-5ef4-4d42-91eb-2becec3a1c8c
92	eeeee@meshfor.com	$2b$12$95rILGuQSoTL1SxxsusFwejU5WhhHYhPAjTAZ6yOK5hfmgPsTkIWO	Minerva	Kennedy	\N	2023-11-09 00:08:55.606658	2023-11-10 09:10:53.886283	\N	t	f2b33798531345aabdd7dbe8258487ba3065f6808ef64237b2dea96a46da944e	\N	f	false	bf657489-dcba-4e1d-8802-834aa1c34b5a
81	emett.greydon@meshfor.com	$2b$12$YiCzQs/8uvxq5.bDlpojg.1rbu37WbXrNtsCPzJlb73V/2uZPgOp.	Constance	Everett	\N	2023-11-03 15:13:39.051879	2023-11-03 15:13:39.05191	\N	t	\N	\N	f	f8127e60-f47c-416c-acf0-ecace31f719f_appstore.png	894dc0a3-be7c-40b0-b3c0-250b44464161
96	cisco.sayler@meshfor.com	$2b$12$0EA.JecLtb8WfFaPsfwqqukO26a1462pZe4fFsA.R0PYjvCN6sGQ2	Dexter	Middleton	\N	2023-11-09 00:08:55.606658	2023-11-10 11:09:50.859295	\N	t	ccdbc340d9df43d4b909af8be5f5172e6f1682e33b9a435aab7db4e6093045b2	\N	f	false	3a44b173-06e1-480a-a328-b5d0c7610f5e
93	silus.fuller@meshfor.com	$2b$12$BzsZfxX6NF5jIMKB/ipGdeMmozx/1PGghC1Y6FhzJcGL7HstBmJ/y	Cullen	Ayala	\N	2023-11-09 00:08:55.606658	2023-11-10 10:15:50.130236	\N	t	6686bf5eec164126b995af28e2c86c0d6b7d42c5d93443e0aa9293c3c41ccc64	\N	f	false	58421cb1-5c82-4ac9-83ba-df9b6eea03db
88	kailum.fender@meshfor.com	$2b$12$MKhG2udtwyMKsZQtn0lgwOZw45jol65BbyyJG.vZ8OCvNy5JPjWJ6	kailum	fender	090078601	2023-11-09 00:08:55.606658	2023-11-10 08:20:27.807718	\N	t	\N	\N	f	false	c40e4266-31e3-4935-8421-40aad7b3b323
94	kamdyn.izair@meshfor.com	$2b$12$UcENN1SMNQo4tyUQz9TcG.KANZjbApHqT4gESbjkZvmMDp5vQSCgi	Caesar	Glenn	\N	2023-11-09 00:08:55.606658	2023-11-10 10:47:55.601431	\N	t	50f799e0075f497e9423380819170e1aa0a011c23f324a5583bf356281a98cb4	\N	f	false	1682e6e8-49d4-4989-90f7-85bcb11e09b9
97	kanya.ellyanna@meshfor.com	$2b$12$hsl.e8L1qdvEXcGtbpK9Me0FKhtz7ld7NY0CXc9dQaKNDk.2MPtQC	Doris	Berry	\N	2023-11-09 00:08:55.606658	2023-11-10 11:25:58.037268	\N	t	ad0aeb04d1fe4106bf646ea9196c66fd618c40d6bd7e4dcea85078adf09ed546	\N	f	false	231b9df7-1f76-487e-85c9-43e73717633c
98	thomas@fastdatascience.com	$2b$12$A7kwaFFzdFvguJhREYJInefEX4jDNB4ri1nCHca5CmJ.QbJcoX.Hq	Thomas	Wood	0790633524	2023-11-09 00:08:55.606658	2023-11-10 12:03:36.08451	\N	t	\N	\N	f	false	2bf43135-9afc-4540-a975-54ea7d96f228
\.


--
-- TOC entry 4244 (class 0 OID 4350498)
-- Dependencies: 245
-- Data for Name: UserResourceUsage; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."UserResourceUsage" (id, user_id, resource_type_id, start_time, end_time) FROM stdin;
\.


--
-- TOC entry 4231 (class 0 OID 4192247)
-- Dependencies: 232
-- Data for Name: UserRole; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."UserRole" (user_id, role_id) FROM stdin;
25	3
25	5
69	3
70	3
71	3
72	3
73	3
74	3
75	3
76	3
77	3
78	3
79	3
80	3
81	3
82	3
83	3
84	3
85	3
86	3
87	3
88	3
89	3
90	3
91	3
92	3
93	3
94	3
95	3
96	3
97	3
98	3
\.


--
-- TOC entry 4237 (class 0 OID 4199447)
-- Dependencies: 238
-- Data for Name: UserSubscription; Type: TABLE DATA; Schema: public; Owner: kjezmrcz
--

COPY public."UserSubscription" (id, user_id, subscription_type_id, start_date, end_date, created_at) FROM stdin;
1	70	4	2023-10-12 23:25:46.455513	2023-10-12 23:26:45.855678	2023-10-12 23:25:46.455526
2	71	4	2023-10-12 23:28:14.480677	2023-10-12 23:28:40.708276	2023-10-12 23:28:14.48069
3	74	4	2023-11-03 15:13:39.230457	2023-11-03 16:17:43.63295	2023-11-03 15:13:39.230475
4	75	4	2023-11-03 15:13:39.230457	2023-11-03 16:18:34.719027	2023-11-03 15:13:39.230475
5	76	4	2023-11-03 15:13:39.230457	2023-11-06 13:00:54.158841	2023-11-03 15:13:39.230475
6	77	4	2023-11-03 15:13:39.230457	2023-11-06 13:12:29.981736	2023-11-03 15:13:39.230475
7	78	4	2023-11-03 15:13:39.230457	2023-11-06 13:13:54.346557	2023-11-03 15:13:39.230475
8	79	4	2023-11-03 15:13:39.230457	2023-11-06 14:10:29.571847	2023-11-03 15:13:39.230475
9	80	4	2023-11-03 15:13:39.230457	2023-11-07 08:24:01.973028	2023-11-03 15:13:39.230475
10	81	4	2023-11-03 15:13:39.230457	2023-11-07 08:38:32.980327	2023-11-03 15:13:39.230475
11	82	4	2023-11-08 22:33:03.524916	2023-11-08 22:33:53.659683	2023-11-08 22:33:03.524928
12	83	4	2023-11-08 22:50:28.92871	2023-11-08 22:51:29.784132	2023-11-08 22:50:28.928725
13	84	4	2023-11-09 00:08:55.772742	2023-11-09 14:34:21.442235	2023-11-09 00:08:55.77276
14	85	4	2023-11-09 00:08:55.772742	2023-11-09 14:35:40.283406	2023-11-09 00:08:55.77276
15	86	4	2023-11-09 00:08:55.772742	2023-11-09 14:37:43.816355	2023-11-09 00:08:55.77276
16	87	4	2023-11-09 00:08:55.772742	2023-11-09 15:31:08.394112	2023-11-09 00:08:55.77276
17	88	4	2023-11-09 00:08:55.772742	2023-11-10 08:14:46.480051	2023-11-09 00:08:55.77276
18	89	4	2023-11-09 00:08:55.772742	2023-11-10 08:27:55.045255	2023-11-09 00:08:55.77276
19	90	4	2023-11-09 00:08:55.772742	2023-11-10 08:40:39.556007	2023-11-09 00:08:55.77276
20	91	4	2023-11-09 00:08:55.772742	2023-11-10 09:02:12.478993	2023-11-09 00:08:55.77276
21	92	4	2023-11-09 00:08:55.772742	2023-11-10 09:10:13.013962	2023-11-09 00:08:55.77276
22	93	4	2023-11-09 00:08:55.772742	2023-11-10 10:14:59.488744	2023-11-09 00:08:55.77276
23	94	4	2023-11-09 00:08:55.772742	2023-11-10 10:44:00.777666	2023-11-09 00:08:55.77276
24	95	4	2023-11-09 00:08:55.772742	2023-11-10 10:53:59.082485	2023-11-09 00:08:55.77276
25	96	4	2023-11-09 00:08:55.772742	2023-11-10 11:08:57.527465	2023-11-09 00:08:55.77276
26	97	4	2023-11-09 00:08:55.772742	2023-11-10 11:22:05.752186	2023-11-09 00:08:55.77276
27	98	4	2023-11-09 00:08:55.772742	2023-11-10 12:03:13.738395	2023-11-09 00:08:55.77276
29	71	2	2023-10-12 23:25:46.455	2023-10-12 23:25:46.455	2023-10-12 23:25:46.455
\.


--
-- TOC entry 4284 (class 0 OID 0)
-- Dependencies: 250
-- Name: Document_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."Document_id_seq"', 1, true);


--
-- TOC entry 4285 (class 0 OID 0)
-- Dependencies: 252
-- Name: Document_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."Document_user_id_seq"', 1, false);


--
-- TOC entry 4286 (class 0 OID 0)
-- Dependencies: 228
-- Name: Role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."Role_id_seq"', 5, true);


--
-- TOC entry 4287 (class 0 OID 0)
-- Dependencies: 241
-- Name: SubscriptionType_currency_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."SubscriptionType_currency_id_seq"', 2, true);


--
-- TOC entry 4288 (class 0 OID 0)
-- Dependencies: 247
-- Name: UserResourceUsage_resource_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."UserResourceUsage_resource_type_id_seq"', 1, false);


--
-- TOC entry 4289 (class 0 OID 0)
-- Dependencies: 246
-- Name: UserResourceUsage_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."UserResourceUsage_user_id_seq"', 1, false);


--
-- TOC entry 4290 (class 0 OID 0)
-- Dependencies: 226
-- Name: User_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public."User_id_seq"', 98, true);


--
-- TOC entry 4291 (class 0 OID 0)
-- Dependencies: 239
-- Name: currecny_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.currecny_id_seq', 3, true);


--
-- TOC entry 4292 (class 0 OID 0)
-- Dependencies: 242
-- Name: resourcetype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.resourcetype_id_seq', 1, true);


--
-- TOC entry 4293 (class 0 OID 0)
-- Dependencies: 248
-- Name: subscriptionattribute_subscription_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.subscriptionattribute_subscription_type_id_seq', 1, false);


--
-- TOC entry 4294 (class 0 OID 0)
-- Dependencies: 233
-- Name: subscriptiontype_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.subscriptiontype_id_seq', 4, true);


--
-- TOC entry 4295 (class 0 OID 0)
-- Dependencies: 244
-- Name: userresourceusage_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.userresourceusage_id_seq', 1, false);


--
-- TOC entry 4296 (class 0 OID 0)
-- Dependencies: 231
-- Name: userrole_role_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.userrole_role_id_seq', 1, false);


--
-- TOC entry 4297 (class 0 OID 0)
-- Dependencies: 230
-- Name: userrole_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.userrole_user_id_seq', 1, false);


--
-- TOC entry 4298 (class 0 OID 0)
-- Dependencies: 235
-- Name: usersubscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.usersubscription_id_seq', 29, true);


--
-- TOC entry 4299 (class 0 OID 0)
-- Dependencies: 237
-- Name: usersubscription_subscription_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.usersubscription_subscription_type_id_seq', 1, false);


--
-- TOC entry 4300 (class 0 OID 0)
-- Dependencies: 236
-- Name: usersubscription_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: kjezmrcz
--

SELECT pg_catalog.setval('public.usersubscription_user_id_seq', 1, false);


--
-- TOC entry 4061 (class 2606 OID 4012228)
-- Name: User User_pkey; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_pkey" PRIMARY KEY (id);


--
-- TOC entry 4076 (class 2606 OID 4349752)
-- Name: Currency currecny_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Currency"
    ADD CONSTRAINT currecny_pk PRIMARY KEY (id);


--
-- TOC entry 4084 (class 2606 OID 4757340)
-- Name: Document document_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Document"
    ADD CONSTRAINT document_pk PRIMARY KEY (id);


--
-- TOC entry 4078 (class 2606 OID 4350493)
-- Name: ResourceType resourcetype_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."ResourceType"
    ADD CONSTRAINT resourcetype_pk PRIMARY KEY (id);


--
-- TOC entry 4064 (class 2606 OID 4192234)
-- Name: Role role_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Role"
    ADD CONSTRAINT role_pk PRIMARY KEY (id);


--
-- TOC entry 4066 (class 2606 OID 4192236)
-- Name: Role role_un; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Role"
    ADD CONSTRAINT role_un UNIQUE (name);


--
-- TOC entry 4082 (class 2606 OID 4392699)
-- Name: SubscriptionAttribute subscriptionattribute_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionAttribute"
    ADD CONSTRAINT subscriptionattribute_pk PRIMARY KEY (subscription_type_id);


--
-- TOC entry 4070 (class 2606 OID 4199424)
-- Name: SubscriptionType subscriptiontype_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionType"
    ADD CONSTRAINT subscriptiontype_pk PRIMARY KEY (id);


--
-- TOC entry 4072 (class 2606 OID 4199429)
-- Name: SubscriptionType subscriptiontype_un; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionType"
    ADD CONSTRAINT subscriptiontype_un UNIQUE (name);


--
-- TOC entry 4080 (class 2606 OID 4350503)
-- Name: UserResourceUsage userresourceusage_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserResourceUsage"
    ADD CONSTRAINT userresourceusage_pk PRIMARY KEY (id);


--
-- TOC entry 4068 (class 2606 OID 4192498)
-- Name: UserRole userrole_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserRole"
    ADD CONSTRAINT userrole_pk PRIMARY KEY (user_id, role_id);


--
-- TOC entry 4074 (class 2606 OID 4199455)
-- Name: UserSubscription usersubscription_pk; Type: CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserSubscription"
    ADD CONSTRAINT usersubscription_pk PRIMARY KEY (id);


--
-- TOC entry 4062 (class 1259 OID 4758322)
-- Name: user_user_resource_identifier_idx; Type: INDEX; Schema: public; Owner: kjezmrcz
--

CREATE INDEX user_user_resource_identifier_idx ON public."User" USING btree (user_resource_identifier);


--
-- TOC entry 4093 (class 2606 OID 4757355)
-- Name: Document document_fk; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."Document"
    ADD CONSTRAINT document_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- TOC entry 4092 (class 2606 OID 4392700)
-- Name: SubscriptionAttribute subscriptionattribute_fk; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionAttribute"
    ADD CONSTRAINT subscriptionattribute_fk FOREIGN KEY (subscription_type_id) REFERENCES public."SubscriptionType"(id);


--
-- TOC entry 4087 (class 2606 OID 4349765)
-- Name: SubscriptionType subscriptiontype_fk; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."SubscriptionType"
    ADD CONSTRAINT subscriptiontype_fk FOREIGN KEY (currency_id) REFERENCES public."Currency"(id);


--
-- TOC entry 4090 (class 2606 OID 4350513)
-- Name: UserResourceUsage userresourceusage_fk; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserResourceUsage"
    ADD CONSTRAINT userresourceusage_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- TOC entry 4091 (class 2606 OID 4350525)
-- Name: UserResourceUsage userresourceusage_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserResourceUsage"
    ADD CONSTRAINT userresourceusage_fk_1 FOREIGN KEY (resource_type_id) REFERENCES public."ResourceType"(id);


--
-- TOC entry 4085 (class 2606 OID 4192252)
-- Name: UserRole userrole_fk; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserRole"
    ADD CONSTRAINT userrole_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- TOC entry 4086 (class 2606 OID 4192257)
-- Name: UserRole userrole_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserRole"
    ADD CONSTRAINT userrole_fk_1 FOREIGN KEY (role_id) REFERENCES public."Role"(id);


--
-- TOC entry 4088 (class 2606 OID 4199456)
-- Name: UserSubscription usersubscription_fk; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserSubscription"
    ADD CONSTRAINT usersubscription_fk FOREIGN KEY (user_id) REFERENCES public."User"(id);


--
-- TOC entry 4089 (class 2606 OID 4199461)
-- Name: UserSubscription usersubscription_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: kjezmrcz
--

ALTER TABLE ONLY public."UserSubscription"
    ADD CONSTRAINT usersubscription_fk_1 FOREIGN KEY (subscription_type_id) REFERENCES public."SubscriptionType"(id);


--
-- TOC entry 4258 (class 0 OID 0)
-- Dependencies: 4257
-- Name: DATABASE kjezmrcz; Type: ACL; Schema: -; Owner: kjezmrcz
--

REVOKE CONNECT,TEMPORARY ON DATABASE kjezmrcz FROM PUBLIC;


--
-- TOC entry 4260 (class 0 OID 0)
-- Dependencies: 25
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO PUBLIC;


-- Completed on 2023-11-19 22:55:42 +04

--
-- PostgreSQL database dump complete
--

