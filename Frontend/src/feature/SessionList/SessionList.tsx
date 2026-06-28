import { useContext } from 'react';
import { Discipline } from '../../component/Discipline/Discipline';
import { ValidationContext } from '../../services/context';

interface SessionList {
}

export const SessionList = ({}: SessionList) => {
    const context = useContext(ValidationContext);
    
    return (
        <div className="comparison-results">
            {context.comparisonResultUnique.map((result: any) => (
                    <Discipline key={result} code_sae={result} sessionList={context.comparisonResult.filter((r: any) => r.code_res_sae === result)} />
                ))
            }
        </div>
    )};