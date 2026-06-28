import { useEffect, useState } from "react";
import { ValidationContext, type ImportedData, type Session } from "./context";
import api from "./api";
import { data } from "react-router-dom";

interface Props {
  children: React.ReactNode;
}

export function ValidationProvider({ children }: Props) {
  const [schedulerList, setSchedulerList] = useState<Session[]>([]);
  const [comparisonResult, setComparisonResult] = useState<Session[]>([]);
  const [comparisonResultUnique, setComparisonResultUnique] = useState<string[]>([]);
  const [firstImport, setFirstImport] = useState<ImportedData | null>(null);
  const [secondImport, setSecondImport] = useState<ImportedData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!firstImport || !secondImport) return;

    const fetchComparison = async () => {
      setLoading(true);
      setError(null);

      try {
        await api.createAnalyticsTimeslotWithEachSpreadsheet(firstImport, secondImport);

        const data: Session[] = await api.getTrueLesson();

        setComparisonResult(data);
        setComparisonResultUnique(
          [...new Set(data.map(r => r.code_res_sae))]
        );
        setSchedulerList(data);
        
        console.log(comparisonResult);
        console.log(comparisonResultUnique);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur");
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [firstImport, secondImport]);

  return (
    <ValidationContext.Provider
      value={{
        schedulerList,
        setSchedulerList,
        firstImport,
        secondImport,
        setFirstImport,
        setSecondImport,
        comparisonResult,
        setComparisonResult,
        comparisonResultUnique,
        setComparisonResultUnique,
        loading,
        setLoading,
        error,
        setError,
      }}
    >
      {children}
    </ValidationContext.Provider>
  );
}