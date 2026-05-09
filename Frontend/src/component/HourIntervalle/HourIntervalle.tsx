import { Paper, Box, Typography, TextField } from '@mui/material';
import './HourIntervalle.css';
import { useState, useRef } from 'react';

interface HourIntervalleProps {
  heureDebut: string;
  heureFin: string;
  onHeureDebutChange: (value: string) => void;
  onHeureFinChange: (value: string) => void;
  refAddAbsence?: React.RefObject<any>; // "any" pour éviter les conflits TS
}

export const HourIntervalle = ({
  heureDebut,
  heureFin,
  onHeureDebutChange,
  onHeureFinChange,
  refAddAbsence
}: HourIntervalleProps) => {

  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');

  const endInputRef = useRef<HTMLInputElement>(null);

  // --- TON NORMALIZE TIME D'ORIGINE ---
  // Il remet automatiquement les 00:00 si le champ est vide
  const normalizeTime = (value: string) => {
    if (!value) return '00:00';

    const parts = value.split(':');

    let hours = parts[0] || '00';
    let minutes = parts[1] || '00';

    hours = hours.padStart(2, '0');
    minutes = minutes.padStart(2, '0');

    return `${hours}:${minutes}`;
  };

  const handleEnter = (
    e: React.KeyboardEvent<HTMLDivElement>,
    value: string,
    setter: (v: string) => void,
    nextRef?: React.RefObject<any>
  ) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // Empêche les comportements inattendus du navigateur
      
      // On lit la valeur directement depuis l'input au moment de l'appui sur Entrée
      const targetValue = (e.target as HTMLInputElement).value;
      const normalized = normalizeTime(targetValue);

      setter(normalized);

      // Notre boucle infaillible pour s'assurer que le bouton reçoit le focus
      let attempts = 0;
      const tryFocus = () => {
        const targetElement = nextRef?.current;
        
        if (targetElement) {
          if (!targetElement.disabled) {
            targetElement.focus();
          } else if (attempts < 10) {
            attempts++;
            setTimeout(tryFocus, 50);
          }
        }
      };

      tryFocus();
    }
  };

  return (
    <Box className="hour-intervalle-container">
      <Typography className="hour-intervalle-title">
        Intervalle de temps
      </Typography>
      <Paper className="hour-intervalle-paper">
        <Box className="hour-intervalle-inputs">
<TextField
  label="Heure de début"
  type="time"
  value={heureDebut}
  onChange={(e) => onHeureDebutChange(e.target.value)}
  fullWidth
  variant="outlined"
  onBlur={(e) => onHeureDebutChange(normalizeTime(e.target.value))}
  onKeyDown={(e) => handleEnter(e, heureDebut, onHeureDebutChange, endInputRef)}
  slotProps={{
    inputLabel: { shrink: true }
  }}
  // --- AJOUT DU STYLE ICI ---
  sx={{
    '& label.Mui-focused': {
      color: '#059669', // Couleur du label au focus
    },
    '& .MuiOutlinedInput-root': {
      '&:hover fieldset': {
        borderColor: '#059669', // Couleur de la bordure au survol
      },
      '&.Mui-focused fieldset': {
        borderColor: '#059669', // Couleur de la bordure au focus
      },
    },
  }}
/>

<TextField
  label="Heure de fin"
  type="time"
  value={heureFin}
  onChange={(e) => onHeureFinChange(e.target.value)}
  fullWidth
  variant="outlined"
  onBlur={(e) => onHeureFinChange(normalizeTime(e.target.value))}
  onKeyDown={(e) => handleEnter(e, heureFin, onHeureFinChange, refAddAbsence)}
  inputRef={endInputRef}
  slotProps={{
    inputLabel: { shrink: true }
  }}
  // --- AJOUT DU STYLE ICI ---
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
        </Box>
      </Paper>
    </Box>
  );
};