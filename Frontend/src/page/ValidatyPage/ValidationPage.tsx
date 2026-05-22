import React, { useState, useEffect } from 'react';
import { ImportArea } from '../../component/ImportArea/ImportArea';
import { DataTable } from '../../component/DataTable/DataTable';
import { LineCompare } from '../../component/LineCompare/LineCompare';
import './ValidationPage.css';
import api from '../../services/api';

interface ImportedData {
  data: any[];
  fileName: string;
}

export const ValidatyPage = () => {
  const [firstImport, setFirstImport] = useState<ImportedData | null>(null);
  const [secondImport, setSecondImport] = useState<ImportedData | null>(null);
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFirstImport = (data: any[], fileName: string) => {
    setFirstImport({ data, fileName });
  };

  const handleSecondImport = (data: any[], fileName: string) => {
    setSecondImport({ data, fileName });
  };

  // Call API when both imports are available
  useEffect(() => {
    if (firstImport && secondImport) {
      const fetchComparison = async () => {
        setLoading(true);
        setError(null);
        try {
          await api.createAnalyticsTimeslotWithEachSpreadsheet(firstImport , secondImport);
          setComparisonResult(await api.getCompareScheduler());
         
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
    <div className="validaty-page">
      <div className="validaty-container">
        <header className="page-header">
          <h1>Vérifier les contraintes</h1>
        </header>
        <main className="validaty-content">
          <div className="import-areas">
            <ImportArea
              title="Créneau prévu (csv)"
              onDataImported={handleFirstImport}
              onDataCleared={() => setFirstImport(null)}
              isUsingAPI={false}
            />
            <ImportArea
              title="Créneau placé (vcs)"
              onDataImported={handleSecondImport}
              onDataCleared={() => setSecondImport(null)}
              isUsingAPI={true}
            />
          </div>
          {(firstImport && secondImport) && (
            <div className="data-tables">
              {loading && <p>Chargement de la comparaison...</p>}
              {error && <p style={{ color: 'red' }}>Erreur: {error}</p>}
              {comparisonResult && (
                <div className="comparison-results">
                  <h2>Résultat de la comparaison</h2>
                  
                  {comparisonResult.length === 0 ? (
                    <p className="no-differences">Tout les créneaux ont bien été placés</p>
                  ) : (
                    <div className={`sections-container ${comparisonResult.filter((item: any) => item.heures > 0).length === 0 || comparisonResult.filter((item: any) => item.heures < 0).length === 0 ? 'single-section' : ''}`}>
                      {comparisonResult.filter((item: any) => item.heures > 0).length > 0 && (
                        <div className="section-unplaced">
                          <h3>Créneaux non-placés</h3>
                          <div className="results-header">
                            <div className="header-cell">Code_Ens</div>
                            <div className="header-cell">Code_Res_SAE</div>
                            <div className="header-cell">Type_ens</div>
                            <div className="header-cell">Heure</div>
                          </div>
                          <div className="results-list">
                            {comparisonResult
                              .filter((item: any) => item.heures > 0)
                              .map((item: any, index: number) => (
                                <LineCompare
                                  key={`unplaced-${index}`}
                                  code_ens={item.code_ens}
                                  code_res_sae={item.code_res_sae}
                                  type_ens={item.type_ens}
                                  heure={item.heures}
                                />
                              ))}
                          </div>
                        </div>
                      )}

                      {/* Créneaux surplacés (heures négatives) */}
                      {comparisonResult.filter((item: any) => item.heures < 0).length > 0 && (
                        <div className="section-overplaced">
                          <h3>Débordement de créneaux</h3>
                          <div className="results-header">
                            <div className="header-cell">Code_Ens</div>
                            <div className="header-cell">Code_Res_SAE</div>
                            <div className="header-cell">Type_ens</div>
                            <div className="header-cell">Heure</div>
                          </div>
                          <div className="results-list">
                            {comparisonResult
                              .filter((item: any) => item.heures < 0)
                              .map((item: any, index: number) => (
                                <LineCompare
                                  key={`overplaced-${index}`}
                                  code_ens={item.code_ens}
                                  code_res_sae={item.code_res_sae}
                                  type_ens={item.type_ens}
                                  heure={item.heures*-1}
                                />
                              ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
