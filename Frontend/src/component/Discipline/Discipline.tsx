
interface Discipline {
    code_sae: string;
    sessionList: any[];
}

export const Discipline = ({ code_sae, sessionList }: Discipline) => {
    return (
        <div className="discipline">
            <h3 className="discipline-title">{code_sae}</h3>
            <table className="discipline-table">                
                <thead>
                    {sessionList.map((session: any) => (
                        <tr key={session.id}>
                            <th>{session.type_ens + " - " + session.heures}</th>
                            <th>temp</th>        
                        </tr>
                    ))}
                    <tr>
                        <th>Détails</th>
                    </tr>
                </thead>
            </table>
            
        </div>
    )};