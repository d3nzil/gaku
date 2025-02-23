import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';


export interface ThemeValues {
    [key: string]: string;
}

// colors based on Selenized theme: https://github.com/jan-warchol/selenized/blob/master/the-values.md
// but there are few custom colors
const lightTheme: ThemeValues = {
    "--bg-color": '#fbf3db',
    "--text-color": '#002b36',
    "--link-color": '#0000ee',
    "--visited-link": '#551a8b',
    "--active-link": '#ff0000',
    "--input-bg": '#fefeee',
    "--correct-answer-bg": 'lightgreen',
    "--incorrect-answer-bg": 'pink',
    "--input-bg-focus": "#ffffff",

};

const darkTheme: ThemeValues = {
    "--bg-color": '#103c48',
    // "--text-color": '#cad8d9',
    "--text-color": '#ebc13d',
    "--link-color": '#84c747',
    "--visited-link": '#bd96ba',
    "--active-link": '#58a3ff',
    // "--input-bg": '#2d5b69',
    "--input-bg": '#103c48',
    "--correct-answer-bg": '#489100',
    "--incorrect-answer-bg": '#82111d',
    "--input-bg-focus": "#2d5b69"
};

enum ThemeType {
    LIGHT = 'LIGHT',
    DARK = 'DARK'
}

type Theme = {
    [k in ThemeType]: ThemeValues;
}

interface ThemeContextType {
    currentThemeType: ThemeType;
    themeData: Theme;
    setThemeValues: (theme: ThemeType, values: ThemeValues) => void;
    setCurrentTheme: (theme: ThemeType) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [themeData, setThemeData] = useState<Theme>({
        [ThemeType.LIGHT]: lightTheme,
        [ThemeType.DARK]: darkTheme
    });
    const savedTheme = localStorage.getItem('theme') as ThemeType;
    const [currentThemeType, setCurrentTheme] = useState<ThemeType>(savedTheme === ThemeType.DARK ? ThemeType.DARK : ThemeType.LIGHT);

    const setThemeValues = (theme: ThemeType, values: ThemeValues) => {
        setThemeData({ ...themeData, [theme]: values });
    };

    const contextValue = {
        currentThemeType,
        themeData,
        setThemeValues,
        setCurrentTheme
    };

    useEffect(() => {
        const themeValues = themeData[currentThemeType];
        const prevThemeValues = themeData[currentThemeType === ThemeType.LIGHT ? ThemeType.DARK : ThemeType.LIGHT];
        localStorage.setItem('theme', currentThemeType);

        // Remove previous theme values
        Object.entries(prevThemeValues).forEach(([key, _]) =>
            document.documentElement.style.removeProperty(key)
        );

        // Set new theme values
        Object.entries(themeValues).forEach(([key, value]) =>
            document.documentElement.style.setProperty(key, value)
        );

    }, [currentThemeType, themeData]);

    return (
        <ThemeContext.Provider value={contextValue}>
            {children}
        </ThemeContext.Provider>
    );
};


export const useTheme = (): ThemeContextType => {
    const context = useContext(ThemeContext);
    if (!context)
    {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};

export {
    ThemeType,
}