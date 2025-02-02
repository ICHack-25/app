import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define the types for the context value
interface UserContextType {
    userId: string | null;
    login: (id: string) => void;
    logout: () => void;
}

// Create the context with a default value
const UserContext = createContext<UserContextType | undefined>(undefined);

// Create a custom hook to use the UserContext
export const useUser = (): UserContextType => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error("useUser must be used within a UserProvider");
    }
    return context;
};

// Define the type for the props of the UserProvider
interface UserProviderProps {
    children: ReactNode;
}

// Create a provider component
export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
    const [userId, setUserId] = useState<string | null>(localStorage.getItem('userId') || null);

    const login = (id: string) => {
        setUserId(id);
        localStorage.setItem('userId', id); // Store user ID in localStorage
    };

    const logout = () => {
        setUserId(null);
        localStorage.removeItem('userId');
    };

    return (
        <UserContext.Provider value={{ userId, login, logout }}>
            {children}
        </UserContext.Provider>
    );
};
