import React, { useMemo, useState } from 'react';
import {useNavigate} from 'react-router-dom';
import { ValidationContext } from '../../services/context';


interface Discipline {
    code_sae: string;
    sessionList: any[];
}

interface Session{
    id: number;
    code_ens: string;
    code_res_sae: string;
    semaine: string;
    heures: number;
    is_valid: boolean;
    type_ens: string;
}

export const Discipline = ({ code_sae, sessionList }: Discipline) => {
    const navigate = useNavigate();
    const context = React.useContext(ValidationContext);


    const handleEachSession = (sessions: Session[]) => 
    {
        const uniqueSessions = sessions.filter
        (
            (item, index, self) =>
                index === self.findIndex
                (
                    s => (s.type_ens.split('_')[0] === item.type_ens.split('_')[0] && Math.abs(s.heures) === Math.abs(item.heures))
                )
        ).map(session => ({ ...session })); 
        
        sessions.forEach(el => {
            uniqueSessions.forEach(el2 => {
                if (
                    el.type_ens.split("_")[0] === el2.type_ens.split("_")[0] &&
                    Math.abs(el.heures) === Math.abs(el2.heures)
                ) {
                    el2.is_valid = el2.is_valid && el.is_valid;
                }
            });
        })
        return uniqueSessions;
    }

    const eachSession = useMemo(
        () => handleEachSession(sessionList),
    [sessionList]
);
    return (
        <div className="discipline">
            <h3 className="discipline-title">{code_sae}</h3>
            <table className="discipline-table">     
                <tbody>
                    {eachSession.map((session: any) => (
                        <tr key={session.id}>
                            <td>{session.type_ens.split('_')[0]} - {Math.abs(session.heures)}h</td>
                            <td
                                className={
                                    session.is_valid ? 'valid' : 'invalid'
                                }
                            >
                                {session.is_valid ? '✓ Valide' : '✗ Non valide'}
                            </td>
                        </tr>
                    ))}
                </tbody>   
            </table>
            <button className="details-button" onClick={() => {navigate(`/session/${code_sae}`)}}>
                Voir les détails
            </button>
        </div>
    )};