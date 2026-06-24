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
                                <tbody>
                    {sessionList.map((session: any) => (
                        <tr key={session.id}>
                            <td>{session.type_ens} - {session.heures}h</td>
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
            <button className="details-button" onClick={() => navigate(`/session/${code_sae}`)}>
                Voir les détails
            </button>
        </div>
    )};