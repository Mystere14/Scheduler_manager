import React, { useContext, useRef, useState } from 'react';
import { DataTable } from '../DataTable/DataTable';
import './ImportArea.css';
import api from '../../service/Api';
import { ValidationContext } from '../../service/Context';

interface ImportAreaProps {
  title: string;
  onDataImported: (data: any[], fileName: string) => void;
  onDataCleared?: () => void;
  isSchedulerPlanned?: boolean;
}

interface ImportedFile {
  data: any[];
  fileName: string;
}

export const ImportArea: React.FC<ImportAreaProps> = ({ title, onDataImported, onDataCleared, isSchedulerPlanned }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const context = useContext(ValidationContext);
  const importedFile = isSchedulerPlanned ? context.firstImport : context.secondImport;
  const [showModal, setShowModal] = useState(false);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const data = await api.createAnalyticsTimeslotByPreprocessedSchedulerPlanned(file);
      if (isSchedulerPlanned) {
        context.setFirstImport({ data: data.data, fileName: file.name });
      } else {
        context.setSecondImport({ data: data.data, fileName: file.name });
      }
      onDataImported(data.data, file.name);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du fichier vCalendar:', error);
      alert('Erreur lors de l\'envoi du fichier vCalendar');
    }
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleSendVcalendarToAPI = async () => {
    fileInputRef.current?.click();
  }

  const handleVcalendarFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const data = await api.createAnalyticsTimeslotFromVcalendar(file);
      if (isSchedulerPlanned) {
        context.setFirstImport({ data: data.data, fileName: file.name });
      } else {
        context.setSecondImport({ data: data.data, fileName: file.name });
      }
      onDataImported(data.data, file.name);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du fichier vCalendar:', error);
      alert('Erreur lors de l\'envoi du fichier vCalendar');
    }
  }

  const handleResetFile = () => {
    onDataImported([], '');
    if (isSchedulerPlanned) {
      context.setFirstImport(null);
    } else {
      context.setSecondImport(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (onDataCleared) {
      onDataCleared();
    }
  };

  const handleViewData = () => {
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  const handleExportFile = () => {
    if (!importedFile) return;

    // Convertir les données en CSV
    const headers = importedFile.data.length > 0 ? Object.keys(importedFile.data[0]) : [];
    const csvContent = [
      headers.join(','),
      ...importedFile.data.map(row => 
        headers.map(header => {
          const value = row[header];
          // Échapper les valeurs contenant des virgules ou des guillemets
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');

    // Créer un blob et télécharger
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `${importedFile.fileName.slice(0, -4)}_export.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <div className="import-area">
        <h2 className="import-area-title">{title}</h2>

        {!importedFile ? (
          <>
          <div className="imported-file-container">
            <div className="imported-file-info empty">
              <div className="file-details">
                <p className="file-name">Aucun fichier importé</p>
              </div>
            </div>

            <div className="file-actions">
              <button className="action-button import-button" onClick={isSchedulerPlanned ? handleImportClick : handleSendVcalendarToAPI }>
                Importer un fichier 
              </button>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={isSchedulerPlanned ?  handleFileSelect : handleVcalendarFileSelect}
              accept={isSchedulerPlanned ? ".csv" : ".vcs"}
              className="hidden-file-input"
            />
          </div>
          </>
        ) : (
            <div className="imported-file-container">
              <div className="imported-file-info">
                <div className="file-icon">✓</div>
                <div className="file-details">
                  <p className="file-name">{`${importedFile.fileName.slice(0, -4)}`}</p>
                </div>
              </div>

              <div className="file-actions">
                <button className="action-button view-button" onClick={handleViewData}>
                  Consulter
                </button>
                <button className="action-button export-button" onClick={handleExportFile} title="Exporter">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                  </svg>
                </button>
                <button className="action-button import-other-button" onClick={handleResetFile} title="Supprimer">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                  </svg>
                </button>
              </div>
            </div>
        )}
      </div>
      
      {showModal && importedFile && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={handleCloseModal}>×</button>
            <div className="modal-body">
              <DataTable
                title={`${importedFile.fileName.slice(0, -4)}`}
                columns={importedFile.data.length > 0 ? Object.keys(importedFile.data[0]) : []}
                data={importedFile.data}
              />
            </div>
          </div>
        </div>
      )}
    </>
  );
};

