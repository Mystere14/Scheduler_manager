import { SchedulerGroup } from '../../feature/SchedulerGroup/SchedulerGroup';
import React, { useState, useEffect, useContext } from 'react';
import { useLocation } from 'react-router-dom';
import './SchedulerList.css';
import { ValidationContext } from '../../services/context';


interface SchedulerList {
}

export const SchedulerList = ({}: SchedulerList) => {
    const location = useLocation();
    const context = useContext(ValidationContext);
    const filteredSchedulers = context.schedulerList.filter((s: any) =>
        s.code_res_sae === location.pathname.split('/')[2]
    );

    const grouped = Object.values(
    filteredSchedulers.reduce((acc: any, item: any) => {
        const key = `${item.type_ens.split('_')[0]}-${Math.abs(item.heures)}h`;

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
        <h2>{filteredSchedulers[0].code_res_sae}</h2>
        {grouped.map((group: any) => (
        
        <div key={group.key}>
            <h3>{group.key}</h3>

            <SchedulerGroup key={group.key} schedulerGroup={group.sessions} />
        </div>
        ))}
    </div>
    );
};