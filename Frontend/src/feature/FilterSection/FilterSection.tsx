import { FilterInput } from '../../component/FilterInput/FilterInput';
import './FilterSection.css';

interface FilterSectionProps {
  filters: {
    codeResSAE: string;
    semaine: string;
    typeEns: string;
    codeEns: string;
    volume: string;
  };
  onFilterChange: (key: string, value: string) => void;
  onClearFilters: () => void;
}

export const FilterSection = ({
  filters,
  onFilterChange,
  onClearFilters,
}: FilterSectionProps) => {
  const filterKeys = [
    { key: 'codeResSAE', label: 'Code Res SAE' },
    { key: 'semaine', label: 'Semaine' },
    { key: 'typeEns', label: 'Type Ens' },
    { key: 'codeEns', label: 'Code Ens' },
    { key: 'volume', label: 'Volume' },
  ];

  return (
    <div className="filter-section">
      <div className="filter-header">
        <h3>Filtres</h3>
        <button className="btn-clear-filters" onClick={onClearFilters}>
          Réinitialiser
        </button>
      </div>
      <div className="filter-grid">
        {filterKeys.map(({ key, label }) => (
          <FilterInput
            key={key}
            label={label}
            value={
              filters[key as keyof typeof filters] || ''
            }
            onChange={(value) => onFilterChange(key, value)}
          />
        ))}
      </div>
    </div>
  );
};
