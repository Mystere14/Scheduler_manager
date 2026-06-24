import { SchedulerLine } from '../../component/SchedulerLine/SchedulerLine';
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './SchedulerList.css';


interface SchedulerList {
    schedulerList: any[];
}

export const SchedulerList = ({ schedulerList }: SchedulerList) => {
    const location = useLocation();
    const filteredSchedulers = schedulerList.filter((s: any) =>
        s.code_res_sae === location.pathname.split('/')[2]
    );
    console.log(`Location path:`, location.pathname.split('/')[2]);
    console.log(`Filtered :`, filteredSchedulers);

    const grouped = Object.values(
    filteredSchedulers.reduce((acc: any, item: any) => {
        const key = `${item.type_ens}-${item.heures}h`;

        if (!acc[key]) {
        acc[key] = {
            key,
            sessions: []
        };
        }

        acc[key].sessions.push(item);

        return acc;
    }, {})
    );

    return (
    <div className="SchedulerList">
        <p className="SchedulerList-title">{location.pathname.split('/')[2]}</p>
        {grouped.map((group: any) => (
        <div key={group.key}>
            <h3>{group.key}</h3>

            <SchedulerLine scheduler={group.sessions} />
        </div>
        ))}
    </div>
    );
};