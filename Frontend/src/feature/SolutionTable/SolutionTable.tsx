import { DataTable } from '../../component/DataTable/DataTable';
import './SolutionTable.css';

interface SolutionTableProps {
  data: Record<string, any>[];
  columns?: string[];
}

export const SolutionTable = ({ data, columns }: SolutionTableProps) => {
  // Use provided columns or extract from data
  const displayColumns = columns && columns.length > 0 
    ? columns 
    : (data.length > 0 ? Object.keys(data[0]) : []);

  return (
    <div className="solution-table">
      <DataTable
        columns={displayColumns}
        data={data}
        title="Solution trouvée"
      />
    </div>
  );
};
