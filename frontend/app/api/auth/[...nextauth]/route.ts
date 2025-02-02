import NextAuth, { SessionStrategy, NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import axios from 'axios';
import { User } from "next-auth";  // Import User type from NextAuth for proper typing

const authOptions: NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID!,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
        }),
    ],
    session: {
        strategy: "jwt" as SessionStrategy, // Use JSON Web Tokens for session handling
        maxAge: 60 * 60 * 24 * 7, // Set session to expire after 7 days (in seconds)
    },
    secret: process.env.NEXTAUTH_SECRET!,
    callbacks: {
        // Sign in callback
        async signIn({ user, account, profile }) {
            // Explicitly type `user` as a NextAuth `User`
            console.log("data sending!");
            try {
                // Preparing data to send to your API
                const newUser = {
                    username: user.name, // Using name or email for the username
                    email: user.email,
                    password_hash: "test", // No password provided (could be generated or set as empty)
                    role: "user", // Default role (you can adjust based on your needs)
                    // created_at: new Date().toISOString(), // Current date and time for created_at
                };
                console.log("data sending!");

                // Send a POST request to your `/adduser` API
                const response = await axios.post('http://localhost:5000/adduser', newUser, {
                    headers: {
                        'Content-Type': 'application/json',  // Ensure correct content type
                        'X-API-KEY': 'testkey123',  // Custom header with API key
                    },
                });

                if (response.status !== 201) {
                    throw new Error('Failed to send POST request');
                }

                const userid = response.data.user_id;
                localStorage.setItem('userId', userid);
                console.log("SET USER ID!");



            } catch (error) {
                console.error('Error sending POST request:', error);
            }

            return true; // Return true to allow sign-in to proceed
        },
        // Session callback
        async session({ session, token }) {
            // Explicitly type `session` as NextAuth `Session`
            try {
                const response = await axios.post('https://your-api-endpoint.com/session-update', {
                    email: session.user?.email,
                    sessionToken: token,
                });

                if (response.status !== 200) {
                    console.error('Failed to update session');
                }
            } catch (error) {
                console.error('Error sending session update request:', error);
            }

            return session; // Always return session to continue processing
        },
    },
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
