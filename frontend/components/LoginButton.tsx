"use client";

import {Button} from "@/components/ui/button";
import { signIn } from "next-auth/react";
export const LoginButton = () => {
    return (
    <Button onClick={async () => {
        // "use server";
        const currentUrl = window.location.href;
        signIn("google", { callbackUrl: currentUrl });
    }}
    >
        Login
    </Button>
    )
};