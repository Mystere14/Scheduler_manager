import React from 'react';
import './ActionButton.css';

interface ActionButtonProps {
  icon: string;
  label: string;
  description?: string;
  onClick: () => void;
}

export const ActionButton: React.FC<ActionButtonProps> = ({
  icon,
  label,
  description,
  onClick,
}) => {
  return (
    <button
      className="action-button"
      onClick={onClick}
      title={description}
    >
      <span className="button-icon">{icon}</span>
      <span className="button-label">{label}</span>
    </button>
  );
};
