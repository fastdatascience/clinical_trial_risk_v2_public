import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import {
    createBrowserRouter,
    createRoutesFromElements,
    Route,
    RouterProvider,
} from "react-router-dom";
import {
    Dashboard,
    FileHistory,
    ForgotPassword,
    GoogleCallback,
    Login,
    Settings,
    SignUp,
    SubscriptionPlans,
} from "./components/pages";
import {
    AuthLayout,
    ProtectedLayout,
    RootLayout,
} from "./components/sharedLayout/layout";
import ResetPassword from "./components/pages/ResetPassword";
import Uploady from "@rpldy/uploady";
import { GoogleOAuthProvider } from "@react-oauth/google";

const router = createBrowserRouter(
    createRoutesFromElements(
        <Route element={<RootLayout />}>
            <Route path="/" element={<ProtectedLayout />}>
                <Route path="/" element={<Dashboard />} index />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/history" element={<FileHistory />} />
            </Route>

            <Route element={<AuthLayout />}>
                <Route path="/login" element={<Login />} index />
                <Route path="/register" element={<SignUp />} />
                <Route path="/forgot-password" element={<ForgotPassword />} />
                <Route path="/:token" element={<ResetPassword />} />
                <Route path="/pricing" element={<SubscriptionPlans />} />
            </Route>

            {/* Google OAuth Callback Route */}
            <Route path="/sign-up/callback" element={<GoogleCallback />} />
        </Route>
    )
);

ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
        <GoogleOAuthProvider clientId={import.meta.env.VITE_SECRET_GOOGLE_REDIRECT_URL}>
            <Uploady accept="image/png, image/jpeg">
                <RouterProvider router={router} />
            </Uploady>
        </GoogleOAuthProvider>
    </React.StrictMode>
);
