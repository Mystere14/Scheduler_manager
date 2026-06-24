import './SchedulerLine.css';
interface SchedulerLine {
    scheduler: any;
}

export const SchedulerLine = ({ scheduler }: SchedulerLine) => {
    
    return (
        <div className="scheduler-line">
            <p>{scheduler[0].type_ens}</p>
            <p>{scheduler[0].code_ens}</p>
            <p className={scheduler[0].is_valid ? "status-valid" : "status-invalid"}>
                {scheduler[0].is_valid ? "✓ Valide" : "✗ Non valide"}
            </p>
        </div>
    );
};