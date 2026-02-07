import { create } from 'zustand';
import type { WorkflowNode, WorkflowEdge, Viewport } from '@/lib/types/workflow';

interface CanvasStore {
  // Canvas state
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  selectedNodeId: string | null;

  // Viewport state
  viewport: Viewport;

  // UI state
  sidebarOpen: boolean;
  configPanelOpen: boolean;
  minimapOpen: boolean;

  // History for undo/redo
  past: Array<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] }>;
  future: Array<{ nodes: WorkflowNode[]; edges: WorkflowEdge[] }>;

  // Actions
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
  addNode: (node: WorkflowNode) => void;
  removeNode: (nodeId: string) => void;
  updateNode: (nodeId: string, data: Partial<WorkflowNode>) => void;
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (edgeId: string) => void;
  setSelectedNode: (nodeId: string | null) => void;
  setViewport: (viewport: Viewport) => void;
  toggleSidebar: () => void;
  toggleConfigPanel: () => void;
  toggleMinimap: () => void;
  autoLayout: () => void;
  fitToScreen: () => void;
  undo: () => void;
  redo: () => void;
  reset: () => void;
}

const initialViewport: Viewport = {
  x: 0,
  y: 0,
  zoom: 1,
};

export const useCanvasStore = create<CanvasStore>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  viewport: initialViewport,
  sidebarOpen: true,
  configPanelOpen: false,
  minimapOpen: true,
  past: [],
  future: [],

  setNodes: (nodes) => set({ nodes }),

  setEdges: (edges) => set({ edges }),

  addNode: (node) =>
    set((state) => {
      // Save state for undo
      const pastEntry = { nodes: state.nodes, edges: state.edges };
      return {
        nodes: [...state.nodes, node],
        past: [pastEntry, ...state.past].slice(0, 50),
        future: [],
      };
    }),

  removeNode: (nodeId) =>
    set((state) => {
      const pastEntry = { nodes: state.nodes, edges: state.edges };
      return {
        nodes: state.nodes.filter((n) => n.id !== nodeId),
        edges: state.edges.filter((e) => e.source !== nodeId && e.target !== nodeId),
        past: [pastEntry, ...state.past].slice(0, 50),
        future: [],
      };
    }),

  updateNode: (nodeId, data) =>
    set((state) => ({
      nodes: state.nodes.map((n) => (n.id === nodeId ? { ...n, ...data } : n)),
    })),

  addEdge: (edge) =>
    set((state) => {
      const pastEntry = { nodes: state.nodes, edges: state.edges };
      return {
        edges: [...state.edges, edge],
        past: [pastEntry, ...state.past].slice(0, 50),
        future: [],
      };
    }),

  removeEdge: (edgeId) =>
    set((state) => {
      const pastEntry = { nodes: state.nodes, edges: state.edges };
      return {
        edges: state.edges.filter((e) => e.id !== edgeId),
        past: [pastEntry, ...state.past].slice(0, 50),
        future: [],
      };
    }),

  setSelectedNode: (nodeId) => set({ selectedNodeId: nodeId }),

  setViewport: (viewport) => set({ viewport }),

  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  toggleConfigPanel: () => set((state) => ({ configPanelOpen: !state.configPanelOpen })),

  toggleMinimap: () => set((state) => ({ minimapOpen: !state.minimapOpen })),

  autoLayout: () =>
    set((state) => {
      // Simple vertical layout algorithm
      const nodes = state.nodes.map((node, index) => ({
        ...node,
        position: { x: 400, y: index * 150 },
      }));
      return { nodes };
    }),

  fitToScreen: () => set({ viewport: { x: 0, y: 0, zoom: 1 } }),

  undo: () =>
    set((state) => {
      if (state.past.length === 0) return state;
      const previous = state.past[0];
      const newPast = state.past.slice(1);
      return {
        nodes: previous.nodes,
        edges: previous.edges,
        past: newPast,
        future: [{ nodes: state.nodes, edges: state.edges }, ...state.future],
      };
    }),

  redo: () =>
    set((state) => {
      if (state.future.length === 0) return state;
      const next = state.future[0];
      const newFuture = state.future.slice(1);
      return {
        nodes: next.nodes,
        edges: next.edges,
        past: [{ nodes: state.nodes, edges: state.edges }, ...state.past],
        future: newFuture,
      };
    }),

  reset: () =>
    set({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      viewport: initialViewport,
      sidebarOpen: true,
      configPanelOpen: false,
      minimapOpen: true,
      past: [],
      future: [],
    }),
}));
