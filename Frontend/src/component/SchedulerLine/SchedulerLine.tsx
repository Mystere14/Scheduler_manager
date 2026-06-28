import './SchedulerLine.css';
interface SchedulerLine {
    scheduler: any;
}

export const SchedulerLine = ({ scheduler }: SchedulerLine) => {
    
    return (
        <div className="scheduler-line">
            <p>{scheduler.type_ens}</p>
            <p>{scheduler.code_ens}</p>
            <p className={scheduler.is_valid ? "status-valid" : "status-invalid"}>
                {scheduler.is_valid ? "✓ Valide" : "✗ Non valide"}
            </p>
        </div>
    );
};