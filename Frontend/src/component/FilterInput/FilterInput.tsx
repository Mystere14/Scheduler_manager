import React from 'react';
import './FilterInput.css';

interface FilterInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export const FilterInput = ({
  label,
  value,
  onChange,
  placeholder,
}: FilterInputProps) => {
  return (
    <div className="filter-input-group">
      <label htmlFor={label}>{label}</label>
      <input
        type="text"
        id={label}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || `Filtrer par ${label}`}
        className="filter-input"
      />
    </div>
  );
};
