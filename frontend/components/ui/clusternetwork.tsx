'use client';

import React from 'react';
import { ThreeEvent } from '@react-three/fiber';
import { GraphCanvas, darkTheme, InternalGraphNode, GraphNode } from 'reagraph';
import { NetworkProps, DataObject, convertToNodes, Node } from '@/components/dataobject';

const nodes = [
    { id: 'n-1', label: 'Node 1', data: { type: 'A', url: 'https://example.com/1' } },
    { id: 'n-2', label: 'Node 2', data: { type: 'B', url: 'https://example.com/2' } },
    { id: 'n-3', label: 'Node 3', data: { type: 'A', url: 'https://example.com/3' } },
    { id: 'n-4', label: 'Node 4', data: { type: 'B', url: 'https://example.com/4' } },
    { id: 'n-5', label: 'Node 5', data: { type: 'A', url: 'https://example.com/5' } },
    { id: 'n-6', label: 'Node 6', data: { type: 'B', url: 'https://example.com/6' } }
];

export const ClusterNetwork = ({data}  : NetworkProps) => {

    const nodes = convertToNodes(data);
    const edges : GraphNode[] = [];

    // Handle node click by opening the node's URL
    const handleNodeClick = (node: InternalGraphNode, props?: any, event?: ThreeEvent<MouseEvent>) => {
        // Extract URL from the clicked node's data
        const nodeData = node.data;
        if (nodeData && nodeData.url) {
            window.open(nodeData.url, '_blank');  // Open URL in a new tab
        }
    };

    return (
        <>
            <div
                style={{
                    width: '60vw',
                    height: '500px',
                    position: 'relative',
                    border: '1px solid #EA5925',
                    overflow: 'hidden',
                    borderRadius: '10px',
                }}
            >
                <GraphCanvas
                    theme={darkTheme}
                    nodes={nodes}
                    draggable
                    edges={[{
                        source: 'n-6',
                        target: 'n-1',
                        id: 'n-6-n-1',
                        label: 'n-6-n-1'
                    }]}
                    clusterAttribute="type"
                    constrainDragging={false}
                    onNodeClick={handleNodeClick}
                />
            </div>
            <div
                style={{
                    zIndex: 9,
                    position: 'absolute',
                    top: 15,
                    right: 15
                }}
            >
            </div>
        </>
    );
};
