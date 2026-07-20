import './SchedulerLine.css';
interface SchedulerLine {
    scheduler: any;
    isExtraScheduler: boolean;
}

export const SchedulerLine = ({ scheduler, isExtraScheduler }: SchedulerLine) => {
    
    return (
        <div className="scheduler-line">
            <p>{scheduler.typeEns}</p>
            <p>{scheduler.codeEns}</p>
            {!isExtraScheduler && (
                <p className={scheduler.isValid ? "status-valid" : "status-invalid"}>
                    {scheduler.isValid ? "✓ Valide" : "✗ Non valide"}
                </p>
            )}
        </div>
    );
};