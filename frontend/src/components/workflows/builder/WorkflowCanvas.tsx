// Workflow Canvas - React Flow Integration

'use client';

import React, { useCallback, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  MarkerType,
  ReactFlowProvider,
  Panel,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { useCanvasStore } from '@/lib/stores/canvas-store';
import { useWorkflowStore } from '@/lib/stores/workflow-store';
import { StepNode } from './nodes/StepNode';
import { Button } from '@/components/ui/button';
import { ZoomIn, ZoomOut, Maximize, Undo, Redo } from 'lucide-react';

const nodeTypes = {
  stepNode: StepNode,
};

interface WorkflowCanvasProps {
  workflowId?: string;
}

function WorkflowCanvasInner({ workflowId }: WorkflowCanvasProps) {
  const {
    nodes: storeNodes,
    edges: storeEdges,
    viewport,
    minimapOpen,
    setNodes,
    setEdges,
    addEdge: addStoreEdge,
    updateNode,
    setSelectedNode,
    fitToScreen,
    undo,
    redo,
  } = useCanvasStore();

  const { setHasUnsavedChanges } = useWorkflowStore();

  // Convert store nodes to React Flow format
  const initialNodes: Node[] = useMemo(
    () =>
      storeNodes.map((node) => ({
        id: node.id,
        type: 'stepNode',
        position: node.position,
        data: node.data,
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      })),
    [storeNodes]
  );

  const initialEdges: Edge[] = useMemo(
    () =>
      storeEdges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        animated: edge.type === 'conditional',
        label: edge.label,
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
        style: {
          stroke: edge.type === 'conditional' ? '#f97316' : '#94a3b8',
          strokeWidth: 2,
        },
      })),
    [storeEdges]
  );

  const [nodes, setNodesState, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdgesState, onEdgesChange] = useEdgesState(initialEdges);

  // Sync changes back to store
  useEffect(() => {
    setNodes(
      nodes.map((node) => ({
        id: node.id,
        type: node.data.type as any,
        position: node.position,
        data: node.data as any,
      }))
    );
  }, [nodes, setNodes]);

  useEffect(() => {
    setEdges(
      edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.type as any,
        label: edge.label as any,
      }))
    );
  }, [edges, setEdges]);

  // Handle new connections
  const onConnect: OnConnect = useCallback(
    (connection: Connection) => {
      const newEdge = {
        id: `e-${connection.source}-${connection.target}`,
        source: connection.source!,
        target: connection.target!,
        type: 'default' as const,
      };
      addStoreEdge(newEdge as any);
      setHasUnsavedChanges(true);
    },
    [addStoreEdge, setHasUnsavedChanges]
  );

  // Handle node selection
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedNode(node.id);
    },
    [setSelectedNode]
  );

  // Handle canvas click (deselect)
  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, [setSelectedNode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S: Save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        // Trigger save - will be handled by parent component
      }

      // Delete: Remove selected node
      if (e.key === 'Delete' || e.key === 'Backspace') {
        // Get selected node from store and remove
        const selectedNodeId = useCanvasStore.getState().selectedNodeId;
        if (selectedNodeId) {
          useCanvasStore.getState().removeNode(selectedNodeId);
          setSelectedNode(null);
          setHasUnsavedChanges(true);
        }
      }

      // Ctrl/Cmd + Z: Undo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
        setHasUnsavedChanges(true);
      }

      // Ctrl/Cmd + Shift + Z: Redo
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && e.shiftKey) {
        e.preventDefault();
        redo();
        setHasUnsavedChanges(true);
      }

      // Escape: Deselect
      if (e.key === 'Escape') {
        setSelectedNode(null);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [undo, redo, setSelectedNode, setHasUnsavedChanges]);

  const handleFitToScreen = useCallback(() => {
    fitToScreen();
  }, [fitToScreen]);

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        defaultViewport={viewport}
        minZoom={0.1}
        maxZoom={2}
        deleteKeyCode="Delete"
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />

        {/* Custom Controls */}
        <Panel position="top-right" className="flex flex-col gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => useCanvasStore.getState().autoLayout()}
            title="Auto Layout"
          >
            <Maximize className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={handleFitToScreen}
            title="Fit to Screen"
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={undo}
            disabled={useCanvasStore.getState().past.length === 0}
            title="Undo (Ctrl+Z)"
          >
            <Undo className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={redo}
            disabled={useCanvasStore.getState().future.length === 0}
            title="Redo (Ctrl+Shift+Z)"
          >
            <Redo className="h-4 w-4" />
          </Button>
        </Panel>

        {/* Minimap */}
        {minimapOpen && (
          <MiniMap
            nodeColor={(node) => {
              switch (node.data.type) {
                case 'trigger':
                  return '#3b82f6';
                case 'action':
                  return '#22c55e';
                case 'condition':
                  return '#f97316';
                case 'wait':
                  return '#a855f7';
                case 'goal':
                  return '#ec4899';
                default:
                  return '#94a3b8';
              }
            }}
            maskColor="rgba(0, 0, 0, 0.05)"
            pannable
            zoomable
          />
        )}

        {/* Controls */}
        <Controls />
      </ReactFlow>
    </div>
  );
}

// Wrapper with ReactFlowProvider
export function WorkflowCanvas(props: WorkflowCanvasProps) {
  return (
    <ReactFlowProvider>
      <WorkflowCanvasInner {...props} />
    </ReactFlowProvider>
  );
}
