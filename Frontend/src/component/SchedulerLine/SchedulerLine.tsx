interface SchedulerLine {
    scheduler: any;
}

export const SchedulerLine = ({ scheduler }: SchedulerLine) => {
    
    console.log(`Scheduler in SchedulerLine:`, scheduler);
    return (
        <div className="scheduler-line">
            <p >{scheduler[0].type_ens}</p>
            <p>{scheduler[0].code_ens}</p>
            <p>{scheduler[0].is_valid ? "Valide" : "Non valide"}</p>
        </div>
    );
};