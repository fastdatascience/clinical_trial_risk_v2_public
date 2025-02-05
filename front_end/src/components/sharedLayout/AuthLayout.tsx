import React from "react"

import { Footer, AuthLayoutHeader } from "../common"
import { Outlet } from "react-router-dom"

const AuthLayout: React.FC = () => {
    return (
        <div className="bg-Gray flex flex-col items-center justify-center">
            <AuthLayoutHeader />
            <Outlet />
            <Footer />
        </div>
    )
}

export default AuthLayout
