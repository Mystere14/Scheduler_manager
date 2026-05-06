import { DataTable } from '../../component/DataTable/DataTable';
import './ImportedDataTable.css';

interface ImportedDataTableProps {
  data: Record<string, any>[];
}

const COLUMNS = [
  'codeResSAE',
  'semaine',
  'typeEns',
  'codeEns',
  'volume',
  'jour',
  'heure',
];

export const ImportedDataTable = ({ data }: ImportedDataTableProps) => {
  // Format columns for display
  const displayColumns = [
    'Code Res SAE',
    'Semaine',
    'Type Ens',
    'Code Ens',
    'Volume',
    'Jour',
    'Heure',
  ];

  // Map data from model keys to display keys
  const formattedData = data.map((row) => ({
    'Code Res SAE': row.codeResSAE,
    'Semaine': row.semaine,
    'Type Ens': row.typeEns,
    'Code Ens': row.codeEns,
    'Volume': row.volume,
    'Jour': row.jour,
    'Heure': row.heure,
  }));

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
