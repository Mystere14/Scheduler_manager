import React from 'react';
import './LineCompare.css';

interface LineCompareProps {
  code_ens: string;
  code_res_sae: string;
  semaine: string;
  type_ens: string;
  heure: number;
}

export const LineCompare: React.FC<LineCompareProps> = ({
  code_ens,
  code_res_sae,
  semaine,
  type_ens,
  heure,
}) => {
  return (
    <div className="line-compare">
      <div className="line-compare-cell code-ens">{code_ens}</div>
      <div className="line-compare-cell code-res-sae">{code_res_sae}</div>
      <div className="line-compare-cell semaine">{semaine}</div>
      <div className="line-compare-cell type-ens">{type_ens}</div>
      <div className="line-compare-cell heure">{heure}</div>
    </div>
  );
};
