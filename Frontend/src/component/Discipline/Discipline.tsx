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
    isExtraSession?: boolean;
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
        
        uniqueSessions.forEach(el => 
            {
                el.isExtraSession = false;
            }
        )

        sessions.forEach(el => {
            uniqueSessions.forEach(el2 => {

                if (el.type_ens.split("_")[0] === el2.type_ens.split("_")[0] &&
                Math.abs(el.heures) === Math.abs(el2.heures)) 
                {
                    if(el.heures > 0 && !el.is_valid)
                    {
                        el2.isExtraSession=true;
                    }
                    else
                    {
                        el2.is_valid = el2.is_valid && el.is_valid;
                    }
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
                                    (!session.is_valid && session.heures < 0) ? 'invalid' : 'valid'
                                }
                            >
                                {(!session.is_valid && session.heures < 0) ? '✗ Non valide' : '✓ Valide'}
                            </td>
                            <td>
                                {(session.isExtraSession) && (
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <line stroke="#faa615" x1="24" y1="24" x2="12" y2="3"></line>
                                        <line stroke="#faa615" x1="1" y1="24" x2="12" y2="3"></line>
                                        <line stroke="#faa615" x1="24" y1="23" x2="1" y2="23"></line>
                                        <line x1="12" y1="8" x2="12" y2="16"></line>
                                        <line x1="12" y1="18" x2="12" y2="20"></line>
                                    </svg>
                                )  
                                }  
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