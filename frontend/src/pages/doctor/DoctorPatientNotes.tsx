import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { doctorApi } from '@/api/doctorApi';
import { DoctorNote, NoteType } from '@/types';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Button } from '@/components/ui/button';
import { FileEdit, Plus, CheckCircle2, AlertCircle, Edit3, X } from 'lucide-react';

export const DoctorPatientNotes: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [notes, setNotes] = useState<DoctorNote[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Note creation form state
  const [isAddingNote, setIsAddingNote] = useState<boolean>(false);
  const [content, setContent] = useState<string>('');
  const [noteType, setNoteType] = useState<NoteType>('ROUTINE_REVIEW');
  const [isShared, setIsShared] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);

  // Note editing state
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState<string>('');
  const [editNoteType, setEditNoteType] = useState<NoteType>('ROUTINE_REVIEW');
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;
    loadNotes();
  }, [id]);

  async function loadNotes() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await doctorApi.getPatientNotes(id!);
      setNotes(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load clinical notes.');
    } finally {
      setIsLoading(false);
    }
  }

  const handleCreateNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim() || content.trim().length < 3) {
      setFormError('Note content must be at least 3 characters.');
      return;
    }
    setIsSaving(true);
    setFormError(null);
    try {
      const newNote = await doctorApi.createPatientNote(id!, {
        content: content.trim(),
        note_type: noteType,
        is_shared_with_patient: isShared,
      });
      setNotes([newNote, ...notes]);
      setContent('');
      setIsAddingNote(false);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || 'Failed to save clinical note.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleStartEdit = (note: DoctorNote) => {
    setEditingNoteId(note.id);
    setEditContent(note.content);
    setEditNoteType(note.note_type);
  };

  const handleUpdateNote = async (noteId: string) => {
    if (!editContent.trim() || editContent.trim().length < 3) {
      alert('Note content must be at least 3 characters.');
      return;
    }
    setIsUpdating(true);
    try {
      const updated = await doctorApi.updateDoctorNote(noteId, {
        content: editContent.trim(),
        note_type: editNoteType,
      });
      setNotes(notes.map((n) => (n.id === noteId ? updated : n)));
      setEditingNoteId(null);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update note.');
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="py-16 text-center">
        <LoadingSpinner size="md" label="Loading clinical notes..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-rose-950/30 border border-rose-800/50 rounded-xl text-xs text-rose-300">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Title & Add Note Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white tracking-tight">Clinical Decision Support Notes</h2>
          <p className="text-xs text-slate-400">
            Record clinician observations, follow-up recommendations, and longitudinal reviews.
          </p>
        </div>

        {!isAddingNote && (
          <Button
            size="sm"
            onClick={() => setIsAddingNote(true)}
            variant="primary"
            className="text-xs gap-1.5 self-start sm:self-auto"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Clinical Note</span>
          </Button>
        )}
      </div>

      {/* New Note Form */}
      {isAddingNote && (
        <form
          onSubmit={handleCreateNote}
          className="p-6 bg-slate-950/90 border border-teal-800/60 rounded-2xl space-y-4 shadow-xl"
        >
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-xs font-bold uppercase tracking-wider text-teal-400">
              New Clinical Decision Support Note
            </h3>
            <button
              type="button"
              onClick={() => {
                setIsAddingNote(false);
                setFormError(null);
              }}
              className="text-slate-500 hover:text-slate-300 transition"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {formError && (
            <div className="p-3 bg-rose-950/40 border border-rose-800/60 rounded-xl text-xs text-rose-300 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Note Category
              </label>
              <select
                value={noteType}
                onChange={(e) => setNoteType(e.target.value as NoteType)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-teal-500"
              >
                <option value="ROUTINE_REVIEW">Routine Clinical Review</option>
                <option value="EMERGENCY_FOLLOW_UP">Emergency Follow-up</option>
                <option value="DIAGNOSTIC_HYPOTHESIS">Diagnostic Hypothesis / Workup</option>
                <option value="DISCHARGE">Discharge / Monitoring Summary</option>
              </select>
            </div>

            <div className="flex items-center pt-6">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isShared}
                  onChange={(e) => setIsShared(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-teal-500 focus:ring-teal-500"
                />
                <span>Share note with patient in patient portal</span>
              </label>
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-semibold text-slate-300">
                Clinician Observations & Plan
              </label>
              <span className="text-[10px] text-slate-500 font-mono">
                {content.length} / 5000
              </span>
            </div>
            <textarea
              rows={4}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter clinical assessment, vestibular test notes, medication adjustments, or rehabilitation instructions..."
              maxLength={5000}
              className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
            />
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => {
                setIsAddingNote(false);
                setFormError(null);
              }}
              className="text-xs"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              size="sm"
              variant="primary"
              isLoading={isSaving}
              className="text-xs"
            >
              Save Clinical Note
            </Button>
          </div>
        </form>
      )}

      {/* Notes Timeline */}
      {notes.length === 0 ? (
        <div className="p-8 text-center bg-slate-950/60 border border-slate-800 rounded-2xl text-xs text-slate-500">
          No clinical notes authored yet. Click "Add Clinical Note" above to enter your first observation.
        </div>
      ) : (
        <div className="space-y-4">
          {notes.map((n) => (
            <div
              key={n.id}
              className="p-6 bg-slate-950/80 border border-slate-800 rounded-2xl space-y-3 shadow-xl"
            >
              {/* Note Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-slate-800/80 gap-2">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-950 text-teal-300 border border-teal-800">
                    {n.note_type.replace(/_/g, ' ')}
                  </span>
                  <span className="text-xs font-bold text-white">{n.doctor_name}</span>
                  <span className="text-[11px] text-slate-400">({n.doctor_specialization})</span>
                </div>

                <div className="flex items-center gap-3 text-[11px] text-slate-500 font-mono">
                  <span>{new Date(n.created_at).toLocaleString()}</span>
                  {editingNoteId !== n.id && (
                    <button
                      onClick={() => handleStartEdit(n)}
                      className="text-teal-400 hover:text-teal-300 transition flex items-center gap-1 font-sans text-xs"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>Edit</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Note Content / Editing Form */}
              {editingNoteId === n.id ? (
                <div className="space-y-3 pt-2">
                  <select
                    value={editNoteType}
                    onChange={(e) => setEditNoteType(e.target.value as NoteType)}
                    className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white"
                  >
                    <option value="ROUTINE_REVIEW">Routine Clinical Review</option>
                    <option value="EMERGENCY_FOLLOW_UP">Emergency Follow-up</option>
                    <option value="DIAGNOSTIC_HYPOTHESIS">Diagnostic Hypothesis / Workup</option>
                    <option value="DISCHARGE">Discharge / Monitoring Summary</option>
                  </select>
                  <textarea
                    rows={4}
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    maxLength={5000}
                    className="w-full p-3 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-teal-500"
                  />
                  <div className="flex justify-end gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setEditingNoteId(null)}
                      className="text-xs"
                    >
                      Cancel
                    </Button>
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleUpdateNote(n.id)}
                      isLoading={isUpdating}
                      className="text-xs"
                    >
                      Save Changes
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-200 whitespace-pre-wrap leading-relaxed">
                  {n.content}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

