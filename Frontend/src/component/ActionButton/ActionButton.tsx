import React from 'react';
import './ActionButton.css';

interface ActionButtonProps {
  icon: string;
  label: string;
  description?: string;
  onClick: () => void;
  href?: string;
}

export const ActionButton: React.FC<ActionButtonProps> = ({
  icon,
  label,
  description,
  onClick,
  href
}) => {
  return (
    <a href={href} >
      <button
        className="action-button"
        onClick={onClick}
        title={description}

      >
        <span className="button-icon">{icon}</span>
        <span className="button-label">{label}</span>
      </button>
    </a>
  );
};
