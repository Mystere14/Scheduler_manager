import {Dialog} from '@mui/material'
import api from '../../services/api'
import { useState, useEffect } from 'react'
import { Box, Accordion, AccordionSummary, AccordionDetails, Typography, Button, TextField } from '@mui/material'
import './AbsenceVisualisation.css'

interface AbsenceVisualisationProps {
    open: boolean
    onClose: () => void
}

interface AbsenceData {
    [key: string]: any[]
}

export const AbsenceVisualisation = ({ open, onClose }: AbsenceVisualisationProps) => {
    const [codesEns, setCodesEns] = useState<string[]>([])
    const [absencesData, setAbsencesData] = useState<AbsenceData>({})
    const [filterCodeEns, setFilterCodeEns] = useState<string>('')
    const [filterDateStart, setFilterDateStart] = useState<string>('')
    const [filterDateEnd, setFilterDateEnd] = useState<string>('')

    const handleRecoverCodeEns = async () => 
    {
        api.getCodeEns().then((response: any) => {
            const data = Array.isArray(response) ? response : (Array.isArray(response.data) ? response.data : []);
            const codes = data.map((item: any) => item.code || item);
            setCodesEns(codes)
        }).catch((error) => {
            console.error('Erreur lors de la récupération des codes_ens:', error);
        });
    }

    const handleRecoverAbsences = async (code_ens: string) => 
    {
        api.getAbsenceByEnseignant(code_ens).then((response: any) => {
            const data = Array.isArray(response) ? response : (Array.isArray(response.data) ? response.data : []);
            setAbsencesData(prev => ({
                ...prev,
                [code_ens]: data
            }))
        }).catch((error) => {
            console.error('Erreur lors de la récupération des absences:', error);
        });
    }

    const handleDeleteAbsence = async (id: string, code_ens: string) => {
        try {
            await api.deleteAbsence(id);
            setAbsencesData(prev => ({
                ...prev,
                [code_ens]: prev[code_ens].filter((absence: any) => absence.id !== id)
            }));
        } catch (error) {
            console.error('Erreur lors de la suppression de l\'absence:', error);
        }
    }

    const getFilteredAbsences = (code: string) => {
        let filtered = absencesData[code] || []

        if (filterDateStart) {
            filtered = filtered.filter((absence: any) => absence.jour >= filterDateStart)
        }

        if (filterDateEnd) {
            filtered = filtered.filter((absence: any) => absence.jour <= filterDateEnd)
        }

        // Trier par date croissante
        filtered = filtered.sort((a: any, b: any) => {
            return new Date(a.jour).getTime() - new Date(b.jour).getTime()
        })

        return filtered
    }

    const getFilteredCodes = () => {
        if (!filterCodeEns) return codesEns
        return codesEns.filter((code) => code.toLowerCase().includes(filterCodeEns.toLowerCase()))
    }

    useEffect(() => {
        handleRecoverCodeEns()
    }, [])

    useEffect(() => {
        if (open) {
            setAbsencesData({})
            handleRecoverCodeEns()
        }
    }, [open])

    return (
        <Dialog open={open} maxWidth="md" fullWidth onClose={onClose}>
            <Box sx={{ padding: 2 }}>
                <h1 className="absence-dialog-title">Visualisation des Absences</h1>
                
                <div className="absence-filter-section">
                    <div className="absence-filter-header">
                        <h3>Filtres</h3>
                        <button 
                            className="btn-clear-filters"
                            onClick={() => {
                                setFilterCodeEns('')
                                setFilterDateStart('')
                                setFilterDateEnd('')
                            }}
                        >
                            Réinitialiser
                        </button>
                    </div>
                    <div className="absence-filter-inputs">
                        <TextField
                            label="Code enseignant"
                            size="small"
                            value={filterCodeEns}
                            onChange={(e) => setFilterCodeEns(e.target.value)}
                            sx={{ flex: 1 }}
                        />
                        <TextField
                            label="Date de début"
                            type="date"
                            size="small"
                            value={filterDateStart}
                            onChange={(e) => setFilterDateStart(e.target.value)}
                            variant="outlined"
                            sx={{ 
                                flex: 1,
                                '& label': { 
                                    transform: 'translate(14px, -9px) scale(0.75)',
                                    backgroundColor: 'white',
                                    padding: '0 4px'
                                },
                                '& label.Mui-focused': {
                                    transform: 'translate(14px, -9px) scale(0.75)'
                                }
                            }}
                        />
                        <TextField
                            label="Date de fin"
                            type="date"
                            size="small"
                            value={filterDateEnd}
                            onChange={(e) => setFilterDateEnd(e.target.value)}
                            variant="outlined"
                            sx={{ 
                                flex: 1,
                                '& label': { 
                                    transform: 'translate(14px, -9px) scale(0.75)',
                                    backgroundColor: 'white',
                                    padding: '0 4px'
                                },
                                '& label.Mui-focused': {
                                    transform: 'translate(14px, -9px) scale(0.75)'
                                }
                            }}
                        />
                    </div>
                </div>
                
                <Box className="absence-list">
                    {getFilteredCodes().map((code) => (
                        <Accordion 
                            key={code}
                            onChange={() => handleRecoverAbsences(code)}
                            className="code-ens-accordion"
                        >
                            <AccordionSummary expandIcon={<span>▼</span>} className="code-ens-accordion-summary">
                                <Typography variant="h6">{code}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                {getFilteredAbsences(code).length > 0 ? (
                                    <div>
                                        {getFilteredAbsences(code).map((absence: any, index: number) => (
                                            <div key={index} className="absence-row">
                                                <p><strong>Date:</strong> {absence.jour}</p>
                                                <p><strong>Heure début:</strong> {absence.heure_debut}</p>
                                                <p><strong>Heure fin:</strong> {absence.heure_fin}</p>
                                                <button 
                                                    className="delete-button"
                                                    onClick={() => handleDeleteAbsence(absence.id, code)}
                                                    title="Supprimer"
                                                >
                                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                        <polyline points="3 6 5 6 21 6"></polyline>
                                                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                                                        <line x1="10" y1="11" x2="10" y2="17"></line>
                                                        <line x1="14" y1="11" x2="14" y2="17"></line>
                                                    </svg>
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <Typography>Aucune absence pour ce code enseignant</Typography>
                                )}
                            </AccordionDetails>
                        </Accordion>
                    ))}
                </Box>
            </Box>
        </Dialog>
    );

}