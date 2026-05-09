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
  
  // 1. Vos styles en ligne
  styles={{
    month: { fontSize: '0.9rem' }
  }}
  
  // 2. Vos classes CSS personnalisées pour les jours
  modifiersClassNames={{
    selected: 'my-selected-date', 
    today: 'my-today-date'   
  }}
  
  // 3. Notre composant personnalisé pour des flèches 100% vertes
  components={{
    Chevron: (props) => {
      const { orientation, className, disabled } = props;
      const greenColor = "#059669";

      const SolidChevron = ({ path }: { path: string }) => (
        <svg 
          className={className} 
          xmlns="http://www.w3.org/2000/svg" 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          style={{
            fill: greenColor,
            color: greenColor,
            stroke: 'none',
            opacity: disabled ? 0.3 : 1, 
            cursor: disabled ? 'default' : 'pointer'
          }}
        >
          <path d={path} />
        </svg>
      );

      if (orientation === 'left') {
        return <SolidChevron path="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />;
      }
      
      if (orientation === 'right') {
        return <SolidChevron path="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />;
      }

      return <svg className={className} />; 
    }
  }}
/>
        <Box className="calendar-actions">
          <Button
            size="small"
            onClick={() => onSelectDates([])}
            disabled={selectedDates.length === 0}
            className='eraseSelection'
          >
            Effacer sélection
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};
