import { ActionButton } from '../ActionButton/ActionButton';
import './ActionButtons.css';

interface ActionButtonsProps {
  onGenerate: () => void;
  onVoid: () => void;
  isGenerating: boolean;
}

export const ActionButtons = ({
  onGenerate,
  onVoid,
  isGenerating
}: ActionButtonsProps) => {
  return (
    <div className="action-buttons">
      {isGenerating && (
        <ActionButton
          icon="⚡"
          label="Générer une solution"
          description="Générer une solution d'emploi du temps"
          onClick={onGenerate}
        />
      )}
      <ActionButton
        icon="📥"
        label="Importer les données"
        description="Importer les données depuis un fichier"
        onClick={onVoid}
      />
      <ActionButton
        icon="📤"
        label="Exporter le tableur"
        description="Exporter la solution en format tableau"
        onClick={onVoid}
      />
    </div>
  );
};
