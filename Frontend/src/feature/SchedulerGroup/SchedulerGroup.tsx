import { SchedulerLine } from '../../component/SchedulerLine/SchedulerLine';

interface SchedulerGroup {
    schedulerGroup: any[];
}

export const SchedulerGroup = ({ schedulerGroup}: SchedulerGroup) => {

    return (
        <div className="SchedulerList">
            {schedulerGroup.map((group: any) => (
                <SchedulerLine key={group.key} scheduler={group} />
            ))}
        </div>
    );
};