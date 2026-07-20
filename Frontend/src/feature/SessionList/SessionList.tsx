import { useContext } from 'react';
import { Discipline } from '../../component/Discipline/Discipline';
import { ValidationContext } from '../../service/Context';

interface SessionList {
}

export const SessionList = ({}: SessionList) => {
    const context = useContext(ValidationContext);
    
    return (
        <div className="comparison-results">
            {context.comparisonResultUnique.map((result: any) => (
                    <Discipline key={result} codeSae={result} sessionList={context.comparisonResult.filter((r: any) => r.codeResSae === result)} />
                ))
            }
        </div>
    )};