import React from 'react';
import { useNavigate } from 'react-router-dom';
import './WelcomePage.css';

interface WelcomePageProps {
  onNavigateToScheduler?: () => void;
  onNavigateToValidaty?: () => void;
}

export const WelcomePage: React.FC<WelcomePageProps> = () => {
  const navigate = useNavigate();

  const handleVerifyConstraints = () => {
    navigate('/validate');
  };

  const handleCreateSchedule = () => {
    navigate('/scheduler');
  };

  return (
    <div className="welcome-page">
      <div className="welcome-container">
        <header className="page-header">
          <h1>Gestionnaire d'emploi du temps</h1>
        </header>
        <main className="welcome-content">
          <div className="buttons-container">
            <button 
              className="primary-button"
              onClick={handleVerifyConstraints}
            >
              <div className="button-content">
                <div className="button-icon">✓</div>
                <div className="button-text">
                  <h2>Vérifier les contraintes</h2>
                </div>
              </div>
            </button>
            <button 
              className="primary-button"
              onClick={handleCreateSchedule}
            >
              <div className="button-content">
                <div className="button-icon">+</div>
                <div className="button-text">
                  <h2>Créer un emploi du temps</h2>
                </div>
              </div>
            </button>
          </div>
        </main>
      </div>
    </div>
  );
};
