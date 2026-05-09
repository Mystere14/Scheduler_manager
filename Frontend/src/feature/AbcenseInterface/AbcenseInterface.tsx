import { useState, useRef } from 'react';
import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Box,
  Button,
  Divider,
} from '@mui/material';
import { Calendar } from '../../component/Calendar/Calendar';
import { HourIntervalle } from '../../component/HourIntervalle/HourIntervalle';
import './AbcenseInterface.css';

// Interface
interface Absence {
  id: number;
  code_ens: string;
  dates: Date[];
  heureDebut: string;
  heureFin: string;
}

interface AbsenceInterfaceProps {
  open: boolean;
  onClose: () => void;
}

export const AbsenceInterface = ({ open, onClose }: AbsenceInterfaceProps) => {
  const [absences, setAbsences] = useState<Absence[]>([]);
  const [selectedCodeEns, setSelectedCodeEns] = useState('');
  const [selectedDates, setSelectedDates] = useState<Date[]>([]);
  const [heureDebut, setHeureDebut] = useState('');
  const [heureFin, setHeureFin] = useState('');

  const addAbsenceRef = useRef<HTMLButtonElement | null>(null);

  // Fonctions de gestion
  const handleCloseAbsenceDialog = () => {
    onClose();
    setSelectedCodeEns('');
    setSelectedDates([]);
    setHeureDebut('');
    setHeureFin('');
  };

  const handleSaveAbsence = () => {
    // J'ai gardé ta logique d'origine
    if (selectedDates.length > 0 && heureDebut && heureFin) {
      const newId = Math.max(...absences.map(a => a.id), 0) + 1;
      setAbsences([...absences, {
        id: newId,
        code_ens: selectedCodeEns,
        dates: selectedDates,
        heureDebut,
        heureFin
      }]);

      setSelectedCodeEns('');
      setSelectedDates([]);
      setHeureDebut('');
      setHeureFin('');
    }
  };

  const handleDeleteAbsence = (id: number) => {
    setAbsences(absences.filter(a => a.id !== id));
  };

  return (
    <Dialog open={open} onClose={handleCloseAbsenceDialog} maxWidth="md" fullWidth>
      <DialogTitle className="absence-dialog-title">
        Gestion des Absences par Code Ens
      </DialogTitle>
      <DialogContent className="absence-dialog-content">
        <Box className="absence-dialog-body">
          <Box className="absence-dialog-layout">
            <Calendar 
              selectedDates={selectedDates}
              onSelectDates={setSelectedDates}
            />

            <Divider orientation="vertical" flexItem />

            <HourIntervalle 
              heureDebut={heureDebut}
              heureFin={heureFin}
              onHeureDebutChange={setHeureDebut}
              onHeureFinChange={setHeureFin}
              refAddAbsence={addAbsenceRef}
            />
          </Box>
        </Box>
      </DialogContent>
      <DialogActions className="absence-dialog-actions">
        <Button className='closeButton' onClick={handleCloseAbsenceDialog}>Fermer</Button>
        <Button
          className={selectedDates.length === 0 || !heureDebut || !heureFin ? '' : 'addAbcenseButton'}
          onClick={handleSaveAbsence}
          disabled={selectedDates.length === 0 || !heureDebut || !heureFin}
          ref={addAbsenceRef}
          disableRipple={true}
          disableFocusRipple={true}
        >
          Ajouter les absences
        </Button>
      </DialogActions>
    </Dialog>
  );
};