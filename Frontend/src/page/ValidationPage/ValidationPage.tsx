import React, { useState, useEffect, useContext  } from 'react';
import { ImportArea } from '../../component/ImportArea/ImportArea';
import './ValidationPage.css';
import { SessionList } from '../../feature/SessionList/SessionList';
import { ValidationContext, type Session } from '../../service/Context';


interface ValidationPage{
}

interface ImportedData {
  data: any[];
  fileName: string;
}

export const ValidationPage = ({}: ValidationPage) => {
  const context = useContext(ValidationContext);  

  const handleFirstImport = (data: any[], fileName: string) => {
    context.setFirstImport({ data, fileName });
  };

  const handleSecondImport = (data: any[], fileName: string) => {
    context.setSecondImport({ data, fileName });
  };
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
              onDataCleared={() => context.setFirstImport(null)}
              isSchedulerPlanned={true}
            />
            <ImportArea
              title="Créneaux placés (vcs)"
              onDataImported={handleSecondImport}
              onDataCleared={() => context.setSecondImport(null)}
              isSchedulerPlanned={false}
            />
          </div>
        
          {(context.firstImport && context.secondImport) && (
            <div className="data-tables">
              {context.loading && (
                <div className="empty-state">
                  <div className="empty-state-icon">⏳</div>
                  <div className="empty-state-text">Chargement de la comparaison...</div>
                </div>
              )}
              {context.error && (
                <div className="empty-state" style={{ borderColor: '#fca5a5', background: '#fef2f2' }}>
                  <div className="empty-state-icon">❌</div>
                  <div className="empty-state-text" style={{ color: '#dc2626' }}>Erreur: {context.error}</div>
                </div>
              )}
              {context.comparisonResult && !context.loading && !context.error && (
                <div>
                  <h2>Contrôle semaine {context.firstImport.data[0].week.split('-')[1]} - semestre {context.firstImport.data[0].codeResSae.split('-')[0]} </h2>
                  
                  <SessionList />
                </div>
              )
              }
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
