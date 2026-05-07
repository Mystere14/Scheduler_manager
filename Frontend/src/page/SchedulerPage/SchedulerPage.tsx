import { useState, useMemo, useRef } from 'react';
import Papa from 'papaparse';
import { ActionButtons } from '../../component/ActionButtons/ActionButtons';
import { FilterSection } from '../../feature/FilterSection/FilterSection';
import { ImportedDataTable } from '../../feature/ImportedDataTable/ImportedDataTable';
import { SolutionTable } from '../../feature/SolutionTable/SolutionTable';
import './SchedulerPage.css';

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

  const handleImport = () => {
    // Trigger file input
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
        
        // Validate that data is an array
        if (Array.isArray(data) && data.length > 0) {
          setImportedData(data);
          setSolutionData([]); // Reset solution data
          
          // Extract column names from NEW data and reset filters accordingly
          const newColumnNames = Object.keys(data[0]);
          const emptyFilters = newColumnNames.reduce((acc, col) => ({ ...acc, [col]: '' }), {});
          setFilters(emptyFilters);
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
                onGenerate={() => {}}
                onExport={handleExport}
                onImport={() => {}}
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
        </header>

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
      </div>
      <input // Hidden file input for importing data to ensure security access to file 
        ref={fileInputRef}
        type="file"
        accept=".csv"
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
    </div>
  );
};
