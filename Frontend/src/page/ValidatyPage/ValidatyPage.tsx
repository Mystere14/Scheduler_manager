import React, { useState } from 'react';
import { ImportArea } from '../../component/ImportArea/ImportArea';
import { DataTable } from '../../component/DataTable/DataTable';
import './ValidatyPage.css';

interface ImportedData {
  data: any[];
  fileName: string;
}

export const ValidatyPage = () => {
  const [firstImport, setFirstImport] = useState<ImportedData | null>(null);
  const [secondImport, setSecondImport] = useState<ImportedData | null>(null);

  const handleFirstImport = (data: any[], fileName: string) => {
    setFirstImport({ data, fileName });
  };

  const handleSecondImport = (data: any[], fileName: string) => {
    setSecondImport({ data, fileName });
  };

  return (
    <div className="validaty-page">
      <div className="validaty-container">
        <header className="page-header">
          <h1>Vérifier les contraintes</h1>
        </header>
        <main className="validaty-content">
          <div className="import-areas">
            <ImportArea
              title="Cours.csv"
              onDataImported={handleFirstImport}
            />
            <ImportArea
              title="EDT.csv"
              onDataImported={handleSecondImport}
            />
          </div>

          {(firstImport && secondImport) && (
            <div className="data-display-section">
              {firstImport && (
                <DataTable
                  title={firstImport.fileName}
                  columns={firstImport.data.length > 0 ? Object.keys(firstImport.data[0]) : []}
                  data={firstImport.data}
                />
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
