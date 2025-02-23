import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import api from '../services/api';

// Common state management

interface CommonState {
    testSessionActive: boolean;
    setTestSessionActive: (active: boolean) => void;
    updateTestSessionStatus: () => Promise<boolean>;
}

const CommonStateContext = createContext<CommonState | undefined>(undefined);

export const CommonStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [testActive, setTestSessionActive] = useState(false);
    const updateTestSessionStatus = async () => {
        const active = await api.getSessionStatus();
        console.log('Updating test session status');
        setTestSessionActive(active);
        return active;
    }

    useEffect(() => {
        updateTestSessionStatus();
    }, []);

    // update the test session status every minute
    useEffect(() => {
        const interval = setInterval(() => {
            console.log('Periodic test session status update');
            updateTestSessionStatus();
        }, 60000);
        return () => clearInterval(interval);
    }, []);

    const contextValue = {
        testSessionActive: testActive,
        setTestSessionActive: setTestSessionActive,
        updateTestSessionStatus: updateTestSessionStatus
    };

    return (
        <CommonStateContext.Provider value={contextValue}>
            {children}
        </CommonStateContext.Provider>
    );
};

export const useCommonState = (): CommonState => {
    const context = useContext(CommonStateContext);
    if (!context)
    {
        throw new Error('useCommonState must be used within a CommonStateProvider');
    }
    return context;
};