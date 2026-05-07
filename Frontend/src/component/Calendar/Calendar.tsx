import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';
import { Paper, Box, Typography, Button } from '@mui/material';
import { fr } from 'date-fns/locale';
import './Calendar.css';

interface CalendarProps {
  selectedDates: Date[];
  onSelectDates: (dates: Date[]) => void;
}

export const Calendar = ({ selectedDates, onSelectDates }: CalendarProps) => {
  return (
    <Box className="calendar-container">
      <Paper className="calendar-paper">
        <Typography className="calendar-title">
          Sélectionner les jours d'absence
        </Typography>
        <DayPicker
          mode="multiple"
          selected={selectedDates}
          onSelect={(dates) => onSelectDates(dates || [])}
          locale={fr}
          styles={{
            month: { fontSize: '0.9rem' }
          }}
        />
        <Box className="calendar-actions">
          <Button
            size="small"
            onClick={() => onSelectDates([])}
            disabled={selectedDates.length === 0}
          >
            Effacer sélection
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};
