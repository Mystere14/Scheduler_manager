import './SchedulerLine.css';
interface SchedulerLine {
    scheduler: any;
    isExtraScheduler: boolean;
}

export const SchedulerLine = ({ scheduler, isExtraScheduler }: SchedulerLine) => {
    
    return (
        <div className="scheduler-line">
            <p>{scheduler.type_ens}</p>
            <p>{scheduler.code_ens}</p>
            {!isExtraScheduler && (
                <p className={scheduler.is_valid ? "status-valid" : "status-invalid"}>
                    {scheduler.is_valid ? "✓ Valide" : "✗ Non valide"}
                </p>
            )}
        </div>
    );
};