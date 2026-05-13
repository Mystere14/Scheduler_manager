import React, { useRef, useState } from 'react';
import Papa from 'papaparse';
import './ImportArea.css';

interface ImportAreaProps {
  title: string;
  onDataImported: (data: any[], fileName: string) => void;
}

interface ImportedFile {
  data: any[];
  fileName: string;
}

export const ImportArea: React.FC<ImportAreaProps> = ({ title, onDataImported }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [importedFile, setImportedFile] = useState<ImportedFile | null>(null);

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
    setImportedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
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
              <button className="action-button view-button" onClick={() => console.log(importedFile.data)}>
                Consulter
              </button>
              <button className="action-button import-other-button" onClick={handleResetFile}>
              Importer un fichier
              </button>
            </div>
          </div>
      )}
    </div>
  );
};
