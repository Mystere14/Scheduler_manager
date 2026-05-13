import React, { useRef, useState } from 'react';
import Papa from 'papaparse';
import { DataTable } from '../DataTable/DataTable';
import './ImportArea.css';

interface ImportAreaProps {
  title: string;
  onDataImported: (data: any[], fileName: string) => void;
  onDataCleared?: () => void;
}

interface ImportedFile {
  data: any[];
  fileName: string;
}

export const ImportArea: React.FC<ImportAreaProps> = ({ title, onDataImported, onDataCleared }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importedFile, setImportedFile] = useState<ImportedFile | null>(null);
  const [showModal, setShowModal] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const fileName = file.name;
        setImportedFile({
          data: results.data as any[],
          fileName
        });
        onDataImported(results.data as any[], fileName);
      },
      error: (error) => {
        console.error('Erreur lors de la lecture du fichier CSV:', error);
        alert('Erreur lors de la lecture du fichier CSV');
      }
    });
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleResetFile = () => {
    onDataImported([], '');
    setImportedFile(null);
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

  return (
    <>
      <div className="import-area">
        <h2 className="import-area-title">{title}</h2>

        {!importedFile ? (
          <div className="imported-file-container">
            <div className="imported-file-info">
              <div className="file-details">
                <p className="file-name">Aucun fichier importé</p>
              </div>
            </div>

            <div className="file-actions">
              <button className="action-button import-button" onClick={handleImportClick}>
                Importer un fichier
              </button>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".csv"
              className="hidden-file-input"
            />
          </div>
        ) : (
            <div className="imported-file-container">
              <div className="imported-file-info">
                <div className="file-icon">✓</div>
                <div className="file-details">
                  <p className="file-name">{importedFile.fileName}</p>
                </div>
              </div>

              <div className="file-actions">
                <button className="action-button view-button" onClick={handleViewData}>
                  Consulter
                </button>
                <button className="action-button import-other-button" onClick={handleResetFile}>
                Supprimer le fichier
                </button>
              </div>
            </div>
        )}
      </div>

      {showModal && importedFile && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-body">
              <DataTable
                title={importedFile.fileName}
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
