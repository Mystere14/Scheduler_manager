import { Paper, Box, Typography, TextField } from '@mui/material';
import './HourIntervalle.css';

interface HourIntervalleProps {
  heureDebut: string;
  heureFin: string;
  onHeureDebutChange: (value: string) => void;
  onHeureFinChange: (value: string) => void;
}

export const HourIntervalle = ({
  heureDebut,
  heureFin,
  onHeureDebutChange,
  onHeureFinChange,
}: HourIntervalleProps) => {
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
            slotProps={{
              inputLabel: { shrink: true }
            }}
          />
          <TextField
            label="Heure de fin"
            type="time"
            value={heureFin}
            onChange={(e) => onHeureFinChange(e.target.value)}
            fullWidth
            variant="outlined"
            slotProps={{
              inputLabel: { shrink: true }
            }}
          />
        </Box>
      </Paper>
    </Box>
  );
};
