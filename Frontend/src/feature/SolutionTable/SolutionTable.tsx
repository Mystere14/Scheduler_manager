import { DataTable } from '../../component/DataTable/DataTable';
import './SolutionTable.css';

interface SolutionTableProps {
  data: Record<string, any>[];
}

const displayColumns = [
  'Code Res SAE',
  'Semaine',
  'Type Ens',
  'Code Ens',
  'Volume',
  'Jour',
  'Heure',
];

export const SolutionTable = ({ data }: SolutionTableProps) => {
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
    <div className="solution-table">
      <DataTable
        columns={displayColumns}
        data={formattedData}
        title="Solution trouvée"
      />
    </div>
  );
};
