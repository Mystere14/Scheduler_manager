import { SchedulerLine } from '../../component/SchedulerLine/SchedulerLine';

interface SchedulerGroup {
    schedulerGroup: any[];
    isExtraScheduler: boolean;
}

export const SchedulerGroup = ({ schedulerGroup, isExtraScheduler }: SchedulerGroup & { isExtraScheduler: boolean }) => {

    return (
        <div className="SchedulerList">
            {schedulerGroup.map((group: any) => (
                <SchedulerLine key={group.key} scheduler={group} isExtraScheduler={isExtraScheduler} />
            ))}
        </div>
    );
};