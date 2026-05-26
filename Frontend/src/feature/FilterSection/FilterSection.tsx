import { FilterInput } from '../../component/FilterInput/FilterInput';
import './FilterSection.css';

interface FilterSectionProps {
  filters: Record<string, string>;
  onFilterChange: (key: string, value: string) => void;
  onClearFilters: () => void;
  columns?: string[];
  formatLabel?: (label: string) => string;
}

export const FilterSection = ({
  filters,
  onFilterChange,
  onClearFilters,
  columns = [],
  formatLabel = (label) => label,
}: FilterSectionProps) => {
  const filterKeys = columns.map((col) => ({
    key: col,
    label: formatLabel(col),
  }));

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
            value={filters[key] || ''}
            onChange={(value) => onFilterChange(key, value)}
          />
        ))}
      </div>
    </div>
  );
};
