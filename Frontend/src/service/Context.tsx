import React from 'react';

export interface Session{
    id: number;
    codeEns: string;
    codeResSae: string;
    week: string;
    hour: number;
    isValid: boolean;
    typeEns: string;
}

export interface ImportedData {
  data: any[];
  fileName: string;
}

interface ValidationContextType {
    schedulerList: Session[];
    setSchedulerList: React.Dispatch<React.SetStateAction<Session[]>>;
    firstImport: ImportedData | null;
    secondImport: ImportedData | null;
    setFirstImport: React.Dispatch<React.SetStateAction<ImportedData | null>>;
    setSecondImport: React.Dispatch<React.SetStateAction<ImportedData | null>>;
    comparisonResult: Session[];
    setComparisonResult: React.Dispatch<React.SetStateAction<Session[]>>;

    comparisonResultUnique: string[];
    setComparisonResultUnique: React.Dispatch<React.SetStateAction<string[]>>;

    loading: boolean;
    setLoading: React.Dispatch<React.SetStateAction<boolean>>;

    error: string | null;
    setError: React.Dispatch<React.SetStateAction<string | null>>;
}

export const ValidationContext = React.createContext<ValidationContextType>({
    schedulerList: [],
    setSchedulerList: () => {},

    firstImport: null,
    setFirstImport: () => {},

    secondImport: null,
    setSecondImport: () => {},

    comparisonResult: [],
    setComparisonResult: () => {},

    comparisonResultUnique: [],
    setComparisonResultUnique: () => {},

    loading: false,
    setLoading: () => {},

    error: null,
    setError: () => {},
});