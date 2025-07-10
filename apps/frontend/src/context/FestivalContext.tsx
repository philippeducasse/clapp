
'use client';

import { createContext, useContext, ReactNode } from 'react';
import { Festival } from '@/interfaces/festival';

const FestivalContext = createContext<Festival | null>(null);

export const FestivalProvider = ({ children, value }: { children: ReactNode, value: Festival }) => {
    return (
        <FestivalContext.Provider value={value}>
            {children}
        </FestivalContext.Provider>
    );
};

export const useFestival = () => {
    const context = useContext(FestivalContext);
    if (!context) {
        throw new Error('useFestival must be used within a FestivalProvider');
    }
    return context;
};
