import { Discipline } from '../../component/Discipline/Discipline';

interface SessionList {
    comparisonResultUnique: string[];
    comparisonResult: any[];
}

export const SessionList = ({ comparisonResultUnique, comparisonResult }: SessionList) => {
    return (
        <div className="comparison-results">
            {comparisonResultUnique.map((result: any) => (
                    <Discipline key={result} code_sae={result} sessionList={comparisonResult.filter((r: any) => r.code_res_sae === result)} />
                ))
            }
        </div>
    )};