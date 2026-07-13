import React, { useMemo, useState } from 'react';
import {useNavigate} from 'react-router-dom';
import { ValidationContext } from '../../service/Context';


interface Discipline {
    codeSae: string;
    sessionList: any[];
}

interface Session{
    id: number;
    codeEns: string;
    codeResSae: string;
    week: string;
    hour: number;
    isValid: boolean;
    typeEns: string;
    isExtraSession?: boolean;
}

export const Discipline = ({ codeSae, sessionList }: Discipline) => {
    const navigate = useNavigate();
    const context = React.useContext(ValidationContext);


    const handleEachSession = (sessions: Session[]) => 
    {
        const uniqueSessions = sessions.filter
        (
            (item, index, self) =>
                index === self.findIndex
                (
                    s => (s.typeEns.split('_')[0] === item.typeEns.split('_')[0] && Math.abs(s.hour) === Math.abs(item.hour))
                )
        ).map(session => ({ ...session })); 
        
        uniqueSessions.forEach(el => 
            {
                el.isExtraSession = false;
            }
        )

        sessions.forEach(el => {
            uniqueSessions.forEach(el2 => {

                if (el.typeEns.split("_")[0] === el2.typeEns.split("_")[0] &&
                Math.abs(el.hour) === Math.abs(el2.hour)) 
                {
                    if(el.hour > 0 && !el.isValid)
                    {
                        el2.isExtraSession=true;
                    }
                    else
                    {
                        el2.isValid = el2.isValid && el.isValid;
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
            <h3 className="discipline-title">{codeSae}</h3>
            <table className="discipline-table">     
                <tbody>
                    {eachSession.map((session: any) => (
                        <tr key={session.id}>
                            <td>{session.typeEns.split('_')[0]} - {Math.abs(session.hour)}h</td>
                            <td
                                className={
                                    (!session.isValid && session.hour < 0) ? 'invalid' : 'valid'
                                }
                            >
                                {(!session.isValid && session.hour < 0) ? '✗ Non valide' : '✓ Valide'}
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
            <button className="details-button" onClick={() => {navigate(`/session/${codeSae}`)}}>
                Voir les détails
            </button>
        </div>
    )};