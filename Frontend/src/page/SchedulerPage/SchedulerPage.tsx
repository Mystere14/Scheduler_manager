import { useState, useMemo, useRef } from 'react';
import Papa from 'papaparse';
import { ActionButtons } from '../../component/ActionButtons/ActionButtons';
import { FilterSection } from '../../feature/FilterSection/FilterSection';
import { ImportedDataTable } from '../../feature/ImportedDataTable/ImportedDataTable';
import { SolutionTable } from '../../feature/SolutionTable/SolutionTable';
import { AbsenceInterface } from '../../feature/AbcenseInterface/AbcenseInterface';
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
  const [absenceDialogOpen, setAbsenceDialogOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Get column names dynamically from data
  const columnNames = importedData.length > 0
    ? Object.keys(importedData[0])
    : [];

  // Initialize filters dynamically based on columns
  const [filters, setFilters] = useState<Filters>(
    columnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {})
  );

  // Filter imported data based on filter values
  const filteredData = useMemo(() => {
    return importedData.filter((row) => {
      return columnNames.every((col) => {
        const filterValue = filters[col];
        const rowValue = (row as Record<string, any>)[col];

        if (filterValue === '') return true;

        return rowValue
          .toString()
          .toLowerCase()
          .includes(filterValue.toLowerCase());
      });
    });
  }, [importedData, filters, columnNames]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleClearFilters = () => {
    const emptyFilters = columnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {});
    setFilters(emptyFilters);
  };

  const handleGenerateSolution = () => {
    // Copy filtered data to solution table, removing volume column
    setSolutionData(filteredData);
  };

  const handleExport = () => {
    // Export filtered data as CSV using PapaParse
    const dataToExport = solutionData.length > 0 ? solutionData : filteredData;
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

      console.log("SENDING:", data);

      res = await api.createInputCours(data);

      console.log("RESPONSE:", res);
    }
  } catch (error) {
    alert(
      'Erreur lors de l’insertion des données : ' +
      (error as Error).message +
      'Here s the problematic data:\n' + JSON.stringify(rows)
    );

    console.log(      'Erreur lors de l’insertion des données : ' +
      (error as Error).message +
      'Here s the problematic data:\n' + JSON.stringify(rows));
  }

  console.log("Final response:", res);
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
          setFilters(emptyFilters);
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
        <div className="controls">
          <ActionButtons
            isGenerating={false}
            isImporting={false}
            onGenerate={() => { }}
            onExport={handleExport}
            onImport={() => { }}
          />

          <FilterSection
            filters={filters}
            onFilterChange={handleFilterChange}
            onClearFilters={handleClearFilters}
            columns={columnNames}
            formatLabel={formatColumnName}
          />
        </div>
        <SolutionTable data={solutionData} columns={columnNames} />
      </div>
    );
  }

  return (
    <div className="scheduler-page">
      <div className="scheduler-container">
        <header className="page-header">
          <h1>Gestionnaire des emplois du temps</h1>
          {importedData.length === 0 || (
            <button className="absence-button" onClick={() => setAbsenceDialogOpen(true)}>
              Gérer les absences
            </button>)}
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
                onExport={handleExport}
                onImport={handleImport}
              />

              <FilterSection
                filters={filters}
                onFilterChange={handleFilterChange}
                onClearFilters={handleClearFilters}
                columns={columnNames}
                formatLabel={formatColumnName}
              />
            </div>
            <ImportedDataTable data={filteredData} columns={columnNames} key={columnNames.join(',')} />
            {solutionData.length > 0 && handleDisplaySolutionTable()}
          </div>
        )}
      </div>



      <input // Hidden file input for importing data to ensure security access to file 
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        className="hidden-file-input"
      />
      <AbsenceInterface open={absenceDialogOpen} onClose={() => setAbsenceDialogOpen(false)} />
    </div>
  );
};
