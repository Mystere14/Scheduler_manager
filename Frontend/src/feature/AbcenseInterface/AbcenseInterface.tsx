import { useState, useRef, useEffect } from 'react';
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
  Autocomplete,
  TextField,
} from '@mui/material';
import { Calendar } from '../../component/Calendar/Calendar';
import { HourIntervalle } from '../../component/HourIntervalle/HourIntervalle';
import './AbcenseInterface.css';
import api from '../../services/api';


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
  const [selectedCodeEns, setSelectedCodeEns] = useState<string[]>([]);
  const [codeEnsList, setCodeEnsList] = useState<string[]>([]);
  const [selectedDates, setSelectedDates] = useState<Date[]>([]);
  const [heureDebut, setHeureDebut] = useState('');
  const [heureFin, setHeureFin] = useState('');

  const addAbsenceRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (open) {
      handleGetCode_ens();
    }
  }, [open]);

  // Fonctions de gestion
  const handleCloseAbsenceDialog = () => {
    onClose();
    setSelectedCodeEns([]);
    setSelectedDates([]);
    setHeureDebut('');
    setHeureFin('');
  };

  const handleSaveAbsence = () => {
    if (selectedCodeEns.length > 0 && selectedDates.length > 0 && heureDebut && heureFin) {
      selectedCodeEns.forEach((codeEns) => {
        const newId = Math.max(...absences.map(a => a.id), 0) + 1;
        setAbsences(prev => [...prev, {
          id: newId,
          code_ens: codeEns,
          dates: selectedDates,
          heureDebut,
          heureFin
        }]);
      });

      setSelectedCodeEns([]);
      setSelectedDates([]);
      setHeureDebut('');
      setHeureFin('');
    }
  };

  const handleDeleteAbsence = (id: number) => {
    setAbsences(absences.filter(a => a.id !== id));
  };

  const handleGetCode_ens = async () => {
    try {
      const res = await api.getCodeEns();
      if (Array.isArray(res)) {
        const codes = res.map((item: any) => item.code);
        setCodeEnsList(codes);
      }
    } catch (error) {
      console.error('Erreur lors de la récupération des codes enseignants:', error);
    }
  };

  return (
    <Dialog open={open} onClose={handleCloseAbsenceDialog} maxWidth="md" fullWidth>
      <DialogTitle className="absence-dialog-title">
        Gestion des Absences par Code Ens
      </DialogTitle>
      <DialogContent className="absence-dialog-content">
        <Box className="absence-dialog-body">
          <Box className="absence-dialog-layout">
            <Box className="code-ens-section">
              <Autocomplete
                multiple
                size="small"
                options={codeEnsList}
                value={selectedCodeEns}
                onChange={(event, newValue) => setSelectedCodeEns(newValue)}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Codes enseignants"
                    placeholder="Sélectionnez un ou plusieurs codes"
                    variant="outlined"
                    size="small"
                    className="code-ens-input"
                    sx={{
                      '& label.Mui-focused': {
                        color: '#059669',
                      },
                      '& .MuiOutlinedInput-root': {
                        '&:hover fieldset': {
                          borderColor: '#059669',
                        },
                        '&.Mui-focused fieldset': {
                          borderColor: '#059669',
                        },
                      },
                    }}
                  />
                )}
                fullWidth
                slotProps={{
                  paper: {
                    sx: { maxHeight: 400 }
                  }
                }}
              />
              <Calendar 
                selectedDates={selectedDates}
                onSelectDates={setSelectedDates}
              />
            </Box>
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
          className={selectedCodeEns.length > 0 && selectedDates.length > 0 && heureDebut && heureFin ? 'addAbcenseButton' : ''}
          onClick={handleSaveAbsence}
          disabled={selectedCodeEns.length === 0 || selectedDates.length === 0 || !heureDebut || !heureFin}
          ref={addAbsenceRef}
          disableRipple={true}
          disableFocusRipple={true}
          size="small"
        >
          Ajouter les absences
        </Button>
      </DialogActions>
    </Dialog>
  );
};