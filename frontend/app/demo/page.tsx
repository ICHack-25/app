"use client";  // Ensure this is client-side code

import React from "react";
import {signIn, useSession} from "next-auth/react";
import { useRouter } from "next/navigation";  // For client-side redirection
import Demo from "@/components/layout/sections/demo";
import {LoginButton} from "@/components/LoginButton";

const Page = () => {
    const { data: session, status } = useSession();
    const router = useRouter();

    // Show loading indicator while session is being fetched
    if (status === "loading") {
        return <div>Loading...</div>;
    }

    // Redirect user to login page if not authenticated
    if (!session) {
        // router.push("/auth/signin");  // Redirect to sign-in page
        // return <LoginButton/>

        // const currentUrl = window.location.href;
        signIn("google", { callbackUrl: "http://localhost:3000/demo" });
        return null;  // Don't render the page content until redirection
    }

    // localStorage.setItem('userId', '1');

    // Render the protected content if the user is authenticated
    return (
        <div>
            <Demo />
        </div>
    );
};

export default Page;
