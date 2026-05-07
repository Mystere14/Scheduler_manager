import { ActionButton } from '../ActionButton/ActionButton';
import './ActionButtons.css';

interface ActionButtonsProps {
    onGenerate: () => void;
    onExport: () => void;
    onImport: () => void;
    isGenerating: boolean;
    isImporting: boolean;
}

export const ActionButtons = ({
    onGenerate,
    onExport,
    onImport,
    isGenerating,
    isImporting
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
            {isImporting && (
                <ActionButton
                    icon="📥"
                    label="Importer les données"
                    description="Importer les données depuis un fichier"
                    onClick={onImport}
                />
            )}

            <ActionButton
                icon="📤"
                label="Exporter le tableur"
                description="Exporter la solution en format tableau"
                onClick={onExport}
            />
        </div>
    );
};
