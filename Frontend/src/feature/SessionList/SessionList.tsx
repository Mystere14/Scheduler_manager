import React, { useState } from 'react';
import { LineCompare } from '../../component/LineCompare/LineCompare';
import './SessionList.css';

interface SessionListProps {
  comparisonResult: any[];
}

interface SubjectData {
  code_res_sae: string;
  plannedCount: number;
  placedCount: number;
  plannedHours: number;
  placedHours: number;
  hasUnplacedIssues: boolean;
  hasExtraIssues: boolean;  
  plannedCourses: any[];
  placedCourses: any[];
}

export const SessionList: React.FC<SessionListProps> = ({ comparisonResult }) => {
  const [expandedSubjects, setExpandedSubjects] = useState<Set<string>>(new Set());

  // Filter real sessions (real_session = true)
  const realSessions = comparisonResult.filter((item: any) => item.real_session === true);

  // Group by code_res_sae (subject/matière)
  const subjectMap = new Map<string, SubjectData>();

  realSessions.forEach((session: any) => {
    if (!subjectMap.has(session.code_res_sae)) {
      subjectMap.set(session.code_res_sae, {
        code_res_sae: session.code_res_sae,
        plannedCount: 0,
        placedCount: 0,
        plannedHours: 0,
        placedHours: 0,
        hasUnplacedIssues: false,
        hasExtraIssues: false,
        plannedCourses: [],
        placedCourses: [],
      });
    }

    const subject = subjectMap.get(session.code_res_sae)!;

    // Separate planned (positive hours) and placed (negative hours)
    if (session.heures > 0) {
      subject.plannedCount += 1;
      subject.plannedHours += session.heures;
      subject.plannedCourses.push(session);
    } else if (session.heures < 0) {
      subject.placedCount += 1;
      subject.placedHours += Math.abs(session.heures);
      subject.placedCourses.push(session);
    }
  });

  // Check for unplaced and extra issues per subject
  comparisonResult.forEach((item: any) => {
    if (item.real_session === false && subjectMap.has(item.code_res_sae)) {
      const subject = subjectMap.get(item.code_res_sae)!;
      if (item.heures > 0) {
        subject.hasUnplacedIssues = true;
      } else if (item.heures < 0) {
        subject.hasExtraIssues = true;
      }
    }
  });

  const subjects = Array.from(subjectMap.values());

  const toggleSubject = (code_res_sae: string) => {
    setExpandedSubjects((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(code_res_sae)) {
        newSet.delete(code_res_sae);
      } else {
        newSet.add(code_res_sae);
      }
      return newSet;
    });
  };

  const getSubjectHighlightClass = (subject: SubjectData): string => {
    if (subject.hasUnplacedIssues) {
      return 'subject-unplaced-issue';
    }
    if (subject.hasExtraIssues) {
      return 'subject-extra-issue';
    }
    return '';
  };

  const getCourseIssueClass = (course: any, isPlanned: boolean): string => {
    if (isPlanned) {
      // For planned courses, check for unplaced issues (heures > 0)
      const unplacedCourses = comparisonResult.filter(
        (item: any) => 
          item.real_session === false && 
          item.heures > 0 && 
          item.code_ens === course.code_ens &&
          item.code_res_sae === course.code_res_sae
      );
      if (unplacedCourses.length > 0) {
        return 'course-unplaced-issue';
      }
    } else {
      // For placed courses, check for extra issues (heures < 0)
      const extraCourses = comparisonResult.filter(
        (item: any) => 
          item.real_session === false && 
          item.heures < 0 && 
          item.code_ens === course.code_ens &&
          item.code_res_sae === course.code_res_sae
      );
      if (extraCourses.length > 0) {
        return 'course-extra-issue';
      }
    }

    return '';
  };

  return (
    <div className="sessions-list-container">
      <h2>Cours</h2>
      
      {subjects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📚</div>
          <div className="empty-state-text">Aucun cours planifié trouvé</div>
        </div>
      ) : (
        <div className="subjects-list">
          {subjects.map((subject) => (
            <div
              key={subject.code_res_sae}
              className={`subject-item ${getSubjectHighlightClass(subject)}`}
            >
              <div
                className="subject-header"
                onClick={() => toggleSubject(subject.code_res_sae)}
              >
                <span className="subject-toggle">
                  {expandedSubjects.has(subject.code_res_sae) ? '▼' : '▶'}
                </span>
                <span className="subject-name">{subject.code_res_sae}</span>
                <span className="subject-stats">
                  Créneaux: {subject.plannedCount}/{subject.placedCount} | 
                  Heures: {subject.plannedHours}h/{subject.placedHours}h
                </span>
              </div>

              {expandedSubjects.has(subject.code_res_sae) && (
                <div className="subject-details">
                  <div className="courses-section planned-section">
                    <h4>Créneaux prévus</h4>
                    <div className="results-header">
                      <div className="header-cell">Code_Ens</div>
                      <div className="header-cell">Code_Res_SAE</div>
                      <div className="header-cell">Type_ens</div>
                      <div className="header-cell">Heure</div>
                    </div>
                    {subject.plannedCourses.length > 0 ? (
                      <div className="courses-list">
                        {subject.plannedCourses.map((course: any, index: number) => (
                          <div
                            key={`planned-${subject.code_res_sae}-${index}`}
                            className={`course-row ${getCourseIssueClass(course, true)}`}
                          >
                            <LineCompare
                              code_ens={course.code_ens}
                              code_res_sae={course.code_res_sae}
                              type_ens={course.type_ens}
                              heure={course.heures}
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-courses">
                        <p>Aucun créneaux prévus</p>
                      </div>
                    )}
                  </div>

                  <div className="courses-section placed-section">
                    <h4>Créneaux placés</h4>
                    <div className="results-header">
                      <div className="header-cell">Code_Ens</div>
                      <div className="header-cell">Code_Res_SAE</div>
                      <div className="header-cell">Type_ens</div>
                      <div className="header-cell">Heure</div>
                    </div>
                    {subject.placedCourses.length > 0 ? (
                      <div className="courses-list">
                        {subject.placedCourses.map((course: any, index: number) => (
                          <div
                            key={`placed-${subject.code_res_sae}-${index}`}
                            className={`course-row ${getCourseIssueClass(course, false)}`}
                          >
                            <LineCompare
                              code_ens={course.code_ens}
                              code_res_sae={course.code_res_sae}
                              type_ens={course.type_ens}
                              heure={Math.abs(course.heures)}
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="empty-courses">
                        <p>Aucun créneaux placés</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
