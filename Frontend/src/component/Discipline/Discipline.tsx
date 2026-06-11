import React from 'react';
import {useNavigate} from 'react-router-dom';

interface Discipline {
    code_sae: string;
    sessionList: any[];
}

export const Discipline = ({ code_sae, sessionList }: Discipline) => {
    const navigate = useNavigate();

    return (
        <div className="discipline">
            <h3 className="discipline-title">{code_sae}</h3>
            <table className="discipline-table">                
                <thead>
                    {sessionList.map((session: any) => (
                        <tr key={session.id}>
                            <th>{session.type_ens + " - " + session.heures}</th>
                            <th>{session.is_valid ? "Valide" : "Non valide"}</th>        
                        </tr>
                    ))}
                    <tr>
                        <th onClick={() => {navigate(`/session/${code_sae}`)}}>Détails</th>
                    </tr>
                </thead>
            </table>
            
        </div>
    )};