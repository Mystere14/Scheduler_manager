import { useState, useMemo } from 'react';
import { ActionButtons } from '../../component/ActionButtons/ActionButtons';
import { FilterSection } from '../../feature/FilterSection/FilterSection';
import { ImportedDataTable } from '../../feature/ImportedDataTable/ImportedDataTable';
import { SolutionTable } from '../../feature/SolutionTable/SolutionTable';
import './SchedulerPage.css';

// Mock data for initial display
const MOCK_DATA = [
  {
    codeResSAE: 'SAE001',
    semaine: 'W01',
    typeEns: 'C',
    codeEns: 'ENS01',
    volume: 2,
    jour: 'Lundi',
    heure: 9,
  },
  {
    codeResSAE: 'SAE001',
    semaine: 'W01',
    typeEns: 'TD',
    codeEns: 'ENS02',
    volume: 1,
    jour: 'Mardi',
    heure: 10,
  },
  {
    codeResSAE: 'SAE002',
    semaine: 'W02',
    typeEns: 'TP',
    codeEns: 'ENS03',
    volume: 3,
    jour: 'Mercredi',
    heure: 14,
  },
  {
    codeResSAE: 'SAE003',
    semaine: 'W01',
    typeEns: 'C',
    codeEns: 'ENS01',
    volume: 2,
    jour: 'Jeudi',
    heure: 11,
  },
  {
    codeResSAE: 'SAE002',
    semaine: 'W02',
    typeEns: 'C',
    codeEns: 'ENS02',
    volume: 2,
    jour: 'Vendredi',
    heure: 9,
  },
    {
    codeResSAE: 'SAE002',
    semaine: 'W02',
    typeEns: 'C',
    codeEns: 'ENS02',
    volume: 2,
    jour: 'Vendredi',
    heure: 9,
  },
    {
    codeResSAE: 'SAE002',
    semaine: 'W02',
    typeEns: 'C',
    codeEns: 'ENS02',
    volume: 2,
    jour: 'Vendredi',
    heure: 9,
  },
    {
    codeResSAE: 'SAE002',
    semaine: 'W02',
    typeEns: 'C',
    codeEns: 'ENS02',
    volume: 2,
    jour: 'Vendredi',
    heure: 9,
  },
    {
    codeResSAE: 'SAE002',
    semaine: 'W02',
    typeEns: 'C',
    codeEns: 'ENS02',
    volume: 2,
    jour: 'Vendredi',
    heure: 9,
  }
];

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
  const [importedData, setImportedData] = useState(MOCK_DATA);
  const [solutionData, setSolutionData] = useState<typeof MOCK_DATA>([]);
  
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

  const handleDisplaySolutionTable = () => {
        return (
        <div className="main-content">
            <div className="controls">
                <ActionButtons
                isGenerating={false}
                onGenerate={handleGenerateSolution}
                onVoid={handleClearFilters}
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
              onGenerate={handleGenerateSolution}
              onVoid={handleClearFilters}
            />

            <FilterSection
              filters={filters}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
              columns={columnNames}
              formatLabel={formatColumnName}
            />
        </div>

          <ImportedDataTable data={filteredData} />
          {solutionData.length > 0 && handleDisplaySolutionTable()}
        </div>
      </div>
    </div>
  );
};
