import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useColorScheme } from 'react-native';

export interface Theme {
  dark: boolean;
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    error: string;
    success: string;
    warning: string;
    info: string;
    white: string;
    black: string;
    gray: string;
    grayLight: string;
    grayDark: string;
  };
  spacing: {
    xs: number;
    sm: number;
    md: number;
    lg: number;
    xl: number;
    xxl: number;
  };
  borderRadius: {
    sm: number;
    md: number;
    lg: number;
    xl: number;
  };
  typography: {
    h1: {
      fontSize: number;
      fontWeight: string;
    };
    h2: {
      fontSize: number;
      fontWeight: string;
    };
    h3: {
      fontSize: number;
      fontWeight: string;
    };
    body: {
      fontSize: number;
      fontWeight: string;
    };
    caption: {
      fontSize: number;
      fontWeight: string;
    };
  };
}

const lightTheme: Theme = {
  dark: false,
  colors: {
    primary: '#007AFF',
    secondary: '#5856D6',
    background: '#FFFFFF',
    surface: '#F2F2F7',
    text: '#000000',
    textSecondary: '#8E8E93',
    border: '#C6C6C8',
    error: '#FF3B30',
    success: '#34C759',
    warning: '#FF9500',
    info: '#007AFF',
    white: '#FFFFFF',
    black: '#000000',
    gray: '#8E8E93',
    grayLight: '#F2F2F7',
    grayDark: '#1C1C1E',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: 'bold',
    },
    h2: {
      fontSize: 24,
      fontWeight: 'bold',
    },
    h3: {
      fontSize: 20,
      fontWeight: '600',
    },
    body: {
      fontSize: 16,
      fontWeight: 'normal',
    },
    caption: {
      fontSize: 14,
      fontWeight: 'normal',
    },
  },
};

const darkTheme: Theme = {
  dark: true,
  colors: {
    primary: '#0A84FF',
    secondary: '#5E5CE6',
    background: '#000000',
    surface: '#1C1C1E',
    text: '#FFFFFF',
    textSecondary: '#8E8E93',
    border: '#38383A',
    error: '#FF453A',
    success: '#32D74B',
    warning: '#FF9F0A',
    info: '#0A84FF',
    white: '#FFFFFF',
    black: '#000000',
    gray: '#8E8E93',
    grayLight: '#1C1C1E',
    grayDark: '#F2F2F7',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  borderRadius: {
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
  },
  typography: {
    h1: {
      fontSize: 32,
      fontWeight: 'bold',
    },
    h2: {
      fontSize: 24,
      fontWeight: 'bold',
    },
    h3: {
      fontSize: 20,
      fontWeight: '600',
    },
    body: {
      fontSize: 16,
      fontWeight: 'normal',
    },
    caption: {
      fontSize: 14,
      fontWeight: 'normal',
    },
  },
};

interface ThemeContextType {
  theme: Theme;
  isDark: boolean;
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark' | 'auto') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const systemColorScheme = useColorScheme();
  const [themeMode, setThemeMode] = useState<'light' | 'dark' | 'auto'>('auto');
  const [isDark, setIsDark] = useState(false);

  // 테마 모드 로드
  const loadThemeMode = async () => {
    try {
      const storedMode = await AsyncStorage.getItem('theme_mode');
      if (storedMode) {
        setThemeMode(storedMode as 'light' | 'dark' | 'auto');
      }
    } catch (error) {
      console.error('테마 모드 로드 오류:', error);
    }
  };

  // 테마 모드 저장
  const saveThemeMode = async (mode: 'light' | 'dark' | 'auto') => {
    try {
      await AsyncStorage.setItem('theme_mode', mode);
    } catch (error) {
      console.error('테마 모드 저장 오류:', error);
    }
  };

  // 테마 토글
  const toggleTheme = () => {
    const newMode = isDark ? 'light' : 'dark';
    setThemeMode(newMode);
    saveThemeMode(newMode);
  };

  // 테마 설정
  const setTheme = (mode: 'light' | 'dark' | 'auto') => {
    setThemeMode(mode);
    saveThemeMode(mode);
  };

  // 현재 테마 결정
  useEffect(() => {
    let shouldBeDark = false;

    switch (themeMode) {
      case 'light':
        shouldBeDark = false;
        break;
      case 'dark':
        shouldBeDark = true;
        break;
      case 'auto':
        shouldBeDark = systemColorScheme === 'dark';
        break;
    }

    setIsDark(shouldBeDark);
  }, [themeMode, systemColorScheme]);

  // 초기화
  useEffect(() => {
    loadThemeMode();
  }, []);

  const theme = isDark ? darkTheme : lightTheme;

  const value: ThemeContextType = {
    theme,
    isDark,
    toggleTheme,
    setTheme,
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}; 