import React, { useState, useEffect } from 'react';
import { ImportArea } from '../../component/ImportArea/ImportArea';
import './ValidationPage.css';
import api from '../../services/api';
import { Discipline } from '../../component/Discipline/Discipline';

interface ValidationPage{
  schedulerList: any[];
  setSchedulerList: React.Dispatch<React.SetStateAction<any[]>>;
}

interface ImportedData {
  data: any[];
  fileName: string;
}

export const ValidationPage = ({ schedulerList, setSchedulerList }: ValidationPage) => {
  const [firstImport, setFirstImport] = useState<ImportedData | null>(null);
  const [secondImport, setSecondImport] = useState<ImportedData | null>(null);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [comparisonResultUnique, setComparisonResultUnique] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFirstImport = (data: any[], fileName: string) => {
    setFirstImport({ data, fileName });
  };

  const handleSecondImport = (data: any[], fileName: string) => {
    setSecondImport({ data, fileName });
  };
  useEffect(() => {
    if (firstImport && secondImport) {
      const fetchComparison = async () => {
        setLoading(true);
        setError(null);
        try {
          
          await api.createAnalyticsTimeslotWithEachSpreadsheet(firstImport , secondImport);
          let data=await api.getlesson();
          setComparisonResult(data);
          const uniqueCodes = [...new Set(data.map((r: any) => r.code_res_sae))];
          setComparisonResultUnique(uniqueCodes);
          setSchedulerList(data);
          
          console.log(`Scheduler list:`, schedulerList);
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Une erreur est survenue');
          console.error('Erreur lors de la comparaison:', err);
        } finally {
          setLoading(false);
        }
      };
      fetchComparison();
    }
  }, [firstImport, secondImport]);

  return (
    <div className="validation-page">
      <div className="validation-container">
        <header className="page-header">
          <h1>Vérifier les contraintes</h1>
        </header>
        <main className="validation-content">
          <div className="import-areas">
            <ImportArea
              title="Créneaux prévus (csv)"
              onDataImported={handleFirstImport}
              onDataCleared={() => setFirstImport(null)}
              isUsingAPI={false}
            />
            <ImportArea
              title="Créneaux placés (vcs)"
              onDataImported={handleSecondImport}
              onDataCleared={() => setSecondImport(null)}
              isUsingAPI={true}
            />
          </div>
          {(firstImport && secondImport) && (
            <div className="data-tables">
              {loading && (
                <div className="empty-state">
                  <div className="empty-state-icon">⏳</div>
                  <div className="empty-state-text">Chargement de la comparaison...</div>
                </div>
              )}
              {error && (
                <div className="empty-state" style={{ borderColor: '#fca5a5', background: '#fef2f2' }}>
                  <div className="empty-state-icon">❌</div>
                  <div className="empty-state-text" style={{ color: '#dc2626' }}>Erreur: {error}</div>
                </div>
              )}
              {comparisonResult && !loading && !error && (
                <div>
                  <h2>Contrôle semaine {firstImport.data[0].semaine.split('-')[1]} - semestre {firstImport.data[0].code_res_sae.split('-')[1]} </h2>

                  <div className="comparison-results">
                    {
                      comparisonResultUnique.map((result: any) => (
                        <Discipline  key={result} code_sae={result} sessionList={comparisonResult.filter((r: any) => r.code_res_sae === result)} />
                      ))
                    }
                  </div>

                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
