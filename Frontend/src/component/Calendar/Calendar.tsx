import { DayPicker } from 'react-day-picker';
import 'react-day-picker/dist/style.css';
import { Paper, Box, Typography, Button } from '@mui/material';
import { fr } from 'date-fns/locale';
import { useState, useRef } from 'react';
import './Calendar.css';


interface CalendarProps {
  selectedDates: Date[];
  onSelectDates: (dates: Date[]) => void;
}

export const Calendar = ({ selectedDates, onSelectDates }: CalendarProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [draggedDays, setDraggedDays] = useState<Set<string>>(new Set());
  const calendarRef = useRef<HTMLDivElement>(null);

  const extractDateFromButton = (button: HTMLElement): Date | null => {
    try {
      // Les boutons de jours de DayPicker ont un aria-label au format: "lundi 1 janvier 2024"
      const ariaLabel = button.getAttribute('aria-label');
      if (!ariaLabel) return null;

      // Chercher si le bouton a un attribut data qui contient la date
      // Alternatively, essayer de parser depuis le contenu texte
      const dayText = button.textContent?.trim();
      if (!dayText) return null;

      // On peut aussi chercher les data attributes
      for (let i = 0; i < button.attributes.length; i++) {
        const attr = button.attributes[i];
        if (attr.name.startsWith('data-')) {
          console.log(`${attr.name}: ${attr.value}`);
        }
      }

      return null;
    } catch (error) {
      return null;
    }
  };

  const getDateKey = (date: Date): string => {
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).tagName === 'BUTTON') {
      setIsDragging(true);
      setDraggedDays(new Set());
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !calendarRef.current) return;

    // Utiliser elementFromPoint pour trouver l'élément sous le curseur
    const element = document.elementFromPoint(e.clientX, e.clientY) as HTMLElement;
    
    // Chercher si c'est ou si ça contient un bouton de jour
    let dayButton: HTMLElement | null = null;
    
    if (element?.tagName === 'BUTTON') {
      dayButton = element;
    } else {
      dayButton = element?.closest('button');
    }

    if (dayButton && calendarRef.current?.contains(dayButton)) {
      // Vérifier que c'est vraiment un bouton de jour (pas les flèches)
      const dayNum = dayButton.textContent?.trim();
      if (dayNum && !isNaN(Number(dayNum)) && Number(dayNum) > 0 && Number(dayNum) <= 31) {
        try {
          const monthTable = dayButton.closest('table');
          if (monthTable) {
            const dateToToggle = new Date(selectedDates[0]?.getFullYear() || new Date().getFullYear(), 
                                          selectedDates[0]?.getMonth() || new Date().getMonth(),
                                          Number(dayNum));
            
            const dateKey = getDateKey(dateToToggle);
            
            // Ne traiter le jour que si on ne l'a pas déjà modifié pendant ce drag
            if (!draggedDays.has(dateKey)) {
              // Vérifier si la date existe
              const dateExists = selectedDates.some(d => 
                d.getFullYear() === dateToToggle.getFullYear() &&
                d.getMonth() === dateToToggle.getMonth() &&
                d.getDate() === dateToToggle.getDate()
              );
              
              // Toggle: ajouter si absent, retirer si présent
              if (dateExists) {
                onSelectDates(selectedDates.filter(d => 
                  !(d.getFullYear() === dateToToggle.getFullYear() &&
                    d.getMonth() === dateToToggle.getMonth() &&
                    d.getDate() === dateToToggle.getDate())
                ));
              } else {
                onSelectDates([...selectedDates, dateToToggle]);
              }
              
              // Marquer ce jour comme modifié
              setDraggedDays(new Set([...draggedDays, dateKey]));
            }
          }
        } catch (error) {
          console.error('Erreur parsing date:', error);
        }
      }
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
    setDraggedDays(new Set());
  };

  return (
    <Box 
      className="calendar-container"
      ref={calendarRef}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      style={{ userSelect: 'none' }}
    >
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
