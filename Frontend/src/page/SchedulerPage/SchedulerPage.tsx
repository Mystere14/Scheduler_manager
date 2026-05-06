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
  codeResSAE: string;
  semaine: string;
  typeEns: string;
  codeEns: string;
  volume: string;
}

export const SchedulerPage = () => {
  const [importedData, setImportedData] = useState(MOCK_DATA);
  const [solutionData, setSolutionData] = useState<typeof MOCK_DATA>([]);
  const [filters, setFilters] = useState<Filters>({
    codeResSAE: '',
    semaine: '',
    typeEns: '',
    codeEns: '',
    volume: '',
  });

  // Filter imported data based on filter values
  const filteredData = useMemo(() => {
    return importedData.filter((row) => {
      return (
        (filters.codeResSAE === '' ||
          row.codeResSAE
            .toLowerCase()
            .includes(filters.codeResSAE.toLowerCase())) &&
        (filters.semaine === '' ||
          row.semaine
            .toLowerCase()
            .includes(filters.semaine.toLowerCase())) &&
        (filters.typeEns === '' ||
          row.typeEns
            .toLowerCase()
            .includes(filters.typeEns.toLowerCase())) &&
        (filters.codeEns === '' ||
          row.codeEns
            .toLowerCase()
            .includes(filters.codeEns.toLowerCase())) &&
        (filters.volume === '' ||
          row.volume.toString().includes(filters.volume.toLowerCase()))
      );
    });
  }, [importedData, filters]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleClearFilters = () => {
    setFilters({
      codeResSAE: '',
      semaine: '',
      typeEns: '',
      codeEns: '',
      volume: '',
    });
  };

  const handleGenerateSolution = () => {
    // Copy filtered data to solution table
    setSolutionData(filteredData);
  };

  return (
    <div className="scheduler-page">
      <div className="scheduler-container">
        <header className="page-header">
          <h1>Gestionnaire des emplois du temps</h1>
        </header>

        <div className="main-content">
          <div className="controls">
            <ActionButtons
              onGenerate={handleGenerateSolution}
              onVoid={handleClearFilters}
            />

            <FilterSection
              filters={filters}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
        </div>

          <ImportedDataTable data={filteredData} />
          {solutionData.length > 0 && <SolutionTable data={solutionData} />}
        </div>
      </div>
    </div>
  );
};
