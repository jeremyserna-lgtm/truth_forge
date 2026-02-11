import React, { useState } from 'react';
import {
  KnowledgeAtom,
  UploadedDocument,
  ArchitecturalPlan,
  HandoffEnvelope,
  ModelConfig
} from '../../../types';
import {
  generateArchitecturalPlan,
  createHandoffEnvelope,
  exportPlanAsMarkdown,
  exportHandoffAsJson
} from '../../../services/geminiService';
import {
  DocumentTextIcon,
  CubeIcon,
  ArrowRightIcon,
  ClipboardDocumentListIcon,
  ArrowDownTrayIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  ArrowPathIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/24/solid';

interface ArchitectViewProps {
  atoms: KnowledgeAtom[];
  documents: UploadedDocument[];
  activeModel: ModelConfig;
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
}

const ArchitectView: React.FC<ArchitectViewProps> = ({
  atoms,
  documents,
  activeModel,
  isLoading,
  setLoading
}) => {
  const [goal, setGoal] = useState('');
  const [plans, setPlans] = useState<ArchitecturalPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<ArchitecturalPlan | null>(null);
  const [envelope, setEnvelope] = useState<HandoffEnvelope | null>(null);

  // Document and atom selection state
  const [selectedDocIds, setSelectedDocIds] = useState<Set<string>>(new Set());
  const [selectedAtomIds, setSelectedAtomIds] = useState<Set<string>>(new Set());
  const [showDocSelector, setShowDocSelector] = useState(false);
  const [showAtomSelector, setShowAtomSelector] = useState(false);

  // Helper functions for selection
  const toggleDocSelection = (docId: string) => {
    setSelectedDocIds(prev => {
      const next = new Set(prev);
      if (next.has(docId)) {
        next.delete(docId);
      } else {
        next.add(docId);
      }
      return next;
    });
  };

  const toggleAtomSelection = (atomId: string) => {
    setSelectedAtomIds(prev => {
      const next = new Set(prev);
      if (next.has(atomId)) {
        next.delete(atomId);
      } else {
        next.add(atomId);
      }
      return next;
    });
  };

  const selectAllDocs = () => {
    setSelectedDocIds(new Set(documents.map(d => d.id)));
  };

  const clearDocSelection = () => {
    setSelectedDocIds(new Set());
  };

  const selectAllAtoms = () => {
    setSelectedAtomIds(new Set(atoms.map(a => a.id)));
  };

  const clearAtomSelection = () => {
    setSelectedAtomIds(new Set());
  };

  // Get selected items for plan generation
  const getSelectedDocuments = (): UploadedDocument[] => {
    return documents.filter(d => selectedDocIds.has(d.id));
  };

  const getSelectedAtoms = (): KnowledgeAtom[] => {
    return atoms.filter(a => selectedAtomIds.has(a.id));
  };

  const handleGeneratePlan = async () => {
    if (!goal.trim()) {
      alert('Please enter a goal - what do you want to exist?');
      return;
    }

    const selectedDocs = getSelectedDocuments();
    const selectedAtomsList = getSelectedAtoms();

    if (selectedAtomsList.length === 0 && selectedDocs.length === 0) {
      alert('No context selected. Please select at least one document or atom.');
      return;
    }

    setLoading(true);
    try {
      const plan = await generateArchitecturalPlan(
        goal,
        selectedAtomsList,
        selectedDocs,
        plans,
        activeModel.id
      );
      setPlans(prev => [plan, ...prev]);
      setSelectedPlan(plan);
      setGoal('');
    } catch (e) {
      console.error('Plan generation failed:', e);
      alert('Failed to generate plan. Check console for details.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateHandoff = () => {
    if (!selectedPlan) return;
    const env = createHandoffEnvelope(selectedPlan, envelope ? [envelope] : []);
    setEnvelope(env);

    // Update plan status
    setPlans(prev =>
      prev.map(p =>
        p.planId === selectedPlan.planId
          ? { ...p, status: 'exported' as const }
          : p
      )
    );
    setSelectedPlan({ ...selectedPlan, status: 'exported' });
  };

  const handleExportMarkdown = () => {
    if (!selectedPlan) return;
    const markdown = exportPlanAsMarkdown(selectedPlan);
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${selectedPlan.planId}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleExportHandoff = () => {
    if (!envelope) return;
    const json = exportHandoffAsJson(envelope);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${envelope.envelopeId}_handoff.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full flex">
      {/* Left Panel: Goal Input & Plan List */}
      <div className="w-1/3 border-r border-slate-800 flex flex-col">
        {/* Goal Input */}
        <div className="p-4 border-b border-slate-800">
          <h2 className="text-lg font-semibold text-white mb-2">Architect</h2>
          <p className="text-sm text-slate-400 mb-4">
            Produce plans from your knowledge. The Implementation Service will build them.
          </p>

          {/* Context Selection */}
          <div className="mb-4 space-y-3">
            {/* Document Selector */}
            <div className="border border-slate-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setShowDocSelector(!showDocSelector)}
                className="w-full px-3 py-2 bg-slate-900 flex items-center justify-between hover:bg-slate-800 transition-colors"
              >
                <span className="flex items-center text-sm text-slate-300">
                  <DocumentTextIcon className="w-4 h-4 mr-2 text-indigo-400" />
                  Documents ({selectedDocIds.size}/{documents.length} selected)
                </span>
                {showDocSelector ? (
                  <ChevronUpIcon className="w-4 h-4 text-slate-500" />
                ) : (
                  <ChevronDownIcon className="w-4 h-4 text-slate-500" />
                )}
              </button>

              {showDocSelector && (
                <div className="border-t border-slate-700 bg-slate-950">
                  {/* Selection controls */}
                  <div className="px-3 py-2 flex space-x-2 border-b border-slate-800">
                    <button
                      onClick={selectAllDocs}
                      className="text-xs px-2 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded"
                    >
                      Select All
                    </button>
                    <button
                      onClick={clearDocSelection}
                      className="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded"
                    >
                      Clear
                    </button>
                  </div>

                  {/* Document list */}
                  <div className="max-h-40 overflow-y-auto">
                    {documents.length === 0 ? (
                      <p className="px-3 py-2 text-xs text-slate-500 italic">
                        No documents available. Upload documents in the Data view.
                      </p>
                    ) : (
                      documents.map(doc => (
                        <label
                          key={doc.id}
                          className="flex items-center px-3 py-2 hover:bg-slate-900 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedDocIds.has(doc.id)}
                            onChange={() => toggleDocSelection(doc.id)}
                            className="mr-2 rounded border-slate-600 bg-slate-800 text-indigo-500 focus:ring-indigo-500"
                          />
                          <span className="text-xs text-slate-300 truncate flex-1">
                            {doc.name}
                          </span>
                          <span className="text-xs text-slate-600 ml-2">
                            {(doc.size / 1024).toFixed(1)}KB
                          </span>
                        </label>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Atom Selector */}
            <div className="border border-slate-700 rounded-lg overflow-hidden">
              <button
                onClick={() => setShowAtomSelector(!showAtomSelector)}
                className="w-full px-3 py-2 bg-slate-900 flex items-center justify-between hover:bg-slate-800 transition-colors"
              >
                <span className="flex items-center text-sm text-slate-300">
                  <CubeIcon className="w-4 h-4 mr-2 text-emerald-400" />
                  Atoms ({selectedAtomIds.size}/{atoms.length} selected)
                </span>
                {showAtomSelector ? (
                  <ChevronUpIcon className="w-4 h-4 text-slate-500" />
                ) : (
                  <ChevronDownIcon className="w-4 h-4 text-slate-500" />
                )}
              </button>

              {showAtomSelector && (
                <div className="border-t border-slate-700 bg-slate-950">
                  {/* Selection controls */}
                  <div className="px-3 py-2 flex space-x-2 border-b border-slate-800">
                    <button
                      onClick={selectAllAtoms}
                      className="text-xs px-2 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded"
                    >
                      Select All
                    </button>
                    <button
                      onClick={clearAtomSelection}
                      className="text-xs px-2 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded"
                    >
                      Clear
                    </button>
                  </div>

                  {/* Atom list */}
                  <div className="max-h-40 overflow-y-auto">
                    {atoms.length === 0 ? (
                      <p className="px-3 py-2 text-xs text-slate-500 italic">
                        No atoms available. Create atoms in the Context or Enrichment views.
                      </p>
                    ) : (
                      atoms.map(atom => (
                        <label
                          key={atom.id}
                          className="flex items-start px-3 py-2 hover:bg-slate-900 cursor-pointer"
                        >
                          <input
                            type="checkbox"
                            checked={selectedAtomIds.has(atom.id)}
                            onChange={() => toggleAtomSelection(atom.id)}
                            className="mr-2 mt-0.5 rounded border-slate-600 bg-slate-800 text-emerald-500 focus:ring-emerald-500"
                          />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-slate-300 line-clamp-2">
                              {atom.content.substring(0, 100)}...
                            </p>
                            {atom.metadata?.theme && (
                              <span className="text-xs text-slate-600">
                                {atom.metadata.theme}
                              </span>
                            )}
                          </div>
                        </label>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Selection summary */}
            {(selectedDocIds.size > 0 || selectedAtomIds.size > 0) && (
              <div className="flex flex-wrap gap-1">
                {Array.from(selectedDocIds).map((id: string) => {
                  const doc = documents.find(d => d.id === id);
                  return doc ? (
                    <span
                      key={id}
                      className="inline-flex items-center px-2 py-0.5 bg-indigo-900/50 text-indigo-300 text-xs rounded-full"
                    >
                      {doc.name.substring(0, 15)}...
                      <button
                        onClick={() => toggleDocSelection(id)}
                        className="ml-1 hover:text-white"
                      >
                        <XMarkIcon className="w-3 h-3" />
                      </button>
                    </span>
                  ) : null;
                })}
                {Array.from(selectedAtomIds).slice(0, 3).map((id: string) => {
                  const atom = atoms.find(a => a.id === id);
                  return atom ? (
                    <span
                      key={id}
                      className="inline-flex items-center px-2 py-0.5 bg-emerald-900/50 text-emerald-300 text-xs rounded-full"
                    >
                      Atom
                      <button
                        onClick={() => toggleAtomSelection(id)}
                        className="ml-1 hover:text-white"
                      >
                        <XMarkIcon className="w-3 h-3" />
                      </button>
                    </span>
                  ) : null;
                })}
                {selectedAtomIds.size > 3 && (
                  <span className="text-xs text-slate-500">
                    +{selectedAtomIds.size - 3} more atoms
                  </span>
                )}
              </div>
            )}
          </div>

          <label className="block text-sm text-slate-300 mb-2">
            What do you want to exist?
          </label>
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="Describe the artifact, feature, or system you want to create..."
            className="w-full h-24 bg-slate-900 border border-slate-700 rounded-lg p-3 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
          />

          <button
            onClick={handleGeneratePlan}
            disabled={isLoading || !goal.trim()}
            className="mt-3 w-full py-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition-colors flex items-center justify-center"
          >
            {isLoading ? (
              <>
                <ArrowPathIcon className="w-4 h-4 mr-2 animate-spin" />
                Generating Plan...
              </>
            ) : (
              <>
                <ClipboardDocumentListIcon className="w-4 h-4 mr-2" />
                Generate Plan
              </>
            )}
          </button>
        </div>

        {/* Plan List */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-medium text-slate-400 mb-3">
            Plans ({plans.length})
          </h3>
          {plans.length === 0 ? (
            <p className="text-sm text-slate-600 italic">
              No plans generated yet. Enter a goal and generate your first plan.
            </p>
          ) : (
            <div className="space-y-2">
              {plans.map((plan) => (
                <button
                  key={plan.planId}
                  onClick={() => setSelectedPlan(plan)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${selectedPlan?.planId === plan.planId
                      ? 'bg-indigo-900/30 border-indigo-500'
                      : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                    }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-white truncate">{plan.goal}</p>
                      <p className="text-xs text-slate-500 mt-1">
                        {new Date(plan.createdAt).toLocaleString()}
                      </p>
                    </div>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${plan.status === 'draft'
                          ? 'bg-yellow-900/50 text-yellow-400'
                          : plan.status === 'exported'
                            ? 'bg-blue-900/50 text-blue-400'
                            : plan.status === 'certified'
                              ? 'bg-green-900/50 text-green-400'
                              : 'bg-red-900/50 text-red-400'
                        }`}
                    >
                      {plan.status}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Right Panel: Plan Details */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {selectedPlan ? (
          <>
            {/* Plan Header */}
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">
                  {selectedPlan.planId}
                </h2>
                <p className="text-sm text-slate-400">
                  {selectedPlan.implementationSteps.length} steps |{' '}
                  {selectedPlan.successCriteria.length} success criteria
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleExportMarkdown}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm rounded-lg flex items-center"
                >
                  <ArrowDownTrayIcon className="w-4 h-4 mr-1" />
                  Export MD
                </button>
                <button
                  onClick={handleCreateHandoff}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm rounded-lg flex items-center"
                >
                  <ArrowRightIcon className="w-4 h-4 mr-1" />
                  Create Handoff
                </button>
              </div>
            </div>

            {/* Plan Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-6">
              {/* Goal */}
              <section>
                <h3 className="text-sm font-medium text-indigo-400 mb-2">GOAL</h3>
                <p className="text-sm text-slate-200">{selectedPlan.goal}</p>
              </section>

              {/* Context */}
              <section>
                <h3 className="text-sm font-medium text-indigo-400 mb-2">CONTEXT</h3>
                <p className="text-sm text-slate-300">{selectedPlan.context}</p>
              </section>

              {/* Requirements */}
              <section>
                <h3 className="text-sm font-medium text-indigo-400 mb-2">REQUIREMENTS</h3>
                <ul className="space-y-1">
                  {selectedPlan.requirements.map((req, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-start">
                      <span className="text-indigo-500 mr-2">•</span>
                      {req}
                    </li>
                  ))}
                </ul>
              </section>

              {/* Implementation Steps */}
              <section>
                <h3 className="text-sm font-medium text-indigo-400 mb-3">
                  IMPLEMENTATION STEPS
                </h3>
                <div className="space-y-3">
                  {selectedPlan.implementationSteps.map((step, i) => (
                    <div
                      key={step.stepId}
                      className="p-3 bg-slate-900 rounded-lg border border-slate-800"
                    >
                      <div className="flex items-center mb-2">
                        <span className="w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center text-xs text-white font-medium mr-2">
                          {i + 1}
                        </span>
                        <span className="text-sm font-medium text-white">
                          {step.stepId}
                        </span>
                        {step.dependencies.length > 0 && (
                          <span className="ml-auto text-xs text-slate-500">
                            depends on: {step.dependencies.join(', ')}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-300 mb-2">{step.description}</p>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-slate-500">Inputs:</span>
                          <ul className="mt-1 text-slate-400">
                            {step.inputs.map((inp, j) => (
                              <li key={j}>• {inp}</li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <span className="text-slate-500">Outputs:</span>
                          <ul className="mt-1 text-slate-400">
                            {step.expectedOutputs.map((out, j) => (
                              <li key={j}>• {out}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Success Criteria */}
              <section>
                <h3 className="text-sm font-medium text-green-400 mb-2 flex items-center">
                  <CheckCircleIcon className="w-4 h-4 mr-1" />
                  SUCCESS CRITERIA
                </h3>
                <ul className="space-y-1">
                  {selectedPlan.successCriteria.map((criterion, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-start">
                      <span className="text-green-500 mr-2">✓</span>
                      {criterion}
                    </li>
                  ))}
                </ul>
              </section>

              {/* Failure Modes */}
              <section>
                <h3 className="text-sm font-medium text-red-400 mb-2 flex items-center">
                  <ExclamationCircleIcon className="w-4 h-4 mr-1" />
                  FAILURE MODES
                </h3>
                <ul className="space-y-1">
                  {selectedPlan.failureModes.map((mode, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-start">
                      <span className="text-red-500 mr-2">⚠</span>
                      {mode}
                    </li>
                  ))}
                </ul>
              </section>

              {/* Handoff Envelope (if created) */}
              {envelope && envelope.payload === selectedPlan && (
                <section className="p-4 bg-blue-900/20 rounded-lg border border-blue-800">
                  <h3 className="text-sm font-medium text-blue-400 mb-2 flex items-center">
                    <ArrowRightIcon className="w-4 h-4 mr-1" />
                    HANDOFF ENVELOPE CREATED
                  </h3>
                  <div className="text-xs text-slate-400 space-y-1">
                    <p>Envelope ID: {envelope.envelopeId}</p>
                    <p>To: {envelope.toService}</p>
                    <p>Cycle: {envelope.context.cycleCount}</p>
                  </div>
                  <button
                    onClick={handleExportHandoff}
                    className="mt-3 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg flex items-center"
                  >
                    <ArrowDownTrayIcon className="w-4 h-4 mr-1" />
                    Export Handoff JSON
                  </button>
                </section>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-slate-600">
            <div className="text-center">
              <ClipboardDocumentListIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Select a plan to view details</p>
              <p className="text-sm mt-1">or generate a new plan from the left panel</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ArchitectView;
