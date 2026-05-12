import { useState, useMemo, useRef } from 'react';
import Papa from 'papaparse';
import { ActionButtons } from '../../component/ActionButtons/ActionButtons';
import { FilterSection } from '../../feature/FilterSection/FilterSection';
import { ImportedDataTable } from '../../feature/ImportedDataTable/ImportedDataTable';
import { SolutionTable } from '../../feature/SolutionTable/SolutionTable';
import { AbsenceInterface } from '../../feature/AbsenceHandler/AbsenceHandler.tsx';
import { AbsenceVisualisation } from '../../feature/AbsenceVisualisation/AbsenceVisualisation.tsx';
import './SchedulerPage.css';
import api from '../../services/api';

interface Filters {
  [key: string]: string;
}

// Format camelCase to readable text (e.g., codeResSAE -> Code Res SAE)
const formatColumnName = (name: string): string => {
  return name
    .replace(/([a-z])([A-Z])/g, '$1 $2') // Add space between lowercase and uppercase
    .replace(/^./, (str) => str.toUpperCase()) // Capitalize first letter
    .trim();
};

export const SchedulerPage = () => {
  const [importedData, setImportedData] = useState<any[]>([]);
  const [solutionData, setSolutionData] = useState<any[]>([]);
  const [absenceHandlerDialogOpen, setAbsenceHandlerDialogOpen] = useState(false);
  const [absenceVisualisationDialogOpen, setAbsenceVisualisationDialogOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const columnNames = importedData.length > 0
    ? Object.keys(importedData[0])
    : [];

  const [filtersImportedData, setFiltersImportedData] = useState<Filters>(
    columnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {})
  );

  const [filtersSolutionData, setFiltersSolutionData] = useState<Filters>(
    columnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {})
  );

  const filteredImportedData = useMemo(() => {
    return importedData.filter((row) => {
      return columnNames.every((col) => {
        const filterValue = filtersImportedData[col] ?? '';
        const rowValue = (row as Record<string, any>)[col];

        if (filterValue === '') return true;

        return rowValue
          .toString()
          .toLowerCase()
          .includes(filterValue.toLowerCase());
      });
    });
  }, [importedData, filtersImportedData, columnNames]);

  const filteredSolutionData = useMemo(() => {
    return solutionData.filter((row) => {
      return columnNames.every((col) => {
        const filterValue = filtersSolutionData[col] ?? '';
        const rowValue = (row as Record<string, any>)[col];

        if (filterValue === '') return true;

        return rowValue
          .toString()
          .toLowerCase()
          .includes(filterValue.toLowerCase());
      });
    });
  }, [solutionData, filtersSolutionData, columnNames]);

  const handleFilterChangeImportedData = (key: string, value: string) => {
    setFiltersImportedData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleFilterChangeSolutionData = (key: string, value: string) => {
    setFiltersSolutionData((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleClearFiltersImported = () => {
    const emptyFilters = columnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {});
    setFiltersImportedData(emptyFilters);
  };

  const handleClearFiltersSolution = () => {
    const emptyFilters = columnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {});
    setFiltersSolutionData(emptyFilters);
  };

  const handleGenerateSolution = () => {
    setSolutionData(importedData);
  };

  const handleExportImportedData  = () => {
    const dataToExport =filteredImportedData;
    const csvString = Papa.unparse(dataToExport);
    const blob = new Blob([csvString], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `scheduler_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportSolutionData = () => {
    const dataToExport = filteredSolutionData;
    const csvString = Papa.unparse(dataToExport);
    const blob = new Blob([csvString], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `scheduler_export_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleSetDatabase = async (rows: any[]) => {
  let res;
  api.deleteInputCours();
  try {
    for (const row of rows) {
      const data = {
        code_res_sae: row.code_res_sae as string,
        semaine: row.semaine as string,
        type_ens: row.type_ens as string,
        code_ens: row.code_ens as string,
        volume: Number(row.volume),
      };

      res = await api.createInputCours(data);
    }
  } catch (error) {
    alert(
      'Erreur lors de l’insertion des données : ' +
      (error as Error).message +
      'Here s the problematic data:\n' + JSON.stringify(rows)
    );
  }
};

  const handleImport = () => {
    fileInputRef.current?.click();

  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const results = Papa.parse(content, { header: true, skipEmptyLines: true });
        const data = results.data as any[];


        if (Array.isArray(data) && data.length > 0) {
          setImportedData(data);
          setSolutionData([]);
          

          const newColumnNames = Object.keys(data[0]);
          const emptyFilters = newColumnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {});
          setFiltersImportedData(emptyFilters);
          setFiltersSolutionData(emptyFilters);
          handleSetDatabase(data);  
        } else {
          alert('Le fichier doit contenir des données CSV valides');
        }
      } catch (error) {
        alert('Erreur lors de la lecture du fichier: ' + (error as Error).message);
      }
    };
    reader.readAsText(file);

    // Reset input so same file can be selected again
    event.target.value = '';
  };

  const handleDisplaySolutionTable = () => {
    return (
      <div className="main-content">
        <div className="controls" id="solution-controls">
          <ActionButtons
            isGenerating={false}
            isImporting={false}
            onGenerate={() => { }}
            onExport={handleExportSolutionData}
            onImport={() => { }}
          />

          <FilterSection
            filters={filtersSolutionData}
            onFilterChange={handleFilterChangeSolutionData}
            onClearFilters={handleClearFiltersSolution}
            columns={columnNames}
            formatLabel={formatColumnName}
          />
        </div>
        <SolutionTable data={filteredSolutionData} columns={columnNames} />
      </div>
    );
  }

  return (
    <div className="scheduler-page">
      <div className="scheduler-container">
        <header className="page-header">
          <h1>Gestionnaire des emplois du temps</h1>
          {importedData.length === 0 || (
            <div className="absence-controls">
              <button className="absence-button" onClick={() => setAbsenceHandlerDialogOpen(true)}>
                Gérer les absences
              </button>
              <button className="absence-button" onClick={() => setAbsenceVisualisationDialogOpen(true)}>
                Visualiser les absences
              </button>
            </div>)}
        </header>

        {importedData.length === 0 ? (
          <div className="empty-state">
            <div className="csv-instructions">
              <p>Veuillez importer un fichier CSV avec ces colonnes</p>
              code_res_sae<br />
              semaine<br />
              type_ens<br />
              code_ens<br />
              volume<br />
            </div>
            <button className="import-button-large" onClick={handleImport}>
              Importer les données
            </button>
          </div>
        ) : (
          <div className="main-content">
            <div className="controls">
              <ActionButtons
                isGenerating={true}
                isImporting={true}
                onGenerate={handleGenerateSolution}
                onExport={handleExportImportedData}
                onImport={handleImport}
                href="#solution-controls"
              />

              <FilterSection
                filters={filtersImportedData}
                onFilterChange={handleFilterChangeImportedData}
                onClearFilters={handleClearFiltersImported}
                columns={columnNames}
                formatLabel={formatColumnName}
              />
            </div>
            <ImportedDataTable data={filteredImportedData} columns={columnNames} key={columnNames.join(',')} />
            {solutionData.length > 0 && handleDisplaySolutionTable()}
          </div>
        )}
      </div>



      <input 
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        className="hidden-file-input"
      />
      <AbsenceInterface open={absenceHandlerDialogOpen} onClose={() => setAbsenceHandlerDialogOpen(false)} />
      <AbsenceVisualisation open={absenceVisualisationDialogOpen} onClose={() => setAbsenceVisualisationDialogOpen(false)} />
    </div>
  );
};
