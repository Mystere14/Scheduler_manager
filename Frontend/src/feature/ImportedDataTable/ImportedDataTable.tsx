import { DataTable } from '../../component/DataTable/DataTable';
import './ImportedDataTable.css';

interface ImportedDataTableProps {
  data: Record<string, any>[];
  columns?: string[];
}

// Format camelCase to readable text (e.g., codeResSAE -> Code Res SAE)
const formatColumnName = (name: string): string => {
  return name
    .replace(/([a-z])([A-Z])/g, '$1 $2') // Add space between lowercase and uppercase
    .replace(/^./, (str) => str.toUpperCase()) // Capitalize first letter
    .trim();
};

export const ImportedDataTable = ({ data, columns }: ImportedDataTableProps) => {
  // Use provided columns or extract from data
  const dataColumns = columns && columns.length > 0 
    ? columns 
    : (data.length > 0 ? Object.keys(data[0]) : []);

  // Format columns for display
  const displayColumns = dataColumns.map(col => formatColumnName(col));

  // Map data dynamically based on available columns
  const formattedData = data.map((row) => {
    const formattedRow: Record<string, any> = {};
    dataColumns.forEach(col => {
      formattedRow[formatColumnName(col)] = row[col];
    });
    return formattedRow;
  });

  return (
    <div className="imported-data-table">
      <DataTable
        columns={displayColumns}
        data={formattedData}
        title="Données importées"
      />
    </div>
  );
};
