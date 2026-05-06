import { useState } from 'react';
import './DataTable.css';

interface DataTableProps {
  columns: string[];
  data: Record<string, number>[];
  title: string;
}

export const DataTable = ({ columns, data, title }: DataTableProps) => {
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  } | null>(null);

  const handleSort = (key: string) => {
    setSortConfig((prev) => {
      if (prev?.key === key) {
        return prev.direction === 'asc'
          ? { key, direction: 'desc' }
          : null;
      }
      return { key, direction: 'asc' };
    });
  };

  const sortedData = [...data].sort((a, b) => {
    if (!sortConfig) return 0;

    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];

    if (aValue < bValue) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  return (
    <div className="data-table-container">
      <h2>{title}</h2>
      <div className="table-wrapper">
        {sortedData.length > 0 ? (
          <table className="excel-table">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th
                    key={col}
                    onClick={() => handleSort(col)}
                    className={`sortable ${
                      sortConfig?.key === col ? `sorted-${sortConfig.direction}` : ''
                    }`}
                  >
                    <div className="header-content">
                      <span>{col}</span>
                      {sortConfig?.key === col && (
                        <span className="sort-indicator">
                          {sortConfig.direction === 'asc' ? '▲' : '▼'}
                        </span>
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedData.map((row, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'even' : 'odd'}>
                  {columns.map((col) => (
                    <td key={`${idx}-${col}`}>
                      <div className="cell-content">{row[col] || '-'}</div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <p>Aucune donnée disponible</p>
          </div>
        )}
      </div>
    </div>
  );
};
